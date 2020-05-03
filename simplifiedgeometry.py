import os
import numpy as np

from ceasiompy.utils.WB.ConvGeometry import geometry
from ceasiompy.utils.cpacsfunctions import aircraft_name, open_tixi, close_tixi, add_uid
from tixi3 import tixi3wrapper as tixi

# currently only works for fuse_length

def transformer(input_file, output_file='output_cpacs.xml', geometry_dict={}):
    """Transforms a CPACS aircraft geometry by rescaling individual sections

    Parameters
    ----------
    input_file : str
        The location of the CPACS file
    output_file : str
        The name of the output file (default output_cpacs.xml)
    geometry_dict : dict
        A dictionary of aircraft geometry parameters with the values
            that the output CPACS file should have
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
    Also translates each section in the z-axis so that sections
    are in the correct location relative to each other

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
    sections_xpath = '/cpacs/vehicles/aircraft/model/fuselages/\
                        fuselage/sections/'
    for i in np.arange(num_sec):
        scaling_xpath = sections_xpath +\
            f'section[{i+1}]/transformation/scaling/'
        translate_xpath = sections_xpath +\
            f'section[{i+1}]/transformation/translation/z'

        # get current values
        x_val = tixi_handle.getDoubleElement(scaling_xpath+'x') 
        y_val = tixi_handle.getDoubleElement(scaling_xpath+'y')
        z_val = tixi_handle.getDoubleElement(scaling_xpath+'z')
        z_val_elem = tixi_handle.getDoubleElement(translate_xpath)

        # update current values
        tixi_handle.updateDoubleElement(scaling_xpath+'x', x_val*scale, '%.8f')
        tixi_handle.updateDoubleElement(scaling_xpath+'y', y_val*scale, '%.8f')
        tixi_handle.updateDoubleElement(scaling_xpath+'z', z_val*scale, '%.8f')
        tixi_handle.updateDoubleElement(translate_xpath, z_val_elem*scale,
                                        '%.8f')

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

    positionings_xpath = '/cpacs/vehicles/aircraft/model/fuselages/\
                            fuselage/positionings'
    num_pos = tixi_handle.getNamedChildrenCount(positionings_xpath,
                                                'positioning')
    for i in np.arange(num_pos):
        length_xpath = positionings_xpath + f'/positioning[{i+1}]/length'
        # get current values
        length = tixi_handle.getDoubleElement(length_xpath)
        # update current values
        tixi_handle.updateDoubleElement(length_xpath, length*scale, '%.8f')
    return tixi_handle


def cpacs_generate(aircraftname, tot_len, nose_frac=0.1, tail_frac=0.1):
    """Generates a new CPACS file with a fuselage defined in it

    Parameters
    ----------
    aircraftname : str
        The name of the aircraft and filename of the output CPACS file
    tot_len : float
        Total length of the fuselage 
    nose_frac : float, default = 0.1
        Fraction of the total length that comprises the nose section
    tail_frac : float, default = 0.1
        Fraction of the total length that comprises the tail section

    Outputs
    -------
    A CPACS file named aircraftname.xml
    """

    # Instantiate class and create handle for it
    tixi_handle = tixi.Tixi3()
    tixi.Tixi3.create(tixi_handle, rootElementName='cpacs')

    # Define schema and fill in header
    tixi_handle.declareNamespace("/cpacs", "http://www.w3.org/2001/XMLSchema-instance", "xsi");

    tixi_handle.registerNamespace("http://www.w3.org/2001/XMLSchema-instance", "xsi");

    tixi_handle.addTextAttribute("/cpacs", "xsi:noNamespaceSchemaLocation", "cpacs_schema.xsd");

    tixi_handle.addCpacsHeader(name=aircraftname, creator='Noah Sadaka', version='N/A', description='...', cpacsVersion='3.2');

    # Create XML elements down to sections
    path_elements = ['vehicles', 'aircraft', 'model', 'fuselages', 'fuselage', 'sections']
    base_path = '/cpacs'
    for i in path_elements:
        tixi_handle.createElement(base_path, i)
        if i == 'model':
            model_path = base_path + '/model'
            add_uid(tixi_handle, model_path, 'CPACSaircraft')
            tixi_handle.addTextElement(model_path, 'description', '...')
            tixi_handle.addTextElement(model_path, 'name', 'Generated Fuselage')
            ref_path = model_path + '/reference'
            tixi_handle.createElement(model_path, 'reference')
            tixi_handle.addDoubleElement(ref_path, 'area', 1, '%f')
            tixi_handle.addDoubleElement(ref_path, 'length', 1, '%f')
            tixi_handle.createElement(ref_path, 'point')
            add_uid(tixi_handle, ref_path+'/point', 'fuse_point1')
            tixi_handle.addDoubleElement(ref_path+'/point', 'x', 0.0, '%f')
            tixi_handle.addDoubleElement(ref_path+'/point', 'y', 0.0, '%f')
            tixi_handle.addDoubleElement(ref_path+'/point', 'z', 0.0, '%f')
        if i == 'fuselage':
            fuse_path = base_path + '/fuselage'
            add_uid(tixi_handle, fuse_path, 'Fuselage_1ID')
            tixi_handle.addTextElement(fuse_path, 'description', 'Generic Fuselage')
            tixi_handle.addTextElement(fuse_path, 'name', 'fuselage_1')
            tixi_handle.createElement(fuse_path, 'transformation')
            trans_path = fuse_path + '/transformation'
            add_uid(tixi_handle, trans_path, 'Fuselage_1ID_transformation1')
            for j in ['rotation', 'scaling', 'translation']:
                    tixi_handle.createElement(trans_path, j)
                    if j == 'translation':
                        tixi_handle.addTextAttribute(f"{trans_path}/{j}", 'refType', 'absLocal')
                    base_uid = 'Fuselage_1ID_transformation1'
                    add_uid(tixi_handle, f"{trans_path}/{j}",
                             f"{base_uid}_{j}1")
                    if j != 'scaling':
                        tixi_handle.addIntegerElement(f"{trans_path}/{j}",
                                                        'x', 0, '%d') 
                        tixi_handle.addIntegerElement(f"{trans_path}/{j}",
                                                        'y', 0, '%d')
                        tixi_handle.addIntegerElement(f"{trans_path}/{j}",
                                                        'z', 0, '%d')
                    else:
                        tixi_handle.addIntegerElement(f"{trans_path}/{j}",
                                                        'x', 1, '%d') 
                        tixi_handle.addIntegerElement(f"{trans_path}/{j}",
                                                        'y', 1, '%d')
                        tixi_handle.addIntegerElement(f"{trans_path}/{j}",
                                                        'z', 1, '%d')
        base_path += f"/{i}"

    # Check that CPACS file matches schema
    #tixi_handle.schemaValidateFromFile('cpacs_schema.xsd')
    close_tixi(tixi_handle, 'cpacs/test_fuse.xml')


def add_section(name, z-coord)


# ------------------------------
# MAIN
# ------------------------------
# for testing purposes, delete later
if os.path.exists('cpacs/test_cpacs.xml'):
    os.remove('cpacs/test_cpacs.xml')
os.system('cp cpacs/original/test_cpacs.xml cpacs/test_cpacs.xml')

#transformer(input_file='cpacs/original/test_cpacs.xml',
#            output_file='cpacs/test_cpacs.xml',
#            geometry_dict={'fuse_length': 30})
cpacs_generate(aircraftname='test_fuselage', tot_len=10, nose_frac=0.1, tail_frac=0.1)
