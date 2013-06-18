# Units for starting the program
program_units = "kN_m_C"

# Radius of "locality" (how far can a robot obtain information about 
# the structure from where it is located. In units specified by program_units
local_radius = 1

# The size of a step that the robot can take. This is expressed in the specified
# program units.
step_length = 0.5

# Length of each beam (in the units specified by program_units)
beam_length = 1

# The number of beams that each robot carries (ie, how many elements can
# construct before travelling off the structure)
beam_capacity = 1

# The size of the division of space into blocks. 
# x,y,z gives the number of blocks at along the x axix, the y axis, and the z axis
# dim_var gives the limit of the structure on the axis indicated by var. 
# Keep in mind that the origin is the bottom-left part of this structure
num_x = 10
num_y = 10
num_z = 10
dim_x = 50
dim_y = 50
dun_z = 50

# This defines how sensitive the program is to accepting errors within the beam structure
epsilon = 0.01