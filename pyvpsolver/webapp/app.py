#!/usr/bin/env python
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).
"""
from __future__ import print_function
from builtins import str
from builtins import object

import os
import sys
import flask
import signal
from flask import Flask, Response
from flask import render_template, json, request, redirect, url_for
from multiprocessing import Process
from pyvpsolver import VPSolver, VBP, MVP, AFG, LP
from pympl import PyMPL

DEBUG = False
PORT = 5555

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        PORT = int(sys.argv[1])

app = Flask(__name__)
app.debug = True


@app.context_processor
def inject_globals():
    """Send global data to templates."""
    data = dict(
        app_name="VPSolver App",
        pages=[
            ("/vbp", "Vector Packing"),
            ("/mvp", "Multiple-choice"),
        ],
    )
    return data


@app.route("/favicon.ico")
def favicon():
    """Favicon route."""
    return flask.send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/")
def index():
    """Render the index page."""
    return redirect(url_for("vbp"))


def load(fname):
    """Load a text file as a string."""
    with open(fname, "r") as f:
        return f.read().strip("\n")


@app.route("/vbp/", defaults={"example": None})
@app.route("/vbp/<example>")
def vbp(example):
    """Render the input page for VBP."""
    title = "Vector Packing"

    example_folder = os.path.join(os.path.dirname(__file__), "data", "examples", "vbp")
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
                input_data = load(os.path.join(example_folder, fname))
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


@app.route("/mvp/", defaults={"example": None})
@app.route("/mvp/<example>")
def mvp(example):
    """Render the input page for MVP."""
    title = "Multiple-choice Vector Packing"

    example_folder = os.path.join(os.path.dirname(__file__), "data", "examples", "mvp")
    examples = [
        ("/mvp/", "", None),
        ("/mvp/vsbpp", "VSBPP", "vsbpp.mvp"),
        ("/mvp/mvp", "MVP", "mvp.mvp"),
    ]

    input_data = ""
    for url, description, fname in examples:
        if request.path == url:
            if fname is not None:
                input_data = load(os.path.join(example_folder, fname))
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
        solver_url="/solve/mvp",
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
        print("Input:\n{0}\n\nOutput:".format(input_))
        output.flush()

    if app_name == "vbp":
        tmpfile = VPSolver.new_tmp_file(ext=".vbp")
        with open(tmpfile, "w") as f:
            f.write(input_)
        instance = VBP.from_file(tmpfile, verbose=False)
        afg = AFG(instance, verbose=True)
        lp_model = LP(afg, verbose=False)
        out, sol = VPSolver.script(
            form["script"], lp_model, afg, pyout=False, verbose=True
        )
    elif app_name == "mvp":
        tmpfile = VPSolver.new_tmp_file(ext=".mvp")
        with open(tmpfile, "w") as f:
            f.write(input_)
        instance = MVP.from_file(tmpfile, verbose=False)
        afg = AFG(instance, verbose=True)
        lp_model = LP(afg, verbose=False)
        out, sol = VPSolver.script(
            form["script"], lp_model, afg, pyout=False, verbose=True
        )

    print("EOF\n")
    output.flush()


class IterativeOutput(object):
    """Iterable class for retrieving workers output"""

    def __init__(self, target, args):
        rfd, wfd = os.pipe()
        args += (os.fdopen(wfd, "w"),)
        self.proc = Process(target=target, args=args)
        self.proc.start()
        self.output = os.fdopen(rfd, "r")

    def __iter__(self):
        """Retrieve the output iteratively."""
        for line in iter(self.output.readline, "EOF\n"):
            yield line.rstrip() + "\n"
        if not self.proc.is_alive():
            print("DONE {0}!".format(self.proc.pid))

    def __del__(self):
        try:
            print("TERMINATE {0}!".format(self.proc.pid))
            os.kill(self.proc.pid, signal.SIGTERM)
            # self.proc.terminate()
        except:
            pass


@app.route("/solve/<app_name>", methods=["POST"])
def solve(app_name):
    """Render the solver page."""
    try:
        args = (app_name, request.method, request.form, request.args)
        return Response(IterativeOutput(solve_worker, args), mimetype="text/plain")
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        pass


def get_ip_address():
    """Return the ip address of 'eth0'."""
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == "__main__":
    print("URL: http://{0}:{1}/".format(get_ip_address(), PORT))
    app.run(host="0.0.0.0", port=PORT, threaded=True)
