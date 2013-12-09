# -*- coding: iso-8859-1 -*-

import os
import json
import warnings
debug = True

def Latte_to_JSON(filename):
    # Check if the definition file exists
    if not os.path.exists(filename):
        raise Exception("LattE file not found.")
    # Read the file
    LattEfile=None
    try:
        LattEfile=open(filename,"r")
    except Exception:
        raise Exception("LattE file could not open.")
    # Load the LattE file
    Lines=LattEfile.readlines()
    linearity=[]
    header=[]
    print Lines

    header=Lines[0].split()
    if debug: print "Header: \n", header, "\n"
    Lines=Lines[1:]

    for line in Lines:
        if line.split()[0]=="linearity":
            linearity=line.split()[2:]
            if debug: print "Linearity: \n", linearity, "\n"
            Lines.remove(line)
        if line.split()[0]=="nonnegative":
            nonnegative=line.split()[2:]
            if debug: print "Non-negative: \n", nonnegative, "\n"
            Lines.remove(line)

    print Lines
    A=[]
    b=[]
    for line in Lines:
        line=line.strip()
        line=line.split()
        b.append((-1)*int(line[0]))
        A.append([ int(i) for i in line[1:]])
    if debug: print "A: \n", A, "\n"
    if debug: print "b: \n", b, "\n"
    E=[ 0 for i in range(int(header[0]))]
    for i in linearity:
        E[int(i)-1]=1
    if debug: print "E: \n", E, "\n"

    outfile=filename+".json"
    print outfile
    if os.path.exists(outfile):
            warnings.warn(Warning(outfile+" already exists."),stacklevel=2)
    try:
        writefile=open(outfile,"w")
    except Exception:
        raise Exception("JSON output file could not open.")
    the_dict={"A":A,"b":b,"E":E}
    json.dump(the_dict, writefile)
    writefile.close()




def JSON_to_Latte(filename):
    # Check if the definition file exists
    if not os.path.exists(filename):
        raise Exception("JSON file not found.")
    # Read the file
    JSONfile=None
    try:
        JSONfile=open(filename,"r")
    except Exception:
        raise Exception("JSON file could not open.")
    # Load the json dictionary
    definition=json.load(JSONfile)

    Lines=[]
    Lines.append(str(len(definition["b"]))+ " " + str(1+len(definition["A"][0])))
    for e in range(len(definition["A"])):
        Lines.append(" ".join([str((-1)*definition["b"][e])] + [ str(i) for i in  definition["A"][e] ]))
    Lines.append("linearity " + str(sum(definition["E"])) + " " + " ".join([ str((i+1)*definition["E"][i]) for i in range(len(definition["E"])) if (i+1)*definition["E"][i]!=0]))
    Lines.append("nonnegative " + " ".join([ str((i+1)) for i in range(len(definition["A"][0]))]))
    if debug: print "Lines \n", Lines


    outfile=filename+".equ"
    if os.path.exists(outfile):
            warnings.warn(Warning(outfile+" already exists."),stacklevel=2)
    try:
        writefile=open(outfile,"w")
    except Exception:
        raise Exception("LattE output file could not open.")

    for line in Lines:
        writefile.write(line)
        writefile.write("\n")
    writefile.close()

Latte_to_JSON("5flow_3.equ")
JSON_to_Latte("5flow_3.equ.json")
