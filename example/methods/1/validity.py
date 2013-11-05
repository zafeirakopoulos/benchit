# -*- coding: iso-8859-1 -*-

def correct(output,answer):
    from sage.all import *
    R=PolynomialRing(QQ,answer[0])
    F=FractionField(R)
    a=F(sage_eval(output[-1], locals=F.gens_dict()))
    b=F(sage_eval(answer[1], locals=F.gens_dict()))
    print a==b
    return a==b
