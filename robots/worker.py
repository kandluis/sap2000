from Helpers import helpers
from robots.builder import Builder
import math, pdb

from Behaviour import constants as BConstants

from variables import ROBOT

class Worker(Builder):
  def __init__(self,name,structure,location,program):
    super(Worker,self).__init__(name,structure,location,program)
    # The number of beams the robot is carrying (picked up at home now)
    self.num_beams = 0

    # Since we aren't carryng any beams
    self.weight = ROBOT['load']

    # Smaller number gives higher priority
    self.memory['dir_priority'] = [0,0,0]

    # Move further in the x-direction?
    self.memory['pos_x'] = None

    # Move further in the y-direction?
    self.memory['pos_y'] = None

  def current_state(self):
    return super(Worker,self).current_state()

  def at_top(self):
    '''
    Returns if we really are at the top
    '''
    def below(beams):
      '''
      Returns whether all of the beams are below us
      '''
      for beam in beams:
        for endpoint in beam.endpoints:

          # If the beam is not close to us and it is greater than our location
          if (not helpers.compare(helpers.distance(self.location,endpoint),0)
            and endpoint[2] > self.location[2]):
            return False

      return True

    if self.beam is not None:
      if (helpers.compare(helpers.distance(self.location,self.beam.endpoints.i),0)
        and self.beam.endpoints.i[2] > self.beam.endpoints.j[2]):
        close = self.beam.endpoints.i
      elif (helpers.compare(helpers.distance(self.location,self.beam.endpoints.j),0)
        and self.beam.endpoints.j[2] > self.beam.endpoints.i[2]):
        close = self.beam.endpoints.j
      else:
        close = None

      if close is not None:
        try:
          beams = self.beam.joints[self.beam.endpoints.i]
          return below(beams)
        except KeyError:
          return True

    return False

  def discard_beams(self,num = 1):
    '''
    Adding ability to change memory
    '''
    super(Worker,self).discard_beams(num)

    # Move down
    if self.num_beams == 0:
      self.memory['pos_z'] = False

  def pickup_beams(self,num = ROBOT['beam_capacity']):
    '''
    Adding ability to change memory
    '''
    super(Worker,self).pickup_beams(num)

    # Move up when you pick one up
    self.memory['pos_z'] = True

  def repairing(self):
    '''
    Place holder for later access.
    '''
    pass

  def filter_directions(self,dirs):
    '''
    Filters the available directions and returns those that move us in the 
    desired direction. Overwritten to take into account the directions in
    which we want to move. When climbing down, it will take the steepest path.
    '''
    # Change stuff up, depending on whether we are in repair mode (but not 
    # construct support mode)
    if self.search_mode and not self.memory['construct_support']:
      self.repairing()

    def bool_fun(string):
      '''
      Returns the correct funtion depending on the information stored in memory
      '''
      if self.memory[string]:
        return (lambda a : a > 0)
      elif self.memory[string] is not None:
        return (lambda a : a < 0)
      else:
        return (lambda a : True)

    # direction functions
    funs = [bool_fun('pos_x'), bool_fun('pos_y'), bool_fun('pos_z')]

    directions =  self.filter_dict(dirs, {}, funs,preferenced=self.search_mode)

    return directions

  def pick_direction(self,directions):
    '''
    Overwritting to pick the direction of steepest descent when climbing down
    instead of just picking a direction randomly. Also takes into account that 
    we might want to travel upward when repairing.
    '''
    def min_max_dir(vs,get_min=True):
      unit_list = [helpers.make_unit(v) for v in vs]
      if get_min:
        val = min(unit_list,key=lambda t : t[2])
      else:
        val = max(unit_list,key=lambda t : t[2])

      index = unit_list.index(val)
      return index,val

    def pick_support(vs):
      '''
      Returns index, sorting_angle of vs.
      '''
      angle_list = [abs(helpers.smallest_angle((1,0,0),v) - 
        BConstants.beam['support_angle']) for v in vs]
      min_val = min(angle_list)
      index = angle_list.index(min_val)
      return index, min_val

    if self.search_mode and not self.memory['construct_support']:
      self.repairing()

    # Pick the closests direction to a support beam
    if self.search_mode and self.at_joint():
      #pdb.set_trace()
      beam, (index,angle) = min([(n, pick_support(vs)) for n,vs in directions.items()],
        key=lambda t: t[1][1])

    # Pick the smalles pos_z whether moving up or down (modification)
    else:
      beam, (index, unit_dir) = min([(n, min_max_dir(vs)) for n,vs in directions.items()],
        key=lambda t : t[1][1][2])

    # We want to return the original direction vector since it contains both
    # information on direction and on distance

    direction = beam, directions[beam][index]
    # Store direction
    self.memory['previous_direction'] = direction
    
    return direction

  def no_available_direction(self):
    '''
    We construct if we truly are at the top of a beam
    '''
    if self.num_beams > 0 and self.at_top():
      self.start_construction = True
      self.memory['broken'] = []
    else:
      super(Worker,self).no_available_direction()

  def basic_rules(self):
    '''
    Decides whether to build or not. Uses some relatively simple rules to decide.
    Here is the basic logic it is following.
    1.  a)  If we are at the top of a beam
        OR
        b)  i)  We are at the specified construction site
            AND
            ii) There is no beginning tube
    AND
    2.  Did not build in the previous timestep
    AND
    3.  Still carrying construction material
    '''

    if (((self.at_site() and not self.structure.started and not self.search_mode
      )) and not self.memory['built'] and self.num_beams > 0):

      self.structure.started = True
      self.memory['built'] = True
      return True
    else:
      self.memory['built'] = False
      return False

  def local_rules(self):
    '''
    Uses the information from SAP2000 to decide what needs to be done. This 
    funtion returns true if we should construct, and return false otherwise.
    Also calls the function start_repair in case a repair is necessary
    '''
    # If the program is not locked, there are no analysis results so True
    if not self.model.GetModelIsLocked():
      return False

    # Analysis results available
    else:
      return False

  def construct(self):
    '''
    Decides whether the robot should construct or not based on some local rules.
    '''
    return self.basic_rules() or self.local_rules()