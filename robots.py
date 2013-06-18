import commandline
from sap2000 import variables
from sap2000.constants import EOBJECT_TYPES

class Automaton:
  def __init__(self,name):
    self.name = name

class Movable(Automaton):
  def __init__(self,name,structure):
    super(Movable, self).__init__(name)
    self.structure = structure

	def move(self):
    '''
    Moves the robot in direction specified by the algorithm
    '''
		direction = self.get_direction()

  def get_direction(self):
    '''
    Returns a triplet with delta x, delta y, and delta z of the direction the robot should
    move in. In a sense, returns a vector <x,y,z>
    '''
    objs_nearby = self.structure.neighbors(self.position)

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
    self.location = location

  def build(self):