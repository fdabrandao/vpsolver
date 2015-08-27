## Python API

The VPSolver Python API has 3 levels:

* [High-level API](#high-level-api): high level wrapper functions, easy and direct usage;
* [Mid-level API](#mid-level-api): objects that wrap calls to VPSolver executables;
* [Low-level API](#low-level-api): direct calls to VPSolver scripts and executables.

### High-level API

Example:

```python
from pyvpsolver.solvers import vbpsolver

W = (5180, 2)
w = [(1120,1), (1250,1), (520,1), (1066,1), (1000,1), (1150,1)]
b = [9, 5, 91, 18, 11, 64]

# Solve a vector packing instance:
obj, sol = vbpsolver.solve(
    W, w, b, verbose=False, script="vpsolver_glpk.sh"
)
print "obj:", obj
print "sol:", sol
vbpsolver.print_solution(obj, sol)
```

The high level API (`pyvpsolver.solvers`) includes two solvers: `vbpsolver` (for vector packing) and `mvbpsolver` (for multiple-choice vector packing).

#### Vector Packing Solver functions

How to import: 

* `from pyvpsolver.solvers import vbpsolver`.

How to use:

* `obj, sol = vbpsolver.solve(W, w, b, verbose=False, script="vpsolver_glpk.sh")`
    * Important arguments:
        * `W`: Bin capacity;
        * `w`: Item weights;
        * `b`: Item demands;
        * `script`: VPSolver script that will be used to solve the model.
    * Returns:
        * `obj`: objective value;
        * `sol`: solution.
* `vbpsolver.print_solution(obj, sol)`
    * Important arguments:
        * `obj`: objective value;
        * `sol`: solution.
    * Outputs:
        * The solution formatted.

Examples: [example_vbp.py](https://github.com/fdabrandao/vpsolver/blob/master/examples/vpsolver/example_vbp.py).

#### Multiple-choice Vector Packing Solver functions

How to import:

* `from pyvpsolver.solvers import mvbpsolver`.

How to use:

* `obj, lst_sol = mvbpsolver.solve(Ws, Cs, Qs, ws, b, verbose=False, script="vpsolver_glpk.sh")`
    * Important arguments:
        * `Ws`: Bin capacities;
        * `Cs`: Bin costs;
        * `Qs`: Number of bins available;
        * `ws`: Item weights;
        * `b`: Item demands;
        * `script`: VPSolver script that will be used to solve the model.
    * Returns:
        * `obj`: objective value;
        * `lst_sol`: a list with solutions for each bin.

* `mvbpsolver.print_solution(obj, lst_sol)`
    * Important arguments:
        * `obj`: objective value
        * `sol`: solution
    * Outputs:
        * The solution formatted.

Examples: [example_mvbp.py](https://github.com/fdabrandao/vpsolver/blob/master/examples/vpsolver/example_mvbp.py) and [example_vsbpp.py](https://github.com/fdabrandao/vpsolver/blob/master/examples/vpsolver/example_vsbpp.py).

### Mid-level API

Example:

```python
from pyvpsolver import VPSolver          # from low-level API
from pyvpsolver import VBP, AFG, MPS, LP # from mid-level API
from pyvpsolver.solvers import vbpsolver # from high-level API

# Create a vector packing instance:
instance = VBP(
    [5180], # bin capacity
    [1120, 1250, 520, 1066, 1000, 1150], # item weights
    [9, 5, 91, 18, 11, 64], # item demands
    verbose=False
)

# Create an arc-flow graph for the instance:
afg = AFG(instanceA, verbose=False)

# Create .mps model for the graph:
mps_model = MPS(afg, verbose=False)

# Solve the model an extract the solution:
out, solution = VPSolver.script("vpsolver_glpk.sh", mps_model, afg, verbose=True)

# Print the solution:
obj, sol = solution
vbpsolver.print_solution(obj, sol)
``` 

How to import:

* `from pyvpsolver import VBP, AFG, MPS, LP`.

Objects:

* `VBP` objects: `VBP(W, w, b, verbose=None)`
    * Important arguments:
        * `W`: Bin capacity;
        * `w`: Item weights;
        * `b`: Item demands.      

* `AFG` objects: `AFG(instance, verbose=None)`
    * Important arguments:
        * `instance`: a `VBP` object.
    * Creates:
        * an arc-flow graph for the vector packing instance.

* `MPS` objects: `MPS(graph, verbose=None)`
    * Important arguments:
        * `graph`: an `AFG` object.
    * Creates:
        * an MPS model.

* `LP` objects: `LP(graph, verbose=None)`
    * Important arguments:
        * `graph`: an `AFG` object.
    * Creates:
        * a LP model.

Examples: [example.py](https://github.com/fdabrandao/vpsolver/blob/master/examples/vpsolver/example.py).

### Low-level API

How to import:

* `from pyvpsolver import VPSolver`.

How to use:

* `VPSolver.vbp2afg(vbp_file, afg_file, verbose=None)`
    * Description: creates arc-flow graphs for vector packing instances.
    * Important arguments:
        * `vbp_file`: a .vbp file or a `VBP` object;
        * `afg_file`: a .afg file.
    * Actions:
        * calls `bin/vbp2afg` to write an arc-flow graph for `vbp_file` in `afg_file`.

* `VPSolver.afg2mps(afg_file, mps_file, verbose=None)`
    * Description: converts arc-flow grafts to MPS models.
    * Important arguments:
        * `afg_file`: a .afg file or a `AFG` object;
        * `mps_file`: a .mps file.
    * Actions:
        * calls `bin/afg2mps` to write the MPS model for `afg_file` in `mps_file`.

* `VPSolver.afg2lp(afg_file, lp_file, verbose=None)`
    * Description: converts arc-flow grafts to LP models.
    * Important arguments:
        * `afg_file`: a .afg file or a `AFG` object;
        * `mps_file`: a .lp file.
    * Actions:
        * calls `bin/afg2lp` to write the LP model for `afg_file` in `lp_file`.

* `VPSolver.vbpsol(afg_file, sol_file, verbose=None)`
    * Description: extracts a vector packing solution from an arc-flow solution.
    * Important arguments:
        * `afg_file`: a .afg file or a `AFG` object;
        * `sol_file`: a .sol solution file.
    * Actions:
        * calls `bin/vbpsol` to extract the vector packing solution from the arc-flow solution `sol_file` associated with the graph `afg_file`.

* `VPSolver.vpsolver(vbp_file, verbose=None)`
    * Description: calls VPSolver.
    * Important arguments:
        * `vbp_file`: a .vbp file or a `VBP` object;.
    * Actions:
        * calls `bin/vpsolver` to solve an instance (requires Gurobi).

* `output, solution = VPSolver.script(script_name, arg1=None, arg2=None, verbose=None)`
    * Description: calls VPSolver scripts.
    * Important arguments:
        * `script_name`: vpsolver script name (e.g., `vpsolver_glpk.sh`);
        * `arg1`, `arg2`: arguments to be passed to the script.
    * Actions:
        * calls `script_name` to solve an instance.
    * Usage examples:
        * `VPSolver.script(script name, .vbp file/VBP object)`;
        * `VPSolver.script(script name, .mps file/MPS object)`;
        * `VPSolver.script(script name, .afg file/VBP object)`;
        * `VPSolver.script(script name, .lp file/LP object)`;
        * `VPSolver.script(script name, .mps file/.lp file/MPS object/LP object, .afg file/AFG object)`.
        * Note: the solution can only be extracted if the graph or the original instance are provided.

* `VPSolver.set_verbose(verbose)`
    * Description: sets the default "verbose" behaviour.
    * Arguments:
        * `verbose`: `True` or `False`.
    * Note: The default behaviour is overridden if the `verbose` argument is set to a value different from `None` in any API call.

***
Copyright © Filipe Brandão. All rights reserved.  
E-mail: <fdabrandao@dcc.fc.up.pt>. [[Homepage](http://www.dcc.fc.up.pt/~fdabrandao/)]