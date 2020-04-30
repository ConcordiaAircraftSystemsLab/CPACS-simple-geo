# CPACS Simplified Geometry Transformer

Resize the aircraft geometry using simple geometrical parameters (fuselage length, wing span, wing area, etc...). Input a [CPACS file](https://www.cpacs.de/) and use the simple geometrical parameter to resize it while all aircraft sections keep their relative sizes.

## Installation

Has the same requirements as [CEASIOMpy](https://ceasiompy.readthedocs.io/en/latest/), so if it is already installed on your machine, this tool will work.

TODO: add a requirements.txt or environment.yml file for easy installation

## Usage

TODO: add documentation once the tool has been created

## Developer's Guide
This section is to aid those developing this tool in the future.

For documentation about what each CPACS tag means and what kind of data it accepts, see the [CPACS documentation](https://cpacs.de/pages/documentation.html). It is also useful to open a CPACS file next to you and examine each tag. Notepad++ supports tag folding for XML files, which is a recommended text editor to open CPACS files in to rapidly find a tag.

Extremely useful libraries are [TIXI](http://tixi.sourceforge.net/Doc/index.html) and [TIGL](https://dlr-sc.github.io/tigl/doc/latest/index.html) for CPACS file manipulation. Documentation about each function can be found in the "Modules" section for each respective page. TIXI contains functions for reading and writing to XML files, while TIGL contains functions for reading from CPACS files and doing CPACS-specific calculations. Also, CEASIOMpy has created some very useful tixi and tigl wrappers and functions for the CPACSfiles, so some of these have been used for this tool. 

A few notes about using TIXI and TIGL in Python. These tools are written in C++ originally, so the usage in python is not the same as shown in the documentation. To begin, we load a CPACS file using open_tixi from CEASIOMpy/utils/cpacsfunctions.py. This creates a tixi handle object, to which you can apply functions from the tixi package. Note that for tigl, you would similarly use the open_tigl function from CEASIOMpy. Say we want to use a function, tixiUpdateDoubleElement to update a number in a CPACS file. The documentation says that the correct usage would be to call tixiUpdateDoubleElement(handle, other parameters). For Python usage, you would actually call tixi_handle.updateDoubleElement(other parameters). Note that the "tixi" at the beginning of the function has been removed, the function is applied to the tixi_handle, and the capital U in update has been made miniscule. Other than these small differences, the usage is the same.
