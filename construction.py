import variables

# Home location
home = (0,0,0)
home_size = (variables.dim_x / 10, variables.dim_y / 10, 0)

# Location where construction is to begin
construction_location = (variables.dim_x / 2, variables.dim_y / 2, 0)
construction_size = (24,24,0)

# Angle Contraint : When wiggling, if no beam is found within this
# angle from the vertical, than the beam is laid at vertical_angle_set (
# which is just an angle, so no direction is actually specified)
# All angles are in degrees.
beam = {
  'length'            : variables.beam_length,
  'angle_constraint'  : 45,
  'vertical_dir_set'  : (0,0,1)
}
