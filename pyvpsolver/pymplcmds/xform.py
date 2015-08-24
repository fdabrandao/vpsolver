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

from math import floor, ceil
from .base import SubModelBase
from ..model import Model
from ..modelutils import writemod

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!  All Book Extended Formulations  !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!  Xform  9/9/2005
!  Contains
!    WW-U
!    WW-U-B
!    WW-U-SC     *DONE!*
!    WW-U-SC,B
!    WW-CC       *DONE!*

!    LS-U1=(MC)
!    LS-U2=(SP)
!    LS-U-B

!Added 30/9/2005
!    DLSI-CC
!    DLSI-CC-B
!    DLS-CC-B
!    DLS-CC-SC

! Added 30/9/05 (not in Xformsimple)
!    WW-U-LB
!    WW-CC-B

!Missing 24/7/07
!    LS-U-SC

! Added 16/12/09
!    LT  Lasdon-Terjung
!    DLS-CC-SC-U with integer (not just 0-1 demands)
"""


def mrange(a, b):
    """Returns a [a, b] range."""
    return xrange(a, b+1)


def cumul_demand(d, NT):
    """
    procedure CumulDemand(
        d : array (range) of real,
        D : array (range,range) of real,
        NT : integer)
        forall (k in 1..NT) D(k,k):=d(k)
        forall (k in 1..NT,l in k+1..NT) D(k,l):=D(k,l-1)+d(l)
        forall (k in 1..NT,l in 1..k-1) D(k,l):=0
    end-procedure
    """
    D = {}
    for k in mrange(1, NT):
        D[k, k] = d[k]
    for k in mrange(1, NT):
        for l in mrange(k+1, NT):
            D[k, l] = D[k, l-1]+d[l]
    for k in mrange(1, NT):
        for l in mrange(1, k-1):
            D[k, l] = 0
    return D


def ww_u_sc(model, s, y, z, d, NT, Tk, prefix=""):
    """
    Wagner-Whitin and Start-up

    procedure XFormWWUSC(
        s : array (range) of linctr,
        y : array (range) of linctr,
        z : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC: integer)

        declarations
            XWW: array (1..NT,range) of linctr
            D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)

        forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0) XWW(k,l) :=
            s(k-1) >= D(k,l) - D(k,l)*y(k) - sum (i in k+1..l) D(i,l)*z(i)

        if MC = 1 then
          forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0 )
          setmodcut(XWW(k,l))
        end-if
    end-procedure
    """
    D = cumul_demand(d, NT)

    # forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0) XWW(k,l) :=
    # s(k-1) >= D(k,l) - D(k,l)*y(k) - sum (i in k+1..l) D(i,l)*z(i)
    for k in mrange(1, NT):
        for l in mrange(k, min(NT, k+Tk-1)):
            if D[l, l] > 0:
                lhs = s[k-1]
                rhs = [D[k, l], (-D[k, l], y[k])]
                for i in mrange(k+1, l):
                    rhs.append((-D[i, l], z[i]))
                model.add_con(lhs, ">=", rhs)


def ww_cc(model, s, y, d, C, NT, Tk, prefix=""):
    """
    Wagner-Whitin, Constant Capacity

    procedure XFormWWCC(
        s : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        C : real,
        NT : integer,
        Tk : integer,
        MC: integer)

        declarations
            ws: array(0..NT-1,range) of mpvar
            gs: array(0..NT-1,range) of real
            ds: array(0..NT-1) of mpvar
            XS,XW:array (1..NT) of linctr
            XKT:array (1..NT,1..NT) of linctr
            D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)


        forall(k in 1..NT,t in k..minlist(NT,k+Tk-1)) create(ws(k-1,t))

        forall(k in 1..NT,t in k..minlist(NT,k+Tk-1)) do
            gs(k-1,t):=D(k,t)-C*floor(D(k,t)/C)
        end-do

        forall(k in 1..NT) do
            XS(k):= s(k-1) >=
                C*ds(k-1)+sum(i in k..minlist(NT,k+Tk-1))gs(k-1,i)*ws(k-1,i)
        end-do
        forall(k in 1..NT) XW(k):=sum(i in k..minlist(NT,k+Tk-1)) ws(k-1,i)<=1
        forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)) XKT(k,t) :=
            ds(k-1)+sum(i in k..t)y(i)+
            sum(i in k..minlist(NT,k+Tk-1)|gs(k-1,i)>=gs(k-1,t))ws(k-1,i) >=
            floor(D(k,t)/C)+1
        if MC=1 then
        forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)) setmodcut(XKT(k,t))
        end-if

    end-procedure
    """
    def wsvar(i, j):
        return prefix+"ws_{0}_{1}".format(i, j)

    def dsvar(i):
        return prefix+"ds_{0}".format(i)

    # ws: array(0..NT-1,range) of mpvar
    # ds: array(0..NT-1) of mpvar
    for k in mrange(1, NT):
        for t in mrange(k, min(NT, k+Tk-1)):
            model.add_var(name=wsvar(k-1, t))
        model.add_var(name=dsvar(k-1))

    # forall(k in 1..NT,t in k..minlist(NT,k+Tk-1))
    # gs(k-1,t):=D(k,t)-C*floor(D(k,t)/C)
    D = cumul_demand(d, NT)
    gs = {}
    for k in mrange(1, NT):
        for t in mrange(k, min(NT, k+Tk-1)):
            gs[k-1, t] = D[k, t]-C*floor(D[k, t]/C)

    # forall(k in 1..NT) XS(k) :=
    # s(k-1) >= C*ds(k-1)+sum(i in k..minlist(NT,k+Tk-1))gs(k-1,i)*ws(k-1,i)
    for k in mrange(1, NT):
        lhs = s[k-1]
        rhs = [(C, dsvar(k-1))]
        for i in mrange(k, min(NT, k+Tk-1)):
            rhs.append((gs[k-1, i], wsvar(k-1, i)))
        model.add_con(lhs, ">=", rhs)

    # forall(k in 1..NT) XW(k) := sum(i in k..minlist(NT,k+Tk-1)) ws(k-1,i)<=1
    for k in mrange(1, NT):
        lhs = [wsvar(k-1, i) for i in mrange(k, min(NT, k+Tk-1))]
        model.add_con(lhs, "<=", 1)

    # forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)) XKT(k,t) :=
    # ds(k-1)+sum(i in k..t)y(i)+
    # sum(i in k..minlist(NT,k+Tk-1)|gs(k-1,i)>=gs(k-1,t)) ws(k-1,i) >=
    # floor(D(k,t)/C)+1
    for k in mrange(1, NT):
        for t in mrange(k, min(NT, k+Tk-1)):
            lhs = [dsvar(k-1)]+[y[i] for i in mrange(k, t)]
            lhs += [
                wsvar(k-1, i)
                for i in mrange(k, min(NT, k+Tk-1))
                if gs[k-1, i] >= gs[k-1, t]
            ]
            rhs = floor(D[k, t]/C)+1
            model.add_con(lhs, ">=", rhs)


class SubWWUSCModel(SubModelBase):
    """Command for creating WW-U-SC extended formulations."""

    def __init__(self, *args, **kwargs):
        SubModelBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, s, y, z, d, NT, Tk=None):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_wwusc{0}_".format(self._cnt)

        assert isinstance(s, list) and len(s) in (NT, NT+1)
        assert isinstance(y, list) and len(y) == NT
        assert isinstance(z, list) and len(z) == NT
        assert isinstance(d, list) and len(d) == NT

        varl = s + y + z

        if len(s) == NT:
            s = {i+1: s[i] for i in xrange(NT)}
            s[0] = 0
        else:
            s = {i: s[i] for i in mrange(0, NT)}
        y = {i+1: y[i] for i in xrange(NT)}
        z = {i+1: z[i] for i in xrange(NT)}
        d = {i+1: d[i] for i in xrange(NT)}

        if Tk is None:
            Tk = NT

        model = Model()
        for var in varl:
            model.add_var(name=var)
        ww_u_sc(model, s, y, z, d, NT, Tk, prefix)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(varl)
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)


class SubWWCCModel(SubModelBase):
    """Command for creating WW-CC extended formulations."""

    def __init__(self, *args, **kwargs):
        SubModelBase.__init__(self, *args, **kwargs)
        self._cnt = 0

    def _evalcmd(self, arg1, s, y, d, C, NT, Tk=None):
        """Evalutates CMD[arg1](*args)."""
        assert arg1 is None
        self._cnt += 1
        prefix = "_wwcc{0}_".format(self._cnt)

        assert isinstance(s, list) and len(s) in (NT, NT+1)
        assert isinstance(y, list) and len(y) == NT
        assert isinstance(d, list) and len(d) == NT

        varl = s + y

        if len(s) == NT:
            s = {i+1: s[i] for i in xrange(NT)}
            s[0] = 0
        else:
            s = {i: s[i] for i in mrange(0, NT)}
        y = {i+1: y[i] for i in xrange(NT)}
        d = {i+1: d[i] for i in xrange(NT)}

        if Tk is None:
            Tk = NT

        model = Model()
        for var in varl:
            model.add_var(name=var)
        ww_cc(model, s, y, d, C, NT, Tk, prefix)
        model.rename_cons(lambda name: prefix+name)

        declared_vars = set(varl)
        self._pyvars["_model"] += writemod.model2ampl(model, declared_vars)
