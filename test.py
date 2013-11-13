# -*- coding: utf-8 -*-

from benchit import *
import time
import os
import sys


import glob
import json
import pandas
pandas.set_option('display.notebook_repr_html', True)
from IPython.display import HTML

from matplotlib import pyplot as plt


##benchfolder=os.path.join("..","partition-analysis-data",sys.argv[1])
#benchfolder=os.path.join(sys.argv[1])
#b=Bench(benchfolder)
#b.read_methods()
#b.read_instances()
#b.read_datasets()
#b.create_benchmarks()

#b.run_benchmarks(600)
#b. generate_json_output()
#of=OutputFactory(b)
#of.generate_rest()

#of.generate_html()

##b.remove_tmp()
#b.create_tarball()