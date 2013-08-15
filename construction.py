import variables

# Home location
home = (variables.dim_x / 2.2, variables.dim_y / 2.2,0)

# Size of home, measured from the home location along the +x, +y, and +z axes
home_size = (40, 40, variables.epsilon)

# The exact center of the defined home square
home_center = tuple([h_coord + size_coord / 2 for h_coord, size_coord in 
      zip(home,home_size)])

# Location where construction is to begin
construction_location = (variables.dim_x / 2, variables.dim_y / 2,0)

# Measured in the same fashion as home_size
construction_size = (40,40,variables.epsilon)

# Exact center of defined construction square
construction_location_center = tuple([h_coord + size_coord / 2 for h_coord, size_coord in 
      zip(construction_location,construction_size)])

# Angle Contraint : When wiggling, if no beam is found within this
# angle from the vertical, than the beam is laid at vertical_angle_set (
# which is just an angle, so no direction is actually specified)
# All angles are in degrees.
beam = {
  # The lenght of the beam
  'length'                    : variables.beam_length,

  # The minumum angle from vertical at which a beam is allowed to be constructed when
  # intersecting with another
  'min_angle_constraint'      : 5,

  # The maximum angle from vertical at which a beam is allowed to intersect with another
  'max_angle_constraint'      : 60,

  # The default vertical direction
  'vertical_dir_set'          : (0,0,1),

  # The limit at a joint at which a beam is considered unsuitable for further travel
  'joint_limit'               : 3.39,

  # The limit along a beam which if exceeded indicated the beam should be reapired
  # This is always the limit (if the class does not inherit from SmartRepairer),
  # or the 'vertical_beam_limit' if the used robot class does inherit)
  'beam_limit'                : 0.55,

  # This limit is only used by classes which inherit from SmartRepairer.
  # It is the limit at which a horizontal beam would be considered in need of 
  # repair.
  'horizontal_beam_limit'     : 8.3,

  # Only used for classes which inherit from IntelligentRepairer
  # If the moment changes at a greater rate than moment_change_limit, then the
  # beam is considered to need repair. 
  'moment_change_limit'       : 0.2,

  # If a beam exceeds this limit at any point, it is considered to have failed.
  # The simulation halts immediately.
  # The structural elements are checked at every timestep
  'structure_check'           : variables.structure_check,

  # The angle from vertical at which a support beam is constructed
  'support_angle'             : 60,

  # The minimum angle at which a support beam is allowed to be constructed if 
  # it intersects with another beam in the structure
  'support_angle_min'         : 0,

  # The maximum angle (from vertical)
  'support_angle_max'         : 60,

  # This is only used for classes which inherit from LeanRepairer
  # This is the angle from the vertical at which a beam is initially constructed
  'construction_angle'        : 30,

  # This is how far a support beam construction from our current beam must
  # occur in order for the beam to be considered acceptable
  'support_angle_difference' : 10,

  # If a beam is within this angle from vertical, it is considered vertical for 
  # the purpose of determining the direction we wish to travel in
  'verticality_angle'        :  5,

  # If a direction is within this angle of the direction of the beam we want to
  # repair, then we consider it a preferred location.
  'direction_tolerance_angle':  30,

  # This is the maximum angle change that can occur due to the moment vector
  'moment_angle_max'         :  45,

  # If there is a joint within this distance of the tip, then the beam is 
  # considered to be support and no longer requires repair
  'joint_distance'           :  48, # inches

  # If there is a joint within this distance of where we want to build, then the
  # robot goes ahead and uses this nearby joint.
  'joint_error'              :  2 # inches
}
