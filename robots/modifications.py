from helpers import helpers
from robots.repairer import Repairer
import construction, math, pdb,variables, random


class NormalRepairer(Repairer):
  '''
  This contains small test modifications for the robot. Things to make the code 
  work as we want it to. Not bug fixes, but just accounting for unexpected edge
  cases
  '''
  def __init__(self,name,structure,location,program):
    super(NormalRepairer,self).__init__(name,structure,location,program)

    self.read_moment = 0

  def current_state(self):
    state = super(NormalRepairer,self).current_state()
    state['read_moment'] = self.read_moment

    return state

  # Small modification to how we determine joints
  def at_joint(self):
    '''
    Updating to return true when we are on a beam AND on the ground. We want to
    consider this a joint so that the robot treats it as one and checks that 
    limit instead of another.
    '''
    return ((self.beam is not None and helpers.compare(self.location[2],0)) or 
      super(NormalRepairer,self).at_joint())

  # Small modification to record the moment that the robot reads at each beam
  def get_moment(self,name):
    # Get the moment as normal
    moment = super(NormalRepairer,self).get_moment(name)

    # Store it to read out every timestep
    self.read_moment = moment

    # Return the moment
    return moment

class RandomUpwardRepairer(NormalRepairer):
  '''
  Climbs upward beams randomly instead of following the least vertical
  '''
  def __init__(self,name,structure,location,program):
    super(RandomUpwardRepairer,self).__init__(name,structure,location,program)

  def pick_direction(self,directions):
    '''
    Overwritting to pick upwards direction randomly
    '''
    # Pick the smalles pos_z when down (modification)
    if not self.memory['pos_z']: 
      return super(RandomUpwardRepairer,self).pick_direction(directions)
    
    else:
      direction = self.random_direction(directions)
      
      # Store direction
      self.memory['previous_direction'] = direction
      
      return direction

class DeflectionRepairer(NormalRepairer):
  '''
  Attemps to build vertical beams such that they counter balance each Otherwise
  '''
  def __init__(self,name,structure,location,program):
    super(DeflectionRepairer,self).__init__(name,structure,location,program)
    
  def get_disturbance(self):
    '''
    Returns the disturbance level for adding a new beam at the tip. This is
    modified so that the disturbance compensates for the angle at which the
    current beam lies (using basic math)
    '''
    def compensate_change(coord,change = variables.epsilon):
      '''
      Returns a random direction that is the right sign so that it compensates 
      for the sign of change
      '''
      if helpers.compare(coord,0):
        return random.uniform(-1 * change,change)
      elif coord < 0:
        return random.uniform(0,change)
      else:
        return random.uniform(-1 * change, 0)

    # We are currently on a beam
    if self.beam is not None:
      i,j = self.beam.endpoints
      v = helpers.make_vector(i,j)
      const_change = lambda x : compensate_change(x,variables.random)
      delta_x, delta_y = const_change(v[0]), const_change(v[1])
      return (delta_x,delta_y,0)
    else:
      return super(DeflectionRepairer,self).get_disturbance()

class SmartRepairer(NormalRepairer):
  '''
  Repairs beams based on a sliding scale repair for beam limits.
  '''
  def __init__(self,name,structure,location,program):
    super(SmartRepairer,self).__init__(name,structure,location,program)

  def beam_check(self,name):
    '''
    Checks a beam to see whether it is in a state that requires repair
    '''
    moment = self.get_moment(name)
    e1,e2 = self.structure.get_endpoints(name,self.location)
    xy_dist = helpers.distance((e1[0],e1[1],0),(e2[0],e2[1],0))
    limit = construction.beam['beam_limit'] + (
      xy_dist / construction.beam['length']) * construction.beam['horizontal_beam_limit']

    return (moment < limit or helpers.compare(moment,limit))

class LeanRepairer(NormalRepairer):
  '''
  Instead of building directly up, this class builds at a specified angle
  from the ground. There are no perfectly vertical tubes, nor even those that
  are almost vertical
  '''
  def __init__(self,name,structure,location,program):
    super(LeanRepairer,self).__init__(name,structure,location,program)

  def get_default(self,ratio_coord,vertical_coord):
    '''
    Returns the coordinate onto which the j-point of the beam to construct 
    should lie
    '''
    # No vertical coordinate this time, since we will use a leaning one
    coord = super(LeanRepairer,self).get_default(ratio_coord,None)
    if coord is not None:
      return coord
    # We need to return one that leans
    else:
      xy_dir = self.non_zero_xydirection()
      scale = 1 / helpers.ratio(construction.beam['construction_angle'])
      vertical = helpers.scale(scale,construction.beam['vertical_dir_set'])
      direction = helpers.make_unit(helpers.sum_vectors(xy_dir,vertical))
      endpoint = helpers.sum_vectors(self.location,helpers.scale(
        construction.beam['length'],direction))

      return endpoint

class OverRepairer(NormalRepairer):
  '''
  Instead of climbing up whatever way it can, this robot goes into repair mode
  as soon as it finds a beam which needs repair. It does this even if there are
  other directions along which it can travel
  '''
  def __init__(self,name,structure,location,program):
    super(OverRepairer,self).__init__(name,structure,location,program)

  def filter_feasable(self,dirs):
    '''
    Overwritting to return the empty set if there are broken beams in memory
    '''
    # Call first, as normal, adding broken to memory
    result = super(NormalRepairer,self).filter_feasable(dirs)

    # Check memory state
    if len(self.memory['broken']) == 0:
      return result
    else:
      return {}

class SmartLeanRepairer(SmartRepairer,LeanRepairer):
  '''
  Combines the sliding ability of smart repairer with deflected construction
  '''
  def __init__(self,name,structure,location,program):
    super(SmartLeanRepairer,self).__init__(name,structure,location,program)

class SmartestRepairer(SmartRepairer,OverRepairer,RandomUpwardRepairer):
  '''
  Combines the sliding scale, the over-repairing nature, and the random movement
  upward into one robot
  '''
  def __init__(self,name,structure,location,program):
    super(SmartestRepairer,self).__init__(name,structure,location,program)

class IntelligentRepairer(NormalRepairer):
  '''
  Add the ability to remember moments (up to one). Uses this information to 
  analyze how quickly the moments are changing on the beam.
  '''
  def __init__(self,name,structure,location,program):
    super(IntelligentRepairer,self).__init__(name,structure,location,program)

    # Keeps track of the previous moment measure
    self.memory['previous_moment'] = None

    # A boolean that tells use whether or not we need to add additional steps to
    # our repair operation
    self.special_repair = True

  def get_moment(self,beam):
    '''
    Stores the previous moment of our current beam in memory
    '''
    moment = super(IntelligentRepairer,self).get_moment(beam)

    if (self.memory['previous_moment'] is None or 
      self.memory['previous_moment'][1] != moment):
      self.memory['previous_moment'] = (beam,moment)

    return moment

  def beam_check(self,name):
    '''
    Overwritting for the purpose of including a check which measures how quickly
    the moment is changing on the beam.
    '''
    curr_moment = self.get_moment(name)
    prev_beam = self.memory['previous_moment'][0]
    prev_moment = self.memory['previous_moment'][1]
    change = curr_moment - prev_moment if prev_beam == name else 0

    if change >= construction.beam['moment_change_limit']:
      self.special_repair = True

    return (curr_moment < construction.beam['beam_limit'] or 
      change >= construction.beam['moment_change_limit'])

  def pre_decision(self):
    '''
    Adding the ability to add more steps to the repair mode.
    '''
    super(IntelligentRepairer,self).pre_decision()

    # Add additional steps if necessary
    if self.repair_mode and self.special_repair:
      self.memory['new_beam_steps'] = 2 * self.memory['new_beam_steps']
      self.special_repair = False

class SlowBuilder(NormalRepairer):
  '''
  Adds an additional check to the decision algorithms. This check is as follows:
    1. If we ever reach the top of a beam (there are no joints at the top) AND
    2. We have not seen a joint within the defined distance (in variables.py)
    3. Then we construct at that location

  Otherwise:
    1. If we reach the top of a beam where we would normally construct
    2. But that beam has no supporting structures withint the specified distance
    3. Go into repair mode.
  '''
  def __init__(self,name,structure,location,program):
    super(SlowBuilder,self).__ini__(name,structure,location,program)

  def no_available_directions(self):
    '''
    Overwritting to start repair of current beam if it meets the correct criteria
    We add the current beam to broken_list - indicating that we need repair - 
    when we meet the following conditions:
      1. At top of beam
      2. No joint within a specified distance (as defined in variables.py)
    '''
    # Find the closest joint on our beam
    # There should always be a joint on a beam (the i-end :))
    distance_to_joint = min(([helpers.distance(self.location,coord) 
      for coord in self.beam.joints]))

    # Add the current beam to broken because it needs support
    if self.at_top() and distance_to_joint > construction.beam['joint_distance']:
      self.memory['broken'] = (self.beam,0)

    # Call the normal function
    super(SlowBuilder,self).no_available_directions()

class MomentAwareBuilder(NormalRepairer):
  '''
  Adds the ability to take into account the direction of the moments, in additional
  to their magnitudes
  '''
  def get_preferred_direction(self,beam):
    # Obtain the moment vector
    u1,u2,u3 = beam.global_default_axes()
    m11,m22,m33 = self.get_moment_magnitudes(beam.name)

    # Quick debugging - making sure the torsion doesn't get too high
    if not helpers.compare(m11,0,4):
      pdb.set_trace()

    # Sum m22 and m33 (m11 is torsion, which doesn't play a role in the direction)
    moment_vector = helpers.sum_vectors(helpers.scale(m22,u2),helpers.scale(m33,u3))
    '''
    Cross axis-1 with the moment vector to obtain the positive clockwise direction
    This keeps the overall magnitude of moment_vector since u1 is a unit vector
      We are always attempting to repair further up the broken beam (closer to 
      the j-end). The cross will always give us the vector in the right direction
      if we do it this way.
    '''
    twist_direction = helpers.cross(moment_vector,u1)

    # Project the twist direction onto the xy-plane and normalize to have a
    # maximum of 45 degree approach (or, as specified in the variables.py)
    # depending on the ratio of moment magnitude to max_magnitude
    xy_change = (twist_direction[0],twist_direction[1],0)

    # The rotation is parallel to the z-axis, so we don't add disturbance
    if helpers.compare(helpers.length(xy_change),0):
      # Return the normal direction - which way is the beam leaning???
      return super(MomentAwareBuilder,self).get_preferred_direction()

    # We know the direction in which the beam is turning
    else:
      # Get direction of travel (this is a unit vector)
      travel = super(MomentAwareBuilder,self).get_preferred_direction()
      
      # Normalize twist to the maximum moment of force -- structure_check
      normal = helpers.normalize(xy_change,construction.beam['structure_check'])

      # The beam is vertical - check to see how large the normalized moment is
      if travel is None:
        # The change is relatively small, so ignore it
        if helpers.length(normal) <= helpers.ratio(construction.beam['verticality_angle']):
          return travel
        else:
          return helpers.make_unit(normal)

      else:
        scalar = 1 / helpers.ratio(construction.beam['moment_angle_max'])
        scaled_travel = helpers.scale(scalar,travel)
        return helpesr.make_unit(helpers.sum_vectors(normal,scaled_travel))