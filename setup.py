#!/usr/bin/env python
""" Basic Setup Script """

from os import system

from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    """ Custom Install Command """

    def run(self):
        try:
            system('/bin/bash ./compile.sh')
        except IOError:
            pass
        install.run(self)

setup(
    name='VPSolver',
    version='0.0.1',
    description='Vector Packing Exact Solver Based on Arc-Flow Formulation',
    author='',
    author_email='',
    packages=['pyvpsolver'],
    include_package_data=True,
    scripts=[
      'bin/vbp2afg',
      'bin/afg2mps',
      'bin/vbpsol',
      'bin/afg2lp',
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
    cmdclass = { 'install' : CustomInstallCommand }
)
