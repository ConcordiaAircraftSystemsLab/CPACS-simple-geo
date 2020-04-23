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
## get number of fuselage positionings
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
    tixi_handle = section_transformer(tixi_handle, scale, ag.fuse_sec_nb[0])
    tixi_handle = positioning_transformer(tixi_handle, scale)
    close_tixi(tixi_handle, output_file)
    return 'done'

def section_transformer(tixi_handle, scale, num_sec):
    """Rescales the section scaling parameter for the fuselage

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be changed
    scale : num
        The value of the scale factor
    num_sec : num
        The number of sections making up the fuselage

    Returns
    -------
    tixi_handle : tixi handle object
        The now edited tixi handle
    """
    sections_xpath = '/cpacs/vehicles/aircraft/model/fuselages/fuselage/sections/'
    for i in np.arange(num_sec):
        section_xpath = sections_xpath + f'section[{i+1}]/transformation/scaling/'
        # get current values
        x_val = tixi_handle.getDoubleElement(section_xpath+'x')
        y_val = tixi_handle.getDoubleElement(section_xpath+'y')
        z_val = tixi_handle.getDoubleElement(section_xpath+'z')
        # update current values
        tixi_handle.updateDoubleElement(section_xpath+'x', x_val*scale, '%.8f')
        tixi_handle.updateDoubleElement(section_xpath+'y', y_val*scale, '%.8f')
        tixi_handle.updateDoubleElement(section_xpath+'z', z_val*scale, '%.8f')

    return tixi_handle

def positioning_transformer(tixi_handle, scale):
    """Rescales the length of each fuselage segment

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be changed
    scale : num
        The value of the scale factor

    Returns
    -------
    tixi_handle : tixi handle object
        The now edited tixi handle
    """

    positionings_xpath = '/cpacs/vehicles/aircraft/model/fuselages/fuselage/positionings'
    num_pos = tixi_handle.getNamedChildrenCount(positionings_xpath, 'positioning')
    for i in np.arange(num_pos):
        length_xpath = positionings_xpath + f'/positioning[{i+1}]/length'
        # get current values
        length = tixi_handle.getDoubleElement(length_xpath)
        # update current values
        tixi_handle.updateDoubleElement(length_xpath, length*scale, '%.8f')
    return tixi_handle



#------------------------------
# MAIN
#------------------------------
# for testing purposes, delete later
if os.path.exists('cpacs/test_cpacs.xml'):
    os.remove('cpacs/test_cpacs.xml')
os.system('cp cpacs/original/test_cpacs.xml cpacs/test_cpacs.xml')

transformer(input_file='cpacs/test_cpacs.xml', output_file='cpacs/test_cpacs.xml', geometry_dict={'fuse_length':10})



