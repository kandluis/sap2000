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
    self.structure = structure
    self.step = variables.step_length
    self.location = location
    self.on_beam = None

	def move(self):
    '''
    Moves the robot in direction specified by the algorithm.
    '''
		direction = self.get_direction()

  def get_directions(self):
    '''
    Returns a list of triplets with delta x, delta y, and delta z of the direction the robot can
    move in. These directions constitute the locations where beams currently exist. Additionally,
    it returns the "box of locality" to which the robot is restricted.
    '''
    true_location = None
    # If we do have a beam (ie, endpoints), verify that the robot is on that beam and
    # correct if necessary. This is done so that floating-point arithmethic errors don't add up.
    if self.on_beam != None:
      e1, e2 = self.on_beam
      if helpers.on_line (e1,e2,self.location):
        true_location = self.location
      else:
        true_location =helpers.correct (e1,e2,self.location)

    # Find beams in the box which intersect the robot's location (ie, where can he walk?)
    crawlable = []
    for beam, (p1,p2) in box:

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. In this class, it simply picks a random
    direction (eventually, it will have a tendency to move upwards)
    '''
    directions = self.get_directions

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

  def construct(self):
    '''
    Decides whether the local conditions dictate 