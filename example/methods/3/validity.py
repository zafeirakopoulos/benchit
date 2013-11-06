# -*- coding: iso-8859-1 -*-

def correct(output,answer):
    from sage.all import *
    R=PolynomialRing(QQ,answer[0])
    F=FractionField(R)
    output_answer=""
    for line_index in range(len(output)):
        if "InputForm=" in output[line_index]:
            output_answer=output_answer+output[line_index].split("=")[1]
            for output_index in range(line_index+1,len(output)):
                output_answer=output_answer+output[output_index].rstrip('\r\n')
                if output[output_index].strip()=="":
                    break
    a=F(sage_eval(output_answer, locals=F.gens_dict()))
    b=F(sage_eval(answer[1], locals=F.gens_dict()))
    print a==b
    return a==b
