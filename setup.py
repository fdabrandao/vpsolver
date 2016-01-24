#!/usr/bin/env python
"""
VPSolver
--------
VPSolver is a vector packing solver based on an arc-flow formulation
with graph compression. VPSolver generates very strong models that can
be solved using general-purpose mixed-integer programming solvers such
as Gurobi and GLPK. For modelling other problems easily, VPSolver
includes a Python API and a modelling toolbox (PyMPL).

Setup
`````

.. code:: bash

    $ pip install pyvpsolver

System requirements
```````````````````

* UNIX-like operating system or a UNIX-like environment such as Cygwin
* g++ >= 4.8; make >= 3.0; bash >= 3.0

Links
`````

* `VPSolver wiki <https://github.com/fdabrandao/vpsolver/wiki>`_
* `GiHub repository <https://github.com/fdabrandao/vpsolver>`_
* `BitBucket repository <https://bitbucket.org/fdabrandao/vpsolver>`_
"""
import os
import re
import ast
from distutils.core import setup, Extension


def ls_dir(base_dir):
    """List files recursively."""
    base_dir = os.path.join(base_dir, "")
    return [
        os.path.join(dirpath.replace(base_dir, "", 1), f)
        for (dirpath, dirnames, files) in os.walk(base_dir)
        for f in files
        if (
            not f.endswith(("~", ".pyc", ".pyo", ".log")) and
            not f.startswith(".")
        )
    ]

_vbp2afg = Extension(
    "_vbp2afg",
    sources=[
        "src/vbp2afg_wrap.cxx", "src/vbp2afg.cpp",
        "src/instance.cpp", "src/graph.cpp",
        "src/arcflow.cpp", "src/common.cpp"
    ],
    extra_compile_args=["-std=c++11", "-Wall", "-O2"],
    undef_macros=['NDEBUG'],
)

_afg2lp = Extension(
    "_afg2lp",
    sources=[
        "src/afg2lp_wrap.cxx", "src/afg2lp.cpp",
        "src/instance.cpp", "src/graph.cpp",
        "src/arcflow.cpp", "src/common.cpp"
    ],
    extra_compile_args=["-std=c++11", "-Wall", "-O2"],
    undef_macros=['NDEBUG'],
)

_afg2mps = Extension(
    "_afg2mps",
    sources=[
        "src/afg2mps_wrap.cxx", "src/afg2mps.cpp",
        "src/instance.cpp", "src/graph.cpp",
        "src/arcflow.cpp", "src/common.cpp"
    ],
    extra_compile_args=["-std=c++11", "-Wall", "-O2"],
    undef_macros=['NDEBUG'],
)

_vbpsol = Extension(
    "_vbpsol",
    sources=[
        "src/vbpsol_wrap.cxx", "src/vbpsol.cpp",
        "src/instance.cpp", "src/graph.cpp",
        "src/arcflow.cpp", "src/arcflowsol.cpp",
        "src/common.cpp"
    ],
    extra_compile_args=["-std=c++11", "-Wall", "-O2"],
    undef_macros=['NDEBUG'],
)

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open("pyvpsolver/__init__.py", "rb") as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode("utf-8")).group(1)))

setup(
    name="pyvpsolver",
    version=version,
    license="AGPLv3+",
    author="Filipe Brandao",
    author_email="fdabrandao@dcc.fc.up.pt",
    url="https://github.com/fdabrandao/vpsolver",
    description="Arc-flow Vector Packing Solver (VPSolver)",
    long_description=__doc__,
    packages=["pyvpsolver"],
    package_data={"": ls_dir("pyvpsolver/")},
    include_package_data=True,
    platforms=["unix", "linux", "osx"],
    scripts=[os.path.join("scripts", f) for f in ls_dir("scripts/")],
    install_requires=open("requirements.txt").read().split("\n"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Topic :: Scientific/Engineering"
    ],
    ext_modules=[_vbp2afg, _afg2lp, _afg2mps, _vbpsol],
)
