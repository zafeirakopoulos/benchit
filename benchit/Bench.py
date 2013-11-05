# -*- coding: iso-8859-1 -*-

import os
import json
import itertools

from jinja2 import Environment, FileSystemLoader

from Method import *
from Instance import *
from Dataset import *
from Benchmark import *


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



    def generate_html(self):
        html_path=os.path.join(os.getcwd(),"benchit","output","html")
        self.html_env = Environment(loader=FileSystemLoader(html_path))
        self.html_tmpl={}
        try:
            self.html_tmpl["general"]= self.html_env.get_template("general.html")
        except Exception:
            raise Exception("Could not load general template")

        # Html for instances
        instances_path=os.path.join(self.results_path,"instances")
        if not os.path.exists(instances_path): os.mkdir(instances_path)
        try:
            self.html_tmpl["instance"]= self.html_env.get_template("instance.html")
        except Exception:
            raise Exception("Could not load instance template")
        # Iterate over all instances
        for instance_key in self.instances:
            instance_html=self.html_tmpl["instance"].render({"instance":self.instances[instance_key]})
            outfile_path=os.path.join(instances_path, instance_key+".html")
            if os.path.exists(outfile_path):
                warnings.warn(Warning("Html already exists."),stacklevel=2)
            try:
                htmlfile=open(outfile_path,"w")
            except Exception:
                raise Exception("Html file could not open.")
            htmlfile.write(instance_html)
            htmlfile.close()

        # Html for methods
        methods_path=os.path.join(self.results_path,"methods")
        if not os.path.exists(methods_path): os.mkdir(methods_path)
        try:
            self.html_tmpl["method"]= self.html_env.get_template("method.html")
        except Exception:
            raise Exception("Could not load method template")
        # Iterate over all methods
        for method_key in self.methods.keys():
            method_html=self.html_tmpl["method"].render({"method":self.methods[method_key]})
            outfile_path=os.path.join(methods_path, method_key+".html")
            if os.path.exists(outfile_path):
                warnings.warn(Warning("Html already exists."),stacklevel=2)
            try:
                htmlfile=open(outfile_path,"w")
            except Exception:
                raise Exception("Html file could not open.")
            htmlfile.write(method_html)
            htmlfile.close()

        # Html for datasets
        datasets_path=os.path.join(self.results_path,"datasets")
        if not os.path.exists(datasets_path): os.mkdir(datasets_path)
        try:
            self.html_tmpl["dataset"]= self.html_env.get_template("dataset.html")
        except Exception:
            raise Exception("Could not load dataset template")
        # Iterate over all datasets
        for dataset_key in self.datasets.keys():
            dataset_html=self.html_tmpl["dataset"].render({"dataset":self.datasets[dataset_key]})
            outfile_path=os.path.join(datasets_path, dataset_key+".html")
            if os.path.exists(outfile_path):
                warnings.warn(Warning("Html already exists."),stacklevel=2)
            try:
                htmlfile=open(outfile_path,"w")
            except Exception:
                raise Exception("Html file could not open.")
            htmlfile.write(dataset_html)
            htmlfile.close()


        # Html for benchmarks
        benchmarks_path=os.path.join(self.results_path,"benchmarks")
        if not os.path.exists(benchmarks_path): os.mkdir(benchmarks_path)
        try:
            self.html_tmpl["benchmark"]= self.html_env.get_template("benchmark.html")
        except Exception:
            raise Exception("Could not load benchmark template")
        # Iterate over all benchmarks
        for benchmark_key in self.benchmarks.keys():
            benchmark=self.benchmarks[benchmark_key]
            metrics=[ [ benchmark.read_output(metric_set_key), benchmark.method.metric_sets_captions[metric_set_key] ] for metric_set_key in range(len(benchmark.method.metric_sets)) ]
            the_dict={"benchmark":benchmark,"method":benchmark.method,"instance":benchmark.instance,"metrics":metrics}
            benchmark_html=self.html_tmpl["benchmark"].render(the_dict)
            outfile_path=os.path.join(benchmarks_path, benchmark_key+".html")
            if os.path.exists(outfile_path):
                warnings.warn(Warning("Html already exists."),stacklevel=2)
            try:
                htmlfile=open(outfile_path,"w")
            except Exception:
                raise Exception("Html file could not open.")
            htmlfile.write(benchmark_html)
            htmlfile.close()

        # Html for by dataset


        bydataset_path=os.path.join(self.results_path,"by_dataset")
        if not os.path.exists(bydataset_path): os.mkdir(bydataset_path)
        try:
            self.html_tmpl["by_dataset"]= self.html_env.get_template("by_dataset.html")
        except Exception:
            raise Exception("Could not load bydataset template")


        # Create a dictionary for method names
        methods={}
        for method_id in self.methods.keys():
            methods[method_id]=[ self.methods[method_id].name, self.methods[method_id].metric_sets_captions]


        print methods

        for dataset_key in self.datasets.keys():
            # Let dataset be the currently examined dataset
            dataset=self.datasets[dataset_key]

            # Create a dictionary: keys are instance ids and values are dictionaries
             # with key the method id and value the dictionary of measurements
            instance_results={}
            for instance in dataset.instances:
                instance_results[instance]={}

            # Read the output ofr each benchmark and asisgn it to the appropriate instance
            benchmarks= [self.benchmarks[benchmark_key] for benchmark_key in dataset.benchmarks ]
            for benchmark in benchmarks:
                data= benchmark.read_output()
                instance_results[benchmark.instance["id"]][benchmark.method.id]=data

            tmp=[ list(itertools.product(*[ [method],range(len(self.methods[method].metric_sets))])) for method in self.methods]

            metric_combo=list(itertools.product(*tmp))

            selector=[]
            for combo in metric_combo:
                tmp_dict={}
                for pair in combo:
                    tmp_dict[pair[0]]=pair[1]
                selector.append(tmp_dict)


            #the_dict={"dataset":dataset,"methods":methods,"instances":dataset.instances,"metric_combinations":metric_combo,"results":instance_results}
            the_dict={"dataset":dataset,"methods":methods,"instances":dataset.instances,"selectors":selector,"results":instance_results}
            by_dataset_html=self.html_tmpl["by_dataset"].render(the_dict)

            outfile_path=os.path.join(bydataset_path, dataset_key+".html")

            if os.path.exists(outfile_path):
                warnings.warn(Warning("Html already exists."),stacklevel=2)
            try:
                htmlfile=open(outfile_path,"w")
            except Exception:
                raise Exception("Html file could not open.")
            htmlfile.write(by_dataset_html)
            htmlfile.close()


    