from sap2000 import variables
from robots import Movable
import helpers

class Worker(Movable):
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)
    self.num_beams = variables.beam_capacity
    self.at_top = False
    self.upwards = False
    self.steps_to_construct = construction.steps_to_start

  def __pickup_beams(num = variables.beam_capacity):
    self.num_beam = self.num_beams + num
    self.weight = self.weight + variables.beam_load * num

  def __discard_beams(num = 1):
    self.num_beam = self.num_beam - num
    self.weight = self.weight - variables.beam_load * num

  def do_action(self):
    '''
    Overwriting the do_action functionality in order to have the robot move up or downward
    (depending on whether he is carrying a beam or not), and making sure that he gets a chance
    to build part of the structure if the situation is suitable.
    '''
    # If we can't construct here, then move
    if not self.construct():
      super(Worker,self).do_action()

    # Otherwise crawl somewhere else
    else:
      super(Worker,self).do_action()

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. This means that if the robot is carrying a beam,
    it wants to move upwards. If it is not, it wants to move downwards. So basically the direction
    is picked by filtering by the z-component
    '''
    def upwards(z):
      return z > 0
    def downwards(z):
      return z < 0
    def filter_dict(dirs, new_dirs, comp_f):
      for beam, vectors in info['directions'].items():
        for vector in vectors:
          # vector[2] = the z-component
          if comt_f(vector[2]):
            new_dirs[beam] = vector
      return new_dirs

    # Get all the possible directions, as normal
    info = self.get_directions_info()

    # Still have beams, so move upwards
    directions = {}
    if self.num_beams > 0 or self.upwards:
      directions = filter_dict(info['directions'], directions, upwards)
    # No more beams, so move downwards
    else:
      directions = filter_dict(info['directions'], directions, downwards)

    from random import choice

    # This will only occur if no direction changes our vertical height. If this is the case, get directions as before
    if directions == {}:
      beam_name = choice(list(info['directions'].keys()))
      direction = choice(info['directions'][beam_name])
    # Otherwise we do have a set of directions taking us in the right place, so randomly pick any of them
    else:
      beam_name = choice(list(diretions.keys()))
      direction = directions[beam_name]

    return {  'beam'      : info['box'][beam_name],
              'direction' : direction }

  def wander(self):
    '''    
    When a robot is not on a structure, it wanders. The wandering in the working class
    works as follows. The robot moves around randomly with the following restrictions:
      The robot moves towards the home location if it has no beams and 
        the home location is detected nearby.
      Otherwise, if it has beams for construction, it moves in a random direction until
      it finds a beam to climb on. Otherwise, after the specified number of steps, it 
      starts its own structure (tower)
    '''
    # Check to see if robot is at home location
    if self.__location[0] <= construction.home_size[0] and self.__location[1] <= construction.home_size[1]:
      self.__pickup_beams(variables.beam_capacity)

    # Check to see if robot should build based on steps taken
    if self.steps_to_construct == 0:
      self.build()

    # Find nearby beams to climb on
    result = self.ground()
    if result == None:
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.__location,helpers.scale(self.__step, helpers.make_unit(direction)))
      self.__change_location_local(new_location)
      self.steps_to_construct -= 1
    else:
      dist, close_beam, direction = result['distance'], result['beam'], result['direction']
      if dist < self.__step and self.num_beams > 0:
        self.beam = close_beam
        self.move(direction,close_beam)
      else:
        direction = self.get_ground_direction()
        new_location = helpers.sum_vectors(self.__location,helpers.scale(self.__step, helpers.make_unit(direction)))
        self.__change_location_local(new_location)
        self.steps_to_construct -= 1


  def build(self):
    '''
    This functions
    '''

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build (in which case)
    It returns the two points that should be connected, or we should continue moving 
    (in which case, it returns None)
    ''' 
    return False