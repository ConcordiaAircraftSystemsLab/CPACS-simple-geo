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
    tixi_handle.declareNamespace("/cpacs", "http://www.w3.org/2001/XMLSchema-instance", "xsi")

    tixi_handle.registerNamespace("http://www.w3.org/2001/XMLSchema-instance", "xsi")

    tixi_handle.addTextAttribute("/cpacs", "xsi:noNamespaceSchemaLocation", "cpacs_schema.xsd")

    tixi_handle.addCpacsHeader(name=aircraftname, creator='Noah Sadaka', version='N/A', description='...', cpacsVersion='3.2')

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

    # Add segments and positionings tag
    tixi_handle.createElement('/cpacs/vehicles/aircraft/model/fuselages/fuselage', 'segments')
    tixi_handle.createElement('/cpacs/vehicles/aircraft/model/fuselages/fuselage', 'positionings')

        
    tixi_handle = build_fuselage(tixi_handle, tot_len, nose_frac, tail_frac, 'Fuselage')

    # Check that CPACS file matches schema
    tixi_handle.schemaValidateFromFile('cpacs_schema.xsd')
    close_tixi(tixi_handle, 'cpacs/test_fuse.xml')


def build_fuselage(tixi_handle, tot_len, nose_frac, tail_frac, name):
    """ Internal function, generate fuselage geometry

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be created
    tot_len : float
        Total length of the fuselage 
    nose_frac : float, default = 0.1
        Fraction of the total length that comprises the nose section
    tail_frac : float, default = 0.1
        Fraction of the total length that comprises the tail section
    name : str
        section name, used to generate a UID

    Returns
    -------
    tixi_handle : tixi handle object
    """

    profile_id, tixi_handle = add_circular_fuse_profile(tixi_handle)
    
    previous_section = ''
    nose_len = nose_frac * tot_len
    tail_len = tail_frac * tot_len
    main_len = tot_len - nose_len - tail_len
    pos_len_vec = [0, nose_len, main_len, tail_len]
    for i in range(1, 5):
        section_uid, tixi_handle = add_section(tixi_handle, name, profile_id, i)  
        if i > 1:
            tixi_handle = add_segment(tixi_handle, name, previous_section, section_uid, i-1)
        if i == 1:
            tixi_handle = add_positioning(tixi_handle, name, pos_len_vec[i-1], section_uid, '', i)
        else:
            tixi_handle = add_positioning(tixi_handle, name, pos_len_vec[i-1], section_uid, previous_section, i)
        previous_section = section_uid

    return tixi_handle


def add_positioning(tixi_handle, name, length, to_section_uid, from_section_uid, pos_num):
    """ Internal function, add positionings to CPACS file

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be created
    name : str
        section name, used to generate a UID
    length : float
        length of segment
    to_section_uid : str
        uid of section at end of segment
    from_section_uid : str
        uid of section at start of section
    pos_num : int
        number corresponding to positioning index

    Returns
    -------
    tixi_handle : tixi handle object
    """

    base_path = '/cpacs/vehicles/aircraft/model/fuselages/fuselage/positionings'
    tixi_handle.createElement(base_path, 'positioning')
    base_path += f"/positioning[{pos_num}]"
    add_uid(tixi_handle, base_path, f"{name}_positioning{pos_num}ID")
    tixi_handle.addTextElement(base_path, 'name', f"{name}_positioning{pos_num}")
    tixi_handle.addDoubleElement(base_path, 'dihedralAngle', 0, '%g')
    tixi_handle.addDoubleElement(base_path, 'sweepAngle', 90, '%g')
    tixi_handle.addTextElement(base_path, 'toSectionUID', to_section_uid)
    tixi_handle.addDoubleElement(base_path, 'length', length, '%g')
    if from_section_uid:
        tixi_handle.addTextElement(base_path, 'fromSectionUID', from_section_uid)
    return tixi_handle


def add_segment(tixi_handle, name, fromUID, toUID, num):
    """ Internal function, add segments to CPACS file

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be created
    name : str
        section name, used to generate a UID
    from_UID : str
        uid of section at start of section
    to_UID : str
        uid of section at end of segment
    num : int
        number corresponding to segment index

    Returns
    -------
    tixi_handle : tixi handle object
    """
    base_path = '/cpacs/vehicles/aircraft/model/fuselages/fuselage/segments'
    tixi_handle.createElement(base_path, 'segment')
    base_path += f"/segment[{num}]"
    segment_name = f"{name}_segment{num}"
    add_uid(tixi_handle, base_path, segment_name+'ID')
    tixi_handle.addTextElement(base_path, 'name', segment_name)
    tixi_handle.addTextElement(base_path, 'fromElementUID', fromUID)
    tixi_handle.addTextElement(base_path, 'toElementUID', toUID)
    return tixi_handle


def add_section(tixi_handle, name, profile_id, section_num):
    """ Internal function, add section to CPACS file

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be created
    name : str
        section name, used to generate a UID
    profile_id : str
        profile ID used for this section
    section_num : int
        number corresponding to which section this is

    Returns
    -------
    tixi_handle : tixi handle object
    section_uid : str
        section UID
    """

    # Create XML infrastructure
    base_path = '/cpacs/vehicles/aircraft/model/fuselages/fuselage/sections'
    tixi_handle.createElement(base_path, 'section')
    base_path += f'/section[{section_num}]'
    section_uid = f"{name}_section{section_num}ID"
    add_uid(tixi_handle, base_path, section_uid)
    tixi_handle.addTextElement(base_path, 'name', name)
    for j in ['transformation', 'elements']:
        tixi_handle.createElement(base_path, j)
        xpath = f"{base_path}/{j}"
        uid_name = f"{name}section{section_num}ID_{j}1"
        if j == 'elements':
            tixi_handle.createElement(xpath, 'element')
            xpath += '/element'
            uid_name = f"{name}section{section_num}ID_element1ID" 
            add_uid(tixi_handle, xpath, uid_name)
            tixi_handle.addTextElement(xpath, 'name', f"{name}section{section_num}element1")
            tixi_handle.addTextElement(xpath, 'profileUID', profile_id)
            tixi_handle.createElement(xpath, 'transformation')
            xpath += '/transformation'
            uid_name = f"{uid_name}_transformation1"
        add_uid(tixi_handle, xpath, uid_name)
        for i in ['rotation', 'scaling', 'translation']:
            tixi_handle.createElement(xpath, i)
            if i == 'translation':
                tixi_handle.addTextAttribute(f"{xpath}/{i}", 'refType', 'absLocal')
            add_uid(tixi_handle, f"{xpath}/{i}", f"{uid_name}_{i}1")
            if i != 'scaling':
                tixi_handle.addIntegerElement(f"{xpath}/{i}", 'x', 0, '%d') 
                tixi_handle.addIntegerElement(f"{xpath}/{i}", 'y', 0, '%d')
                tixi_handle.addIntegerElement(f"{xpath}/{i}", 'z', 0, '%d')
            else:
                tixi_handle.addIntegerElement(f"{xpath}/{i}", 'x', 1, '%d') 
                tixi_handle.addIntegerElement(f"{xpath}/{i}", 'y', 1, '%d')
                tixi_handle.addIntegerElement(f"{xpath}/{i}", 'z', 1, '%d')

    return section_uid, tixi_handle


def add_circular_fuse_profile(tixi_handle):
    """Adds a circular profile to the CPACS file

    Parameters
    ----------
    tixi_handle : tixi handle object
        A tixi handle to the cpacs file to be created

    Returns
    -------
    tixi_handle : tixi handle object
    profile_id : str
        uID of the profile,
    """

    base_path = '/cpacs/vehicles'
    tixi_handle.createElement(base_path, 'profiles')
    base_path += '/profiles'
    tixi_handle.createElement(base_path, 'fuselageProfiles')
    base_path+= '/fuselageProfiles'
    tixi_handle.createElement(base_path, 'fuselageProfile')
    base_path+= '/fuselageProfile'
    profile_id = 'fuselageCircleProfileID'
    add_uid(tixi_handle, base_path, profile_id)
    tixi_handle.addTextElement(base_path, 'name', 'Circle')
    tixi_handle.addTextElement(base_path, 'description', 'Profile build up from set of points on circle where dimensions are 1 ... -1')
    tixi_handle.createElement(base_path, 'pointList')
    base_path += '/pointList'
    
    # Add points
    x_vec = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    y_vec = [0.0,0.0774924206719,0.154518792808,0.230615870742,0.305325997695,0.378199858172,0.4487991802,0.516699371152,0.581492071288,0.642787609687,0.700217347767,0.753435896328,0.802123192755,0.84598642592,0.884761797177,0.91821610688,0.946148156876,0.968389960528,0.984807753012,0.995302795793,0.999811970449,0.998308158271,0.990800403365,0.977333858251,0.957989512315,0.932883704732,0.902167424781,0.866025403784,0.824675004109,0.778364911924,0.727373641573,0.672007860556,0.612600545193,0.549508978071,0.483112599297,0.413810724505,0.342020143326,0.268172612761,0.192712260548,0.116092914125,0.0387753712568,-0.0387753712568,-0.116092914125,-0.192712260548,-0.268172612761,-0.342020143326,-0.413810724505,-0.483112599297,-0.549508978071,-0.612600545193,-0.672007860556,-0.727373641573,-0.778364911924,-0.824675004109,-0.866025403784,-0.902167424781,-0.932883704732,-0.957989512315,-0.977333858251,-0.990800403365,-0.998308158271,-0.999811970449,-0.995302795793,-0.984807753012,-0.968389960528,-0.946148156876,-0.91821610688,-0.884761797177,-0.84598642592,-0.802123192755,-0.753435896328,-0.700217347767,-0.642787609687,-0.581492071288,-0.516699371152,-0.4487991802,-0.378199858172,-0.305325997695,-0.230615870742,-0.154518792808,-0.0774924206719,0.0]
    z_vec = [1.0,0.996992941168,0.987989849477,0.97304487058,0.952247885338,0.925723969269,0.893632640323,0.85616689953,0.813552070263,0.766044443119,0.713929734558,0.657521368569,0.597158591703,0.533204432802,0.466043519703,0.396079766039,0.323733942058,0.249441144058,0.173648177667,0.0968108707032,0.0193913317718,-0.0581448289105,-0.13533129975,-0.211703872229,-0.286803232711,-0.360177724805,-0.431386065681,-0.5,-0.565606875487,-0.627812124672,-0.686241637869,-0.740544013109,-0.790392669519,-0.835487811413,-0.875558231302,-0.910362940966,-0.939692620786,-0.963370878616,-0.981255310627,-0.993238357742,-0.999247952504,-0.999247952504,-0.993238357742,-0.981255310627,-0.963370878616,-0.939692620786,-0.910362940966,-0.875558231302,-0.835487811413,-0.790392669519,-0.740544013109,-0.686241637869,-0.627812124672,-0.565606875487,-0.5,-0.431386065681,-0.360177724805,-0.286803232711,-0.211703872229,-0.13533129975,-0.0581448289105,0.0193913317718,0.0968108707032,0.173648177667,0.249441144058,0.323733942058,0.396079766039,0.466043519703,0.533204432802,0.597158591703,0.657521368569,0.713929734558,0.766044443119,0.813552070263,0.85616689953,0.893632640323,0.925723969269,0.952247885338,0.97304487058,0.987989849477,0.996992941168,1.0]
    tixi_handle.addFloatVector(base_path, 'x', x_vec, len(x_vec), '%g')
    tixi_handle.addFloatVector(base_path, 'y', y_vec, len(y_vec), '%g')
    tixi_handle.addFloatVector(base_path, 'z', z_vec, len(z_vec), '%g')



    return profile_id, tixi_handle





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
