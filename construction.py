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
  'length'                    : variables.beam_length,
  'min_angle_constraint'      : 5,
  'angle_constraint'          : 45,
  'max_angle_constraint'      : 80,
  'vertical_dir_set'          : (0,0,1),
  'joint_limit'               : variables.joint_limit,
  'beam_limit'                : 1.6,
  'horizontal_beam_limit'     : 4,
  'structure_check'           : variables.structure_check,
  'support_angle'             : 60,
  'support_angle_min'         : 30,
  'support_angle_max'         : 85,

  # This is the angle from the vertical at which a beam is initially constructed
  'construction_angle'        : 30,

  # This is the angle between the beam we want to repair and the beam we are
  # currently on.
  # If the actual angle is greater, then we add a support beam
  # If it is less, then we repair directly
  'direct_repair_limit'      : 90,

  # This is how far a support beam construction from our current beam must
  # occur in order for the beam to be considered acceptable
  'support_angle_difference' : 10,

  # If a beam is within this angle from vertical, it is considered vertical for 
  # the purpose of determining the direction we wish to travel in
  'verticality_angle'        :  5
}
