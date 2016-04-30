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
from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from builtins import object
import six

import os
import sys
import signal
import atexit
import shutil
import tempfile
import subprocess
from .afgraph import AFGraph
from .utils import inf, get_opt


class VBP(object):
    """
    Wrapper for .vbp files.
    """

    def __init__(self, W, w, b, binary=False, verbose=False):
        self.vbp_file = VPSolver.new_tmp_file(".vbp")
        with open(self.vbp_file, "w") as f:
            print(len(W), file=f)  # ndims
            print(" ".join(map(str, W)), file=f)  # W
            print(len(w), file=f)  # m
            for i in range(len(w)):  # items
                row = list(w[i])+[b[i]]
                assert len(row) == len(W)+1
                print(" ".join(map(str, row)), file=f)
            print("BINARY{{{:d}}};".format(binary), file=f)
        if verbose:
            with open(self.vbp_file, "r") as f:
                print(f.read())
        self.m = len(b)
        self.ndims = len(W)
        self.binary = binary
        self.W, self.w, self.b = W, w, b
        self.labels = list(range(self.m))

    @classmethod
    def from_str(cls, content, binary=None, verbose=None):
        lst = content.split()
        for i in range(len(lst)):
            try:
                assert int(lst[i]) == float(lst[i])
                lst[i] = int(lst[i])
            except:
                break
        ndims = lst.pop(0)
        W = lst[:ndims]
        lst = lst[ndims:]
        m = lst.pop(0)
        w, b = [], []
        for i in range(m):
            w.append(lst[:ndims])
            lst = lst[ndims:]
            b.append(lst.pop(0))
        if binary is None:
            binary = bool(int(get_opt("BINARY", content, False)))
        assert lst == [] or str(lst[0]).startswith("$")
        return cls(W, w, b, binary, verbose)

    @classmethod
    def from_file(cls, vbp_file, binary=None, verbose=None):
        with open(vbp_file, "r") as f:
            return cls.from_str(f.read(), binary=None, verbose=None)

    @property
    def filename(self):
        """Return the filename."""
        return self.vbp_file

    def weights(self):
        """Return item weights."""
        return {i: tuple(self.w[i]) for i in range(self.m)}

    def capacities(self):
        """Return bin capacities."""
        return [tuple(self.W)]

    def __del__(self):
        try:
            os.remove(self.vbp_file)
        except:
            pass


class MVP(object):
    """
    Wrapper for .mvp files.
    """

    def __init__(self, Ws, Cs, Qs, ws, b, binary=False, verbose=False):
        self.mvp_file = VPSolver.new_tmp_file(".mvp")
        with open(self.mvp_file, "w") as f:
            ndims = len(Ws[0])
            print(ndims, file=f)  # ndims
            print(len(Ws), file=f)  # nbtypes
            assert len(Ws) == len(Cs)
            assert len(Ws) == len(Qs)
            for Wi, Ci, Qi in zip(Ws, Cs, Qs):  # Ws, Cs, Qs
                assert len(Wi) == ndims
                if Qi == inf:
                    Qi = -1
                print(" ".join(map(str, list(Wi)+[Ci]+[Qi])), file=f)
            assert len(ws) == len(b)
            print(len(ws), file=f)  # m
            p = 0
            for i in range(len(ws)):  # items
                print("{} {}".format(len(ws[i]), b[i]), file=f)
                for j, w in enumerate(ws[i]):
                    assert len(w) == ndims
                    print(" ".join(map(str, w)), file=f)
                    p += 1
            print("BINARY{{{:d}}};".format(binary), file=f)
        if verbose:
            with open(self.mvp_file, "r") as f:
                print(f.read())
        self.m = len(b)
        self.ndims = ndims
        self.binary = binary
        self.Ws, self.Cs, self.Qs = Ws, Cs, Qs
        self.ws, self.b = ws, b
        self.labels = [
            (i, j)
            for i in range(len(self.ws))
            for j in range(len(self.ws[i]))
        ]

    @classmethod
    def from_str(cls, content, binary=None, verbose=None):
        lst = content.split()
        for i in range(len(lst)):
            try:
                assert int(lst[i]) == float(lst[i])
                lst[i] = int(lst[i])
            except:
                break
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
        if binary is None:
            binary = bool(int(get_opt("BINARY", content, False)))
        assert lst == [] or str(lst[0]).startswith("$")
        return cls(Ws, Cs, Qs, ws, b, binary, verbose)

    @classmethod
    def from_file(cls, mvp_file, binary=None, verbose=None):
        with open(mvp_file, "r") as f:
            return cls.from_str(f.read(), binary=None, verbose=None)

    @property
    def filename(self):
        """Return the filename."""
        return self.mvp_file

    def weights(self):
        """Return item weights."""
        return {
            (i, j): tuple(self.ws[i][j])
            for i in range(len(self.ws))
            for j in range(len(self.ws[i]))
        }

    def capacities(self):
        """Return bin capacities."""
        return list(map(tuple, self.Ws))

    def __del__(self):
        try:
            os.remove(self.mvp_file)
        except:
            pass


class AFG(object):
    """
    Wrapper for .afg files.
    """

    def __init__(self, instance, method=-3, binary=None, vtype="I",
                 verbose=None):
        assert isinstance(instance, (VBP, MVP))
        self.instance = instance
        self.afg_file = VPSolver.new_tmp_file(".afg")
        if isinstance(instance, (VBP, MVP)):
            instance_file = instance.filename
            binary = instance.binary
        self.output = VPSolver.vbp2afg(
            instance_file, self.filename, method, binary, vtype,
            verbose=verbose
        )

    def graph(self):
        """Return the graph as an AFGraph object."""
        with open(self.filename, "r") as f:
            content = f.read()
        labels = self.instance.labels
        S = int(get_opt("S", content))
        Ts = list(map(int, get_opt("Ts", content).split(",")))
        ids = list(map(int, get_opt("IDS", content).split(",")))
        arcs = list(map(int, get_opt("ARCS", content).split()))
        LOSS = int(get_opt("LOSS", content))
        V, A = set([]), []
        for i in range(0, len(arcs), 3):
            u, v, i = arcs[i:i+3]
            V.add(u)
            V.add(v)
            if i == LOSS:
                A.append((u, v, LOSS))
            else:
                A.append((u, v, labels[ids[i]]))
        return AFGraph(V, A, S, Ts, LOSS)

    def draw(self, svg_file, lpaths=False, graph_attrs=None, verbose=False):
        """Draw the arc-flow graph in .svg format."""
        if lpaths:
            weights = self.instance.weights()
            capacities = self.instance.capacities()
        else:
            weights = None
            capacities = None
        self.graph().draw(
            svg_file, weights=weights, capacities=capacities, lpaths=lpaths,
            graph_attrs=graph_attrs, verbose=verbose
        )

    @property
    def filename(self):
        """Return the filename."""
        return self.afg_file

    def __del__(self):
        try:
            os.remove(self.afg_file)
        except:
            pass


class MPS(object):
    """
    Wrapper for .mps files.
    """

    def __init__(self, graph, verbose=None):
        assert isinstance(graph, AFG)
        self.afg_graph = graph
        self.mps_file = VPSolver.new_tmp_file(".mps")
        self.output = VPSolver.afg2mps(
            graph.filename, self.filename, verbose=verbose
        )

    @property
    def filename(self):
        """Return the filename."""
        return self.mps_file

    def __del__(self):
        try:
            os.remove(self.mps_file)
        except:
            pass


class LP(object):
    """
    Wrapper for .lp files.
    """

    def __init__(self, graph, verbose=None):
        assert isinstance(graph, AFG)
        self.afg_graph = graph
        self.lp_file = VPSolver.new_tmp_file(".lp")
        self.output = VPSolver.afg2lp(
            graph.filename, self.filename, verbose=verbose
        )

    @property
    def filename(self):
        """Return the filename."""
        return self.lp_file

    def __del__(self):
        try:
            os.remove(self.lp_file)
        except:
            pass


class VPSolver(object):
    """
    Tools for calling VPSolver binaries and scripts.
    """

    VPSOLVER_EXEC = "vpsolver"
    VBP2AFG_EXEC = "vbp2afg"
    AFG2MPS_EXEC = "afg2mps"
    AFG2LP_EXEC = "afg2lp"
    VBPSOL_EXEC = "vbpsol"

    TMP_DIR = tempfile.mkdtemp()
    TMP_CNT = 0
    PLIST = []
    VERBOSE = True

    @staticmethod
    def set_verbose(verbose):
        """Enable/disable verbose output."""
        if verbose is not None:
            VPSolver.VERBOSE = verbose

    @staticmethod
    def new_tmp_file(ext="tmp"):
        """Create a temporary file."""
        if not ext.startswith("."):
            ext = ".{}".format(ext)
        fname = "{}/{}{}".format(VPSolver.TMP_DIR, VPSolver.TMP_CNT, ext)
        VPSolver.TMP_CNT += 1
        if not os.path.exists(VPSolver.TMP_DIR):
            os.makedirs(VPSolver.TMP_DIR)
        return fname

    @staticmethod
    @atexit.register
    def clear():
        """Delete temporary files and kills child processes."""
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
        """Log message."""
        if verbose is None:
            verbose = VPSolver.VERBOSE
        if verbose:
            print(msg)

    @staticmethod
    def run(cmd, tee=None, grep=None, grepv=None, verbose=None):
        """Run a system command."""
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
                    if f is sys.stdout and line.startswith("PYSOL="):
                        continue
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
            raise RuntimeError("failed to run '{}'".format(cmd))

    @staticmethod
    def parse_vbpsol(vpsol_output):
        """Transform 'vbpsol' plaintext solutions into python data."""
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
        """Call 'vbpsol' to extract vector packing solutions."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.filename
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.VBPSOL_EXEC, afg_file, sol_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return VPSolver.parse_vbpsol(output)

    @staticmethod
    def vpsolver(instance_file, method=-3, binary=None, vtype="I",
                 print_inst=False, pyout=True, verbose=None):
        """Call 'vpsolver' to solve .vbp instances."""
        if isinstance(instance_file, (VBP, MVP)):
            if binary is None:
                binary = int(instance_file.binary)
            instance_file = instance_file.filename
        if binary is None:
            binary = -1
        out_file = VPSolver.new_tmp_file()
        opts = "{:d} {:d} {} {:d} {:d}".format(
            method, binary, vtype, print_inst, pyout
        )
        VPSolver.run(
            "{} {} {}".format(VPSolver.VPSOLVER_EXEC, instance_file, opts),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)

    @staticmethod
    def vbp2afg(instance_file, afg_file, method=-3, binary=None, vtype="I",
                verbose=None):
        """Call 'vbp2afg' to create arc-flow graphs for .vbp instances."""
        if isinstance(instance_file, (VBP, MVP)):
            if binary is None:
                binary = int(instance_file.binary)
            instance_file = instance_file.filename
        if binary is None:
            binary = -1
        out_file = VPSolver.new_tmp_file()
        opts = "{:d} {:d} {}".format(method, binary, vtype)
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.VBP2AFG_EXEC, instance_file, afg_file, opts
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
        """Call 'afg2mps' to create .mps models for arc-flow graphs."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.filename
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.AFG2MPS_EXEC, afg_file, mps_file, opts
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
        """Call 'afg2lp' to create .lp models for arc-flow graphs."""
        if isinstance(afg_file, AFG):
            afg_file = afg_file.filename
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(
            "{} {} {} {}".format(
                VPSolver.AFG2LP_EXEC, afg_file, lp_file, opts
            ),
            tee=out_file,
            verbose=verbose
        )
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output

    @staticmethod
    def script(script_name, arg1=None, arg2=None, options=None, pyout=True,
               verbose=None):
        """Call a VPSolver scripts and return a vector packing solution."""
        cmd = script_name
        for arg in [arg1, arg2]:
            if isinstance(arg, MPS):
                cmd += " --mps {}".format(arg.filename)
            elif isinstance(arg, LP):
                cmd += " --lp {}".format(arg.filename)
            elif isinstance(arg, AFG):
                cmd += " --afg {}".format(arg.filename)
            elif isinstance(arg, VBP):
                cmd += " --vbp {}".format(arg.filename)
            elif isinstance(arg, MVP):
                cmd += " --mvp {}".format(arg.filename)
            elif isinstance(arg, six.string_types):
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
        if pyout is True:
            cmd += " --pyout"
        out_file = VPSolver.new_tmp_file()
        VPSolver.run(cmd, tee=out_file, verbose=verbose)
        with open(out_file) as f:
            output = f.read()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)

    @staticmethod
    def script_wsol(script_name, model, options=None, verbose=None):
        """Call a VPSolver script and return an arc-flow solution."""
        cmd = script_name
        if isinstance(model, MPS):
            cmd += " --mps {}".format(model.filename)
        elif isinstance(model, LP):
            cmd += " --lp {}".format(model.filename)
        elif isinstance(model, six.string_types):
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
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
