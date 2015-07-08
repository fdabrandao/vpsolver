"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2015, Filipe Brandao
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

import unittest
import os
sdir = os.path.dirname(__file__)
if sdir != "":
    os.chdir(sdir)
import sys
sys.path.insert(0, "../../../")

from pyvpsolver.modlang import AMPLParser, glpk_mod2lp


class TestAMPLParser(unittest.TestCase):

    def test_empty(self):
        parser = AMPLParser()
        parser.input = ""
        parser.parse()
        self.assertEqual(parser.output, "")

    def test_set(self):
        parser = AMPLParser()
        parser.input = """
        $SET[A]{range(5)};
        """
        parser.parse()
        self.assertIn("set A := {0,1,2,3,4};", parser.output)

    def test_param(self):
        parser = AMPLParser()
        parser.input = """
        $PARAM[NAME]{"something"};
        $PARAM[VALUE]{10};
        $PARAM[P]{{'a': 1, 'b': 2}};
        """
        parser.parse()
        self.assertIn("param NAME := 'something';", parser.output)
        self.assertIn("param VALUE := 10;", parser.output)
        self.assertIn("param P := ['a']1['b']2;", parser.output)

    def test_comments(self):
        parser = AMPLParser()
        parser.input = """
        /*$SET[A]{range(5)};*/
        #$PARAM[VALUE]{10};
        """
        parser.parse()
        self.assertNotIn("set A := {0,1,2,3,4};", parser.output)
        self.assertNotIn("param VALUE := 10;", parser.output)

if __name__ == "__main__":
    unittest.main()
