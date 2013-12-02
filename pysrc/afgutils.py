"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013, Filipe Brandao
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

from colors import *
from random import *

class AFGUtils:
    @staticmethod
    def load_graph(afg_file):
        f = open(afg_file, 'r')
        s = f.read()
        s = s[s.find('#GRAPH_BEGIN#'):]
        s = s[:s.find('#GRAPH_END#\n')]
        s = s.replace('#GRAPH_BEGIN#', '')
        lst = s.split()
        lst.pop(0) #S:
        S = int(lst.pop(0))
        lst.pop(0) #T:
        T = int(lst.pop(0))
        lst.pop(0) #NV:
        NV = int(lst.pop(0))
        lst.pop(0) #NA:
        NA = int(lst.pop(0))        
        lst = map(int, lst)        
        A = []
        V = set([])
        for i in xrange(0,len(lst),3):
            u, v, i = lst[i:i+3]       
            V.add(u)
            V.add(v)
            A.append((u,v,i))
        V = sorted(V)
        return V, A, S, T
        
    @staticmethod        
    def draw(svg_file, Vlbls, A, S=None, T=None, multigraph=True):    
        from pygraphviz.agraph import AGraph    
        g = AGraph(rankdir='LR', directed=True, bgcolor='white', text='black', 
                   font_color='white', ranksep='1.0', nodesep='0.10', strict=not multigraph)
        #g.node_attr['shape'] = 'point'
        g.node_attr['shape'] = 'circle'
        g.node_attr['color'] = 'black'
        g.node_attr['fontcolor'] = 'black' 
        g.node_attr['fontstyle'] = 'bold' 
        g.node_attr['penwidth'] = '2.0'

        M = max(i for (u,v,i) in A)
                 
        if S != None:
            Vlbls[S] = 'S'
        if T != None:
            Vlbls[T] = 'T'
                         
        if multigraph:
            colors = uniquecolors(M+1)
            shuffle(colors)
            
            for (u,v,i) in A:
                assert u != v
                ul = Vlbls[u]
                vl = Vlbls[v]
                if i == M:                
                    g.add_edge(ul,vl,color='black', penwidth=4)                
                else:
                    g.add_edge(ul,vl,color=colors[i%len(colors)], penwidth='%d' % 4, label='')

        else:
            colors = uniquecolors(1000)
            shuffle(colors)        
            
            links = {}
            for (u, v, i) in A:
                if (u,v) not in links:
                    links[u,v] = []
                links[u,v].append(i)  
                
            for (ind, (u, v)) in enumerate(links):
                assert u != v
                ul = Vlbls[u]
                vl = Vlbls[v]
                print len(links[u,v])
                if max(links[u,v]) == M:                
                    g.add_edge(ul,vl,color='black', penwidth=4)                
                if min(links[u,v]) != M:
                    g.add_edge(ul,vl,color=colors[ind%len(colors)], penwidth='%d' % 4, label='')

        g.draw(svg_file, format='svg', prog='dot')
        print "see %s!" % svg_file

