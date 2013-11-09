# -*- coding: utf-8 -*-

from benchit import *
import time
import os
import sys

benchfolder=os.path.join("..","partition-analysis-data",sys.argv[1])
b=Bench(benchfolder)
b.read_methods()
b.read_instances()
b.read_datasets()
b.create_benchmarks()

b.run_benchmarks(100)
b. generate_json_output()
of=OutputFactory(b)
of.generate_rest()

of.generate_html()
