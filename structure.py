'''
This file establishes the structure and keeps track of all beam elements added to
it. This is done for the sake of efficiency, as we only want to query the SAP program
when absolutely necessary. The following functions are all helpful
'''
from sap2000 import variables
import math

class Structure:
  def __init__(self):
    # number of boxes
    self.num = variables.num_x, variables.num_y, variables.num_z

    # size of each box
    self.box_size = variables.dim_x / variables.num_x, variables.dim_y / variables.num_y, variables.dim_y / variables.num_y

    # size of the entire structure
    self.size = variables.dim_x, variables.dim_y, variables.dim_z

    # Storage of information
    self.model =  [[[{} for k in range(variables.num_x)] for j in range(variables.num_y)] for i in range(variables.num_z)]

  def __get_indeces(self,point):
    '''
    Returns the indeces of the box containing the specified point 
    '''
    def get_index(coord,axis):
      '''
      Returns index associated with the coord.
      '''
      return math.floor(coord / axis)

    x,y,z = point
    dim_x, dim_y, dim_z = self.size
    xi, yi, zi = get_index(x,dim_x), get_index(y,dim_y), get_index(z,dim_z)
    return xi, yi, zi

  def __path(self,coord1, coord2):
    '''
    Traverses the line formed between coord1 and coord2. Returns a list of points on the line that
    are likely to be in different boxes. This will NOT miss any points that are in difference boxes,
    but might return multiple points in the same box. The set of points also includes coord1, coord2
    '''
    # The beam isn't long enough to span multiple boxes
    minimum_size = min(self.box_size)
    if variables.beam_length < minimum_size:
      return [coord1,coord2]

    # Otherwise, trace the path by moving minimum_size along the beam
    else:
      # get step sizes
      steps = math.floor(variables.beam_length / minimum_size)
      x1,y1,z1 = coord1
      x2,y2,z2 = coord2
      step_x, step_y, step_z = (x2 - x1) / steps, (y2 - y1) / steps, (z2 - z1) / steps

      # While steps are available, calculate all possible points
      points = [coord1, coord2]
      for i in range(steps):
        x1 += step_x
        y1 += step_y
        z1 += step_y
        points.append((x1,y1,y2))

      return points

  def get_box(self,point):
    '''
    Finds the box containing the specified point and returns a dictionary containing the names
    and point coordinates of the objects for which any part is contained within the box
    '''
    xi, yi, zi = self.__get_indeces(point)
    num_x, num_y, num_z = self.num

    # Catch Errors 
    try:
      return (self.model[xi][yi][zi])
    except IndexError:
      print ("The coordinate, {}, is not in the structure and should never have been. Please check the add function in structure.py".format(point))

  def add_beam(self,p1,p2,name):
    ''' 
    Function to add the name and endpoint combination of a beam
    to all of the boxes that contain it. Returns the number of boxes (which should be at least 1)
    '''
    def addpoint(p):
      '''
      Function to add an arbitrary point to its respective box. Returns number of boxes changed.
      '''
      # Getting indeces
      xi,yi,zi = self.__get_indeces(p)

      # Adding endpoints/name to boxes that contain them
      try:
        if name in self.model[xi][yi][zi]:
          return 0
        else:
          self.model[xi][yi][zi].update({name: (p1,p2)})
          return 1
      except IndexError:
        print ("The coordinate {}, is not in the structure. Something went wront in addpoint()".format(p))

    # Add endpoints
    total_boxes = 0
    for point in self.__path(p1, p2):
      total_boxes += addpoint(point)

    # If something went wrong, kill the program
    assert total_boxes > 0

    return total_boxes

  def remove_beam(self,name,point=None):
    '''
    This function removes the beam element referred to by the specified name from all the boxes that
    contained it. If a point contained by the element is given, then it makes the removal faster.
    Otherwise, the entire structure is searched for the name, and all references removed. Returns
    true if the removal is successfull, false otherwise (ie, cannot find the element)
    '''
    # no point given, so cycle through entire structure
    deleted = False
    if point == None:
      for wall in self.model:
        for column in wall:
          for box in colum:
            if name in box:
              del box[name]
              deleted = True

    # point is given, so no need to cycle. Just find endpoints.
    else:
      xi, yi, zi = self.__get_indeces(point)
      # found the beam, now get endpoints to find rest of it
      if name in self.model[xi][yi][zi]:
        p1,p2 = self.model[xi][yi][zi][name]
        for p in self.__path(p1,p2):
          x,y,z = self.__get_indeces(p)
          if name in self.model[xi][yi][zi]:
            del self.model[xi][yi][zi][name]
            deleted = True
          else:
            print ("There should be a point, but there is not. Check add in structure.py.")
            assert 0 == 1

      # the beam isn't located in the specified box
      else: 
        print ("The beam was not found with the specified point")

    return deleted