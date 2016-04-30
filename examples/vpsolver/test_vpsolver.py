#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function

inf = float("inf")


def test_vbpsolver():
    """Test vbpsolver."""
    from pyvpsolver import VPSolver
    from pyvpsolver.solvers import vbpsolver
    W, w, b = (1,), [(1,)], [1]
    lp_file = VPSolver.new_tmp_file(".lp")
    mps_file = VPSolver.new_tmp_file(".mps")
    svg_file = VPSolver.new_tmp_file(".svg")

    solution = vbpsolver.solve(W, w, b, script="vpsolver_glpk.sh")
    vbpsolver.print_solution(solution)
    obj, patterns = solution
    assert obj == 1

    solution = vbpsolver.solve(
        W, w, b, lp_file=lp_file, mps_file=mps_file, svg_file=svg_file,
        script="vpsolver_glpk.sh"
    )
    vbpsolver.print_solution(solution)
    obj, patterns = solution
    assert obj == 1


def test_mvpsolvers():
    """Test mvpsolvers."""
    from pyvpsolver import VPSolver
    from pyvpsolver.solvers import mvpsolver2013, mvpsolver2016
    Ws, Cs, Qs, ws, b = [(1,)], [1], [inf], [[(1,)]], [1]
    for mvpsolver in [mvpsolver2013, mvpsolver2016]:
        solution = mvpsolver.solve(
            Ws, Cs, Qs, ws, b, script="vpsolver_glpk.sh"
        )
        mvpsolver.print_solution(solution)
        obj, patterns = solution
        assert obj == 1

        lp_file = VPSolver.new_tmp_file(".lp")
        mps_file = VPSolver.new_tmp_file(".mps")
        svg_file = VPSolver.new_tmp_file(".svg")

        solution = mvpsolver.solve(
            Ws, Cs, Qs, ws, b, lp_file=lp_file, mps_file=mps_file,
            svg_file=svg_file, script="vpsolver_glpk.sh"
        )
        mvpsolver.print_solution(solution)
        obj, patterns = solution
        assert obj == 1


def test_scripts():
    """Test scripts."""
    from pyvpsolver import VPSolver, VBP, MVP, AFG, LP, MPS
    VPSolver.clear()
    vbp = VBP(W=(1,), w=[(1,)], b=[1], verbose=True)
    mvp = MVP(Ws=[(1,)], Cs=[1], Qs=[inf], ws=[[(1,)]], b=[1], verbose=True)
    for instance in [vbp, mvp]:
        afg = AFG(instance, verbose=True)
        lp = LP(afg, verbose=True)
        mps = MPS(afg, verbose=True)
        VPSolver.set_verbose(False)
        output, solution = VPSolver.script("vpsolver_glpk.sh", instance)
        assert solution[0] == 1
        if isinstance(instance, VBP):
            instance_file = instance.vbp_file
        elif isinstance(instance, MVP):
            instance_file = instance.mvp_file
        output, solution = VPSolver.script("vpsolver_glpk.sh", instance_file)
        assert solution[0] == 1
        output, solution = VPSolver.script("vpsolver_glpk.sh", afg)
        assert solution[0] == 1
        output, solution = VPSolver.script("vpsolver_glpk.sh", afg, lp)
        assert solution[0] == 1
        output, solution = VPSolver.script("vpsolver_glpk.sh", afg, mps)
        assert solution[0] == 1
        output, solution = VPSolver.script("vpsolver_glpk.sh", lp)
        assert solution is None
        output, solution = VPSolver.script("vpsolver_glpk.sh", mps)
        assert solution is None
        output, solution = VPSolver.script("vpsolver_glpk.sh", afg.afg_file)
        assert solution[0] == 1
        output, solution = VPSolver.script("vpsolver_glpk.sh", lp.lp_file)
        assert solution is None
        output, solution = VPSolver.script("vpsolver_glpk.sh", mps.mps_file)
        assert solution is None


def test_draw():
    """Test scripts."""
    from pyvpsolver import VPSolver, VBP, MVP, AFG
    vbp = VBP(W=(1,), w=[(1,)], b=[1])
    mvp = MVP(Ws=[(1,)], Cs=[1], Qs=[inf], ws=[[(1,)]], b=[1])
    svg_file = VPSolver.new_tmp_file(".svg")
    for instance in [vbp, mvp]:
        afg = AFG(instance)
        try:
            afg.draw(svg_file, lpaths=True)
        except Exception as e:
            print(repr(e))


def test_lowlevel():
    """Test low-level API."""
    from pyvpsolver import VPSolver, VBP, MVP, AFG
    vbp = VBP(W=(1,), w=[(1,)], b=[1])
    mvp = MVP(Ws=[(1,)], Cs=[1], Qs=[inf], ws=[[(1,)]], b=[1])
    afg_file = VPSolver.new_tmp_file(".afg")
    lp_file = VPSolver.new_tmp_file(".lp")
    mps_file = VPSolver.new_tmp_file(".mps")
    VPSolver.vbp2afg(vbp, afg_file)
    VPSolver.vbp2afg(mvp, afg_file)
    VPSolver.vbp2afg(vbp.vbp_file, afg_file)
    VPSolver.vbp2afg(mvp.mvp_file, afg_file)
    VPSolver.afg2lp(afg_file, lp_file)
    VPSolver.afg2mps(afg_file, mps_file)
    VPSolver.afg2lp(AFG(vbp), lp_file)
    VPSolver.afg2mps(AFG(mvp), mps_file)


if __name__ == "__main__":
    test_vbpsolver()
    test_mvpsolvers()
    test_scripts()
    test_draw()
    test_lowlevel()
