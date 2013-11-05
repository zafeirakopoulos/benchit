# -*- coding: iso-8859-1 -*-

import os
import warnings
import threading
import subprocess
import signal
import time 

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

        print "running (method, instance): ", self.method.id, self.instance["id"]

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
