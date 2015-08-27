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

from math import floor, ceil

"""
The set of models included in this file come from the library of reformulations
LS-LIB proposed in:
  Production Planning by Mixed Integer Programming (Pochet and Wolsey 2006).
The implementations are a direct translation from the LS-LIB's xform.mos file.
"""

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!  All Book Extended Formulations  !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!  Xform  9/9/2005
!  Contains
!    WW-U        **DONE!** (XFormWWU)
!    WW-U-B      **DONE!** (XFormWWUB)
!    WW-U-SC     **DONE!** (XFormWWUSC)
!    WW-U-SC,B   **DONE!** (XFormWWUSCB) needs to be checked!
!    WW-CC       **DONE!** (XFormWWCC)

!    LS-U1=(MC)  **DONE!** (XFormLSU1)
!    LS-U2=(SP)  **DONE!** (XFormLSU2)
!    LS-U-B      **DONE!** (XFormLSUB)

!Added 30/9/2005
!    DLSI-CC
!    DLSI-CC-B
!    DLS-CC-B    !!TODO!!!
!    DLS-CC-SC

! Added 30/9/05 (not in Xformsimple)
!    WW-U-LB     **DONE!** (XFormWWULB) has no effect on clb.mod!
!    WW-CC-B     **DONE!** (XFormWWCCB) wrong solution on clb.mod

!Missing 24/7/07
!    LS-U-SC

! Added 16/12/09
!    LT  Lasdon-Terjung
!    DLS-CC-SC-U with integer (not just 0-1 demands)
"""


def mrange(a, b):
    """Returns a range [a, b]."""
    return xrange(a, b+1)


def CumulDemand(d, NT):
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


def XFormWWU(model, s, y, d, NT, Tk, prefix=""):
    """
    Basic Wagner-Whitin

    procedure XFormWWU(
        s : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC: integer)

        declarations
            XWW: array (1..NT,range) of linctr
            D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)
        forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0)
          XWW(k,l):=s(k-1) >= D(k,l) - sum (i in k..l) D(i,l)*y(i)
        if MC = 1 then
        forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0)
          setmodcut(XWW(k,l))
        end-if
    end-procedure
    """
    # CumulDemand(d,D,NT)
    D = CumulDemand(d, NT)

    # forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0) XWW(k,l) :=
    # s(k-1) >= D(k,l) - sum (i in k..l) D(i,l)*y(i)
    for k in mrange(1, NT):
        for l in mrange(k, min(NT, k+Tk-1)):
            if D[l, l] > 0:
                rhs = [D[k, l]]+[
                    (-D[i, l], y[i])
                    for i in mrange(k, l)
                ]
                model.add_con(s[k-1], ">=", rhs)


def XFormWWUB(model, s, r, y, d, NT, Tk, prefix=""):
    """
    Wagner-Whitin and Backlogging

    procedure XFormWWUB(
        s : array (range) of linctr,
        r : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC : integer)

        declarations
            a,b: array(1..NT) of mpvar
            XA,XB:array(1..NT,1..NT) of linctr
            XY:array(1..NT) of linctr
            D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)

        forall (t in 1..NT) XY(t):=a(t)+b(t)+y(t)>=1

        forall (k in 1..NT,t in k..minlist(NT,k+Tk-1) | D(t,t)>0) XA(k,t) :=
          s(k-1)>=sum(i in k..t) D(i,i)*a(i) - sum (i in k..t-1) D(i+1,t)*y(i)
        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k | D(t,t)>0) XB(k,t) :=
          r(k)>=sum(i in t..k) D(i,i)*b(i) - sum (i in t+1..k) D(t,i-1)*y(i)
        if MC=1 then
        forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)| D(t,t)>0)
          setmodcut(XA(k,t))
        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k | D(t,t)>0)
          setmodcut(XB(k,t))
        end-if
    end-procedure
    """
    # CumulDemand(d,D,NT)
    D = CumulDemand(d, NT)

    def avar(i):
        return prefix+"a_{0}".format(i)

    def bvar(i):
        return prefix+"b_{0}".format(i)

    # a,b: array(1..NT) of mpvar
    for i in mrange(1, NT):
        model.add_var(name=avar(i), lb=0)
        model.add_var(name=bvar(i), lb=0)

    # forall (t in 1..NT) XY(t) :=
    # a(t)+b(t)+y(t)>=1
    for t in mrange(1, NT):
        model.add_con([avar(t), bvar(t), y[t]], ">=", 1)

    # forall (k in 1..NT,t in k..minlist(NT,k+Tk-1) | D(t,t)>0) XA(k,t) :=
    # s(k-1)>=sum(i in k..t) D(i,i)*a(i) - sum (i in k..t-1) D(i+1,t)*y(i)
    for k in mrange(1, NT):
        for t in mrange(k, min(NT, k+Tk-1)):
            if D[t, t] > 0:
                rhs = []
                for i in mrange(k, t):
                    rhs.append((D[i, i], avar(i)))
                for i in mrange(k, t-1):
                    rhs.append((-D[i+1, t], y[i]))
                model.add_con(s[k-1], ">=", rhs)

    # forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k | D(t,t)>0) XB(k,t) :=
    # r(k)>=sum(i in t..k) D(i,i)*b(i) - sum (i in t+1..k) D(t,i-1)*y(i)
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k):
            if D[t, t] > 0:
                rhs = [
                    (D[i, i], bvar(i))
                    for i in mrange(t, k)
                ]+[
                    (-D[t, i-1], y[i])
                    for i in mrange(t+1, k)
                ]
                model.add_con(r[k], ">=", rhs)


def XFormWWUSC(model, s, y, z, d, NT, Tk, prefix=""):
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
    # CumulDemand(d,D,NT)
    D = CumulDemand(d, NT)

    # forall (k in 1..NT,l in k..minlist(NT,k+Tk-1)| D(l,l)>0) XWW(k,l) :=
    # s(k-1) >= D(k,l) - D(k,l)*y(k) - sum (i in k+1..l) D(i,l)*z(i)
    for k in mrange(1, NT):
        for l in mrange(k, min(NT, k+Tk-1)):
            if D[l, l] > 0:
                rhs = [D[k, l], (-D[k, l], y[k])]
                for i in mrange(k+1, l):
                    rhs.append((-D[i, l], z[i]))
                model.add_con(s[k-1], ">=", rhs)


def XFormWWUSCB(model, s, r, y, z, w, d, NT, Tk, prefix=""):
    """
    Wagner-Whitin, Backlogging and Start-up

    procedure XFormWWUSCB(
        s : array (range) of linctr,
        r : array (range) of linctr,
        y : array (range) of linctr,
        z : array (range) of linctr,
        w : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC: integer)

        declarations
            a,b: array(1..NT) of mpvar
            XA,XB:array(1..NT,1..NT) of linctr
            XY:array(1..NT) of linctr
        end-declarations

        ! Modification 9/2/04 to be checked
        !forall (t in 1..NT) XY(t):=a(t)+b(t)+y(t)>=1
        forall (t in 1..NT | d(t) > 0) XY(t):=a(t)+b(t)+y(t)>=1


        ! modification  9/2/04
        forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)| d(t) > 0)
          !XA(k,t):=s(k-1)>=sum(l in k..t) d(l)*(a(l)-sum(i in k+1..l) w(i))
          ! 2nd modification 12/12/07. No
          XA(k,t):=s(k-1)>=sum(l in k..t) d(l)*(a(l)-sum(i in k..l-1) w(i))
          !XA(k,t):=s(k-1) >= sum(l in k..t) d(l)*(a(l) -if(l>k,y(k),0)-
          !  if(l>k+1,sum(i in k+1..l-1) z(i),0))
        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k | d(t) > 0)
          XB(k,t):=r(k) >= sum(l in t..k) d(l)*(b(l) - sum(i in l+1..k) z(i))
        if MC=1 then
          forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)| d(t) > 0)
            setmodcut(XA(k,t))
          forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k | d(t) > 0)
            setmodcut(XB(k,t))
        end-if
    end-procedure
    """
    def avar(i):
        return prefix+"a_{0}".format(i)

    def bvar(i):
        return prefix+"b_{0}".format(i)

    # a,b: array(1..NT) of mpvar
    for i in mrange(1, NT):
        model.add_var(name=avar(i), lb=0)
        model.add_var(name=bvar(i), lb=0)

    # forall (t in 1..NT | d(t) > 0) XY(t) :=
    # a(t)+b(t)+y(t)>=1
    for t in mrange(1, NT):
        if d[t] > 0:
            model.add_con([avar(t), bvar(t), y[t]], ">=", 1)

    # forall (k in 1..NT,t in k..minlist(NT,k+Tk-1)| d(t) > 0) XA(k,t) :=
    # s(k-1)>=sum(l in k..t) d(l)*(a(l)-sum(i in k..l-1) w(i))
    for k in mrange(1, NT):
        for k in mrange(k, min(NT, k+Tk-1)):
            if d[t] > 0:
                rhs = []
                for l in mrange(k, t):
                    rhs.append((d[l], avar(l)))
                    for i in mrange(k, l-1):
                        rhs.append((-d[l], w[i]))
                model.add_con(s[k-1], ">=", rhs)

    # forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k | d(t) > 0) XB(k,t) :=
    # r(k) >= sum(l in t..k) d(l)*(b(l) - sum(i in l+1..k) z(i))
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k):
            if d[t] > 0:
                rhs = []
                for l in mrange(t, k):
                    rhs.append((d[l], bvar(l)))
                    for i in mrange(l+1, k):
                        rhs.append((-d[l], z[i]))
                model.add_con(r[k], ">=", rhs)


def XFormWWULB(model, s, y, d, L, NT, Tk, prefix=""):
    """
    Wagner-Whitin, Constant Lower Bound

    procedure XFormWWULB(
        s : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        L : real,
        NT : integer,
        Tk : integer,
        MC : integer)

        declarations
            Ts=1..NT
            Ts0=0..NT
            ws: array(Ts0,range) of mpvar
            gs: array(Ts0,range) of real
            ds: array(Ts0) of mpvar
            XS,XW:array(Ts0) of linctr
            XLKT:array(Ts0,Ts0) of linctr
            XRKT:array(Ts0,Ts0,Ts0) of linctr
            D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)
        forall(k in Ts0,t in k+1..minlist(NT,k+Tk))
            gs(k,t):=D(k+1,t)-L*(ceil(D(k+1,t)/L)-1)
        forall(k in Ts0,t in maxlist(0,k-Tk)..k-1)
            gs(k,t):=L*(floor(D(t+1,k)/L)+1)-D(t+1,k)
        forall(k in Ts0)
            gs(k,k):=L
        forall(k in Ts0,t in maxlist(0,k-Tk)..minlist(NT,k+Tk)|gs(k,t)<>0)
            create(ws(k,t))

        forall(k in Ts0) XS(k):=
          s(k)>=L*ds(k)+
          sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk))gs(k,i)*ws(k,i)
        forall(k in Ts0) XW(k):=
          sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk)) ws(k,i)<=1
        forall (k in Ts0,l in k+1..minlist(NT,k+Tk),t in k..l) XRKT(k,l,t) :=
          ds(k)+
          sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk)|gs(k,i)>=gs(k,t))ws(k,i)>=
          floor( (D(k+1,l)-gs(k,t))/L)+1+
          sum(i in k+1..l)
            (floor((D(k+1,i-1)-gs(k,t))/L) - floor( (D(k+1,l)-gs(k,t))/L))*y(i)
        forall(k in Ts0,t in maxlist(0,k-Tk)..k-1) XLKT(k,t) :=
          ds(k)+
          sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk)|gs(k,i)>=gs(k,t))ws(k,i)>=
          sum(i in t+1..k)y(i)-floor(D(t+1,k)/L)
    end-procedure
    """
    # Ts=1..NT
    # Ts0=0..NT
    Ts = mrange(1, NT)
    Ts0 = mrange(0, NT)

    def wsvar(i, j):
        return prefix+"ws_{0}_{1}".format(i, j)

    def dsvar(i):
        return prefix+"ds_{0}".format(i)

    # CumulDemand(d,D,NT)
    D = CumulDemand(d, NT)

    gs = {}
    # forall(k in Ts0,t in k+1..minlist(NT,k+Tk))
    # gs(k,t):=D(k+1,t)-L*(ceil(D(k+1,t)/L)-1)
    for k in Ts0:
        for t in mrange(k+1, min(NT, k+Tk)):
            gs[k, t] = D[k+1, t]-L*(ceil(D[k+1, t]/float(L))-1)

    # forall(k in Ts0,t in maxlist(0,k-Tk)..k-1)
    # gs(k,t):=L*(floor(D(t+1,k)/L)+1)-D(t+1,k)
    for k in Ts0:
        for t in mrange(max(0, k-Tk), k-1):
            gs[k, t] = L*(floor(D[t+1, k]/float(L))+1)-D[t+1, k]

    # forall(k in Ts0)
    # gs(k,k):=L
    for k in Ts0:
        gs[k, k] = L

    # ws: array(Ts0,range) of mpvar
    # ds: array(Ts0) of mpvar
    # forall(k in Ts0,t in maxlist(0,k-Tk)..minlist(NT,k+Tk)|gs(k,t)<>0)
    #   create(ws(k,t))
    for k in Ts0:
        model.add_var(name=dsvar(k), lb=0)
        for t in mrange(max(0, k-Tk), min(NT, k+Tk)):
            if gs[k, t] != 0 or True:  # possible bug: gs[k, t] != 0?
                model.add_var(name=wsvar(k, t), lb=0)

    # forall(k in Ts0) XS(k) :=
    # s(k)>=L*ds(k)+sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk))gs(k,i)*ws(k,i)
    for k in Ts0:
        rhs = [
            (gs[k, i], wsvar(k, i))
            for i in mrange(max(0, k-Tk), min(NT, k+Tk))
            if gs[k, i] != 0
        ]
        model.add_con(s[k], ">=", rhs)

    # forall(k in Ts0) XW(k) :=
    # sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk)) ws(k,i)<=1
    for k in Ts0:
        lhs = [
            wsvar(k, i)
            for i in mrange(max(0, k-Tk), min(NT, k+Tk))
        ]
        model.add_con(lhs, "<=", 1)

    # forall (k in Ts0,l in k+1..minlist(NT,k+Tk),t in k..l) XRKT(k,l,t) :=
    # ds(k)+sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk)|gs(k,i)>=gs(k,t))
    #   ws(k,i)
    # >=
    # floor( (D(k+1,l)-gs(k,t))/L)+1+sum(i in k+1..l)
    #   (floor((D(k+1,i-1)-gs(k,t))/L) - floor( (D(k+1,l)-gs(k,t))/L))*y(i)
    for k in Ts0:
        for l in mrange(k+1, min(NT, k+Tk)):
            for t in mrange(k, l):
                lhs = [dsvar(k)]+[
                    wsvar(k, i)
                    for i in mrange(max(0, k-Tk), min(NT, k+Tk))
                    if gs[k, i] >= gs[k, t]
                ]
                rhs = [floor((D[k+1, l]-gs[k, t])/float(L))+1]
                for i in mrange(k+1, l):
                    # possible bug: floor((D[k+1, i-1]-gs[k, t])/float(L))
                    #               D[1, 0] is undefined
                    coef = (
                        floor((D[k+1, i-1]-gs[k, t])/float(L)) -
                        floor((D[k+1, l]-gs[k, t])/float(L))
                    )
                    rhs.append((coef, y[i]))
                model.add_con(lhs, ">=", rhs)

    # forall(k in Ts0,t in maxlist(0,k-Tk)..k-1) XLKT(k,t) :=
    # ds(k)+sum(i in maxlist(0,k-Tk)..minlist(NT,k+Tk)|gs(k,i)>=gs(k,t))
    #   ws(k,i)
    # >= sum(i in t+1..k)y(i)-floor(D(t+1,k)/L)
    for k in Ts0:
        for t in mrange(max(0, k-Tk), k-1):
            lhs = [dsvar(k)]+[
                wsvar(k, i)
                for i in mrange(max(0, k-Tk), min(NT, k+Tk))
                if gs[k, i] >= gs[k, t]
            ]
            rhs = [y[i] for i in mrange(t+1, k)]+[-floor(D[t+1, k]/float(L))]
            model.add_con(lhs, ">=", rhs)


def XFormWWCC(model, s, y, d, C, NT, Tk, prefix=""):
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
            model.add_var(name=wsvar(k-1, t), lb=0)
        model.add_var(name=dsvar(k-1), lb=0)

    # CumulDemand(d,D,NT)
    # forall(k in 1..NT,t in k..minlist(NT,k+Tk-1))
    # gs(k-1,t):=D(k,t)-C*floor(D(k,t)/C)
    D = CumulDemand(d, NT)
    gs = {}
    for k in mrange(1, NT):
        for t in mrange(k, min(NT, k+Tk-1)):
            gs[k-1, t] = D[k, t]-C*floor(D[k, t]/float(C))

    # forall(k in 1..NT) XS(k) :=
    # s(k-1) >= C*ds(k-1)+sum(i in k..minlist(NT,k+Tk-1))gs(k-1,i)*ws(k-1,i)
    for k in mrange(1, NT):
        rhs = [(C, dsvar(k-1))]
        for i in mrange(k, min(NT, k+Tk-1)):
            rhs.append((gs[k-1, i], wsvar(k-1, i)))
        model.add_con(s[k-1], ">=", rhs)

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
            model.add_con(lhs, ">=", floor(D[k, t]/float(C))+1)


def XFormWWCCB2(model, s, r, y, D, C, T1, TN, prefix=""):
    """
    Wagner-Whitin, Constant Capacity and Backlogging (auxiliar function)

    procedure XFormWWCCB(
        s : array (range) of linctr,
        r : array (range) of linctr,
        y : array (range) of linctr,
        D : array (range,range) of real,
        C : real,
        T1: integer,
        TN: integer,
        MC: integer)

        declarations
            T0=T1-1
            Ts=T1..TN
            Ts0=T0..TN
        end-declarations

        declarations
            ws,wr: array(Ts0,Ts0) of mpvar
            gs,gr: array(Ts0,Ts0) of real
            ds,dr: array(Ts0) of mpvar
            Tkk,b:integer
            a:real
            XS,XR,XWS,XWR:array(Ts0) of linctr
            XLT:array(Ts,Ts,Ts0) of linctr
        end-declarations

        forall(k in Ts0,t in T0..k-1) gr(k,t):=D(t+1,k)-C*floor(D(t+1,k)/C)
        forall(k in Ts0,t in T0..k-1) gs(k,t):=C*ceil(D(t+1,k)/C)-D(t+1,k)

        forall(k in Ts0,t in k+1..TN) gs(k,t):=D(k+1,t)-C*floor(D(k+1,t)/C)
        forall(k in Ts0,t in k+1..TN) gr(k,t):=C*ceil(D(k+1,t)/C)-D(k+1,t)

        forall(k in Ts0) gs(k,k):=0
        forall(k in Ts0) gr(k,k):=0

        forall(k in T0..TN-1) XS(k):=s(k)>=C*ds(k)+sum(i in Ts0)gs(k,i)*ws(k,i)
        forall(k in Ts) XR(k):=r(k)>=C*dr(k)+sum(i in Ts0)gr(k,i)*wr(k,i)
        forall(k in T0..TN-1) XWS(k):=sum(i in Ts0) ws(k,i)<=1
        forall(k in Ts) XWR(k):=sum(i in Ts0) wr(k,i)<=1
        forall (k in Ts,l in k..TN,t in Ts0 | ceil( (D(k,l)-gr(l,t))/C) > 0)
            XLT(k,l,t):=ds(k-1)+dr(l)+sum(i in k..l)y(i)+
                         sum(i in Ts0|gs(k-1,i)>=gs(k-1,t))ws(k-1,i)+
                         sum(i in Ts0|gr(l,i)>gr(l,t))wr(l,i)>=
                         ceil( (D(k,l)-gr(l,t))/C)
        !if MC=1 then
        !forall (k in Ts,l in k..TN,t in Ts0) setmodcut(XLT(k,l,t))
        !end-if
    """
    # T0=T1-1
    # Ts=T1..TN
    # Ts0=T0..TN
    T0 = T1-1
    Ts = mrange(T1, TN)
    Ts0 = mrange(T0, TN)

    def wsvar(i, j):
        return prefix+"ws_{0}_{1}".format(i, j)

    def wrvar(i, j):
        return prefix+"wr_{0}_{1}".format(i, j)

    def dsvar(i):
        return prefix+"ds_{0}".format(i)

    def drvar(i):
        return prefix+"dr_{0}".format(i)

    # ws,wr: array(Ts0,Ts0) of mpvar
    for i in Ts0:
        for j in Ts0:
            if wsvar(i, j) not in model.vars:
                model.add_var(name=wsvar(i, j), lb=0)
            if wrvar(i, j) not in model.vars:
                model.add_var(name=wrvar(i, j), lb=0)

    # ds,dr: array(Ts0) of mpvar
    for i in Ts0:
        if dsvar(i) not in model.vars:
            model.add_var(name=dsvar(i), lb=0)
        if drvar(i) not in model.vars:
            model.add_var(name=drvar(i), lb=0)

    gr, gs = {}, {}
    # forall(k in Ts0,t in T0..k-1) gr(k,t):=D(t+1,k)-C*floor(D(t+1,k)/C)
    # forall(k in Ts0,t in T0..k-1) gs(k,t):=C*ceil(D(t+1,k)/C)-D(t+1,k)
    for k in Ts0:
        for t in mrange(T0, k-1):
            gr[k, t] = D[t+1, k]-C*floor(D[t+1, k]/float(C))
            gs[k, t] = C*ceil(D[t+1, k]/float(C))-D[t+1, k]

    # forall(k in Ts0,t in k+1..TN) gs(k,t):=D(k+1,t)-C*floor(D(k+1,t)/C)
    # forall(k in Ts0,t in k+1..TN) gr(k,t):=C*ceil(D(k+1,t)/C)-D(k+1,t)
    for k in Ts0:
        for t in mrange(k+1, TN):
            gs[k, t] = D[k+1, t]-C*floor(D[k+1, t]/float(C))
            gr[k, t] = C*ceil(D[k+1, t]/float(C))-D[k+1, t]

    # forall(k in Ts0) gs(k,k):=0
    # forall(k in Ts0) gr(k,k):=0
    for k in Ts0:
        gs[k, k] = 0
        gr[k, k] = 0

    # forall(k in T0..TN-1) XS(k) :=
    # s(k)>=C*ds(k)+sum(i in Ts0)gs(k,i)*ws(k,i)
    for k in mrange(T0, TN-1):
        rhs = [(C, dsvar(k))]
        for i in Ts0:
            rhs.append((gs[k, i], wsvar(k, i)))
        model.add_con(s[k], ">=", rhs)

    # forall(k in Ts) XR(k) :=
    # r(k)>=C*dr(k)+sum(i in Ts0)gr(k,i)*wr(k,i)
    for k in Ts:
        rhs = [(C, drvar(k))]
        for i in Ts0:
            rhs.append((gr[k, i], wrvar(k, i)))
        model.add_con(r[k], ">=", rhs)

    # forall(k in T0..TN-1) XWS(k) :=
    # sum(i in Ts0) ws(k,i)<=1
    for k in mrange(T0, TN-1):
        model.add_con([wsvar(k, i) for i in Ts0], "<=", 1)

    # forall(k in Ts) XWR(k) :=
    # sum(i in Ts0) wr(k,i)<=1
    for k in Ts:
        model.add_con([wrvar(k, i) for i in Ts0], "<=", 1)

    # forall (k in Ts,l in k..TN,t in Ts0 | ceil( (D(k,l)-gr(l,t))/C) > 0)
    # ds(k-1)+dr(l)+sum(i in k..l)y(i)+
    # sum(i in Ts0|gs(k-1,i)>=gs(k-1,t))ws(k-1,i)+
    # sum(i in Ts0|gr(l,i)>gr(l,t))wr(l,i)  # possible bug: shouldn't be >=?
    # >= ceil( (D(k,l)-gr(l,t))/C)
    for k in Ts:
        for l in mrange(k, TN):
            for t in Ts0:
                if ceil((D[k, l]-gr[l, t])/float(C)) > 0:
                    lhs = [dsvar(k-1), drvar(l)]
                    for i in mrange(k, l):
                        lhs.append(y[i])
                    for i in Ts0:
                        if gs[k-1, i] >= gs[k-1, t]:
                            lhs.append(wsvar(k-1, i))
                    for i in Ts0:
                        if gr[l, i] >= gr[l, t]:
                            lhs.append(wrvar(l, i))
                    model.add_con(lhs, ">=", ceil((D[k, l]-gr[l, t])/float(C)))


def XFormWWCCB(model, s, r, y, d, C, NT, Tk, prefix=""):
    """
    Wagner-Whitin, Constant Capacity and Backlogging

    procedure XFormWWCCB(
        s : array (range) of linctr,
        r : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        C : real,
        NT: integer,
        Tk: integer,
        MC: integer)

        declarations
          t1,t2:integer
          D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)
        ! modified 30/4/04: added if condition
        if(2 <=Tk and Tk <= NT) then
            t1:=2-Tk
            repeat
              t1+=Tk-1
              t2:=minlist(NT,t1+Tk+Tk-3)
              XFormWWCCB(s,r,y,D,C,t1,t2,MC)
            until (t2>=NT)
        end-if
    end-procedure
    """
    # CumulDemand(d,D,NT)
    D = CumulDemand(d, NT)
    if 2 <= Tk <= NT:
        t1 = 2-Tk
        while True:
            t1 += Tk-1
            t2 = min(NT, t1+Tk+Tk-3)
            XFormWWCCB2(model, s, r, y, D, C, t1, t2, prefix)
            if t2 >= NT:
                break


def XFormLSU1(model, s, x, y, d, NT, Tk, prefix=""):
    """
    Multi-commodity for LS-U

    procedure XFormLSU1(
        s : array (range) of linctr,
        x : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC : integer)

        declarations
            MUC,YC: array (1..NT,range) of linctr
            XC,SC: array (1..NT) of linctr
            xx:dynamic array (1..NT,1..NT) of mpvar
            xs:dynamic array (0..NT-1,1..NT) of mpvar
        end-declarations

        forall(k in 1..NT,t in maxlist(1,k-Tk+1)..k) create(xx(t,k))
        forall(k in 1..NT,t in maxlist(1,k-Tk+1)..k) create(xs(t-1,k))

        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k) MUC(t,k):=
            xx(t,k)+xs(t-1,k)=if(t=k,d(t),xs(t,k))
        forall (t in 1..NT) XC(t):=x(t)>=sum(k in t..NT) xx(t,k)
        forall (t in 1..NT) SC(t):=s(t-1)>=sum(k in t..NT) xs(t-1,k)
        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k) YC(t,k):=
            d(k)*y(t)>=xx(t,k)
        if MC=1 then
            forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k)
            setmodcut(YC(t,k))
        end-if
    end-procedure
    """
    def xxvar(i, j):
        return prefix+"xx_{0}_{1}".format(i, j)

    def xsvar(i, j):
        return prefix+"xs_{0}_{1}".format(i, j)

    # xx:dynamic array (1..NT,1..NT) of mpvar
    # xs:dynamic array (0..NT-1,1..NT) of mpvar
    # forall(k in 1..NT,t in maxlist(1,k-Tk+1)..k) create(xx(t,k))
    # forall(k in 1..NT,t in maxlist(1,k-Tk+1)..k) create(xs(t-1,k))
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k):
            model.add_var(name=xxvar(t, k), lb=0)
            model.add_var(name=xsvar(t-1, k), lb=0)

    # forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k) MUC(t,k) :=
    # xx(t,k)+xs(t-1,k)=if(t=k,d(t),xs(t,k))
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k):
            lhs = [xxvar(t, k), xsvar(t-1, k)]
            rhs = d[t] if t == k else xsvar(t, k)
            model.add_con(lhs, "=", rhs)

    # forall (t in 1..NT) XC(t) :=
    # x(t)>=sum(k in t..NT) xx(t,k)
    for t in mrange(1, NT):
        rhs = [xxvar(t, k) for k in mrange(t, NT)]
        model.add_con(x[t], ">=", rhs)

    # forall (t in 1..NT) SC(t) :=
    # s(t-1)>=sum(k in t..NT) xs(t-1,k)
    for t in mrange(1, NT):
        rhs = [xsvar(t-1, k) for k in mrange(t, NT)]
        model.add_con(s[t-1], ">=", rhs)

    # forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k) YC(t,k) :=
    # d(k)*y(t)>=xx(t,k)
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k):
            model.add_con((d[k], y[t]), ">=", xxvar(t, k))


def XFormLSU2(model, s, x, y, d, NT, Tk, prefix=""):
    """
    Shortest path for LS-U

    procedure XFormLSU2(
        s : array (range) of linctr,
        x : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC : integer)

        declarations
            X,Y: array (1..NT) of linctr
            SP1,SP2: array (0..NT+1) of linctr
            S: array (0..NT-1) of linctr
            u:dynamic array (0..NT,0..NT) of mpvar
            v1,v2,w:dynamic array (0..NT) of mpvar
            D : array (range,range) of real
        end-declarations

        CumulDemand(d,D,NT)
        forall(t in 1..NT-Tk+1) create(w(t))
        forall(t in 0..NT-Tk+1) create(v1(t))
        forall(t in Tk-1..NT) create(v2(t))
        forall(i in 0..NT, j in i..minlist(i+Tk-2,NT)) create(u(i,j))

        forall (t in 0..NT+1) SP1(t):=
            if(t>=1,sum(i in 0..t-1) u(i,t-1)+v2(t-1),1) =
            if (t<=NT,sum(i in t..NT) u(t,i)+v1(t),1)
        forall (t in 1..NT-Tk+2) SP2(t):=
            v1(t-1)+if(t>1,w(t-1),0)=if(t<NT-Tk+2,w(t),0)+v2(t+Tk-2)
        forall (t in 1..NT) X(t):=
            x(t)>=sum(i in t..NT) D(t,i)*u(t,i)+D(t,t+Tk-1)*v1(t)
        forall (t in 1..NT) Y(t):=
            y(t)>=sum(i in t..NT|D(t,i)>0) u(t,i)+if(D(t,t+Tk-1)>0,v1(t),0)
        forall (t in 0..NT-1) S(t):=
            s(t) >=
            sum(i in 0..t,j in t+1..NT) D(t+1,j)*u(i,j)+
            if(t<=NT-Tk,D(t+1,t+Tk)*w(t+1),0)+
            sum(i in t+1..minlist(NT,t+Tk-1))D(t+1,i)*v2(i)
    ! Ignore the value of MC

    end-procedure
    """
    # CumulDemand(d,D,NT)
    D = CumulDemand(d, NT)

    def v1var(i):
        return prefix+"v1_{0}".format(i)

    def v2var(i):
        return prefix+"v2_{0}".format(i)

    def wvar(i):
        return prefix+"w_{0}".format(i)

    def uvar(i, j):
        return prefix+"u_{0}_{1}".format(i, j)

    # v1,v2,w:dynamic array (0..NT) of mpvar
    # forall(t in 1..NT-Tk+1) create(w(t))
    # forall(t in 0..NT-Tk+1) create(v1(t))
    # forall(t in Tk-1..NT) create(v2(t))
    for t in mrange(1, NT-Tk+1):
        model.add_var(name=wvar(t), lb=0)
    for t in mrange(0, NT):  # possible bug: NT or NT-Tk+1?
        model.add_var(name=v1var(t), lb=0)
    for t in mrange(0, NT):  # possible bug: 0 or Tk-1?
        model.add_var(name=v2var(t), lb=0)

    # u:dynamic array (0..NT,0..NT) of mpvar
    # forall(i in 0..NT, j in i..minlist(i+Tk-2,NT)) create(u(i,j))
    for i in mrange(0, NT):
        for j in mrange(i, min(i+Tk, NT)):  # possible bug: i+Tk or i+Tk-2?
            model.add_var(name=uvar(i, j), lb=0)

    # forall (t in 0..NT+1) SP1(t):=
    #   if(t>=1,sum(i in 0..t-1) u(i,t-1)+v2(t-1),1) =
    #   if (t<=NT,sum(i in t..NT) u(t,i)+v1(t),1)
    for t in mrange(0, NT+1):
        if t >= 1:
            lhs = []
            for i in mrange(0, t-1):
                lhs.append(uvar(i, t-1))
                lhs.append(v2var(t-1))
        else:
            lhs = 1
        if t <= NT:
            rhs = []
            for i in mrange(t, NT):
                rhs.append(uvar(t, i))
                rhs.append(v1var(t))
        else:
            rhs = 1
        model.add_con(lhs, "=", rhs)

    # forall (t in 1..NT-Tk+2) SP2(t):=
    # v1(t-1)+if(t>1,w(t-1),0)=if(t<NT-Tk+2,w(t),0)+v2(t+Tk-2)
    for t in mrange(1, NT-Tk+2):
        lhs = [v1var(t-1)]
        if t > 1:
            lhs.append(wvar(t-1))
        rhs = [v2var(t+Tk-2)]
        if t < NT-Tk+2:
            rhs.append(wvar(t))
        model.add_con(lhs, "=", rhs)

    # forall (t in 1..NT) X(t):=
    # x(t)>=sum(i in t..NT) D(t,i)*u(t,i)+D(t,t+Tk-1)*v1(t)
    for t in mrange(1, NT):
        rhs = []
        for i in mrange(t, NT):
            rhs.append((D[t, i], uvar(t, i)))
            # possible bug: t+Tk-1 or min(t+Tk-1, NT)?
            rhs.append((D[t, min(t+Tk-1, NT)], v1var(t)))
        model.add_con(x[t], ">=", rhs)

    # forall (t in 1..NT) Y(t):=
    # y(t)>=sum(i in t..NT|D(t,i)>0) u(t,i)+if(D(t,t+Tk-1)>0,v1(t),0)
    for t in mrange(1, NT):
        rhs = []
        for i in mrange(t, NT):
            if D[t, i] > 0:
                rhs.append(uvar(t, i))
                # possible bug: min(t+Tk-1, NT) or t+Tk-1?
                if D[t, min(t+Tk-1, NT)] > 0:
                    rhs.append(v1var(t))
        model.add_con(y[t], ">=", rhs)

    # forall (t in 0..NT-1) S(t):=
    #   s(t) >=
    #   sum(i in 0..t,j in t+1..NT) D(t+1,j)*u(i,j)+
    #   if(t<=NT-Tk,D(t+1,t+Tk)*w(t+1),0)+
    #   sum(i in t+1..minlist(NT,t+Tk-1))D(t+1,i)*v2(i)
    for t in mrange(0, NT-1):
        rhs = []
        for i in mrange(0, t):
            for j in mrange(t+1, NT):
                rhs.append((D[t+1, j], uvar(i, j)))
            if t < NT-Tk:
                rhs.append((D[t+1, t+Tk], wvar(t+1)))
            for i in mrange(t+1, min(NT, t+Tk-1)):
                rhs.append((D[t+1, i], v2var(i)))
        model.add_con(s[t], ">=", rhs)


def XFormLSU(model, s, x, y, d, NT, Tk, prefix=""):
    """
    LS-U

    procedure XFormLSU(
        s : array (range) of linctr,
        x : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC : integer)

     XFormLSU1(s,x,y,d,NT,Tk,MC)
    end-procedure
    """
    return XFormLSU1(model, s, x, y, d, NT, Tk, prefix)


def XFormLSUBMC(model, s, r, x, y, d, NT, Tk, prefix=""):
    """
    procedure XFormLSUBMC(
        s : array (range) of linctr,
        r : array (range) of linctr,
        x : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC : integer)

        declarations
            QC,Y: array (1..NT,range) of linctr
            X: array (1..NT) of linctr
            S,R: array (0..NT) of linctr
            xx:dynamic array (1..NT,1..NT) of mpvar
            xs,xr:dynamic array (0..NT,1..NT) of mpvar
        end-declarations

        forall(k in 1..NT,t in maxlist(1,k-Tk+1)..minlist(NT,k+Tk-1))
            create(xx(t,k))
        forall(k in 1..NT,t in maxlist(1,k-Tk+1)..k) create(xs(t-1,k))
        forall(k in 1..NT,t in k..minlist(NT,k+Tk-1)) create(xr(t,k))

        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k-1)
            QC(t,k):=xx(t,k)+xs(t-1,k)=xs(t,k)
        forall (k in 1..NT,t in k+1..minlist(NT,k+Tk-1))
            QC(t,k):=xx(t,k)+xr(t,k)=xr(t-1,k)
        forall (k in 1..NT)
            QC(k,k):=xx(k,k)+xs(k-1,k)+xr(k,k)=d(k)
        forall (t in 1..NT) X(t):=x(t)>=sum(k in 1..NT) xx(t,k)
        forall (t in 0..NT) S(t):=s(t)>=sum(k in t+1..NT) xs(t,k)
        forall (t in 0..NT) R(t):=r(t)>=sum(k in 1..t) xr(t,k)
        forall (k in 1..NT,t in maxlist(1,k-Tk+1)..minlist(NT,k+Tk-1))
            Y(t,k):=d(k)*y(t)>=xx(t,k)
    end-procedure
    """
    def xxvar(i, j):
        return prefix+"xx_{0}_{1}".format(i, j)

    def xsvar(i, j):
        return prefix+"xs_{0}_{1}".format(i, j)

    def xrvar(i, j):
        return prefix+"xr_{0}_{1}".format(i, j)

    # xx:dynamic array (1..NT,1..NT) of mpvar
    # forall(k in 1..NT,t in maxlist(1,k-Tk+1)..minlist(NT,k+Tk-1))
    # create(xx(t,k))
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), min(NT, k+Tk-1)):
            model.add_var(name=xxvar(t, k), lb=0)

    # xs,xr:dynamic array (0..NT,1..NT) of mpvar
    # forall(k in 1..NT,t in maxlist(1,k-Tk+1)..k) create(xs(t-1,k))
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k):
            model.add_var(name=xsvar(t-1, k), lb=0)

    # forall(k in 1..NT,t in k..minlist(NT,k+Tk-1)) create(xr(t,k))
    for k in mrange(1, NT):
        for t in mrange(k, min(NT, k+Tk-1)):
            model.add_var(name=xrvar(t, k), lb=0)

    # forall (k in 1..NT,t in maxlist(1,k-Tk+1)..k-1) QC(t,k) :=
    # xx(t,k)+xs(t-1,k)=xs(t,k)
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), k-1):
            model.add_con([xxvar(t, k), xsvar(t-1, k)], "=", xsvar(t, k))

    # forall (k in 1..NT,t in k+1..minlist(NT,k+Tk-1)) QC(t,k) :=
    # xx(t,k)+xr(t,k)=xr(t-1,k)
    for k in mrange(1, NT):
        for t in mrange(k+1, min(NT, k+Tk-1)):
            model.add_con([xxvar(t, k), xrvar(t, k)], "=", xrvar(t-1, k))

    # forall (k in 1..NT) QC(k,k) :=
    # xx(k,k)+xs(k-1,k)+xr(k,k)=d(k)
    for k in mrange(1, NT):
        model.add_con([xxvar(k, k), xsvar(k-1, k), xrvar(k, k)], "=", d[k])

    # forall (t in 1..NT) X(t) :=
    # x(t)>=sum(k in 1..NT) xx(t,k)
    for t in mrange(1, NT):
        model.add_con(x[t], ">=", [xxvar(t, k) for k in mrange(1, NT)])

    # forall (t in 0..NT) S(t) :=
    # s(t)>=sum(k in t+1..NT) xs(t,k)
    for t in mrange(0, NT):
        model.add_con(s[t], ">=", [xsvar(t, k) for k in mrange(t+1, NT)])

    # forall (t in 0..NT) R(t) :=
    # r(t)>=sum(k in 1..t) xr(t,k)
    for t in mrange(0, NT):
        if t >= 1:
            lhs = r[t]  # possible bug: no r[0]
        else:
            lhs = 0
        model.add_con(lhs, ">=", [xrvar(t, k) for k in mrange(1, t)])

    # forall (k in 1..NT,t in maxlist(1,k-Tk+1)..minlist(NT,k+Tk-1)) Y(t,k) :=
    # d(k)*y(t)>=xx(t,k)
    for k in mrange(1, NT):
        for t in mrange(max(1, k-Tk+1), min(NT, k+Tk-1)):
            model.add_con((d[k], y[t]), ">=", xxvar(t, k))


def XFormLSUB(model, s, r, x, y, d, NT, Tk, prefix=""):
    """
    LS-U-B

    procedure XFormLSUB(
        s : array (range) of linctr,
        r : array (range) of linctr,
        x : array (range) of linctr,
        y : array (range) of linctr,
        d : array (range) of real,
        NT : integer,
        Tk : integer,
        MC : integer)

     XFormLSUBMC(s,r,x,y,d,NT,Tk,MC)

    end-procedure
    """
    XFormLSUBMC(model, s, r, x, y, d, NT, Tk, prefix)
