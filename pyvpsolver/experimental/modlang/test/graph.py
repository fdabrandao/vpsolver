#!/usr/bin/python
import sys
sys.path.insert(0, "../../../../")

from pyvpsolver.experimental.modlang import *

ampl = ParserAMPL("graph.mod")
ampl.writeMOD("tmp/graph.out.mod")
glpk_mod2lp(ampl.model_file, "tmp/graph.lp")
out, varvalues = VPSolver.script_wsol(
    "vpsolver_gurobi.sh", "tmp/graph.lp", verbose=True
)
sol, varvalues = ampl.FLOW.extract(varvalues, verbose=True)
print
print "sol:", sol
print "varvalues:", [(k, v) for k, v in sorted(varvalues.items())]
print

os.system("glpsol --math " + ampl.model_file + "| grep -v Generating")
