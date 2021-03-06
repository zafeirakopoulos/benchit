# -*- coding: iso-8859-1 -*-

import os
import imp

class Dataset(object):
    # A unique id for the dataset
    id=None
    # A list of instances
    instances=[]
    # The json definition of the dataset
    definition=None
    # The filters  of the dataset
    filters=None
    # A list of benchmark ids
    benchmarks=None

    #results=[]

    def __init__(self,bench, id, definition):
        self.id=id
        self.definition=definition
        self.instances=[]
        self.benchmarks=[]
        self.filters=definition["filters"]

        # Import the functions filtering the attributes.
        readers_file_path=os.path.join(bench.datasets_path,"attributes.py")
        if not os.path.exists(readers_file_path):
            raise Exception(readers_file_path+" is not a valid path.")
        # Load the attribute reader functions
        areaders = imp.load_source(bench.datasets_path , os.path.join(bench.datasets_path,"attributes.py"))

        # The instances that pass the filters are stored here
        instances_tmp=[]
        # Iterate over all instances loaded in this Bench
        for instance_key in bench.instances.keys():
            # An indicator vector: 1 for pass, 0 for fail test
            indicator=[]
            # For each attribute related to the dataset
            for attr in self.filters.keys():
                # Get the function filtering the data
                areader=getattr(areaders, attr)
                # Check if the test passes
                indicator.append( str(areader(bench.instances[instance_key]))==self.filters[attr])
            # If all test pass, then add to the instances to be added.
            if sum(indicator)==len(indicator):
                # Add instance to the tmp list
                self.instances.append(instance_key)

