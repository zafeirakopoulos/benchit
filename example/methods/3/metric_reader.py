# -*- coding: iso-8859-1 -*-

def total_time(output):
    if output==[]: return "-"
    for line in range(len(output)):
        if ">  time(E_Oge(t, [vx], [va]));" in output[line]:
            return output[line+1]
