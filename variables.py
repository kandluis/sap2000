# Units for starting the program
program_units = "kip_in_F"

# Radius of "locality" (how far can a robot obtain information about 
# the structure from where it is located. In units specified by program_units
local_radius = 12 # 1 ft

# The size of a step that the robot can take. This is expressed in the specified
# program units.
step_length = 12 # 1 ft

# Length of each beam (in the units specified by program_units)
beam_length = 120 # 10ft

# The number of beams that each robot carries (ie, how many elements can
# construct before travelling off the structure)
beam_capacity = 10

# The size of the division of space into blocks. 
# x,y,z gives the number of blocks along the x axix, the y axis, and the z axis
# dim_var gives the limit of the structure on the axis indicated by var. 
# Keep in mind that the origin is the bottom-left part of this structure
origin = (0,0,0)
num_x = 100
num_y = 100
num_z = 100
dim_x = 1200 # 100 ft
dim_y = 1200
dim_z = 1200

# This defines how sensitive the program is to accepting errors within the beam 
# structure
epsilon = 0.0001

# This defines the mass of each robot in the units specified by program_units
robot_load = 0.025 # This is around 35 pounds in kip.

# This defines the load of each beam carried by the robots
beam_load = 0.010 # This is around twelve pounds in kN

# Name of the load case for the robots
robot_load_case = "ROBOTS"

# Name of the material property defined for the beams
frame_property_name = "Scaffold Tube"
material_property  = "A500GrB42"
outside_diameter = 1.9 # inches
wall_thickness = 0.145 # inches

material_type = "MATERIAL_STEEL"
material_subtype = "MATERIAL_STEEL_SUBTYPE_ASTM_A500GrB_Fy42"

# The number of timesteps before an analysis model is saved.
analysis_timesteps = 20
