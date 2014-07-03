
# constants used to calculate behaviour parameters
from variables import BEAM,ROBOT,MATERIAL, PROGRAM

joint_limit = BEAM['length'] * MATERIAL['beam_load'] / 2
beam_limit = joint_limit + (MATERIAL['beam_load'] + ROBOT['load'])*BEAM['length']


# Angle Contraint : When wiggling, if no beam is found within this
# angle from the vertical, than the beam is laid at vertical_angle_set (
# which is just an angle, so no direction is actually specified)
# All angles are in degrees.
beam = {
  # The lenght of the beam
  'length'                    : BEAM['length'],

  # The minumum angle from vertical at which a beam is allowed to be constructed when
  # intersecting with another
  'min_angle_constraint'      : 5,

  # The maximum angle from vertical at which a beam is allowed to intersect with another
  'max_angle_constraint'      : 60,

  # The default vertical direction
  'vertical_dir_set'          : (0,0,1),

  # Angle base beams make relative to ground
  'ground_angle'              : 60,

  # The limit at a joint at which a beam is considered unsuitable for further travel
  'joint_limit'               : joint_limit,

  # The limit along a beam which if exceeded indicated the beam should be reapired
  # This is always the limit (if the class does not inherit from SmartRepairer),
  # or the 'vertical_beam_limit' if the used robot class does inherit)
  'beam_limit'                : 0.55, #should be beam_limit above, but modified

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
  'structure_check'           : PROGRAM['structure_check'],

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

  # This is the angle between the beam we want to repair and the beam we are
  # currently on.
  # If the actual angle is greater, then we add a support beam
  # If it is less, then we repair directly
  'direct_repair_limit'      : 90,

  # This is how far a support beam construction from our current beam must
  # occur in order for the beam to be considered acceptable
  'support_angle_difference' : 10,

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
