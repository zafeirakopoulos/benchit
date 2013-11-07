# -*- coding: iso-8859-1 -*-


def total_time(output):
    if output==[]: return "-"
    for line in output:
        if "= {" in line:
            return line.split()[1].rstrip(",").lstrip("{")


