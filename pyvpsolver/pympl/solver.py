"""
This code is part of the Mathematical Programming Toolbox PyMPL.

Copyright (C) 2015-2015, Filipe Brandao
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
from builtins import range
from builtins import object

import os
import sys
import signal
import atexit
import shutil
import tempfile
import subprocess


class Solver(object):
    """Tools for calling solver wrappers."""

    TMP_DIR = tempfile.mkdtemp()
    TMP_CNT = 0
    PLIST = []
    VERBOSE = True

    @staticmethod
    def set_verbose(verbose):
        """Enables/disables verbose output."""
        if verbose is not None:
            Solver.VERBOSE = verbose

    @staticmethod
    def new_tmp_file(ext="tmp"):
        """Creates temporary files."""
        if not ext.startswith("."):
            ext = ".{0}".format(ext)
        fname = "{0}/{1}{2}".format(Solver.TMP_DIR, Solver.TMP_CNT, ext)
        Solver.TMP_CNT += 1
        return fname

    @staticmethod
    @atexit.register
    def clear():
        """Deletes temporary files and kills child processes."""
        for p in Solver.PLIST:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except:
                pass
        try:
            shutil.rmtree(Solver.TMP_DIR)
        except:
            pass

    @staticmethod
    def log(msg, verbose=None):
        """Log function."""
        if verbose is None:
            verbose = Solver.VERBOSE
        if verbose:
            print(msg)

    @staticmethod
    def run(cmd, tee=None, grep=None, grepv=None, verbose=None):
        """Runs system commands."""
        if verbose is None:
            verbose = Solver.VERBOSE

        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )
        Solver.PLIST.append(proc)

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
        if exit_code != 0:
            raise Exception("failed to run '{0}'".format(cmd))

    @staticmethod
    def script_wsol(script_name, model, options=None, verbose=None):
        """Calls solver scripts and returns the solutions."""
        cmd = script_name
        if model.endswith(".mps"):
            cmd += " --mps {0}".format(model)
        elif model.endswith(".lp"):
            cmd += " --lp {0}".format(model)
        else:
            raise Exception("Invalid file extension!")
        if options is not None:
            cmd += " --options \"{0}\"".format(options)
        out_file = Solver.new_tmp_file()
        sol_file = Solver.new_tmp_file(".sol")
        Solver.run(
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
    print("signal received: {0}".format(signal_))
    Solver.clear()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
