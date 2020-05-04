# Here are examples of how to use the CPACS fuselage creation function and
#   fuselage rescaling length function

# Import the functions
from simplifiedgeometry import transformer, cpacs_generate


# ----------------------
# Fuselage resizing tool
# ----------------------

# Define path to CPACS file you want to change
# Note that this path will need to be changed for it to work for you
cpacs_in = 'cpacs/original/test_cpacs.xml'
# define what you want the output file to be named
cpacs_out = 'cpacs/test_cpacs.xml'
# set the fuselage length in the output file
fuse_length_out = 30

# Run the resizing function
transformer(cpacs_in, cpacs_out, geometry_dict={'fuse_length': fuse_length_out})

# done!


# -------------------------------
# Fuselage and CPACS file creator
# -------------------------------

# name of the outputfile. Placed in '/cpacs', so full path will be
# /cpacs/aircraftname
aircraftname = 'cpacs_generate_test'
# total length of the fuselage
tot_len = 20
# Optionally, define what fraction of the fuselage length
# is made up by the nose and tail sections
# by default, these are both set to 0.1
nose_frac = 0.2
tail_frac = 0.05
# generate the fuselage
cpacs_generate(aircraftname, tot_len, nose_frac, tail_frac)

# done!
