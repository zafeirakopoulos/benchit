# -*- coding: iso-8859-1 -*-


def read_output(self, metric_set_key=0):
    # Open the output file for reading.
    if not os.path.exists(self.outfile_path):
        warnings.warn(Warning(self.outfile_path+" does not exist."),stacklevel=2)
    try:
        read_file=open(self.outfile_path,"rw")
    except Exception:
        raise Exception("Outfile could not open.")

    # Choose for this method the metric set indicated in the args
    metrics=self.method.metric_sets[metric_set_key]

    # Read the output in a list of lines
    lines=read_file.readlines()
    data_dict={}

    print self.method.id, self.instance["id"]
    for metric_key in metrics.keys():
        if metric_key=="correct":
            data_dict[metric_key]=self.instance[metrics["correct"]]
        else:
            metric_callable=metrics[metric_key].reader
            answer=metric_callable(lines)
            if answer!=None:
                data_dict[metric_key]=answer


    if "correct" in metrics.keys():
        answer=self.method.validity(lines,data_dict["correct"])
        if answer:
            data_dict["correct"]=True
        else:
            data_dict["correct"]=False

    #print data_dict
    return data_dict
