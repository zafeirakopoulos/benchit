# -*- coding: iso-8859-1 -*-

import os
import json
import itertools

from jinja2 import Environment, FileSystemLoader

from Method import *
from Instance import *
from Dataset import *
from Benchmark import *

from OutputFactory import *

class Bench(object):
    root_path=None
    methods_path=None
    datasets_path=None
    instances_path=None
    methods_file_path=None
    datasets_file_path=None
    instances_file_path=None
    results_path=None

    bench_definition=None

    methods_env = None
    systems_env = None

    # System templates
    systems_tmpl={}

    # A dictionary of methods. The method id is the key.
    methods={}
    # A dictionary of instances. The instance id is the key.
    instances={}
    # A dictionary of datasets. The dataset id is the key.
    datasets={}
    # A dictionary of benchmarks.
    benchmarks={}

    #Output Factory
    OF=None

    def __init__(self, bench_name):
        self.root_path=os.path.join(os.getcwd(),bench_name)

        # The name of the json definition is fixed
        definition_path=os.path.join(self.root_path,"definition.json")

        # Check if the definition file exists
        if not os.path.exists(definition_path):
            raise Exception("Bench definition not found.")
        # Read the file
        try:
            definition_file=open(definition_path)
        except Exception:
            raise Exception("Bench definition file could not open.")
        # Load the json dictionary
        self.bench_definition=json.load(definition_file)

        # The methods path is fixed
        self.methods_path=os.path.join(self.root_path,"methods")

        # The datasets path is fixed
        self.datasets_path=os.path.join(self.root_path,"datasets")

        # The instances path is fixed
        self.instances_path=os.path.join(self.root_path,"instances")

        # The results path is fixed. Create if it does not exist
        self.results_path=os.path.join(self.root_path,"results")
        if not os.path.exists(self.results_path):
            os.mkdir(self.results_path)

        # The tmp path is fixed. Create if it does not exist
        self.tmp_path=os.path.join(self.root_path,"tmp")
        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)


        # The methods path is fixed
        self.methods_file_path=os.path.join(self.root_path,"methods",self.bench_definition["methods"]+".json")

        # The datasets path is fixed
        self.datasets_file_path=os.path.join(self.root_path,"datasets",self.bench_definition["datasets"]+".json")

        # The instances path is fixed
        # TODO: Allow more than one files
        self.instances_file_path=os.path.join(self.root_path,"instances",self.bench_definition["instances"]+".json")


    def read_methods(self):

        # Find the path of the methods definition
        methods_file_path=os.path.join(self.methods_path,self.bench_definition["methods"]+".json")

        # Check if the definition file exists
        if not os.path.exists(methods_file_path):
            raise Exception(methods_file_path+" is not a valid path.")
        # Read the file
        try:
            methods_file=open(methods_file_path)
        except Exception:
            raise Exception("Methods file could not open.")

        # Load from json the list of method definitions
        methods_list=json.load(methods_file)

        # Load the template environments for systems
        self.systems_env = Environment(loader=FileSystemLoader(os.path.join(self.methods_path,"systems")))
        for system in [ method["system"] for method in methods_list]:
            try:
                self.systems_tmpl[system]= self.systems_env.get_template(str(system)+".tmpl")
            except Exception:
                raise Exception("Could not load initialization template for "+str(system)+".")

        # Load the template environments for methods
        self.methods_env = Environment(loader=FileSystemLoader(os.path.join(self.methods_path)))

        # Load the methods available in the bench
        for method_definition in methods_list:
            self.methods[method_definition["id"]]= Method(self,method_definition)

        return 0


    #Add the functionality of opening multiple instances files
    def read_instances(self):
        # The name of the json file given in the benchmarks definition
        # The file has to be placed in the instances subfolder
        if not os.path.exists(self.instances_file_path):
            raise Exception(self.instances_file_path+" is not a valid path.")
        try:
            instances_file=open(self.instances_file_path)
        except Exception:
            raise Exception("Instances file could not open.")

        # Load the json contents
        instances_list=json.load(instances_file)

        # Iterate over the defintion dictionaries, loaded by json.
        # Create ONE dictionary for all instances in this Bench.
        for instance in instances_list:
            self.instances[instance["id"]]=Instance(instance)
        return 0


    def read_datasets(self):

        if not os.path.exists(self.datasets_file_path):
            raise Exception(self.datasets_file_path+" is not a valid path.")
        try:
            datasets_file=open(self.datasets_file_path)
        except Exception:
            raise Exception("Datasets file could not open.")

        # Load the json contents
        datasets_list=json.load(datasets_file)


        # Create the Datasets
        for i in range(len(datasets_list)):
            self.datasets[str(i+1)]=Dataset(self,i+1,datasets_list[i])
        return 0

    def create_benchmarks(self,method_ids=None,dataset_ids=None):
        # If no methods are specified use all methods loaded
        if method_ids==None:
            method_ids=self.methods.keys()
        # If no datasets are specified use all datasets loaded
        if dataset_ids==None:
            dataset_ids=self.datasets.keys()
        # Maybe turn keys to strings

        # Select the instance ids appearing in a dataset
        all_instance_ids=list(set([i for i in itertools.chain.from_iterable([self.datasets[dataset_id].instances for dataset_id in dataset_ids])]))

        benchmark_id=1
        # Iterate over all instance ids
        for instance_id in all_instance_ids:
            # For each method specified (the key)
            for method_id in method_ids:
                # Create a benchmark
                benchmark=Benchmark(self,method_id,instance_id)
                self.benchmarks[str(benchmark_id)]=benchmark
                # Iterate over all datasets specified.
                for dataset_id in dataset_ids:
                    # Check if the instance belongs to the dataset
                    if instance_id in self.datasets[dataset_id].instances:
                        self.datasets[dataset_id].benchmarks.append(str(benchmark_id))
                benchmark_id=benchmark_id+1
        return 0

    def run_benchmarks(self, timeout=0, dataset_ids=None):
        if dataset_ids==None:
            dataset_ids=self.datasets.keys()

        # Select all benchmark ids appearing in the datasets
        all_benchmark_ids=list(set([i for i in itertools.chain.from_iterable([self.datasets[dataset_id].benchmarks for dataset_id in dataset_ids])]))

        for benchmark_id in all_benchmark_ids:
            self.benchmarks[benchmark_id].run(timeout)


    def generate_json_output(self):
        self.json_path=os.path.join(self.results_path,"json")
        if not os.path.exists(self.json_path): os.mkdir(self.json_path)

        for benchmark_key in self.benchmarks.keys():
            benchmark=self.benchmarks[benchmark_key]
            metrics= benchmark.create_json_output(self)

    def generate_rest_output(self):
        self.rest_path=os.path.join(self.results_path,"rest")
        if not os.path.exists(self.rest_path): os.mkdir(self.rest_path)

        if self.OF==None: self.OF=OutputFactory(self)
        self.OF.generate_rest()