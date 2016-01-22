"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2015, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
from builtins import map
from builtins import range
from builtins import object

import os
import sys
import signal
import atexit
import shutil
import tempfile
import subprocess
from .graphutils import AFGraph

inf = float("inf")


class VBP(object):
    """Wrapper for .vbp files."""

    def __init__(self, W, w, b, verbose=None):
        self.vbp_file = VPSolver.new_tmp_file(".vbp")
        with open(self.vbp_file, "w") as f:
            if isinstance(W, int):
                W = [W]
            else:
                W = list(W)
            # ndims
            print(len(W), file=f)
            # W
            print(" ".join(map(str, W)), file=f)
            # m
            print(len(w), file=f)
            # items
            for i in range(len(w)):
                if isinstance(w[i], int):
                    row = [w[i], b[i]]
                else:
                    row = list(w[i])+[b[i]]
                assert len(row) == len(W)+1
                print(" ".join(map(str, row)), file=f)
        if verbose:
            with open(self.vbp_file, "r") as f:
                print(f.read())
        self.m = len(b)
        self.ndims = len(W)
        self.W, self.w, self.b = W, w, b

    @classmethod
    def from_file(cls, vbp_file, verbose=None):
        with open(vbp_file, "r") as f:
            lst = list(map(int, f.read().split()))
            ndims = lst.pop(0)
            W = lst[:ndims]
            lst = lst[ndims:]
            m = lst.pop(0)
            w, b = [], []
            for i in range(m):
                w.append(lst[:ndims])
                lst = lst[ndims:]
                b.append(lst.pop(0))
            assert lst == []
        return cls(W, w, b, verbose)

    def __del__(self):
        try:
            os.remove(self.vbp_file)
        except:
            pass


class MVP(object):
    """Wrapper for .mvp files."""

    def __init__(self, Ws, Cs, Qs, ws, b, verbose=None):
        self.mvp_file = VPSolver.new_tmp_file(".mvp")
        with open(self.mvp_file, "w") as f:
            # ndims
            ndims = len(Ws[0])
            print(ndims, file=f)
            # nbtypes
            print(len(Ws), file=f)
            assert len(Ws) == len(Cs)
            assert len(Ws) == len(Qs)
            # Ws, Cs, Qs
            for Wi, Ci, Qi in zip(Ws, Cs, Qs):
                assert len(Wi) == ndims
                if Qi == inf:
                    Qi = -1
                print(" ".join(map(str, list(Wi)+[Ci]+[Qi])), file=f)
            # m
            assert len(ws) == len(b)
            print(len(ws), file=f)
            # items
            for i in range(len(ws)):
                print("{} {}".format(len(ws[i]), b[i]), file=f)
                for w in ws[i]:
                    assert len(w) == ndims
                    print(" ".join(map(str, w)), file=f)
        if verbose:
            with open(self.mvp_file, "r") as f:
                print(f.read())
        self.m = len(b)
        self.ndims = ndims
        self.Ws, self.Cs, self.Qs = Ws, Cs, Qs
        self.ws, self.b = ws, b

    @classmethod
    def from_file(cls, mvp_file, verbose=None):
        with open(mvp_file, "r") as f:
            lst = list(map(int, f.read().split()))
            ndims = lst.pop(0)
            nbtypes = lst.pop(0)
            Ws, Cs, Qs = [], [], []
            for i in range(nbtypes):
                Ws.append(lst[:ndims])
                lst = lst[ndims:]
                Cs.append(lst.pop(0))
                Qs.append(lst.pop(0))
            m = lst.pop(0)
            ws, b = [], []
            for i in range(m):
                ws.append([])
                qi = lst.pop(0)
                bi = lst.pop(0)
                b.append(bi)
                for j in range(qi):
                    ws[i].append(lst[:ndims])
                    lst = lst[ndims:]
            assert lst == []
        return cls(Ws, Cs, Qs, ws, b, verbose)

    def __del__(self):
        try:
            os.remove(self.vbp_file)
        except:
            pass


class AFG(object):
    """Wrapper for .afg files."""

    def __init__(
            self, instance, compress=-2, binary=False, vtype="I",
            verbose=None):
        assert isinstance(instance, (VBP, MVP))
        self.instance = instance
        self.afg_file = VPSolver.new_tmp_file(".afg")
        if isinstance(instance, VBP):
            instance_file = instance.vbp_file
        elif isinstance(instance, MVP):
            instance_file = instance.mvp_file
        self.output = VPSolver.vbp2afg(
            instance_file, self.afg_file, compress, binary, vtype,
            verbose=verbose
        )
        self.V, self.A, self.S, self.T = None, None, None, None

    def graph(self):
        """Returns the graph as an AFGraph object."""
        return AFGraph.from_file(self.afg_file)

    def __del__(self):
        try:
            os.remove(self.afg_file)
        except:
            pass


class MPS(object):
    """Wrapper for .mps files."""

    def __init__(self, graph, verbose=None):
        assert isinstance(graph, AFG)
        self.afg_graph = graph
        self.mps_file = VPSolver.new_tmp_file(".mps")
        self.output = VPSolver.afg2mps(
            graph.afg_file, self.mps_file, verbose=verbose
        )

    def __del__(self):
        try:
            os.remove(self.mps_file)
        except:
            pass


class LP(object):
    """Wrapper for .lp files."""

    def __init__(self, graph, verbose=None):
        assert isinstance(graph, AFG)
        self.afg_graph = graph
        self.lp_file = VPSolver.new_tmp_file(".lp")
        self.output = VPSolver.afg2lp(
            graph.afg_file, self.lp_file, verbose=verbose
        )

    def __del__(self):
        try:
            os.remove(self.lp_file)
        except:
            pass


class VPSolver(object):
    """Tools for calling VPSolver binaries and scripts."""

    VPSOLVER_PATH = "vpsolver"
    VBP2AFG_PATH = "vbp2afg"
    AFG2MPS_PATH = "afg2mps"
    AFG2LP_PATH = "afg2lp"
    VBPSOL_PATH = "vbpsol"

    TMP_DIR = tempfile.mkdtemp()
    TMP_CNT = 0
    PLIST = []
    VERBOSE = True

    @staticmethod
    def set_verbose(verbose):
        """Enables/disables verbose output."""
        if verbose is not None:
            VPSolver.VERBOSE = verbose

    @staticmethod
    def new_tmp_file(ext="tmp"):
        """Creates temporary files."""
        if not ext.startswith("."):
            ext = ".{}".format(ext)
        fname = "{}/{}{}".format(VPSolver.TMP_DIR, VPSolver.TMP_CNT, ext)
        VPSolver.TMP_CNT += 1
        return fname

    @staticmethod
    @atexit.register
    def clear():
        """Deletes temporary files and kills child processes."""
        for p in VPSolver.PLIST:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except:
                pass
        try:
            shutil.rmtree(VPSolver.TMP_DIR)
        except:
            pass

    @staticmethod
    def log(msg, verbose=None):
        """Log function."""
        if verbose is None:
            verbose = VPSolver.VERBOSE
        if verbose:
            print(msg)

    @staticmethod
    def run(cmd, tee=None, grep=None, grepv=None, verbose=None):
        """Runs system commands."""
        if verbose is None:
            verbose = VPSolver.VERBOSE

        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        VPSolver.PLIST.append(proc)

        def pipe_output(fin, fout_list, grep=None, grepv=None):
            while True:
                line = fin.readline().decode("utf-8")
                if not line:
                    break
                if grep is not None and grep not in line:
                    continue
                if grepv is not None and grepv in line:
                    continue
                for f in fout_list:
                    f.write(line)
                    f.flush()

        if tee is None:
            if verbose:
                pipe_output(proc.stdout, [sys.stdout], grep, grepv)
        else:
            with open(tee, "w") as ftee:
                if verbose:
                    pipe_output(proc.stdout, [sys.stdout, ftee], grep, grepv)
                else:
                    pipe_output(proc.stdout, [ftee], grep, grepv)

        exit_code = proc.wait()
        proc.stdout.close()
        if exit_code != 0:
            raise Exception("failed to run '{}'".format(cmd))

    @staticmethod
    def parse_vbpsol(vpsol_output):
        """Transforms 'vbpsol' plaintext solutions into python data."""
        marker = "PYSOL="
        if marker in vpsol_output:
            vpsol_output = vpsol_output[vpsol_output.find(marker)+len(marker):]
            vpsol_output = vpsol_output[:vpsol_output.find("\n")]
            obj, sol = eval(vpsol_output)
            return obj, sol
        else:
            return None

    @staticmethod
    def vbpsol(afg_file, sol_file, opts="0 1", verbose=None):
        """Calls 'vbpsol' to extract vector packing solutions."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.VBPSOL_PATH, afg_file, sol_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return VPSolver.parse_vbpsol(output)

    @staticmethod
    def vpsolver(
            instance_file, compress=-2, binary=False, vtype="I",
            print_inst=False, pyout=True, verbose=None):
        """Calls 'vpsolver' to solve .vbp instances."""
        if isinstance(instance_file, VBP):
            instance_file = instance_file.vbp_file
        elif isinstance(instance_file, MVP):
            instance_file = instance_file.mvp_file
        out_file = VPSolver.new_tmp_file()
        opts = "{:d} {:d} {} {:d} {:d}".format(
            compress, binary, vtype, print_inst, pyout
        )
        VPSolver.run(
            "{} {} {}".format(VPSolver.VPSOLVER_PATH, instance_file, opts),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)

    @staticmethod
    def vbp2afg(
            instance_file, afg_file, compress=-2, binary=False, vtype="I",
            verbose=None):
        """Calls 'vbp2afg' to create arc-flow graphs for .vbp instances."""
        if isinstance(instance_file, VBP):
            instance_file = instance_file.vbp_file
        elif isinstance(instance_file, MVP):
            instance_file = instance_file.mvp_file
        out_file = VPSolver.new_tmp_file()
        opts = "{} {} {}".format(compress, binary, vtype)
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.VBP2AFG_PATH, instance_file, afg_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output

    @staticmethod
    def afg2mps(afg_file, mps_file, opts="", verbose=None):
        """Calls 'afg2mps' to create .mps models for arc-flow graphs."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.AFG2MPS_PATH, afg_file, mps_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output

    @staticmethod
    def afg2lp(afg_file, lp_file, opts="", verbose=None):
        """Calls 'afg2lp' to create .lp models for arc-flow graphs."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.AFG2LP_PATH, afg_file, lp_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output

    @staticmethod
    def script(script_name, arg1=None, arg2=None, options=None, verbose=None):
        """Calls VPSolver scripts and returns vector packing solutions."""
        cmd = script_name
        for arg in [arg1, arg2]:
            if isinstance(arg, MPS):
                cmd += " --mps {}".format(arg.mps_file)
            elif isinstance(arg, LP):
                cmd += " --lp {}".format(arg.lp_file)
            elif isinstance(arg, AFG):
                cmd += " --afg {}".format(arg.afg_file)
            elif isinstance(arg, VBP):
                cmd += " --vbp {}".format(arg.vbp_file)
            elif isinstance(arg, MVP):
                cmd += " --mvp {}".format(arg.mvp_file)
            elif isinstance(arg, str):
                if arg.endswith(".mps"):
                    cmd += " --mps {}".format(arg)
                elif arg.endswith(".lp"):
                    cmd += " --lp {}".format(arg)
                elif arg.endswith(".afg"):
                    cmd += " --afg {}".format(arg)
                elif arg.endswith(".vbp"):
                    cmd += " --vbp {}".format(arg)
                elif arg.endswith(".mvp"):
                    cmd += " --mvp {}".format(arg)
                else:
                    raise Exception("Invalid file extension!")
        if options is not None:
            cmd += " --options \"{}\"".format(options)
        cmd += " --pyout"
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(cmd, tee=out_file, verbose=verbose)
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)

    @staticmethod
    def script_wsol(script_name, model, options=None, verbose=None):
        """Calls VPSolver scripts and returns arc-flow solutions."""
        cmd = script_name
        if isinstance(model, MPS):
            cmd += " --mps {}".format(model.mps_file)
        elif isinstance(model, LP):
            cmd += " --lp {}".format(model.lp_file)
        elif isinstance(model, str):
            if model.endswith(".mps"):
                cmd += " --mps {}".format(model)
            elif model.endswith(".lp"):
                cmd += " --lp {}".format(model)
            else:
                raise Exception("Invalid file extension!")
        if options is not None:
            cmd += " --options \"{}\"".format(options)
        out_file = VPSolver.new_tmp_file()
        sol_file = VPSolver.new_tmp_file(".sol")
        VPSolver.run(
            "{} --wsol {}".format(cmd, sol_file),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        try:
            with open(sol_file) as f:
                sol = f.read().split()
                values = {}
                assert len(sol) % 2 == 0
                for i in range(0, len(sol), 2):
                    var, value = sol[i], float(sol[i+1])
                    if int(value) == value:
                        value = int(value)
                    if value != 0:
                        values[var] = value
            os.remove(sol_file)
        except:
            values = None
        return output, values


def signal_handler(signal_, frame):
    """Signal handler for a cleaner exit."""
    print("signal received: {}".format(signal_))
    VPSolver.clear()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
