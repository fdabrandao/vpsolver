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

import os
import atexit
import shutil
import tempfile
from model import *
from afgutils import *

class VBP:
    def __init__(self, W, w, b, verbose=None):
        self.vbp_file = VPSolver.new_tmp_file(".vbp")
        f = open(self.vbp_file,"w")
        if type(W)==int: 
            W=[W]
        else: 
            W = list(W)
        print >>f, len(W)
        print >>f, " ".join(map(str,W))
        print >>f, len(w)
        for i in xrange(len(w)):
            if type(w[i])==int: 
                row = [w[i],b[i]]
            else: 
                row = list(w[i])+[b[i]]
            assert len(row) == len(W)+1
            print >>f, " ".join(map(str,row))
        f.close()
        if verbose:
            f = open(self.vbp_file,"r")
            print f.read()
            f.close()
        self.m = len(b)
        self.ndims = len(W)
        self.W, self.w, self.b = W, w, b

    @classmethod        
    def fromFile(cls, vbp_file, verbose=None):
        f = open(vbp_file, "r")
        lst = map(int,f.read().split())
        ndims = lst.pop(0)
        W = lst[:ndims]
        lst = lst[ndims:]
        m = lst.pop(0)
        w, b = [], []
        for i in xrange(m):
            w.append(lst[:ndims])
            lst = lst[ndims:]
            b.append(lst.pop(0))        
        return cls(W, w, b, verbose)
        
    def __del__(self):
        try:
            os.remove(self.vbp_file)
        except:
            pass

class AFG:
    def __init__(self, instance, opts="", verbose=None):
        assert isinstance(instance, VBP)
        VPSolver.set_verbose(verbose)
        self.instance = instance
        self.afg_file = VPSolver.new_tmp_file(".afg")
        self.output = VPSolver.vbp2afg(instance.vbp_file, self.afg_file, opts)
        self.V, self.A, self.S, self.T = None, None, None, None

    def graph(self):        
        return AFGraph.fromFile(self.afg_file)    

    def __del__(self):
        try:
            os.remove(self.afg_file)
        except:
            pass            
        
class MPS:
    def __init__(self, graph, verbose=None):
        assert isinstance(graph, AFG)
        VPSolver.set_verbose(verbose)
        self.afg_graph = graph
        self.mps_file = VPSolver.new_tmp_file(".mps")
        self.output = VPSolver.afg2mps(graph.afg_file, self.mps_file)
        
    def __del__(self):
        try:
            os.remove(self.mps_file)    
        except:
            pass            
  
class LP:
    def __init__(self, graph, verbose=None):
        assert isinstance(graph, AFG)
        VPSolver.set_verbose(verbose)
        self.afg_graph = graph
        self.lp_file = VPSolver.new_tmp_file(".lp")
        self.output = VPSolver.afg2lp(graph.afg_file, self.lp_file)
        
    def __del__(self):
        try:
            os.remove(self.lp_file)          
        except:
            pass            

class VPSolver:
    VPSOLVER = "vpsolver"
    VBP2AFG = "vbp2afg"
    AFG2MPS = "afg2mps"
    AFG2LP = "afg2lp"
    VBPSOL = "vbpsol"    
    
    TMP_DIR = tempfile.mkdtemp()
    TMP_CNT = 0       
    REDIRECT = "2>&1"

    @staticmethod
    def set_verbose(verbose):
        if verbose != None:
            if verbose:
                VPSolver.REDIRECT = "2>&1"                                
            else:
                VPSolver.REDIRECT = "> /dev/null 2>&1"

    @staticmethod        
    def new_tmp_file(ext = "tmp"):        
        if not ext.startswith("."): ext = "."+ext
        fname = "%s/%d%s" % (VPSolver.TMP_DIR, VPSolver.TMP_CNT, ext)
        VPSolver.TMP_CNT += 1
        return fname

    @staticmethod    
    @atexit.register    
    def clear():
        shutil.rmtree(VPSolver.TMP_DIR)

    @staticmethod           
    def parse_vbpsol(vpsol_output):
        try:
            s = vpsol_output.strip()
            lst = s[s.rfind("Objective:"):].split("\n")
            lst[0] = lst[0].replace("Objective: ", "")
            obj = int(lst[0])
            lst = lst[2:]
            lst = map(lambda x: x.split("x"), lst)
            sol = []
            for mult, pat in lst:
                mult = int(mult)
                pat = pat.replace("i=","")
                pat = pat.replace("[","").replace("]","")
                pat = map(lambda x: int(x)-1,pat.split(","))
                sol.append((mult,pat))
        except:
            return None                
        return obj, sol

    @staticmethod           
    def vbpsol(afg_file, sol_file, opts="", verbose=None):            
        VPSolver.set_verbose(verbose)  
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file        
        out_file = VPSolver.new_tmp_file()        
        os.system("%s %s %s %s | tee %s %s" % (VPSolver.VBPSOL, afg_file, sol_file, opts, out_file, VPSolver.REDIRECT))
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)        
        return output
   
    @staticmethod     
    def vpsolver(vbp_file, opts="", verbose=None):
        VPSolver.set_verbose(verbose)
        if isinstance(vbp_file, VBP):
            vbp_file = vbp_file.vbp_file        
        out_file = VPSolver.new_tmp_file()
        os.system("%s %s %s | tee %s %s" % (VPSolver.VPSOLVER, vbp_file, opts, out_file, VPSolver.REDIRECT))
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)     
        return output, VPSolver.parse_vbpsol(output)        

    @staticmethod  
    def vbp2afg(vbp_file, afg_file, opts="", verbose=None):
        VPSolver.set_verbose(verbose)
        if isinstance(vbp_file, VBP):
            vbp_file = vbp_file.vbp_file
        out_file = VPSolver.new_tmp_file()        
        os.system("%s %s %s %s | tee %s %s" % (VPSolver.VBP2AFG, vbp_file, afg_file, opts, out_file, VPSolver.REDIRECT))
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)        
        return output
        
    @staticmethod          
    def afg2mps(afg_file, mps_file, opts="", verbose=None):
        VPSolver.set_verbose(verbose)
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file 
        out_file = VPSolver.new_tmp_file()
        os.system("%s %s %s %s | tee %s %s" % (VPSolver.AFG2MPS, afg_file, mps_file, opts, out_file, VPSolver.REDIRECT))
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)        
        return output

    @staticmethod  
    def afg2lp(afg_file, lp_file, opts="", verbose=None):
        VPSolver.set_verbose(verbose)
        if isinstance(afg_file, AFG):
            afg_file = afg_file.afg_file                    
        out_file = VPSolver.new_tmp_file()
        os.system("%s %s %s %s | tee %s %s" % (VPSolver.AFG2LP, afg_file, lp_file, opts, out_file, VPSolver.REDIRECT))
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)        
        return output   

    @staticmethod     
    def script(script_name, arg1=None, arg2=None, verbose=None):
        VPSolver.set_verbose(verbose)
        cmd = script_name
        for arg in [arg1, arg2]:
            if isinstance(arg, MPS):
                cmd += " --mps " + arg.mps_file
            elif isinstance(arg, LP):
                cmd += " --lp " + arg.lp_file
            elif isinstance(arg, AFG):
                cmd += " --afg " + arg.afg_file        
            elif isinstance(arg, VBP):
                cmd += " --vbp " + arg.vbp_file  
            elif isinstance(arg, str):
                if arg.endswith(".mps"):
                    cmd += " --mps " + arg
                elif arg.endswith(".lp"):
                    cmd += " --lp " + arg 
                elif arg.endswith(".afg"):
                    cmd += " --afg " + arg 
                elif arg.endswith(".vbp"):
                    cmd += " --vbp " + arg
                else:
                    raise Exception("Invalid file extension!")                                        
        out_file = VPSolver.new_tmp_file()
        os.system("%s | tee %s %s" % (cmd, out_file, VPSolver.REDIRECT))               
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)
        return output, VPSolver.parse_vbpsol(output)                   

    @staticmethod     
    def script_wsol(script_name, model, verbose=None):
        VPSolver.set_verbose(verbose)
        cmd = script_name
        if isinstance(model, MPS):
            cmd += " --mps " + model.mps_file
        elif isinstance(model, LP):
            cmd += " --lp " + model.lp_file
        elif isinstance(model,str):
            if model.endswith(".mps"):
                cmd += " --mps " + model
            elif model.endswith(".lp"):
                cmd += " --lp " + model 
            else:
                raise Exception("Invalid file extension!")     
        out_file = VPSolver.new_tmp_file()
        sol_file = VPSolver.new_tmp_file(".sol")
        os.system("%s --wsol %s | tee %s %s" % (cmd, sol_file, out_file, VPSolver.REDIRECT))               
        f = open(out_file)
        output = f.read()
        f.close()
        os.remove(out_file)   
        try:
            f = open(sol_file)  
            sol = f.read().split()
            vals = {}
            assert len(sol)%2 == 0
            for i in xrange(0,len(sol),2):                    
                var, value = sol[i], int(round(float(sol[i+1])))
                if value != 0:
                    vals[var] = value
            f.close()
            os.remove(sol_file)
        except:
            vals = None                           
        return output, vals

