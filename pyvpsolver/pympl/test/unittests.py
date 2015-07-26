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

from pyvpsolver.pympl import PyMPL


class TestPyMPL(unittest.TestCase):
    """Unittests for the PyMPL class"""

    def test_empty(self):
        """Tests empty files"""
        parser = PyMPL()
        parser.input = ""
        parser.parse()
        self.assertEqual(parser.output, "")

    def test_set(self):
        """Tests $SET[name]{values} calls"""
        parser = PyMPL()
        parser.input = """
        $SET[A]{range(5)};
        $SET[^B]{range(5)};
        """
        parser.parse()
        self.assertIn("set A := {0,1,2,3,4};", parser.output)
        self.assertNotIn("set B := {0,1,2,3,4};", parser.output)
        self.assertNotIn("set ^B := {0,1,2,3,4};", parser.output)

    def test_param(self):
        """Tests $PARAM[name]{value} calls"""
        parser = PyMPL()
        parser.input = """
        $PARAM[NAME]{"something"};
        $PARAM[^NAME2]{"something"};
        $PARAM[VALUE]{10};
        $PARAM[P]{{'a': 1, 'b': 2}};
        """
        parser.parse()
        self.assertIn("param NAME := 'something';", parser.output)
        self.assertNotIn("param NAME2 := 'something';", parser.output)
        self.assertNotIn("param ^NAME2 := 'something';", parser.output)
        self.assertIn("param VALUE := 10;", parser.output)
        self.assertIn("param P := ['a']1['b']2;", parser.output)

    def test_var(self):
        """Tests $VAR[name]{typ, lb, ub} calls"""
        parser = PyMPL()
        parser.input = """
        $VAR[x]{"integer", 0, 10};
        $VAR[^z]{"integer", 0, 10};
        $EXEC{VAR['y']("binary")};
        """
        parser.parse()
        self.assertIn("var x, integer, >= 0, <= 10;", parser.output)
        self.assertNotIn("var z, integer, >= 0, <= 10;", parser.output)
        self.assertNotIn("var ^z, integer, >= 0, <= 10;", parser.output)
        self.assertIn("var y, binary;", parser.output)

    def test_con(self):
        """Tests $CON[name]{lincomb, sign, rhs} calls"""
        parser = PyMPL()
        parser.input = """
        $VAR[x1]{}; $VAR[x2]{}; $VAR[x3]{};
        $CON[xyz]{[("x1",5),("x2",15),("x3",10)],">=",20};
        $CON[^xyz2]{[("x1",5),("x2",15),("x3",10)],">=",20};
        """
        parser.parse()
        self.assertIn("s.t. xyz: +5*x1+15*x2+10*x3 >= 20;", parser.output)
        self.assertNotIn("s.t. xyz2: +5*x1+15*x2+10*x3 >= 20;", parser.output)

    def test_stmt(self):
        """Tests $STMT{stmt} calls"""
        parser = PyMPL()
        parser.input = """
        $EXEC{stmt = "s.t. {0}: x1 >= 10;".format("test")};
        $STMT{stmt};
        """
        parser.parse()
        self.assertIn("s.t. test: x1 >= 10;", parser.output)

    def test_eval(self):
        """Tests ${expression}$ calls"""
        parser = PyMPL()
        parser.input = """
        var x1, >= ${2+6}$, <= ${10*5}$;
        """
        parser.parse(comment_cmds=False)
        self.assertIn("var x1, >= 8, <= 50;", parser.output)

    def test_comments(self):
        """Tests valid comments"""
        parser = PyMPL()
        parser.input = """
        /* $SET[A]{range(5)};*/
        # $PARAM[VALUE]{10};
        # ... $PARAM[VALUE2]{10}; ...
        param a := "/*";
        $PARAM[Y]{10};
        param b := "*/";
        """
        parser.parse()
        self.assertNotIn("set A := {0,1,2,3,4};", parser.output)
        self.assertNotIn("param VALUE := 10;", parser.output)
        self.assertNotIn("param VALUE2 := 10;", parser.output)
        self.assertIn("param Y := 10;", parser.output)
        self.assertIn("/*IGNORED:$SET[A]{range(5)};*/", parser.output)
        self.assertIn("# $PARAM[VALUE]{10};", parser.output)
        self.assertIn("/*EVALUATED:$PARAM[Y]{10};*/", parser.output)

    def test_exceptions(self):
        """Tests if exceptions are thrown correctly"""
        parser = PyMPL()
        parser.input = """$EXEC{print 1/0};"""
        with self.assertRaises(ZeroDivisionError):
            parser.parse()
        parser.input = """$SET[X]{0};"""
        with self.assertRaises(TypeError):
            parser.parse()
        parser.input = """$FLOW[Z]{100, [10, 10]};"""
        with self.assertRaises(TypeError):
            parser.parse()
        parser.input = """$FLOW[Z]{100, 10};"""
        with self.assertRaises(TypeError):
            parser.parse()
        parser.input = """$SET[X]{};"""
        with self.assertRaises(TypeError):
            parser.parse()
        parser.input = """$SET[X]{[1,2,3]};$SET[X]{[1,2]};"""
        with self.assertRaises(AssertionError):
            parser.parse()
        parser.input = """$SET[2X]{[1,2,3]};"""
        with self.assertRaises(AssertionError):
            parser.parse()


if __name__ == "__main__":
    unittest.main()
