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
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)
import sys
sys.path.insert(0, "../../")

import flask
from flask import Flask, Response
from flask import render_template, json, request, redirect, url_for
from multiprocessing import Process
from pyvpsolver import VPSolver, VBP, AFG, LP
from pyvpsolver.modlang import AMPLParser
import signal

app = Flask(__name__)
app.debug = True

DEBUG = False


@app.context_processor
def inject_globals():
    """Sends global data to templates."""
    data = dict(
        app_name="VPSolver APP",
        pages=[
            ("/vbp", "Vector Packing"),
            ("/modlang", "ModLang"),
        ],
    )
    return data


@app.route("/favicon.ico")
def favicon():
    """Favicon route."""
    return flask.send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico", mimetype='image/vnd.microsoft.icon'
    )


@app.route("/")
def index():
    """Renders the index page."""
    return redirect(url_for("vbp"))


def load(fname):
    """Loads a text file as a string."""
    with open(fname, "r") as f:
        return f.read().strip("\n")


@app.route("/vbp/", defaults={"example": None})
@app.route("/vbp/<example>")
def vbp(example):
    """Renders the input page."""
    title = "Vector Packing"

    example_folder = "data/examples/vbp/"
    examples = [
        ("/vbp/", "", None),
        ("/vbp/bpp", "BPP", "bpp.vbp"),
        ("/vbp/csp", "CSP", "csp.vbp"),
        ("/vbp/vbp", "VBP", "vbp.vbp"),
    ]

    input_data = ""
    for url, description, fname in examples:
        if request.path == url:
            if fname is not None:
                input_data = load(example_folder+fname)
            break

    scripts = [
        ("vpsolver_glpk.sh", "GLPK"),
        ("vpsolver_gurobi.sh", "GUROBI"),
        ("vpsolver_cplex.sh", "CPLEX"),
        ("vpsolver_coinor.sh", "COIN-OR"),
        ("vpsolver_lpsolve.sh", "LPSOLVE"),
        ("vpsolver_scip.sh", "SCIP"),
    ]

    return render_template(
        "input.html",
        title=title,
        examples=examples,
        scripts=scripts,
        input_data=input_data,
        solver_url="/solve/vbp",
    )


@app.route("/modlang/", defaults={"example": None})
@app.route("/modlang/<example>")
def modlang(example):
    """Renders the input page."""
    title = "ModLang: AMPL extension"

    example_folder = "data/examples/modlang/"
    examples = [
        ("/modlang/", "", None),
        ("/modlang/example1", "Cutting Stock", "example1.mod"),
        ("/modlang/example2", "Variable Sized Bin Packing", "example2.mod"),
    ]

    input_data = ""
    for url, description, fname in examples:
        if request.path == url:
            if fname is not None:
                input_data = load(example_folder+fname)
            break

    return render_template(
        "input.html",
        title=title,
        examples=examples,
        input_data=input_data,
        solver_url="/solve/modlang",
    )


def solve_worker(app_name, method, form, args, output=sys.stdout):
    """Worker for solving the problem in a separate process."""
    VPSolver.PLIST = []

    def signal_handler(sig, frame):
        """Signal handler for cleaner exit."""
        for p in VPSolver.PLIST:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except Exception as e:
                pass
        sys.exit(0)
    signal.signal(signal.SIGTERM, signal_handler)

    sys.stdout = output
    sys.stderr = output
    input_ = form["input"].strip("\n")
    if DEBUG:
        print "Input:\n{0}\n\nOutput:".format(input_)
        sys.stdout.flush()
        sys.stderr.flush()

    if app_name == "vbp":
        tmpfile = VPSolver.new_tmp_file(ext=".vbp")
        with open(tmpfile, "w") as f:
            f.write(input_)
        instance = VBP.fromFile(tmpfile, verbose=False)
        afg = AFG(instance, verbose=True)
        lp_model = LP(afg, verbose=False)
        out, sol = VPSolver.script(form["script"], lp_model, afg, verbose=True)
    elif app_name == "modlang":
        tmpfile = VPSolver.new_tmp_file(ext=".mod")
        parser = AMPLParser()
        parser.input = input_
        parser.parse()
        parser.write(tmpfile)
        VPSolver.run("glpsol --math {0} | grep -v Generating".format(tmpfile))

    print "EOF"


class IterativeOutput(object):
    """Iterable class for retrieving workers output"""
    def __init__(self, target, args):
        rfd, wfd = os.pipe()
        args += (os.fdopen(wfd, "w"),)
        self.proc = Process(target=target, args=args)
        self.proc.start()
        self.output = os.fdopen(rfd, "r")

    def __iter__(self):
        """Retrieves the output iteratively."""
        for line in iter(self.output.readline, "EOF\n"):
            yield line.rstrip() + "\n"
        if not self.proc.is_alive():
            yield "DONE!\n"

    def __del__(self):
        try:
            print "TERMINATE %d!" % self.proc.pid
            os.kill(self.proc.pid, signal.SIGTERM)
            # self.proc.terminate()
        except:
            pass


@app.route("/solve/<app_name>", methods=["POST"])
def solve(app_name):
    """Renders the solver page."""
    try:
        args = (app_name, request.method, request.form, request.args)
        return Response(
            IterativeOutput(solve_worker, args), mimetype="text/plain"
        )
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, threaded=True)
