# -*- coding: utf-8 -*-
import os
import sys
#sphinx_path="benchit/packages//Sphinx-1.2b3-py2.7.egg"
#sys.path.append(sphinx_path)
import sphinx
from jinja2 import Environment, FileSystemLoader
import json

debug = True
class OutputFactory(object):

    bench=None
    output_env=None
    
    def __init__(self, bench):
        self.bench=bench
        output_path=os.path.join(os.getcwd(),"benchit","output")
        self.output_env= Environment(loader=FileSystemLoader(output_path))


    def generate_html(self):

        # Create the conf.py file for sphinx. For the moment just copy the file from the template.

        try:
             conf_tmpl=self.output_env.get_template("sphinx.tmpl")
             configpy=conf_tmpl.render()
             try:
                conffile=open(os.path.join(self.bench.rest_path,"conf.py" ),"w")
                conffile.write(configpy)
                conffile.close()
             except Exception:
                raise Exception("config.py could not open.")
        except Exception:
            raise Exception("Could not create config.py.")
        
        # Build the html
        sphinx.main(["sphinx-build ",self.bench.rest_path,self.bench.html_path])
        
        
    def generate_rest(self):
        self.bench.rest_path=os.path.join(self.bench.results_path,"rest")
        if not os.path.exists(self.bench.rest_path): os.mkdir(self.bench.rest_path)

        instances_toc=[]
        datasets_toc=[]
        benchmarks_toc=[]        

        instance_tmpl=self.output_env.get_template("instance.tmpl")
        if debug: print "Instances: \n", self.bench.instances, "\n"                
        
        for instance_key in self.bench.instances.keys():
            render_data={}
            render_data.update(self.bench.instances[instance_key])
            if debug: print "Render data: \n", render_data, "\n"                

            instances_toc.append("instance_"+str(self.bench.instances[instance_key]["id"]))
            bench_rst=instance_tmpl.render(render_data)
            filepath=os.path.join(self.bench.rest_path, "instance_"+str(self.bench.instances[instance_key]["id"])+".rst" )
            outfile=open( filepath ,"w")
            outfile.write(bench_rst) 
            outfile.close()



        all_json=[]
        for benchmark_file in os.listdir(self.bench.json_path):
            jsonfilename=os.path.join(self.bench.json_path, benchmark_file)
            try:
                jsonfile=open( jsonfilename ,"r")
                data=json.load(jsonfile)
                jsonfile.close()
                all_json.append(data)
            except Exception:
                raise Exception("Could not open json file "+benchmark_file)
            
        benchmark_tmpl=self.output_env.get_template("benchmark.tmpl")        
        for benchmark_data in all_json:
            render_data={}
            render_data.update(benchmark_data)
            render_data.update({"method":self.bench.methods[benchmark_data["method"]], "instance":self.bench.instances[benchmark_data["instance"]]})
            benchmarks_toc.append(str(benchmark_data["method"])+"_"+str(benchmark_data["instance"]))
            bench_rst=benchmark_tmpl.render(render_data)
            filepath=os.path.join(self.bench.rest_path, str(benchmark_data["method"])+"_"+str(benchmark_data["instance"])+".rst" )
            outfile=open( filepath ,"w")
            outfile.write(bench_rst) 
            outfile.close()

        toctree="Bench \n-------- \n.. toctree:: \n  :maxdepth: 1\n\n"
        toctree=toctree+ "  instances.rst \n"
        toctree=toctree+ "  benchmarks.rst \n"        
        outfile=open( os.path.join(self.bench.rest_path, "index.rst" ) ,"w")
        outfile.write(toctree) 
        outfile.close()            
       
        if debug: print "Instances Toc: \n", instances_toc, "\n"                
        if debug: print "Benchmarks Toc: \n", benchmarks_toc, "\n"                

        toctree="Instances \n------------ \n.. toctree:: \n  :maxdepth: 1\n\n"
        for filename in instances_toc:
            toctree=toctree+ "  "+filename + " \n"
        outfile=open( os.path.join(self.bench.rest_path, "instances.rst" ) ,"w")
        outfile.write(toctree) 
        outfile.close()            


        toctree="Benchmarks \n------------ \n.. toctree:: \n  :maxdepth: 1\n\n"
        for filename in benchmarks_toc:
            toctree=toctree+ "  "+filename + " \n"
        outfile=open( os.path.join(self.bench.rest_path, "benchmarks.rst" ) ,"w")
        outfile.write(toctree) 
        outfile.close()            

