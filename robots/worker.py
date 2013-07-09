from helpers import helpers
from robots.builder import Builder
import pdb, variables

class Worker(Builder):
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)
    # The number of beams the robot is carrying (picked up at home now)
    self.num_beams = 0

    # Move further in the x-direction?
    self.memory['pos_x'] = None

    # Move further in the y-direction?
    self.memory['pos_y'] = None

  def at_top(self):
    '''
    Returns if we really are at the top, in which case build
    '''
    if self.beam is not None:
      for endpoint in self.beam.endpoints:
        if helpers.compare(helpers.distance(self.location,endpoint),0):
          return True

    return False

  def current_state(self):
    '''
    Returns current state of robot
    '''
    state = super(Worker,self).current_state()
    return state

  def discard_beams(self,num = 1):
    '''
    Adding ability to change memory
    '''
    super(Worker,self).discard_beams(num)
    if self.num_beams == 0:
      self.memory['pos_z'] = False

  def pickup_beams(self,num = variables.beam_capacity):
    '''
    Adding ability to change memory
    '''
    super(Worker,self).pickup_beams(num)
    self.memory['pos_z'] = True

  def filter_directions(self,dirs):
    '''
    Filters the available directions and returns those that move us in the 
    desired direction. Overwritten to take into account the directions in
    which we want to move. When climbing down, it will take the steepest path.
    '''
    def bool_fun(string):
      '''
      Returns the correct funtion depending on the information stored in memory
      '''
      if self.memory[string]:
        return (lambda a : a > 0)
      elif self.memory[string] is not None:
        return (lambda a : a < 0)
      else:
        return (lambda a: True)

    # Get the current bending 

    # direction functions
    funs = [bool_fun('pos_x'), bool_fun('pos_y'), bool_fun('pos_z')]

    directions =  self.filter_dict(dirs, {}, funs)

    return directions

  def elect_direction(self,directions):
    # Climb down the steepest descent
    if not self.memory['pos_z']:
      beam, direction = min([(n, helpers.make_unit(v))for n,v in directions.items()],
        key=lambda t : t[1][2])
      return (beam, directions[beam])

    # Randomly moving up
    else:
      return super(Worker,self).elect_direction(directions)

  def no_available_direction(self):
    '''
    Change start construction to true
    '''
    # Do parent class' work  
    super(Worker,self).no_available_direction()

    # Construct a beam instead of moving if we have beams left
    if self.num_beams > 0 and self.at_top():
      self.start_construction = True

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

    if (((self.at_site() and not self.structure.started)) and not 
      self.memory['built'] and 
      self.num_beams > 0):

      self.structure.started = True
      self.memory['built'] = True
      self.memory['construct'] += 1
      return True
    else:
      self.memory['built'] = False
      return False

  def start_repair(self,beam):
    '''
    Initializes the repair of the specified beam. Figures out which direction to
    travel in and stores it within the robot's memory, then tells it to climb
    down in a specific direction if necessary.
    '''

  def local_rules(self):
    '''
    Uses the information from SAP2000 to decide what needs to be done. This 
    funtion returns true if we should construct, and return false otherwise.
    Also calls the function start_repair in case a repair is necessary
    '''
    # If the program is not locked, there are no analysis results so True
    if not self.model.GetModelIsLocked():
      return True

    # Analysis results available
    else:
      return True

  def construct(self):
    '''
    Decides whether the robot should construct or not
    '''
    return self.basic_rules() and self.local_rules()

class Repairer(Worker):
  def __init__(self,structure,location,program):
    super(Repairer,self).__init__(structure,location,program)