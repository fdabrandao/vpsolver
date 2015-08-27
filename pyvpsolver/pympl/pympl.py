"""
This code is part of the Mathematical Modelling Toolbox PyMPL.

Copyright (C) 2015-2015, Filipe Brandao
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

import re
import sys
from .cmds import SubmodBase
from .cmds import CmdSet, CmdParam, CmdVar, CmdCon, CmdStmt
from .cmds import SubmodVBPFlow, CmdVBPGraph, CmdVBPLoad
from .cmds import SubmodATSPMTZ, SubmodATSPSCF, SubmodATSPMCF
from .cmds import SubmodSOS1, SubmodSOS2, SubmodPWL
from .cmds import SubmodWWU, SubmodWWUB
from .cmds import SubmodWWUSC, SubmodWWUSCB, SubmodWWULB
from .cmds import SubmodWWCC, SubmodWWCCB
from .cmds import SubmodLSU, SubmodLSU1, SubmodLSU2, SubmodLSUB


class PyMPL(object):
    """PyMPL parser."""

    DEBUG = False
    t_CMD = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_ARGS1 = r'(?:.*?(?=]\s*{))'
    t_ARGS2 = r'(?:.*?(?=}\s*;))'
    t_ARGS3 = r'(?:.*?(?=}))'
    t_STRING1 = r'(?:"(?:[^"\\]|\\.)*")'
    t_STRING2 = r"(?:'(?:[^'\\]|\\.)*')"
    t_STRING = t_STRING1+r'|'+t_STRING2
    t_COMMENT = r'#[^\n]*|/\*.*?(?=\*/)\*/'
    t_CMD = (
        r'('+t_STRING+r'|'+t_COMMENT+r')'
        r'|\$('+t_CMD+r')\s*(\['+t_ARGS1+r'\])?\s*{('+t_ARGS2+r')}\s*;'
        r'|\${('+t_ARGS3+r')}\$'
    )

    EXEC_CMD = "EXEC"
    DEFAULT_CMDS = {
        "SET": CmdSet,
        "PARAM": CmdParam,
        "VAR": CmdVar,
        "CON": CmdCon,
        "STMT": CmdStmt,
        "ATSP_MTZ": SubmodATSPMTZ,
        "ATSP_SCF": SubmodATSPSCF,
        "ATSP_MCF": SubmodATSPMCF,
        "VBP_LOAD": CmdVBPLoad,
        "VBP_FLOW": SubmodVBPFlow,
        "VBP_GRAPH": CmdVBPGraph,
        "SOS1": SubmodSOS1,
        "SOS2": SubmodSOS2,
        "PWL": SubmodPWL,
        "WW_U": SubmodWWU,
        "WW_U_B": SubmodWWUB,
        "WW_U_SC": SubmodWWUSC,
        "WW_U_SCB": SubmodWWUSCB,
        "WW_U_LB": SubmodWWULB,
        "WW_CC": SubmodWWCC,
        "WW_CC_B": SubmodWWCCB,
        "LS_U": SubmodLSU,
        "LS_U1": SubmodLSU1,
        "LS_U2": SubmodLSU2,
        "LS_U_B": SubmodLSUB,
    }

    def __init__(self, locals_=None, globals_=None):
        if locals_ is None:
            locals_ = {}
        if globals_ is None:
            globals_ = globals()

        self._sets = {}
        self._params = {}
        self._locals = {}
        for var in locals_:
            self._locals[var] = locals_[var]
        for var in globals_:
            if var not in self._locals:
                self._locals[var] = globals_[var]
        self._submodels = set()

        self._locals["_model"] = ""
        self._locals["_defs"] = ""
        self._locals["_data"] = ""
        self._locals["_sets"] = self._sets
        self._locals["_params"] = self._params

        self._cmds = [PyMPL.EXEC_CMD, None]
        for cmd, cls in self.DEFAULT_CMDS.items():
            self.add_cmd(cmd, cls)

        self.input = ""
        self.output = ""

    def add_cmd(self, cmd, cmdcls):
        """Adds a new command to the parser."""
        self._locals[cmd] = cmdcls(cmd, self._locals, self._sets, self._params)
        self._cmds.append(cmd)

    def parse(self, mod_in=None, mod_out=None, comment_cmds=True):
        """Parses the input file."""
        if mod_in is not None:
            self.read(mod_in)
        self.output = self.input

        rgx = re.compile(PyMPL.t_CMD, re.DOTALL)
        for match in rgx.finditer(self.input):
            comment, call, args1, args2, args3 = match.groups()
            assert call in self._cmds
            strmatch = self.input[match.start():match.end()]
            clean_strmatch = strmatch.strip("/*# ")

            if PyMPL.DEBUG:
                print "\n---\n{0}\n{1}\n---\n".format(strmatch, match.groups())

            if comment is not None:
                if comment_cmds and comment.startswith("/*"):
                    self.output = self.output.replace(
                        strmatch, "/*IGNORED:{0}*/".format(clean_strmatch)
                    )
                continue

            try:
                self._locals["_model"] = ""
                self._locals["_defs"] = ""
                self._locals["_data"] = ""
                if call is None:
                    res = str(eval(args3, self._locals))
                elif call == PyMPL.EXEC_CMD:
                    assert args1 is None
                    exec(args2, self._locals)
                    res = str(self._locals["_model"])
                else:
                    if call in self._locals:
                        if issubclass(type(self._locals[call]), SubmodBase):
                            self._submodels.add(call)
                    if args1 is not None:
                        args1 = "'''{0}'''".format(args1[1:-1])
                    exec(
                        "{0}[{1}]({2})".format(call, args1, args2),
                        self._locals
                    )
                    res = str(self._locals["_model"])
                res += self._locals["_defs"]
                self._add_data(self._locals["_data"])
            except:
                exctype, value, traceback = sys.exc_info()
                msg = str(value)+"\n\t"
                msg += "(while evaluating {0} at line {1:d} col {2:d})".format(
                    "$"+call+("[...]" if args1 is not None else "")+"{...}",
                    self.input[:match.start()].count("\n")+1,
                    match.start()-self.input[:match.start()].rfind("\n"),
                )
                raise exctype, msg, traceback

            if comment_cmds:
                res = "/*EVALUATED:{0}*/{1}".format(
                    clean_strmatch, res
                )

            self.output = self.output.replace(strmatch, res, 1)

        if mod_out is not None:
            self.write(mod_out)

    def _add_data(self, data):
        """Adds data to the model."""
        if data != "":
            data_stmt = re.search("data\\s*;", self.output, re.DOTALL)
            end_stmt = re.search("end\\s*;", self.output, re.DOTALL)
            if data_stmt is not None:
                match = data_stmt.group(0)
                self.output = self.output.replace(match, match+"\n"+data)
            else:
                if end_stmt is None:
                    self.output += "data;\n" + data + "\nend;"
                else:
                    match = end_stmt.group(0)
                    self.output = self.output.replace(
                        match, "data;\n" + data + "\nend;"
                    )

    def read(self, mod_in):
        """Reads the input file."""
        with open(mod_in, "r") as fin:
            self.input = fin.read()

    def write(self, mod_out):
        """Writes the output to a file."""
        with open(mod_out, "w") as fout:
            print >>fout, self.output

    def submodels(self):
        """Returns the names of submodels used."""
        return self._submodels

    def __getitem__(self, varname):
        """Returns the internal variable varname."""
        return self._locals[varname]

    def __setitem__(self, varname, value):
        """Sets the internal variable varname."""
        self._locals[varname] = value
