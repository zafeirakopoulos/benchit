# -*- coding: iso-8859-1 -*-

class Metric(object):
    # The name of the metric is the key in the json definition
    name=None

    # The caption for printing
    caption=None

    # The function that reads the metric value
    reader=None

    def __init__(self, name,caption, reader):
        self.name=name
        self.caption=caption
        self.reader=reader