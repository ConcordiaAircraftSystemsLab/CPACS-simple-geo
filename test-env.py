import tixi
import tigl
import os
import numpy as np

import time
from ceasiompy.utils.WB.ConvGeometry import geometry
from ceasiompy.utils.cpacsfunctions import aircraft_name


# create function that takes in the CPACS file, some kwargs with geometry, and the name of the CPACS file to output

# For now, I'll just be using fuse length for testing/dev

def transformer(input_file, output_file='output_cpacs.xml', geometry_dict={}):
    """Transforms a CPACS aircraft geometry by rescaling individual sections

    Parameters
    ----------
    input_file : str
        The location of the CPACS file
    output_file : str
        The name of the output file (default output_cpacs.xml)
    geometry_dict : dict
        A dictionary of aircraft geometry parameters with the values that the output CPACS file should have
        dict keywords: fuselage_length, wing_span
    """
    # Framework:
    # check geometry dict and determine which geo parameters will be changing

    # run the geometry module on each relevant parameter to get geometrical information of each section
    name = aircraft_name(input_file)
    ag = geometry.geometry_eval(input_file, name)
    current_fuse_length = ag.fuse_length
    return ag

def get_uids(cpacs_file, main_aircraft_part):
    """
    Internal functions, gets the UIDs of all sections in a main aircraft part

    Parameters
    ----------
    cpacs_file : str
        location of the cpacs file
    main_aircraft_part : str
        name of the main aircraft part
        valid names: fuselage
    """


if os.path.exists('cpacs/test_cpacs.xml'):
    os.remove('cpacs/test_cpacs.xml')
    os.system('cp cpacs/original/test_cpacs.xml cpacs/test_cpacs.xml')

transformer(input_file='cpacs/test_cpacs.xml', geometry_dict={'fuse_length':10})

