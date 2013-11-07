# -*- coding: iso-8859-1 -*-

import os
import warnings
import threading
import subprocess
import signal
import time 

import json

class Benchmark(object):
    method=None
    instance=None

    outfile=None
    errfile=None
    outfile_path=None

    command=None
    codefile=None
    process=None

    def __init__(self,bench, method_id,instance_id):
        self.method=bench.methods[str(method_id)]
        self.instance=bench.instances[str(instance_id)]

        # Create the output file. This will be used to read the results
        self.outfile_path=os.path.join(bench.tmp_path,str(method_id)+"_"+str(instance_id)+".out")
        if os.path.exists(self.outfile_path):
            warnings.warn(Warning(self.outfile_path+" already exists."),stacklevel=2)

        # Create the error file.
        self.errfile_path=os.path.join(bench.tmp_path,str(method_id)+"_"+str(instance_id)+".err")
        if os.path.exists(self.errfile_path):
            warnings.warn(Warning(self.errfile_path+" already exists!"),stacklevel=2)

        # Create a file where the code to be executed will be placed
        codefile_path=os.path.join(bench.tmp_path,str(method_id)+"_"+str(instance_id)+".code")
        if os.path.exists(codefile_path):
            warnings.warn(Warning(codefile_path+" already exists."),stacklevel=2)
        try:
            self.codefile=open(codefile_path,"w")
        except Exception:
            raise Exception("Codefile could not open.")


        #Create the code
        method_code=self.method.code.render(self.instance.items() + self.method.definition["parameters"].items())
        system_code=bench.systems_tmpl[self.method.definition["system"]].render({"method_code":method_code})

        # Write code to the codefile
        self.codefile.write(system_code)
        self.codefile.close()

        self.command=self.method.definition["system_call"] + " " + codefile_path


    def run(self, timeout=0):

        def target():

            # Create the output file. This will be used to read the results
            try:
                self.outfile=open(self.outfile_path,"w")
            except Exception:
                raise Exception("Outfile could not open.")

            # Create the error file.
            try:
                self.errfile=open(self.errfile_path,"w")
            except Exception:
                raise Exception("Errfile could not open.")
            self.process = subprocess.Popen(self.command, shell=True, preexec_fn=os.setsid, stdout=self.outfile, stderr=self.errfile)
            self.process.wait()
            self.outfile.flush()
            os.fsync(self.outfile)
            self.outfile.close()
            self.errfile.close()

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            while self.process.poll()==None:
                os.killpg(self.process.pid,signal.SIGTERM)
                time.sleep(1)
                os.system("pkill -9 MathKernel")
                print "trying to kill"

            thread.join()



    def create_json_output(self,bench):
        # Open the output file for reading.
        if not os.path.exists(self.outfile_path):
            warnings.warn(Warning(self.outfile_path+" does not exist."),stacklevel=2)
        try:
            read_file=open(self.outfile_path,"rw")
        except Exception:
            raise Exception("Outfile could not open.")


        # Read the output in a list of lines
        lines=read_file.readlines()
        data_dict={}



        for metric_key in self.method.metrics.keys():
            if metric_key=="correct":
                data_dict[metric_key]=self.instance[self.method.metrics["correct"]]
            else:
                metric_callable=self.method.metrics[metric_key].reader
                answer=metric_callable(lines)
                if answer!=None:
                    data_dict[metric_key]=answer

        if "correct" in self.method.metrics.keys():
            answer=self.method.validity(lines,data_dict["correct"])
            if answer:
                data_dict["correct"]=True
            else:
                data_dict["correct"]=False


        # Create a file where the code to be executed will be placed
        jsonfile_path=os.path.join(bench.json_path,str(self.method.id)+"_"+str(self.instance["id"])+".json")
        if os.path.exists(jsonfile_path):
            warnings.warn(Warning(jsonfile_path+" already exists."),stacklevel=2)
        try:
            self.jsonfile=open(jsonfile_path,"w")
        except Exception:
            raise Exception("JSON file could not open.")

        json.dump(data_dict, self.jsonfile)



