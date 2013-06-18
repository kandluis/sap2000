from sap2000 import variables
from sap2000.constants import EOBJECT_TYPES
import helpers

class Automaton:
  def __init__(self,model):
    self._model = model

class Movable(Automaton):
  def __init__(self,structure,location,model):
    super(Movable, self).__init__(model)
    self.__structure = structure
    self.__step = variables.step_length
    self.__location = location
    self.on_beam = None

  def __change_location(self,new_location, new_beam = "", new_beam_points=None):
    '''
    Function that takes care of changing the location of the robot on the
    SAP2000 program. Removes the current load from the previous location (ie,
    the previous beam), and shifts it to the new beam (specified by the new location)
    It also updates the current beam
    '''
    self.__location = new_location
    self.on_beam = new_beam_points

  def __get_walkable(self,beams):
    '''
    Returns all of the beams in beams which intersect the robots location
    '''
    crawlable = {}
    for beam, (e1,e2) in beams:
      if helpers.on_line(e1,e2,self.__location):
        crawlable.update({beam : (e1,e2)})

    return crawlable

  def get_location(self):
    '''
    Provides easy access to the location
    '''
    return self.__location

  def move(self):
    '''
    Moves the robot in direction specified by the algorithm.
    '''
    move_info = self.get_direction()
    length = helpers.length(move_info['direction'])

    # The direction is smaller than the usual step, so move exactly by direction
    if length < self.__step:
      new_location = helpers.sum_vectors(self.__location, move_info['direction'])
      self.__change_location(new_location, move_info['beam'], move_info['endpoints'])

    # The direction is larger than the usual step, so move only the usual step in the specified direction
    else:
      movement = helpers.scale(self.__step, helpers.make_unit(move_info['direction']))
      new_location = helper.sum_vectors(self.__location, movement)
      self.__change_location(new_location, move_info['beam'], move_info['endpoints'])

  def get_directions_info(self):
    '''
    Returns a list of triplets with delta x, delta y, and delta z of the direction the robot can
    move in. These directions constitute the locations where beams currently exist. Additionally,
    it returns the "box of locality" to which the robot is restricted containing all of the beams
    nearby that the robot can detect (though, this should only be used for finding a connection,
    as the robot itself SHOULD only measure the stresses on its current beam)
    '''
    # If we do have a beam (ie, endpoints), verify that the robot is on that beam and
    # correct if necessary. This is done so that floating-point arithmethic errors don't add up.
    if self.on_beam != None:
      e1, e2 = self.on_beam
      if not (helpers.on_line (e1,e2,self.__location)):
        self.__change_location(helpers.correct (e1,e2,self.__location), self.on_beam)

    # Obtain all local objects
    box = self.__structure.get_box(self.__location)

    # Find beams in the box which intersect the robot's location (ie, where can he walk?)
    crawlable = self.__get_walkable(box)

    # Convert endpoints of beams into direction vectors
    directions_info = []
    for beam, (p1,p2) in crawlable:
      directions_info.append(beam,helpers.make_vector(self.__location,p1))
      directions_info.append(beam,helpers.make_vector(self.__location,p2))

    return {  'box'         : box,
              'directions'  : directions_info }

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. In this class, it simply picks a random
    direction (eventually, it will have a tendency to move upwards when carrying a beam
    and downwards when needing material for the structure). The direction 
    is also returned with it's corresponding beam.
    '''
    from random import choice

    info = self.get_directions_info()
    beam, direction = choice(info['directions'])

    return {  'beam'      : beam,
              'endpoints' : info['box'][beam],
              'direction' : direction }

class Worker(Movable):
  def __init__(self,structure,location,model):
    super(Worker,self).__init__(structure,location,model)
    self.beams = variables.beam_capacity

  def move(self):
    '''
    Overwrites the move functionality of Movable to provide the chance to build in a timestep
    instead of moving to another space.
    '''
    if contruct() == None:
      super(Worker,self).move()
    else:
      self.build()

  def build(self):
    pass

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build (in which case)
    It returns the two points that should be connected, or we should continue moving 
    (in which case, it returns None)
    ''' 
    None