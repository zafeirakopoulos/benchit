# -*- coding: iso-8859-1 -*-

def nvars(instance):
    return len(instance["A"][0])

def nrelations(instance):
    return len(instance["A"])
    
def equations(instance):
    return nrelations(instance)==sum(instance["E"])
    
def mixed(instance):
    return (nrelations(instance)!=sum(instance["E"])) & (sum(instance["E"])!=0)