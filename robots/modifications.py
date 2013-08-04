from helpers import helpers
from robots.repairer import Repairer
import construction, math, pdb,variables, random


class NormalRepairer(Repairer):
  def __init__(self,name,structure,location,program):
    super(NormalRepairer,self).__init__(name,structure,location,program)


class RandomUpwardRepairer(NormalRepairer):
  '''
  Climbs upward beams randomly instead of following the least vertical
  '''
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