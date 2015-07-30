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

import os
import sys
import signal
import atexit
import shutil
import tempfile
import subprocess
from .graphutils import AFGraph


class VBP(object):
    """Wrapper for .vbp files."""

    def __init__(self, W, w, b, verbose=None):
        self.vbp_file = VPSolver.new_tmp_file(".vbp")
        with open(self.vbp_file, "w") as f:
            if isinstance(W, int):
                W = [W]
            else:
                W = list(W)
            print >>f, len(W)
            print >>f, " ".join(map(str, W))
            print >>f, len(w)
            for i in xrange(len(w)):
                if isinstance(w[i], int):
                    row = [w[i], b[i]]
                else:
                    row = list(w[i])+[b[i]]
                assert len(row) == len(W)+1
                print >>f, " ".join(map(str, row))
        if verbose:
            with open(self.vbp_file, "r") as f:
                print f.read()
        self.m = len(b)
        self.ndims = len(W)
        self.W, self.w, self.b = W, w, b

    @classmethod
    def from_file(cls, vbp_file, verbose=None):
        with open(vbp_file, "r") as f:
            lst = map(int, f.read().split())
            ndims = lst.pop(0)
            W = lst[:ndims]
            lst = lst[ndims:]
            m = lst.pop(0)
            w, b = [], []
            for i in xrange(m):
                w.append(lst[:ndims])
                lst = lst[ndims:]
                b.append(lst.pop(0))
        return cls(W, w, b, verbose)

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
        assert isinstance(instance, VBP)
        self.instance = instance
        self.afg_file = VPSolver.new_tmp_file(".afg")
        self.output = VPSolver.vbp2afg(
            instance.vbp_file, self.afg_file, compress, binary, vtype,
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

    VPSOLVER = "vpsolver"
    VBP2AFG = "vbp2afg"
    AFG2MPS = "afg2mps"
    AFG2LP = "afg2lp"
    VBPSOL = "vbpsol"

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
            ext = ".{0}".format(ext)
        fname = "{0}/{1}{2}".format(VPSolver.TMP_DIR, VPSolver.TMP_CNT, ext)
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
            print msg

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
                line = fin.readline()
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
        if exit_code != 0:
            raise Exception("failed to run '{0}'".format(cmd))

    @staticmethod
    def parse_vbpsol(vpsol_output):
        """Transforms 'vbpsol' plaintext solutions into python data."""
        try:
            s = vpsol_output.strip()
            lst = s[s.rfind("Objective:"):].split("\n")
            lst[0] = lst[0].replace("Objective: ", "")
            obj = int(lst[0])
            lst = lst[2:]
            lst = map(lambda x: x.split("x"), lst)
            sol = []
            for mult, pat in lst:
                mult = int(mult)
                pat = pat.replace("i=", "")
                pat = pat.replace("[", "").replace("]", "")
                pat = map(lambda x: int(x)-1, pat.split(","))
                sol.append((mult, pat))
        except:
            return None
        return obj, sol

    @staticmethod
    def vbpsol(afg_file, sol_file, opts="", verbose=None):
        """Calls 'vbpsol' to extract vector packing solutions."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{0} {1} {2} {3}".format(
                VPSolver.VBPSOL, afg_file, sol_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output

    @staticmethod
    def vpsolver(vbp_file, compress=-2, binary=False, vtype="I", verbose=None):
        """Calls 'vpsolver' to solve .vbp instances."""
        if isinstance(vbp_file, VBP):
            vbp_file = vbp_file.vbp_file
        out_file = VPSolver.new_tmp_file()
        opts = "{0} {1} {2}".format(compress, binary, vtype)
        VPSolver.run(
            "{0} {1} {2}".format(VPSolver.VPSOLVER, vbp_file, opts),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)

    @staticmethod
    def vbp2afg(
            vbp_file, afg_file, compress=-2, binary=False, vtype="I",
            verbose=None):
        """Calls 'vbp2afg' to create arc-flow graphs for .vbp instances."""
        if isinstance(vbp_file, VBP):
            vbp_file = vbp_file.vbp_file
        out_file = VPSolver.new_tmp_file()
        opts = "{0} {1} {2}".format(compress, binary, vtype)
        VPSolver.run(
            "{0} {1} {2} {3}".format(
                VPSolver.VBP2AFG, vbp_file, afg_file, opts
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
            "{0} {1} {2} {3}".format(
                VPSolver.AFG2MPS, afg_file, mps_file, opts
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
            "{0} {1} {2} {3}".format(VPSolver.AFG2LP, afg_file, lp_file, opts),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output

    @staticmethod
    def script(script_name, arg1=None, arg2=None, verbose=None):
        """Calls VPSolver scripts and returns vector packing solutions."""
        cmd = script_name
        for arg in [arg1, arg2]:
            if isinstance(arg, MPS):
                cmd += " --mps {0}".format(arg.mps_file)
            elif isinstance(arg, LP):
                cmd += " --lp {0}".format(arg.lp_file)
            elif isinstance(arg, AFG):
                cmd += " --afg {0}".format(arg.afg_file)
            elif isinstance(arg, VBP):
                cmd += " --vbp {0}".format(arg.vbp_file)
            elif isinstance(arg, str):
                if arg.endswith(".mps"):
                    cmd += " --mps {0}".format(arg)
                elif arg.endswith(".lp"):
                    cmd += " --lp {0}".format(arg)
                elif arg.endswith(".afg"):
                    cmd += " --afg {0}".format(arg)
                elif arg.endswith(".vbp"):
                    cmd += " --vbp {0}".format(arg)
                else:
                    raise Exception("Invalid file extension!")
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(cmd, tee=out_file, verbose=verbose)
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)

    @staticmethod
    def script_wsol(script_name, model, verbose=None):
        """Calls VPSolver scripts and returns arc-flow solutions."""
        cmd = script_name
        if isinstance(model, MPS):
            cmd += " --mps {0}".format(model.mps_file)
        elif isinstance(model, LP):
            cmd += " --lp {0}".format(model.lp_file)
        elif isinstance(model, str):
            if model.endswith(".mps"):
                cmd += " --mps {0}".format(model)
            elif model.endswith(".lp"):
                cmd += " --lp {0}".format(model)
            else:
                raise Exception("Invalid file extension!")
        out_file = VPSolver.new_tmp_file()
        sol_file = VPSolver.new_tmp_file(".sol")
        VPSolver.run(
            "{0} --wsol {1}".format(cmd, sol_file),
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
                for i in xrange(0, len(sol), 2):
                    var, value = sol[i], float(sol[i+1])
                    if abs(round(value)-value) < 1e-5:
                        value = int(round(value))
                    if value != 0:
                        values[var] = value
            os.remove(sol_file)
        except:
            values = None
        return output, values


def signal_handler(signal_, frame):
    """Signal handler for a cleaner exit."""
    print "signal received: {0}".format(signal_)
    VPSolver.clear()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
