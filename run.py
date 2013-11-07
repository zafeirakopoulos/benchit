# -*- coding: iso-8859-1 -*-

from benchit import *

b=Bench("example")
b.read_methods()
b.read_instances()
b.read_datasets()
b.create_benchmarks()
#b.run_benchmarks(100)
b. generate_json_output()
#b.generate_html()

