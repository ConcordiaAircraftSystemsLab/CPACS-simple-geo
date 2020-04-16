
import os
import numpy as np

import time
from ceasiompy.utils.WB.ConvGeometry import geometry
from ceasiompy.utils.cpacsfunctions import aircraft_name


# create function that takes in the CPACS file, some kwargs with geometry, and the name of the CPACS file to output

# For now, I'll just be using fuse length for testing/dev

def transformer(input_file, output_file='output_cpacs.xml', geometry_dict={}):
    # check geometry dict and determine which geo parameters will be changing

    # run the geometry module on each relevant parameter to get geometrical information of each section
    name = aircraft_name(input_file)
    ag = geometry.geometry_eval(input_file, name)
    current_fuse_length = ag.fuse_length
    return ag


transformer(input_file='cpacs/test_cpacs.xml', geometry_dict={'fuse_length':10})

