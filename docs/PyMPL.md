# PyMPL

PyMPL is a python extension to the AMPL modelling language that adds new statements for evaluating python code within AMPL models.

## Table of Contents
  * [Examples](#examples)
  * [PyMPL statements](#pympl-statements)

## Examples

``vector_packing.mod``:

```ampl
# Load a vector packing instance from a file:
$LOAD_VBP[instance1{I,D}]{"instance1.vbp", i0=1};

var x{I}, >= 0;

# Generate an arc-flow model for instance1:
$FLOW[Z]{_instance1.W, _instance1.w, ["x[%d]"%i for i in _sets['I']]};
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
$FLOW[^Z[1]]{W1, ws, ["x[1, %d]"%i for i in _sets['I']]};
$FLOW[^Z[2]]{W2, ws, ["x[2, %d]"%i for i in _sets['I']]};
$FLOW[^Z[3]]{W3, ws, ["x[3, %d]"%i for i in _sets['I']]};
# Note: the ^prefix is used to avoid the redefinition of Z

minimize obj: sum{t in T} C[t] * Z[t];
s.t. demand{i in I}: sum{t in T} x[t, i] >= b[i];

solve;
display{t in T} Z[t]; # number of bins of type t used
display sum{t in T} C[t] * Z[t]; # cost
end;
```
``arcflow.mod``

```ampl
# Load a vector packing instance from a file: 
$LOAD_VBP[instance1{I,D}]{"instance.vbp", i0=1}; 

# Generate the arc_flow graph and create sets V and A for the set of vertices and arcs, respectively:
$GRAPH[V,A]{_instance1.W, _instance1.w, _sets['I']};

var Z, integer, >= 0; # amount of flow in the feedback arc
var f{A}, integer, >= 0; # amount of flow in each arc

# Objective:
maximize obj: Z;

# Flow conservation constraints:
s.t. flowcon{k in V diff {'S','T'}}: 
sum{(u,v,i) in A: v == k} f[u,v,i] - sum{(u,v,i) in A: u == k} f[u, v, i] = 0;
s.t. flowconS: sum{(u,v,i) in A: u == 'S'} f[u,v,i] = Z;
s.t. flowconT: sum{(u,v,i) in A: v == 'T'} f[u,v,i] = Z;

# Demand constraints:
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} >= instance1_b[i];

solve;
end;
```

## PyMPL statements

There are three types of calls:

1. `${python code}$`
 
  * [EVAL](#eval): `${python expression}$`

2. `$CMD{python parameters or code};`

  * [EXEC](#exec): `$EXEC{python code};`
  * [STMT](#stmt): `$STMT{python expression};`

3. `$CMD[AMPL parameters]{python arguments or code};` 

  * [SET](#set): `$SET[set_name]{values};`
  * [PARAM](#param): `$PARAM[param_name]{values, i0=0};`
  * [VAR](#var): `$VAR[var_name]{typ="", lb=None, ub=None};`
  * [CON](#con): `$CON[constraint_name]{left, sign, right};`

4. Additional statements for arc-flow models and vector packing:

  * [LOAD_VBP](#load_vbp): `$LOAD_VBP[name]{fname, i0=0, d0=0};`
  * [FLOW](#flow): `$FLOW[zvar]{W, w, b, bounds=None};`
  * [GRAPH](#graph): `$GRAPH[V_name, A_name]{W, w, labels, bounds=None};`

**Note**: The values between `[]` are usually used to name new AMPL variables, constraints, sets, or parameters. Names starting with a `^` indicate that the corresponding AMPL element should not be defined by the command. This prefix is useful when the corresponding AMPL element was declared previously and we do not want to declared it again.

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
    * `'param_name'`: parameter name.
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
$PARAM[D]{{'a': 1, 'b': 2}};
$PARAM[L0]{[1,2,3], i0=0};
$PARAM[L1]{[1,2,3], i0=1}; # `i0` is the initial index if `values` is a list
...
```
 
is replaced by:

```ampl
param NAME := 'name';
param VALUE := 10;
param D := ['a']1['b']2;
param L0 := [0]1[1]2[2]3;
param L1 := [1]1[2]2[3]3;
```
Note: Is is possible to call external functions (i.e., `$PARAM[X]{some_function(...)}`) that return the parameter.

#### VAR
Usage: `$VAR[var_name]{typ="", lb=None, ub=None};`
 
Description: creates AMPL variables.

Parameters:

  * AMPL:
    * `'var_name'`: variable name.
  * Python:
    * `typ`: variable type (e.g., "integer");
    * `lb`: variable lower bound;
    * `ub`: variable upper bound.

Creates:

  * AMPL:
    * creates a variable named `'var_name'`.

Examples:  

```ampl
...
$VAR[x]{"integer", 0, 10};
$VAR[y]{"binary"};
$VAR[z]{ub=abs((2**7)/5-135)};
...
```
 
is replaced by:

```ampl
var x, integer, >= 0, <= 10;
var y, binary; 
var z, <= 110;
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
$CON[con2]{[("x1",5)],">=",[("x2",-15),("x3",-10),20]};
$CON[con3]{-20,">=",[("x1",-5),("x2",-15),("x3",-10)]};
$CON[con4]{-20,">=",[(-5, "x1"),("x2",-15),(-10, "x3")]};
$CON[con5]{[-20, "x1"],">=",[(-4, "x1"),("x2",-15),(-10, "x3")]};
$CON[con6]{"x1",">=",[(-4, "x1"),20,("x2",-15),(-10, "x3")]};
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
``` 
Note: all the original constraints are just different representations of the same constraint.

### Detailed description of vector packing and arc-flow statements

#### LOAD_VBP
Usage: `$LOAD_VBP[name]{fname, i0=0, d0=0};`

Description: loads vector packing instances.

Parameters:

  * AMPL:
    * Option 1: `'name'` -> symbolic name for the instance;
    * Option 2: `'name{Iname}'` -> symbolic name for the instance and for the index set;
    * Option 3: `'name{Iname, Dname}'` -> symbolic name for the instance, for the index set and for the dimension set;
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
$LOAD_VBP[instance{I,D}]{"instance.vbp", i0=1, d0=0}
...
```
 
is replaced by:

```ampl
param instance1_m := 4; # number of different item types
param instance1_n := 17;# total number of items
param instance1_p := 2; # number of dimensions
set I := {1,2,3,4};     # index set for items (starting at `i0`)
set D := {0,1};         # index set for dimensions (starting at `d0`)
param instance1_W{D};   # bin capacity
param instance1_b{I};   # item demands
param instance1_w{I,D}; # item weights
```

#### FLOW
Usage: `$FLOW[zvar_name]{W, w, b, bounds=None};`

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
$LOAD_VBP[instance1{I,D}]{"instance.vbp",1};
var x{I}, >= 0;
$FLOW[Z]{_instance1.W, _instance1.w, ["x[%d]"%i for i in _sets['I']]};    

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

#### GRAPH
Usage: `$GRAPH[V_name, A_name]{W, w, labels, bounds=None};`

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
$LOAD_VBP[instance1{I,D}]{"instance.vbp", i0=1}; 
$GRAPH[V,A]{_instance1.W, _instance1.w, _sets['I']};

var Z, integer, >= 0; # amount of flow in the feedback arc
var f{A}, integer, >= 0; # amount of flow in each arc

# Objective:
maximize obj: Z;

# Flow conservation constraints:
s.t. flowcon{k in V diff {'S','T'}}: 
  sum{(u,v,i) in A: v == k} f[u,v,i] - sum{(u,v,i) in A: u == k} f[u, v, i] = 0;
s.t. flowconS: sum{(u,v,i) in A: u == 'S'} f[u,v,i] = Z;
s.t. flowconT: sum{(u,v,i) in A: v == 'T'} f[u,v,i] = Z;

# Demand constraints:
s.t. demand{k in I}: sum{(u,v,i) in A: i == k} >= instance1_b[i];

solve;
end;
```

Note: the source vertex is `'S'`, the target is `'T'`, and loss arcs are labeled with `'LOSS'`.


***
Copyright © Filipe Brandão. All rights reserved.  
E-mail: <fdabrandao@dcc.fc.up.pt>. [[Homepage](http://www.dcc.fc.up.pt/~fdabrandao/)]