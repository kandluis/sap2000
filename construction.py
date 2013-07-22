import variables

# Home location
home = (variables.dim_x / 2.2, variables.dim_y / 2.2,0)
home_size = (36, 36, variables.epsilon)

# Location where construction is to begin
construction_location = (variables.dim_x / 2, variables.dim_y / 2,0)
construction_size = (36,36,variables.epsilon)

# Angle Contraint : When wiggling, if no beam is found within this
# angle from the vertical, than the beam is laid at vertical_angle_set (
# which is just an angle, so no direction is actually specified)
# All angles are in degrees.
beam = {
  'length'                : variables.beam_length,
  'angle_constraint'      : 45,
  'vertical_dir_set'      : (0,0,1),
  'joint_limit'           : variables.joint_limit,
  'beam_limit'            : 0.1,
  'horizontal_beam_limit' : variables.joint_limit,
  'structure_check'       : variables.structure_check,
  'support_angle'         : 60,
  'support_angle_min'     : 30,
  'support_angle_max'     : 80,

  # This is the angle from the vertical at which a beam is initially constructed
  'construction_angle'    : 30
}
