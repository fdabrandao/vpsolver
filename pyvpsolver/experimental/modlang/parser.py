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

import os
import re
from .. import *
from .cmd import *


class AMPLParser(object):
    def __init__(self, mod_in, mod_out=None, locals_=None, globals_=None):
        if locals_ is None:
            locals_ = {}
        if globals_ is None:
            globals_ = globals()
        pyvars = locals_

        sets, params = {}, {}
        SET = CmdSet(pyvars, sets, params)
        PARAM = CmdParam(pyvars, sets, params)
        FLOW = CmdFlow(pyvars, sets, params)
        GRAPH = CmdGraph(pyvars, sets, params)
        LOAD_VBP = CmdLoadVBP(pyvars, sets, params)
        pyvars["_model"] = ""
        pyvars["_sets"] = sets
        pyvars["_params"] = params
        pyvars["SET"] = SET
        pyvars["PARAM"] = PARAM
        pyvars["FLOW"] = FLOW
        pyvars["GRAPH"] = GRAPH
        pyvars["LOAD_VBP"] = LOAD_VBP
        self.FLOW = FLOW

        with open(mod_in, "r") as f:
            text = f.read()

        rgx_cmd = "[a-zA-Z_][a-zA-Z0-9_]*"
        rgx_arg1 = "[^\]]*"
        rgx_arg2 = """"(?:[^"]|\")*"|'(?:[^']|\')*'|[^}]*"""
        rgx = re.compile(
            "(#|/\*\s*)?(?:"
            "\$("+rgx_cmd+")\s*(\["+rgx_arg1+"\])?\s*{("+rgx_arg2+")}\s*;"
            "|\${("+rgx_arg2+")}"
            ")(?:\s*\*/)?",
            re.DOTALL
        )

        self._result = text[:]
        for match in rgx.finditer(text):
            comment, call, args1, args2, args3 = match.groups()
            assert call in (
                "EXEC", "EVAL", "SET", "PARAM",
                "LOAD_VBP", "FLOW", "GRAPH", None
            )
            strmatch = text[match.start():match.end()]

            if comment is not None:
                result = result.replace(
                    strmatch, "/*IGNORED:"+strmatch.strip("/**/")+"*/"
                )
                continue
            if call is None:
                res = eval(args3, globals_, locals_)
            elif call == "EVAL":
                res = eval(args2, globals_, locals_)
            elif call == "EXEC":
                assert args1 is None
                locals_["_model"] = ""
                exec(args2, globals_, locals_)
                res = locals_["_model"]
            else:
                if args1 is None:
                    call = "%s[%s](%s)" % (call, args1, args2)
                else:
                    call = "%s['''%s'''](%s)" % (call, args1.strip("[]"), args2)
                locals_["_model"] = ""
                exec(call, globals_, locals_)
                res = locals_["_model"]

            self._result = self._result.replace(
                strmatch, "/*EVALUATED:%s*/%s" % (strmatch, res)
            )

        defs = "#BEGIN_DEFS\n"
        defs += LOAD_VBP.defs + SET.defs + PARAM.defs + GRAPH.defs
        defs += "#END_DEFS\n"
        self._add_defs(defs)

        data = "#BEGIN_DATA\n"
        data += LOAD_VBP.data + PARAM.data
        data += "#END_DATA\n"
        self._add_data(data)

        if mod_out is not None:
            self._mod_out = mod_out
        else:
            self._mod_out = VPSolver.new_tmp_file(".mod")

        self.write_mod(self._mod_out)

    def _add_defs(self, defs):
        self._result = defs + self._result

    def _add_data(self, data):
        data_stmt = re.search("data\s*;", self._result, re.DOTALL)
        end_stmt = re.search("end\s*;", self._result, re.DOTALL)
        if data_stmt is not None:
            match = data_stmt.group(0)
            self._result = self._result.replace(match, match+"\n"+data)
        else:
            if end_stmt is None:
                self._result += "data;\n" + data + "\nend;"
            else:
                match = end_stmt.group(0)
                self._result = self._result.replace(
                    match, "data;\n" + data + "\nend;"
                )

    def write_mod(self, fname_mod):
        f = open(fname_mod, "w")
        print >>f, self._result
        f.close()

    @property
    def model(self):
        return self._result

    @property
    def model_file(self):
        return self._mod_out
