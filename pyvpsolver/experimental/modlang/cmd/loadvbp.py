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

from .... import *
from utils import *

class CmdLoadVBP:
    def __init__(self, pyvars):
        self.defs = ""
        self.data = ""
        self.pyvars = pyvars

    def __getitem__(self, name):
        return lambda *args: self.evalcmd(name, args)

    def evalcmd(self, name, args):
        match = re.match("\s*("+rgx_varname+")\s*({"+rgx_varname+"}|{\s*"+rgx_varname+"\s*,\s*"+rgx_varname+"\s*})?\s*", name)
        assert match != None
        name, index = match.groups()
        index_I, index_D = name+"_I", name+"_D"
        if index != None:
            index = index.strip('{ }')
            index = index.split(',')
            if len(index) == 2:
                index_I = index[0].strip()
                index_D = index[1].strip()
            elif len(index) == 1:
                index_I = index[0].strip()
        assert 1 <= len(args) <= 3
        fname = args[0]
        i0 = args[1] if len(args) > 1 else 0
        d0 = args[2] if len(args) > 2 else 0
        instance = VBP.fromFile(fname, verbose=False)

        self.pyvars[name] = instance
        self.defs += "#BEGIN_DEFS: Instance[%s]\n" % name
        self.defs += "param %s_m := %d;\n" % (name, instance.m)
        self.pyvars[name+"_m"] = instance.m
        self.defs += "param %s_n := %d;\n" % (name, sum(instance.b))
        self.pyvars[name+"_n"] = sum(instance.b)
        self.defs += "param %s_p := %d;\n" % (name, instance.ndims)
        self.pyvars[name+"_p"] = instance.ndims
        self.defs += "set %s := %d..%d;\n" % (index_I, i0, i0+instance.m)
        self.pyvars[index_I] = range(i0, i0+instance.m)
        self.defs += "set %s := %d..%d;\n" % (index_D, d0, d0+instance.ndims)
        self.pyvars[index_D] = range(d0, d0+instance.ndims)
        self.defs += "param %s_W{%s};\n" % (name, index_D)
        self.defs += "param %s_b{%s};\n" % (name, index_I)
        self.defs += "param %s_w{%s,%s};\n" % (name, index_I, index_D)
        self.defs += "#END_DEFS: %s\n" % name

        self.data += "#BEGIN_DATA: Intance[%s]\n" % name
        self.data += "param %s_W default 0 := " % name
        W = {}
        for i in xrange(instance.ndims):
            if instance.W[i] != 0:
                self.data += "[%d]%d" % (i0+i, instance.W[i])
            W[i0+i] = instance.W[i]
        self.data += ";\n"
        self.pyvars[name+"_W"] = W
        self.data += "param %s_b default 0 := " % name
        b = {}
        for i in xrange(instance.m):
            if instance.b[i] != 0:
                self.data += "[%d]%d" % (i0+i, instance.b[i])
            b[i0+i] = instance.b[i]
        self.data += ";\n"
        self.pyvars[name+"_b"] = b
        self.data += "param %s_w default 0 := " % name
        w = {}
        for i in xrange(instance.m):
            for d in xrange(instance.ndims):
                if instance.w[i][d] != 0:
                    self.data += "[%d,%d]%d" % (i0+i, d0+d, instance.w[i][d])
                w[i0+i, d0+d] = instance.w[i][d]
        self.data += ";\n"
        self.pyvars[name+"_w"] = w
        self.data += "#END_DATA: %s\n" % name
