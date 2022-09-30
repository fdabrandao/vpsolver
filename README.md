## Arc-flow Vector Packing Solver (VPSolver)

Copyright (C) 2013-2022, Filipe Brandão <fdabrandao@gmail.com>
Faculdade de Ciências, Universidade do Porto  
Porto, Portugal. All rights reserved.

---
[VPSolver](https://github.com/fdabrandao/vpsolver) is a multiple-choice vector packing solver based on an arc-flow formulation with graph compression (see, e.g., [\[1\]](#references)). VPSolver generates very strong models (equivalent to Gilmore and Gomory's) that can be solved using general-purpose mixed-integer programming
solvers such as Gurobi and GLPK (see, e.g., [\[2\]](#references) and [\[3\]](#references)). VPSolver does not explicitly require any MIP solver in particular, though a good  MIP solver may be necessary for solving large models.

![](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)
[![](https://travis-ci.org/fdabrandao/vpsolver.svg?branch=master)](https://travis-ci.org/fdabrandao/vpsolver)
[![Coverage Status](https://coveralls.io/repos/github/fdabrandao/vpsolver/badge.svg?branch=develop)](https://coveralls.io/github/fdabrandao/vpsolver)

For modelling other problems easily, VPSolver includes a [Python API](https://github.com/fdabrandao/vpsolver/wiki/Python-API), a modelling toolbox ([PyMPL](https://github.com/fdabrandao/pympl/)), and a [Web App](#vpsolver-web-app). VPSolver has been successfully compiled and run on Linux, macOS, and Windows. VPSolver can also be used in [Docker containers](#docker).

For more details, please refer to the [project wiki](https://github.com/fdabrandao/vpsolver/wiki) or to the [manual](https://github.com/fdabrandao/vpsolver/tree/master/docs/vpsolver_manual.pdf).

#### Repositories
* Project Homepage: <http://vpsolver.fdabrandao.pt>
* GiHub repository: <https://github.com/fdabrandao/vpsolver>
* BitBucket repository: <https://bitbucket.org/fdabrandao/vpsolver>
* Docker repository: <https://hub.docker.com/r/fdabrandao/vpsolver>
* PyPI repository: <https://pypi.python.org/pypi/pyvpsolver>

## Requirements
#### Mandatory

- To use vpsolver scripts for various solvers:
  * MIP solver: Gurobi, CPLEX, GLPK, COIN-OR, SCIP, lp_solve, ...
  * UNIX-like operating system or a UNIX-like environment such as [Cygwin](https://www.cygwin.com/) on Windows
  * `g++`, `clang`, or `Visual Studio`; `cmake >= 3.3`; `bash >= 3.0`

- To build the vpsolver executable linked to Gurobi:
  * `gurobi`
  * `cmake >= 3.3`

#### Optional
For the [Python API](https://github.com/fdabrandao/vpsolver/wiki/Python-API) and Web App:

* `python-2.7` or `python-3.x`
* `python-pip`
* `python-dev`
* `glpk-utils`
 
#### Platforms
It has been successfully compiled and run on the following platforms:

* **Linux**
* **macOS**
* **Windows** (note that vpsolver scripts require bash)

## Setup
Without the python interface: 

```bash
$ mkdir build
$ cd build/
$ cmake ..
$ cmake --build . --config Release
```
Note: In order to compile the components that require Gurobi, you need to have set the environment variable `GUROBI_HOME` or specify the location of the Gurobi installation in the third step:
- Linux: `cmake .. -DGUROBI_DIR=/opt/gurobi952/linux64/`
- macOS: `cmake .. -DGUROBI_DIR=/Library/gurobi952/macos_universal2/`
- Windows: `cmake .. -DGUROBI_DIR=C:\\gurobi952\\win64`

With the python interface: 

```
$ pip install -r requirements.txt
$ pip install . --upgrade
$ cd examples; py.test -v --cov pyvpsolver
```
Or simply install from the [repository](https://pypi.python.org/pypi/pyvpsolver):

```
$ pip install pyvpsolver
```

## Python interface

The python interface is fully compatible with both python 2 and 3. 

Jupyter Notebooks for a quick introduction:

* [Simple VBP example](https://github.com/fdabrandao/vpsolver/blob/master/examples/notebooks/example_vbp.ipynb)
* [Simple MVP example](https://github.com/fdabrandao/vpsolver/blob/master/examples/notebooks/example_mvp.ipynb)

## Docker

### Docker Setup

Docker is an open platform for building, shipping and running applications. Docker allows VPSolver to run on a large variety of platforms with very little effort.

Install Docker [[Docker installation instructions](https://docs.docker.com/installation/)].

Option 1: simply `pull` VPSolver from Docker repository (without building):

```bash
$ docker pull fdabrandao/vpsolver
```

Option 2: `clone` VPSolver and `build` locally:

```bash 
$ git clone https://github.com/fdabrandao/vpsolver.git vpsolver
$ docker build -t fdabrandao/vpsolver vpsolver
```

### Usage
Directly using the command line interface:

```bash
$ docker run --rm -it fdabrandao/vpsolver bash
root@55d14f6b6f32:~# source venv2.7/bin/activate # load a virtualenv
(venv2.7)root@55d14f6b6f32:~# python examples/vpsolver/example_vbp.py
...
```

or through the VPSolver Web App (example URL: `http://172.17.0.60:5555/`):

```bash
$ docker run --rm -it -p 5555 fdabrandao/vpsolver 
eth0      Link encap:Ethernet  HWaddr 02:42:ac:11:00:3c  
          inet addr:172.17.0.60  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:acff:fe11:3c/64 Scope:Link
          UP BROADCAST  MTU:1500  Metric:1
          RX packets:2 errors:0 dropped:0 overruns:0 frame:0
          TX packets:2 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:168 (168.0 B)  TX bytes:180 (180.0 B)

URL: http://172.17.0.60:5555/
 * Running on http://0.0.0.0:5555/
...
```

For more details, please refer to the [project wiki](https://github.com/fdabrandao/vpsolver/wiki/docker).

## VPSolver binaries

* `$ bin/vpsolver intance.vbp/.mvp`: solves a multiple-choice vector packing instance using the method described in [\[1\]](#references). Note: requires Gurobi 5.0.0 or superior;
* `$ bin/vbp2afg instance.vbp/.mvp graph.afg`: builds an arc-flow graph `graph.afg` for `instance.vbp/.mvp`;
* `$ bin/afg2mps graph.afg model.mps`: creates a MPS model `model.mps` for `graph.afg`;
* `$ bin/afg2lp graph.afg model.lp`: creates a LP model `model.lp` for `graph.afg`;
* `$ bin/vbpsol graph.afg vars.sol`: extracts a vector packing solution from an arc-flow solution `vars.sol` associated with the graph `graph.afg`.

Usage:

```
# 1. Build the arc-flow graph graph.afg for example.vbp:  
$ bin/vbp2afg example.vbp graph.afg  
# 2. Convert the arc-flow graph into a .mps file model.mps:  
$ bin/afg2mps graph.afg model.mps  
# 3. Solve the MIP model and store the solution in vars.sol:
$ scritps/vpsolver_gurobi.sh --mps model.mps --wsol vars.sol
# 4. Extract the vector packing solution:  
$ bin/vbpsol graph.afg vars.sol  
```

For more details, please refer to the [manual](https://github.com/fdabrandao/vpsolver/tree/master/docs/vpsolver_manual.pdf).

## VPSolver Scripts
VPSolver includes several scripts for solving arc-flow models using different
solvers:

* `scripts/vpsolver_gurobi.sh`: Gurobi
* `scripts/vpsolver_cplex.sh`: IBM CPLEX
* `scripts/vpsolver_coinor.sh`: COIN-OR CBC
* `scripts/vpsolver_glpk.sh`: GLPK
* `scripts/vpsolver_scip.sh`: SCIP
* `scripts/vpsolver_lpsolve.sh`: lp_solve

Usage:

```bash
$ vpsolver_X.sh --vbp/--mvp instance.vbp/.mvp
$ vpsolver_X.sh --afg graph.afg
$ vpsolver_X.sh --mps/--lp model.mps/.lp
$ vpsolver_X.sh --mps/--lp model.mps/.lp --afg graph.afg
```

For more details, please refer to the [manual](https://github.com/fdabrandao/vpsolver/tree/master/docs/vpsolver_manual.pdf).

## Folders

* [docs](https://github.com/fdabrandao/vpsolver/tree/develop/docs): documentation
* [scripts](https://github.com/fdabrandao/vpsolver/tree/develop/scripts): vpsolver scripts
* [src](https://github.com/fdabrandao/vpsolver/tree/develop/src): vpsolver source code in C++
* [pyvpsolver](https://github.com/fdabrandao/vpsolver/tree/develop/pyvpsolver): pyvpsolver source code in Python
* [examples](https://github.com/fdabrandao/vpsolver/tree/develop/examples): vpsolver and pyvpsolver examples
* [examples/notebooks](https://github.com/fdabrandao/vpsolver/tree/develop/examples/notebooks/): jupyter notebooks
* [docs/reports](https://github.com/fdabrandao/vpsolver/tree/develop/examples/docs/reports/): technical reports on the underlying algorithms and models

## References

The current solution method is described in:

* [1] Brandão, F. (2016). _VPSolver 3: Multiple-choice Vector Packing Solver._ [arXiv:1602.04876](http://arxiv.org/abs/1602.04876).

VPSolver was proposed in:

* [2] Brandão, F. and Pedroso, J. P. (2016). _Bin packing and related problems: General arc-flow formulation with graph compression._
Computers & Operations Research, 69:56 – 67.  
doi: [http://dx.doi.org/10.1016/j.cor.2015.11.009](http://dx.doi.org/10.1016/j.cor.2015.11.009).

* [3] Brandão, F. and Pedroso, J. P. (2013). _Bin Packing and Related Problems:
General Arc-flow Formulation with Graph Compression._ Technical Report
DCC-2013-08, Faculdade de Ciências da Universidade do Porto, Universidade do
Porto, Portugal. [arXiv:1310.6887](http://arxiv.org/abs/1310.6887).

See also:

* [4] Brandão, F. and Pedroso, J. P. (2013). _Multiple-choice Vector Bin Packing:
Arc-flow Formulation with Graph Compression._ Technical Report DCC-2013-13,
Faculdade de Ciências da Universidade do Porto, Universidade do Porto, Portugal. [arXiv:1312.3836](http://arxiv.org/abs/1312.3836)

* [5] Brandão, F. and Pedroso, J. P. (2013). _Cutting Stock with Binary Patterns:
Arc-flow Formulation with Graph Compression._ Technical Report DCC-2013-09,
Faculdade de Ciências da Universidade do Porto, Universidade do Porto, Portugal. [arXiv:1502.02899](http://arxiv.org/abs/1502.02899).

* [6] Brandão, F. (2012). _Bin Packing and Related Problems: Pattern-Based Approaches._ 
Master’s thesis, Faculdade de Ciências da Universidade do Porto, Portugal.

* [7] Computational results on several benchmark test data sets:  
https://research.fdabrandao.pt/research/vpsolver/results/


***
Copyright © 2013-2022 [Filipe Brandão](https://fdabrandao.pt) < [fdabrandao@gmail.com](mailto:fdabrandao@gmail.com) >. All rights reserved.