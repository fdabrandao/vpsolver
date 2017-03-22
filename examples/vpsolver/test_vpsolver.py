#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2017, Filipe Brandao
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
    vbpsolver.print_solution(obj, patterns)


def test_mvpsolvers():
    """Test mvpsolvers."""
    from pyvpsolver import VPSolver
    from pyvpsolver.solvers import mvpsolver2013, mvpsolver2016
    Ws = [(100, 75), (75, 50), (75, 50), (100, 100)]
    Cs = [3, 2, 3, 100]
    Qs = [inf, -1, -1, -1]
    ws = [[(75, 50)], [(40, 75), (25, 25)]]
    b = [2, 1]
    for mvpsolver in [mvpsolver2013, mvpsolver2016]:
        solution = mvpsolver.solve(
            Ws, Cs, Qs, ws, b, script="vpsolver_glpk.sh"
        )
        mvpsolver.print_solution(solution)
        obj, patterns = solution
        assert obj == 5

        lp_file = VPSolver.new_tmp_file(".lp")
        mps_file = VPSolver.new_tmp_file(".mps")
        svg_file = VPSolver.new_tmp_file(".svg")

        solution = mvpsolver.solve(
            Ws, Cs, Qs, ws, b, lp_file=lp_file, mps_file=mps_file,
            svg_file=svg_file, script="vpsolver_glpk.sh", verbose=True
        )
        mvpsolver.print_solution(solution)
        obj, patterns = solution
        assert obj == 5
        mvpsolver.print_solution(obj, patterns)


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
        output, solution = VPSolver.script(
            "vpsolver_glpk.sh", instance, options="--seed 1234"
        )
        assert solution[0] == 1
        if isinstance(instance, (VBP, MVP)):
            instance_file = instance.filename
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
        output, solution = VPSolver.script("vpsolver_glpk.sh", afg.filename)
        assert solution[0] == 1
        output, solution = VPSolver.script("vpsolver_glpk.sh", lp.filename)
        assert solution is None
        output, solution = VPSolver.script("vpsolver_glpk.sh", mps.filename)
        assert solution is None


def test_vbpsol():
    """Test vbpsol."""
    from pyvpsolver import VPSolver, VBP, MVP, AFG, LP, MPS
    vbp = VBP(W=(1,), w=[(1,)], b=[1], verbose=True)
    afg = AFG(vbp, verbose=True)
    lp = LP(afg, verbose=True)
    sol_file = VPSolver.new_tmp_file(".sol")
    output, solution = VPSolver.script_wsol("vpsolver_glpk.sh", lp)
    assert isinstance(solution, dict)
    with open(sol_file, "w") as f:
        lst = []
        for var, value in solution.items():
            lst.append(str(var))
            lst.append(str(value))
        print(" ".join(lst), file=f)
    obj, patterns = VPSolver.vbpsol(afg, sol_file)
    assert obj == 1


def test_draw():
    """Test scripts."""
    from pyvpsolver import VPSolver, VBP, MVP, AFG
    vbp = VBP(W=(1,), w=[(1,)], b=[1])
    mvp = MVP(Ws=[(1,)], Cs=[1], Qs=[inf], ws=[[(1,)]], b=[1])
    svg_file = VPSolver.new_tmp_file(".svg")
    for instance in [vbp, mvp]:
        afg = AFG(instance)
        try:
            afg.draw(
                svg_file, lpaths=True, graph_attrs={"size": "8,8"}
            )
        except Exception as e:
            print(repr(e))
        try:
            VPSolver.afg2svg(afg, svg_file)
        except Exception as e:
            print(repr(e))
        try:
            VPSolver.afg2svg(afg.filename, svg_file)
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
    svg_file = VPSolver.new_tmp_file(".svg")
    VPSolver.vbp2afg(vbp, afg_file)
    VPSolver.vbp2afg(mvp, afg_file)
    VPSolver.vbp2afg(vbp.filename, afg_file)
    VPSolver.vbp2afg(mvp.filename, afg_file)
    VPSolver.afg2lp(afg_file, lp_file)
    VPSolver.afg2mps(afg_file, mps_file)
    VPSolver.afg2lp(AFG(vbp), lp_file)
    VPSolver.afg2mps(AFG(mvp), mps_file)


if __name__ == "__main__":
    test_vbpsolver()
    test_mvpsolvers()
    test_scripts()
    test_vbpsol()
    test_draw()
    test_lowlevel()
