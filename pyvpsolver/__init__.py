"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao <fdabrandao@gmail.com>
"""

__version__ = "3.1.3"

from .afgraph import AFGraph
from .vpsolver import VPSolver, VBP, MVP, AFG, MPS, LP
from . import solvers
