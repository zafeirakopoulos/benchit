# -*- coding: utf-8 -*-

from benchit import *
import time

b=Bench("example")
b.read_methods()
b.read_instances()
b.read_datasets()
b.create_benchmarks()

b.run_benchmarks(10)
b. generate_json_output()
of=OutputFactory(b)
#time.sleep(5)
of.generate_rest()

of.generate_html()