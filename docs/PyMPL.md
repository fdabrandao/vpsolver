# PyMPL

PyMPL is a python extension to the AMPL modelling language that adds new statements for evaluating python code within AMPL models.

## Table of Contents
  * [Examples](#examples)
  * [PyMPL parser](#pympl-parser)
  * [PyMPL statements](#pympl-statements)

## Examples

``piecewise_linear.mod``

```ampl
# Evaluate python code:
$EXEC{
xvalues = [0, 10, 15, 25, 30, 35, 40, 45, 50, 55, 60, 70]
yvalues = [0, 20, 15, 10, 0, 50, 18, 0, 15, 24, 10, 15]
};

var u >= 0;
# Model a piecewise linear function given a list of pairs (x, y=f(x)):
$PWL[x,y]{zip(xvalues, yvalues)};

maximize obj: 2*x + 15*y;
s.t. A: 3*x + 4*y <= 250;
s.t. B: 7*x - 2*y + 3*u <= 170;

solve;
display x, y, u;
display "Objective:", 2*x + 15*y;
end;
```

``vector_packing.mod``:

```ampl
# Load a vector packing instance from a file:
$VBP_LOAD[instance1{I,D}]{"instance1.vbp", i0=1};

var x{I}, >= 0;

# Generate an arc-flow model for instance1:
$VBP_FLOW[Z]{_instance1.W, _instance1.w, ["x[%d]"%i for i in _sets['I']]};
# Variable declarations and flow conservation constraints will be created here

minimize obj: Z;
s.t. demand{i in I}: x[i] >= instance1_b[i]; # demand constraints

solve;
display Z;
end;
```

``variable_size_bin_packing.mod``:

```ampl
# Evaluate python code:
$EXEC{
# Bin capacities:
W1 = [100]
W2 = [120]
W3 = [150]

# Bin costs:
Costs = [100, 120, 150]

# Item weights:
ws = [[10], [14], [17], [19], [24], [29], [32], [33], [36],
      [38], [40], [50], [54], [55], [63], [66], [71], [77],
      [79], [83], [92], [95], [99]]

# Item demands:
b = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
};

# Generate a parameter 'b' for the demand:
$PARAM[b{I}]{b, i0=1};

# Generate a parameter 'C' for the cost:
$PARAM[C{T}]{Costs, i0=1};

# Feedback arcs for each graph:
var Z{T}, integer, >= 0;
# Assignment variables:
var x{T, I}, integer, >= 0;
# Generate an arc-flow graph for each bin type:
$VBP_FLOW[^Z[1]]{W1, ws, ["x[1, %d]"%i for i in _sets['I']]};
$VBP_FLOW[^Z[2]]{W2, ws, ["x[2, %d]"%i for i in _sets['I']]};
$VBP_FLOW[^Z[3]]{W3, ws, ["x[3, %d]"%i for i in _sets['I']]};
# Note: the ^prefix is used to avoid the redefinition of Z

minimize obj: sum{t in T} C[t] * Z[t];
s.t. demand{i in I}: sum{t in T} x[t, i] >= b[i];

solve;
display{t in T} Z[t]; # number of bins of type t used
display sum{t in T} C[t] * Z[t]; # cost
end;
```
## PyMPL parser

```python
from pyvpsolver import PyMPL  # import the parser

# Create a parser and pass local and global variables to the model:
parser = PyMPL(locals_=locals(), globals_=globals())`

# Parse a file with PyMPL statements and produce a valid AMPL model:
parser.parse("pympl_model.mod", "ampl_model.mod")

# Call GLPK to solve the model if the original model uses only valid GMPL statements:
os.system("glpsol --math ampl_model.mod")

# Call AMPL to solve the model:
os.system("ampl ampl_model.mod")
```

[[Folder with examples](https://github.com/fdabrandao/vpsolver/blob/master/examples/pympl/)]

Advanced features:
* Given a function `f(varname)` that given a variable name returns its value:

  * If any command used implements solution extraction you can use `parser[command_name].extract(f)`;
  * If any command used implements cut generation you can use `parser[command_name].separate(f)` to generate cutting planes.

## PyMPL statements

There are three types of statements:

1. `${python code}$`
 
  * [EVAL](#eval): `${python expression}$`

2. `$CMD{python parameters or code};`

  * [EXEC](#exec): `$EXEC{python code};`
  * [STMT](#stmt): `$STMT{python expression};`

3. `$CMD[AMPL parameters]{python arguments or code};` 

  * [SET](#set): `$SET[set_name]{values};`
  * [PARAM](#param): `$PARAM[param_name]{values, i0=0};`
  * [VAR](#var): `$VAR[var_name]{typ="", lb=None, ub=None, index_set=None};`
  * [CON](#con): `$CON[constraint_name]{left, sign, right};`

Additional statements:

1. Statements for [VPSolver](https://github.com/fdabrandao/vpsolver):

  * [VBP_LOAD](#vbp_load): `$VBP_LOAD[name]{fname, i0=0, d0=0};`
  * [VBP_FLOW](#vbp_flow): `$VBP_FLOW[zvar]{W, w, b, bounds=None};`
  * [VBP_GRAPH](#vbp_graph): `$VBP_GRAPH[V_name, A_name]{W, w, labels, bounds=None};`

2. Statements for special ordered sets and piecewise linear functions:

  * [SOS1](#sos1): `$SOS1{varl, ub=1};`
  * [SOS2](#sos2): `$SOS2{varl, ub=1};`
  * [PWL](#pwl): `$PWL[var_x, var_y]{xyvalues};`

3. Statements for TSP:

  * [ATSP_MTZ](#atsp_mtz): `$ATSP_MTZ{xvars, DL=False, cuts=False};`
  * [ATSP_SCF](#atsp_scf): `$ATSP_SCF{xvars, cuts=False};`
  * [ATSP_MCF](#atsp_mcf): `$ATSP_SCF{xvars, cuts=False};`

**Note**: The values between `[]` are usually used to name new AMPL variables, constraints, sets, or parameters. Names starting with a `^` indicate that the corresponding AMPL element should not be defined by the command. This prefix is useful when the corresponding AMPL element was declared before and we do not want to declared it again.

### Detailed description of general PyMPL statements

#### EVAL
Usage: `${python expression}$`

Description: is replaced by the result of `eval("python expression")`.  

Parameters:

  * Python:
    * valid python expression.

Creates:

  * AMPL:
    * is replaced by the result of evaluating the expression.

Examples:  
```ampl
...
var x1, >= ${2+6}$, <= ${10*5}$;
s.t. con1: x + y <= ${abs((2**7)/5-135)}$ * z;
...
```
is replaced by:
```ampl
...
var x1, >= 8, <= 50;
s.t. con1: x + y <= 110 * z;
...
```

#### EXEC
Usage: `$EXEC{python code};`

Description: executes python code.

Parameters:

  * Python:
    * valid python code.

Creates:

  * AMPL:
    * May create anything that results from calls to PyMPL commands.
  * Python:
    * May create new python variables/functions/etc. that can be used in the following statements.

Examples:  

```ampl
...
$EXEC{
for i in range(3):
    STMT("var x{0}, integer, >= 0, <= {1};".format(i, i+1))
};
...
```
 
is replaced by:

```ampl
var x0, integer, >= 0, <= 1;
var x1, integer, >= 0, <= 2;
var x2, integer, >= 0, <= 3;
```

Note: you call use PyMPL commands inside python code as follows:
  * `$CMD[...]{...};` are equivalent to `CMD["..."](...)` in python code;
  * `$CMD{...};` are equivalent to `CMD(...)` in python code.

#### STMT
Usage: `$STMT{python expression};`

Description: is replaced by the result of `eval("python expression")`.  

Parameters:

  * Python:
    * valid python expression.

Creates:

  * AMPL:
    * is replaced by the result of evaluating the expression.

Examples:  

```ampl
...
$STMT{"s.t. con1: x + y <= {0} * z;".format(abs((2**7)/5-135))};
$EXEC{stmt = "s.t. {0}: x >= 10;".format("test")};
$STMT{stmt};
...
```

is replaced by:

```ampl
...
s.t. con1: x + y <= 110 * z;
s.t. test: x >= 10;
...
```
Note: `$STMT{expression};` is equivalent to `${expression}$` ([EVAL](#eval)).

#### SET
Usage: `$SET[set_name]{values};`

Description: creates an AMPL sets.

Parameters:

  * AMPL:
    * `'set_name'`: set name.
  * Python:
    * `values`: list of values.

Creates:

  * AMPL:
    * a set named `'set_name'`.
  * Python:
    * `_set['set_name']`: list of values.

Examples:  

```ampl
...
$SET[A]{range(5)};
$SET[B]{zip(range(5),range(5))};
...
```
 
is replaced by:

```ampl
set A := {0,1,2,3,4};
set B := {(0,0),(1,1),(2,2),(3,3),(4,4)};
```
Note: Is is possible to call external functions (i.e., `$SET[X]{some_function(...)}`) that return the set.

#### PARAM
Usage: `$PARAM[param_name]{values, i0=0};`

Description: creates AMPL parameters.

Parameters:

  * AMPL:
    * Option 1: `'param_name'` -> parameter name;  
    * Option 2: `'param_name{Index_name}'` -> parameter name and index name.
  * Python:
    * `values`: dictionary of key:value pairs or a list of values;
    * `i0`: initial index if `values` is a list of values.

Creates:

  * AMPL:
    * a parameter named `'param_name'`.
  * Python:
    * `_param['param_name']`: dictionary with the parameter data.

Examples:  

```ampl
...
$PARAM[NAME]{"name"}; 
$PARAM[VALUE]{10};
$PARAM[D{I}]{{'a': 1, 'b': 2}};
$PARAM[L0]{[1,2,3], i0=0};
$PARAM[L1]{[1,2,3], i0=1}; # `i0` is the initial index if `values` is a list
...
```
 
is replaced by:

```ampl
param NAME := 'name';
param VALUE := 10;
param D := ['a']1['b']2;
set I := {'a','b'};
param L0 := [0]1[1]2[2]3;
param L1 := [1]1[2]2[3]3;
```
Note: Is is possible to call external functions (i.e., `$PARAM[X]{some_function(...)}`) that return the parameter.

#### VAR
Usage: `$VAR[var_name]{typ="", lb=None, ub=None, index_set=None};`
 
Description: creates AMPL variables.

Parameters:

  * AMPL:
    * Option 1: `'var_name'` ->  variable name;
    * Option 2: `'var_name{Iname}'` -> variable name and index name (`index_set` must be provided).
  * Python:
    * `typ`: variable type (e.g., "integer");
    * `lb`: variable lower bound;
    * `ub`: variable upper bound;
    * `index_set`: index set for the variable.

Creates:

  * AMPL:
    * creates a variable named `'var_name'`.

Examples:  

```ampl
...
$VAR[x]{"integer", 0, 10};
$VAR[y]{"binary"};
$VAR[z]{ub=abs((2**7)/5-135)};
$VAR[xs{I}]{"integer", index_set=range(3)};
...
```
 
is replaced by:

```ampl
var x, integer, >= 0, <= 10;
var y, binary; 
var z, <= 110;
set I := {0,1,2};
var xs{I}, integer;
```

#### CON
Usage: `$CON[constraint_name]{left, sign, right};`

Description: creates AMPL constraints.

Parameters:

  * AMPL:
    * `'constraint_name'`: constraint name.
  * Python:
    * `left`: list of variable names, values, or pairs (variable name, coefficient);
    * `sign`: constraint type (">=", "=", "<=");
    * `right`: list of variable names, values, or pairs (variable name, coefficient).

Creates:

  * AMPL:
    * a constraint named `'constraint_name'`.

Examples:

```ampl
...
$CON[con1]{[("x1",5),("x2",15),("x3",10)],">=",20};
$CON[con2]{[("x1",5),("x2",15),-20],">=",("x3",-10)};
$CON[con3]{[("x1",5)],">=",[("x2",-15),("x3",-10),20]};
$CON[con4]{-20,">=",[("x1",-5),("x2",-15),("x3",-10)]};
$CON[con5]{-20,">=",[(-5, "x1"),("x2",-15),(-10, "x3")]};
$CON[con6]{[-20, "x1"],">=",[(-4, "x1"),("x2",-15),(-10, "x3")]};
$CON[con7]{"x1",">=",[(-4, "x1"),20,("x2",-15),(-10, "x3")]};
...
```
 
is replaced by:

```ampl
s.t. con1: +5*x1+15*x2+10*x3 >= 20;
s.t. con2: +5*x1+15*x2+10*x3 >= 20;
s.t. con3: +5*x1+15*x2+10*x3 >= 20;
s.t. con4: +5*x1+15*x2+10*x3 >= 20;
s.t. con5: +5*x1+15*x2+10*x3 >= 20;
s.t. con6: +5*x1+15*x2+10*x3 >= 20;
s.t. con7: +5*x1+15*x2+10*x3 >= 20;
``` 
Note: all the original constraints are just different representations of the same constraint.

### Statements for VPSolver

#### VBP_LOAD
Usage: `$VBP_LOAD[name]{fname, i0=0, d0=0};`

Description: loads vector packing instances.

Parameters:

  * AMPL:
    * Option 1: `'name'` -> symbolic name for the instance;
    * Option 2: `'name{Iname}'` -> symbolic name for the instance, and for the index set;
    * Option 3: `'name{Iname, Dname}'` -> symbolic name for the instance, for the index set, and for the dimension set;
  * Python:
    * `fname`: file name;
    * `i0`: initial index for items (default 0);
    * `d0`: initial index for dimensions (default 0);

Creates:

  * AMPL:
    * `param name_m`: number of different item types;
    * `param name_n`: total number of items;
    * `param name_p`: number of dimensions;
    * `param name_W`: bin capacity;
    * `param name_b`: item demands;
    * `param name_w`: item weights;
    * `set name_I`: index set for items (if no other name was specified);
    * `set name_D`: index set for dimensions (if no other name was specified).
  * Python:
    * `_set['set_name']` lists for each set;
    * `_param['param_name']` dictionaries for each param;

Examples:

`instance.vbp`:

```
2
10 3
4
3 1 4
5 2 3
8 1 1
4 1 9
```

`model.mod`:

```ampl
...
$VBP_LOAD[instance{I,D}]{"instance.vbp", i0=1, d0=0}
...
```
 
is replaced by:

```ampl
param instance_m := 4; # number of different item types
param instance_n := 17;# total number of items
param instance_p := 2; # number of dimensions
set I := {1,2,3,4};    # index set for items (starting at `i0`)
set D := {0,1};        # index set for dimensions (starting at `d0`)
param instance_W{D};   # bin capacity
param instance_b{I};   # item demands
param instance_w{I,D}; # item weights
```

#### VBP_FLOW
Usage: `$VBP_FLOW[zvar_name]{W, w, b, bounds=None};`

Description: generates arc-flow models for vector packing instances.

Parameters:

  * AMPL:
    * `zvar_name`: variable name for the amount of flow in the feedback arc (which corresponds to the number of bins used);
  * Python:
    * `W`: bin capacity;
    * `w`: item weights;
    * `b`: item demands (may include strings with variable names if the demand is not fixed);
    * `bounds`: maximum demand for each item.  

Creates:

  * AMPL:
    * an arc-flow model for the vector packing instance (variables and constraints);
    * a variable `'zvar_name'` for the amount of flow in the feedback arc.
  * Python:
    * stores information for solution extraction.

Examples:

```ampl
$VBP_LOAD[instance1{I,D}]{"instance.vbp",1};
var x{I}, >= 0;
$VBP_FLOW[Z]{_instance1.W, _instance1.w, ["x[%d]"%i for i in _sets['I']]};    

minimize obj: Z;
s.t. demand{i in I}: x[i] >= instance1_b[i]; # demand constraints

solve;
end;
```
 
is replaced by:

```ampl
var x{I}, >= 0;  
/* arc-flow model for instance.vbp */
/* Z is the amount of flow on the feedback arc */
/* x[i] = amount of flow on arcs associated with item i */
minimize obj: Z;
s.t. demand{i in I}: x[i] >= instance1_b[i]; # demand constraints

solve;
end;
```

#### VBP_GRAPH
Usage: `$VBP_GRAPH[V_name, A_name]{W, w, labels, bounds=None};`

Description: generates arc-flow graphs for vector packing instances.  

Parameters:

  * AMPL:
    * `V_name`: name for the set of vertices;
    * `A_name`: name for the set of arcs.
  * Python:
    * `W`: bin capacity;
    * `w`: item weights;
    * `labels`: item labels ;
    * `bounds`: maximum demand for each item.

Creates:

  * AMPL:
    * `set 'V_name'`: set of vertices;
    * `set 'A_name'`: set of arcs.
  * Python:
    * `_sets['V_name']`: set of vertices;
    * `_sets['A_name']`: set of arcs;

Examples:

```ampl
$VBP_LOAD[instance1{I,D}]{"instance.vbp", i0=1}; 
$VBP_GRAPH[V,A]{_instance1.W, _instance1.w, _sets['I']};

# Variables:
var Z, integer, >= 0; # amount of flow in the feedback arc
var f{A}, integer, >= 0; # amount of flow in each arc
# Objective:
maximize obj: Z;
# Flow conservation constraints:
s.t. flowcon{k in V}: 
    sum{(u,v,i) in A: v == k} f[u,v,i]  - sum{(u,v,i) in A: u == k} f[u, v, i] 
    = if k == 'T' then Z else
      if k == 'S' then -Z else
      0;
# Demand constraints:
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} >= instance1_b[i];
```

Note: the source vertex is `'S'`, the target is `'T'`, and loss arcs are labeled with `'LOSS'`.

### Statements for special ordered sets and piecewise linear functions

#### SOS1
Usage: `$SOS1{varl, ub=1};`

Description: creates a special ordered set of type 1 (SOS1) for a set of variables. At most one variable in a SOS1 can take a strictly positive value.

Parameters:

  * Python:
    * `varl`: list of variable names;
    * `ub`: largest possible value if non-zero (default 1).

Creates:

  * AMPL:
    * creates a variables and constraints to model the special ordered set.

Example:

```ampl
var x{1..3}, >= 0;
$SOS1{["x[1]", "x[2]", "x[3]"]};
```

#### SOS2
Usage: `$SOS2{varl, ub=1};`

Description: creates a special ordered set of type 2 (SOS2) for a set of variables.  At most two variables in a SOS2 can take a strictly positive value, and if two are non-zero these must be consecutive in their ordering.

Parameters:

  * Python:
    * `varl`: list of variable names;
    * `ub`: largest possible value if non-zero (default 1).

Creates:

  * AMPL:
    * creates a variables and constraints to model the special ordered set.

Example:

```ampl
$PARAM[X{I}]{[0, 10, 15, 25, 30, 35, 40, 45, 50, 55, 60, 70]};
$PARAM[Y{^I}]{[0, 20, 15, 10, 0, 50, 18, 0, 15, 24, 10, 15]};
# Model a piecewise linear function
var x;
var y;
# Model a piecewise linear function using a special ordered set of type 2:
var z{I}, >= 0;
s.t. fix_x: x = sum{i in I} X[i] * z[i];
s.t. fix_y: y = sum{i in I} Y[i] * z[i];
s.t. convexity: sum{i in I} z[i] = 1;
$SOS2{["z[%d]"%i for i in _sets['I']]};
```

#### PWL
Usage: `$PWL[var_x, var_y]{xyvalues};`

Description: models a piecewise linear function given a list of pairs (x, y=f(x)).

Parameters:

  * AMPL:
    * `'var_x'`: name for the first variable;
    * `'var_y'`: name for the second variable.
  * Python:
    * 'xyvalues': list of pairs (x, y=f(x)) for the piecewise linear function f(x).

Creates:

  * AMPL:
    * creates variables `'var_x'` and `'var_y'`;
    * creates a variables and constraints to model the piecewise linear function (`'var_y'` = f(`'var_x'`)).

Examples:

```ampl
$EXEC{
xvalues = [0, 10, 15, 25, 30, 35, 40, 45, 50, 55, 60, 70]
yvalues = [0, 20, 15, 10, 0, 50, 18, 0, 15, 24, 10, 15]
};
$PWL[x,y]{zip(xvalues, yvalues)};
```

### Statements for TSP

#### ATSP_MTZ
Usage: `$ATSP_MTZ{xvars, DL=False, cuts=False};`

Description: creates a submodel for TSP using Miller, Tucker and Zemlin (MTZ) (1960) subtour elimination constraints.

Parameters:

  * Python:
    * `xvars`: list of binary variables for the arcs in the graph;
    * `DL`: if `True` uses Desrochers and Laporte (1991) lifted MTZ inequalities;
    * `cuts`: if `True` stores information for cut generation.

Creates:

  * AMPL:
    * A submodel for TSP projected on `xvars` variables.
  * Python:
    * stores information for cut generation if requested.

Examples:

```ampl
$SET[V]{set of vertices};
$SET[A]{set of arcs};
$PARAM[cost{^A}]{cost of each arc};
var x{A}, binary;
minimize total: sum{(i,j) in A} cost[i,j] * x[i,j];
$ATSP_MTZ{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, DL=True, cuts=True};
```

#### ATSP_SCF
Usage: `$ATSP_SCF{xvars, cuts=False};`

Description: creates a submodel for TSP using the single commodity flow model of Gavish and Graves (1978).

Parameters:

  * Python:
    * `xvars`: list of binary variables for the arcs in the graph;
    * `cuts`: if `True` stores information for cut generation.

Creates:

  * AMPL:
    * A submodel for TSP projected on `xvars` variables.
  * Python:
    * stores information for cut generation if requested.

Examples:

```ampl
$SET[V]{set of vertices};
$SET[A]{set of arcs};
$PARAM[cost{^A}]{cost of each arc};
var x{A}, binary;
minimize total: sum{(i,j) in A} cost[i,j] * x[i,j];
$ATSP_SCF{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}, cuts=True};
```

#### ATSP_MCF
Usage: `$ATSP_SCF{xvars, cuts=False};`

Description: creates a submodel for TSP using the multi commodity flow model of Wong (1980) and Claus (1984).

Parameters:

  * Python:
    * `xvars`: list of binary variables for the arcs in the graph;
    * `cuts`: if `True` stores information for cut generation.

Creates:

  * AMPL:
    * A submodel for TSP projected on `xvars` variables.
  * Python:
    * stores information for cut generation if requested.

Examples:

```ampl
$SET[V]{set of vertices};
$SET[A]{set of arcs};
$PARAM[cost{^A}]{cost of each arc};
var x{A}, binary;
minimize total: sum{(i,j) in A} cost[i,j] * x[i,j];
$ATSP_MCF{{(i,j): "x[%d,%d]"%(i,j) for i, j in _sets['A']}};
```

***
Copyright © Filipe Brandão. All rights reserved.  
E-mail: <fdabrandao@dcc.fc.up.pt>. [[Homepage](http://www.dcc.fc.up.pt/~fdabrandao/)]