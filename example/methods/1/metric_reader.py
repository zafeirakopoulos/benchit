# -*- coding: iso-8859-1 -*-

def total_time(output):
    if output==[]: return "-"
    for line in output:
        if "total time taken" in line:
            return line.split()[-1]


def sc(output):
    if output==[]: return "-"
    for line in output:
        if "symbolic cones computation took" in line:
            return line.split()[-1]


def ncones(output):
    if output==[]: return "-"    
    for line in output:
        if "total number of symbolic cones is" in line:
            return line.split()[-1]

def generating(output):
    if output==[]: return "-"
    for line in output:
        if "generating function computation took" in line:
            return line.split()[-1]            

def fundpar(output):
    if output==[]: return "-"
    for line in output:
        if "fund par enumeration" in line:
            return line.split()[-1]

#def correct(output,answer):
    #print "-----------------------"
    #print output[-1]
    #print answer
    #print "======================="    
    #return output[-1]==answer
