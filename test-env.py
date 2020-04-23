import tixi3 as tixi
import tigl
import os
import numpy as np

import time
from ceasiompy.utils.WB.ConvGeometry import geometry
from ceasiompy.utils.cpacsfunctions import aircraft_name, open_tixi, close_tixi, get_uid

# For now, I'll just be using fuse length for testing/dev

# Framework
## Load in Cpacs file
## Create a tixi handle
## Also create an aircraft name
## send to geometry_eval to get length and number of segments
## Calculate the scale factor from the total length
## Get the scaling for each section using xpath and tixiGetDoubleElement
## Get the length for each fuselage positioning
## Rewrite the section scaling by rescaling with scale factor
## Rewrite the fuselage positioning length by rescaling with scale factor
## Close tixi handle using output_file name

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
  
    fuse_length_change = geometry_dict.get('fuse_length', 'None')


    name = aircraft_name(input_file)
    ag = geometry.geometry_eval(input_file, name)
    fuse_length = ag.fuse_length[0]
    scale = fuse_length_change/fuse_length

    tixi_handle = open_tixi(input_file)
    fuselage_xpath = '/cpacs/vehicles/aircraft/model/fuselages/fuselage'
    #uid = get_uid(tixi_handle, '/cpacs/vehicles/profiles/fuselageProfiles/fuselageProfile[1]')
    test = tixi_handle.getDoubleElement(fuselage_xpath+'/positionings/positioning[2]/length')
    return test

if os.path.exists('cpacs/test_cpacs.xml'):
    os.remove('cpacs/test_cpacs.xml')
os.system('cp cpacs/original/test_cpacs.xml cpacs/test_cpacs.xml')

print(transformer(input_file='cpacs/test_cpacs.xml', geometry_dict={'fuse_length':10}))


