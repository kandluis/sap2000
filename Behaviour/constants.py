
# constants used to calculate behaviour parameters
from variables import BEAM, ROBOT, MATERIAL, PROGRAM

joint_limit = BEAM['length'] * MATERIAL['beam_load'] / 2
beam_limit = joint_limit + (MATERIAL['beam_load'] + ROBOT['load'])*BEAM['length']

# All angles are in degrees.
beam = {
  # The lenght of the beam
  'length'                    : BEAM['length'],

  # Angle base beams make relative to ground
  'ground_angle'              : 45,

  # Angle non-base beams make relative to each other
  'beam_angle'                : 90,

  # Maximum # of beams within radius from endpoint of beam you want to add
  'max_beam_density'          : 5,

  # Radius for sphere within which # of beam endpoints are counted
  'density_radius'            : BEAM['length']/2,

  # If there is a joint within this distance of the robot, then
  # it is too close to place another beam down.
  'joint_distance'           :  24, # inches

  # The limit at a joint at which a beam is considered unsuitable for further travel
  'joint_limit'               : joint_limit,

  # If a beam exceeds this limit at any point, it is considered to have failed.
  # The simulation halts immediately.
  # The structural elements are checked at every timestep
  'structure_check'           : PROGRAM['structure_check'],

  # True means tripod is dropped at construction site at start.
  'tripod'                    : True,

}

prob = {
  # P(placing beam while still climbing, and not at top yet)
  'random_beam'               : 0.05,

  # P(placing beam while still climbing ONLY if on tripod base beam)
  'tripod'                    : 0.3,

  # P(adding beam to ground if no nearby beam is detected in robot local radius)
  'add_base'                  : 0.1,

  # P(climbing steepest path at given timestep while climbing up)
  'steep_climb'               : 0.5,

  # probability used in exponential build out/up function when density is too high
  'build_out'                 : 0.5,

}

robot = {
  
  # number of steps to wander away from construction site center
  'wander'                    : 20,

}


# Angle Contraint : When wiggling, if no beam is found within this
# angle from the vertical, than the beam is laid at vertical_angle_set (
# which is just an angle, so no direction is actually specified)
# All angles are in degrees.
beam_unused = {
  # The lenght of the beam
  'length'                    : BEAM['length'],

  # Angle base beams make relative to ground
  'ground_angle'              : 90,

  # Angle non-base beams make relative to each other
  'beam_angle'                : 45,

  # Maximum # of beams within beam distance from endpoint of another beam
  'max_beam_density'          : 5,

  # The minumum angle from vertical at which a beam is allowed to be constructed when
  # intersecting with another
  'min_angle_constraint'      : 5,

  # The maximum angle from vertical at which a beam is allowed to intersect with another
  'max_angle_constraint'      : 60,

  # The default vertical direction
  'vertical_dir_set'          : (0,0,1),

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
  'joint_distance'           :  36, # inches

  # If there is a joint within this distance of where we want to build, then the
  # robot goes ahead and uses this nearby joint.
  'joint_error'              :  2 # inches
}
