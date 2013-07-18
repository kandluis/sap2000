import math

# Units for starting the program
program_units = "kip_in_F"

# Radius of "locality" (how far can a robot obtain information about 
# the structure from where it is located. In units specified by program_units
local_radius = 12 # 1 ft

# The size of a step that the robot can take. This is expressed in the specified
# program units.
step_length = 12 # .5 ft

# Length of each beam (in the units specified by program_units)
beam_length = 120 # 10ft

# This dictates the maximum randomness when setting a new beam
random = beam_length / 20

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

# This defines the mass of each robot in the units specified by program_units
robot_load = 0.035 # kip

# This defines the load of each beam carried by the robots
beam_load = 0.027 # kip

# Name of the load case for the robots
robot_load_case = "DEAD"

# Name of the material property defined for the beams
frame_property_name = "Scaffold Tube"
material_property  = "A500GrB42"
outside_diameter = 1.9 # inches
wall_thickness = 0.145 # inches

material_type = "MATERIAL_STEEL"
material_subtype = "MATERIAL_STEEL_SUBTYPE_ASTM_A500GrB_Fy42"

steel_yield = 42 #ksi
density_ = 0.28 # pci
cross_sect_area = math.pi * ((outside_diameter / 2)**2 - (outside_diameter / 2 -
  wall_thickness)**2) # in*in
moment_of_intertia = math.pi * ((outside_diameter/2)**4 - (outside_diameter / 2 -
  wall_thickness)**4) / 4

# Calculating limits
joint_limit = beam_length * beam_load / 2
structure_check = steel_yield * moment_of_intertia / (outside_diameter / 2)
beam_limit = joint_limit + (beam_load + robot_load)*beam_length

# The number of timesteps before an analysis model is saved.
analysis_timesteps = 100
