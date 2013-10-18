import math

# Units for starting the program
program_units = "kip_in_F"

# Radius of "locality" (how far can a robot obtain information about 
# the structure from where it is located. In units specified by program_units
local_radius = 36 # 3 ft

# The size of a step that the robot can take. This is expressed in the specified
# program units.
step_length = 10 # .5 ft

# This dictactes what is considered a significant length in the visualization
# We only record events that occur at a length higher than this
visualization = { 'step'        : 1, #in
                  'scaling'     : 1, # in
                  'robot_size'  : 18  } # ft

# This turns on and off recordning the deflection
deflection = True

# This is a switch as to whether the robot can read moments along a beam (True)
# or not (False)
read_beam = True

# Length of each beam (in the units specified by program_units)
beam_length = 120 # 10ft

# This dictates the maximum randomness when setting a new beam
random = beam_length / 25
random_percentage = 0.33

# The number of beams that each robot carries (ie, how many elements can
# construct before travelling off the structure)
beam_capacity = 1

# The size of the division of space into blocks. 
# x,y,z gives the number of blocks along the x axix, the y axis, and the z axis
# dim_var gives the limit of the structure on the axis indicated by var. 
# Keep in mind that the origin is the bottom-left part of this structure
origin = (0,0,0)
num_x = 10
num_y = 10
num_z = 100
dim_x = 1700 # 100 ft
dim_y = 1700
dim_z = 170000

# This defines how sensitive the program is to accepting errors within the beam 
# structure
epsilon = 0.0001

# If true, then we record data when moving down the structure. This slows down
# the simulation significantly.
collect_data = True

# This defines the mass of each robot in the units specified by program_units
robot_load = 0.035 # kip

# Name of the load case for the robots
robot_load_case = "DEAD"
wind_case = "Wind"
wind_combo = "D+W"

######################################################
# Name of the material property defined for the beams
frame_property_name = "Scaffold Tube"
material_property  = "A500GrB42"
outside_diameter = 3.0 # inches(1.9)
wall_thickness = 0.188 # inches (0.144)
steel_density = 490

material_type = "MATERIAL_STEEL"
material_subtype = "MATERIAL_STEEL_SUBTYPE_ASTM_A500GrB_Fy42"

steel_yield = 42 #ksi
density = steel_density / (12**3) # pci
cross_sect_area = math.pi * ((outside_diameter / 2)**2 - (outside_diameter / 2 -
  wall_thickness)**2) # in*in
moment_of_intertia = math.pi * ((outside_diameter/2)**4 - (outside_diameter / 2 -
  wall_thickness)**4) / 4
beam_load = cross_sect_area * beam_length * density / 1000 # kip
#####################################################

# Calculating limits
joint_limit = beam_length * beam_load / 2
structure_check = steel_yield * moment_of_intertia / (outside_diameter / 2)
beam_limit = joint_limit + (beam_load + robot_load)*beam_length

# The number of timesteps before an analysis model is saved.
analysis_timesteps = 200
########################################################

# Wind pattern settings
'''
THESE SETTINGS ARE NOW TAKEN CARE OF MANUALLY THROUGH A TEMPLATE LOCATED In
C:\SAP 2000\ template.sbd

exposureFrom indicated the source of the wind exposure
1 = From extents of rigid diaphragms
2 = From area objects
3 = From frame objeccs (open structure)
4 = From area objects and frame objects (open structure)
'''
exposureFrom = 3

'''
dirAngle is the direction angle of the wind load. This
only applies when exposureFrom is 1
'''
dirAngle = 0

# Windward coefficient (exposureFrom must be 1)
cpw = 1

# Leeward coefficient (exposureFrom must be 1)
cpl = 1

# Indicated the desired case from ASCE7-05 (exposureFrom must be 1)
asceCase = 1
ascee1 = 1
ascee2 = 1

'''
This item is True if the top and bottom elevations of the wind load are user 
specified. It is False if the elevations are determined by the program.

topZ and bottomZ only appy when userZ is set to True
'''
userZ = False
topZ = 1
bottomZ = 1

# The wind speed in mph
windSpeed = 90

'''
exposureType indicating the exposure Category
1 = B
2 = C
3 = D
'''
exposureType = 2

importanceFactor = 1

# The topological factor
kzt = 1

gustFactor = .85

# The directionality factor
kd = .85

'''
solidGrossRatio is the solid area divided by gross area ratio for open frame
structure loading.

This only applies when exposureFrom is 3 or 4
'''
solidGrossRatio = .2

userExposure = False

######################################################
