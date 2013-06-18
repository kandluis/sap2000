# provides access to the program, model variables
import commandline

from sap2000 import variables
from sap2000.constants import EOBJECT_TYPES

class Automaton:
  def __init__(self,name):
    self.name = name

class Movable(Automaton):
  def __init__(self,name,structure,location):
    super(Movable, self).__init__(name)
    self._structure = structure
    self._step = variables.step_length
    self.location = location
    self.on_beam = None

	def __change_location(self,new_location, new_beam_points = None):
    '''
    Function that takes care of changing the location of the robot on the
    SAP2000 program. Removes the current load from the previous location (ie,
    the previous beam), and shifts it to the new beam (specified by the new location)
    It also updates the current beam
    '''
    self.location = new_location
    self.on_beam = new_beam_points

def __get_walkable(self,beams):
  '''
  Returns all of the beams in beams which intersect the robots location
  '''
  crawlable = {}
  for beam, (e1,e2) in beams:
    if helpers.on_line(e1,e2,self.location):
      crawlable.update(beam: (e1,e2))

  return crawlable

  def move(self):
    '''
    Moves the robot in direction specified by the algorithm.
    '''
		move_info = self.get_direction()
    length = helpers.length(move_info['direction'])

    # The direction is smaller than the usual step, so move exactly by direction
    if length < self._step:
      pass
    else:
      pass

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
      if not (helpers.on_line (e1,e2,self.location)):
        self.__change_location(helpers.correct (e1,e2,self.location), self.on_beam)

    # Obtain all local objects
    box = self._structure.get_box(true_location)

    # Find beams in the box which intersect the robot's location (ie, where can he walk?)
    crawlable = self.__get_walkable(box)

    # Convert endpoints of beams into direction vectors
    directions_info = []
    for beam, (p1,p2) in crawlable:
      directions.append(beam,helpers.make_vector(self.location,p1))
      directions.append(beam,helpers.make_vector(self.location,p2))

    return box, directions_info

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. In this class, it simply picks a random
    direction (eventually, it will have a tendency to move upwards). The direction 
    is also returned with it's corresponding beam.
    '''
    from random import choice

    box, directions_info = self.get_directions_info()
    beam, direction = choice(directions_info)

    return {  'beam'      : beam,
              'endpoints' : box[beam],
              'direction' : direction }

    '''
    ## Some TEST code we decided not to use
    range = variable.local_radius/2
    x,y,z = self.location
    selectObject = model.SelectObject

    # calculate box coordinates
    xmin,xmax = x - range, x + range
    ymin,ymax = y - range, y + range
    zmin,zmax = z - range, y + range

    # select box using program
    selectObject.CoordinateRange(xmin,xmax,ymin,ymax,zmin,zmax,IncludeIntersections=True)
    return_value, number, types, names = selectObject.GetSelected()
    helpers.check(return_value, "An error occurred when obtaining the direction. GetSelected returned non-zero")
    '''

class Worker(Movable):
  def __init__(self,name,structure,location):
    super(Worker,self).__init__(name,structure)
    self.beams = variables.beam_capacity

  def move(self):
    '''
    Overwrites the move functionality of Movable to provide the chance to build in a timestep
    instead of moving to another space.
    '''
    if contruct() = None:
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