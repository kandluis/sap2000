from builder import Builder
import helpers,variables, pdb

class Worker(Builder):
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)
    # The number of beams the robot is carrying (picked up at home now)
    self.num_beams = 0

    # Move further in the x-direction?
    self.memory['pos_x'] = None

    # Move further in the y-direction?
    self.memory['pos_y'] = None

  def current_state(self):
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
    super(Worker,self).no_available_direction()

    # Construct a beam instead of moving if we have beams left
    if self.num_beams > 0:
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

    if (((self.at_site() and self.structure.tubes == 0)) and not 
      self.memory['built'] and 
      self.num_beams > 0):

      self.memory['built'] = True
      self.memory['construct'] += 1
      return True
    else:
      self.memory['built'] = False
      return False

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build.
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
    # Check to see if we have an analysis model!

class Repairer(Worker):
  def __init__(self,structure,location,program):
    super(Repairer,self).__init__(structure,location,program)