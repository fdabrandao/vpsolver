#!/usr/bin/env python
""" Basic Setup Script """
"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2014, Filipe Brandao
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

from os import system

from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    """ Custom Install Command """

    def run(self):
        try:
            system('/bin/bash ./compile.sh')
            system('/bin/cp bin/* ' + self.install_scripts)
        except IOError:
            pass
        install.run(self)

setup(
    name='VPSolver',
    version='1.1',
    description='Vector Packing Exact Solver Based on Arc-Flow Formulation',
    author='',
    author_email='',
    packages=['pyvpsolver'],
    include_package_data=True,
    scripts=[
      'scripts/vpsolver_coinor.sh',
      'scripts/vpsolver_glpk.sh',
      'scripts/vpsolver_gurobi.sh',
      'scripts/vpsolver_lpsolve.sh',
      'scripts/vpsolver_cplex.sh',
    ],
    url='',
    license='LICENSE',
    long_description=open('README').read(),
    keywords='',
    classifiers=[
      'Development Status :: 1 - Planning',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Topic :: Scientific/Engineering'
    ],
    cmdclass = { 'install' : CustomInstallCommand },
    use_2to3 = True
)
