# -*- coding: utf-8 -*-

import os
import imp
from Metric import *
from jinja2 import Environment, FileSystemLoader

debug = True
class Method(object):
    # The id of the method. Has to fit with the path.
    id=None

    # The definition of the method.
    definition=None

    # A dictionary of metrics
    metrics={}

    # the function for checking the validity of the answer
    validity=None

    # The template generating code for this method
    code=None

    # A boolean stating if there is a validity check for the method
    has_validity=False

    # Given the bench environment and the method id
    def __init__(self, bench, definition):
        # The method id as given in its definition
        self.id=definition["id"]

        # The definition of the method.
        self.definition=definition

        # Read the template from the methods_env defined in bench
        self.code=bench.methods_env.get_template(os.path.join(definition["id"],"code.tmpl"))

        # Load the metric reader functions
        mod_name=os.path.join(bench.methods_path,str(self.id))
        mreaders = imp.load_source(mod_name , os.path.join(bench.methods_path,str(self.id),"metric_reader.py"))

        # Create a dictionary of metrics.
        self.metrics={}
        for metric in self.definition["metrics"]:
            if "correct" in metric: # maybe this should be == to avoid picking other metrics
                self.has_validity=True
                # Load the validity check function
                # Note: We can make "correct" to be a keyword given in the
                # definition in order to check different things
                vreaders = imp.load_source(mod_name,os.path.join(bench.methods_path,str(self.id),"validity.py"))
                self.validity = getattr(vreaders, "correct")
                #self.metrics["correct"]=Metric("correct", "correct", self.validity)
                # This would ruin the choice of which uinstance field is the correct value
                self.metrics.update({metric[0]:metric[1]})
                print self.metrics


            if "correct" not in metric: # maybe this should be == to avoid picking other metrics                
                self.metrics[metric[0]]=Metric(metric[0],metric[1],getattr(mreaders, metric[0]))

        if debug: print "method name: \n", self.definition["name"], "\n"                
        if debug: print "method metrics: \n", self.metrics, "\n"                

