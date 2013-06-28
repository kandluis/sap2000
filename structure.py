'''
This file establishes the structure and keeps track of all beam elements added to
it. This is done for the sake of efficiency, as we only want to query the SAP program
when absolutely necessary. The following functions are all helpful
'''
from beams import Beam
from errors import OutofBox
import math, sys,helpers, variables

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

    # Keeps track of how many tubes we have in the structure
    self.tubes = 0

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

    dim_x, dim_y, dim_z = self.box_size
    xi, yi, zi = get_index(x,dim_x), get_index(y,dim_y), get_index(z,dim_z)
    return xi, yi, zi

  def __path(self,coord1, coord2):
    '''
    Traverses the line formed between coord1 and coord2. Returns a list of points on the line that
    lie in different boxes. This will NOT miss any points that are in difference boxes. The basic
    method is to find the intersection of the line with one of the faces of the cube formed by the
    box. There should not be multiple points, but this has not been proven. It might return two points
    that are in the same box.
    '''
    def get_sign(n):
      '''
      Returns the sign of the number
      '''
      if n == 0:
        return None
      else:
        return n > 0

    # move from coord1 to coord2. Here, we determine the sign of the change (pos = True, neg = False, or None)
    signs = get_sign(coord2[0] - coord1[0]), get_sign(coord2[1] - coord1[1]), get_sign(coord2[2] - coord1[2])
    line = helpers.make_vector(coord1,coord2)

    def crawl(point):
      # get the current box boundaries (bottom left corner - (0,0,0) is starting) and coordinates
      xi, yi, zi = self.__get_indeces(point)
      bounds = xi * self.box_size[0], yi * self.box_size[1], zi * self.box_size[2]

      # This is defined here to have access to the above signs and bounds
      def closest(p):
        '''
        Returns which coordinate in p is closest to the boundary of a box (x = 0, y = 1, z = 2), 
        and the absolute change in that coordinate.
        '''
        def distance(i):
          '''
          i is 0,1,2 for x,y,z
          '''
          if signs[i] == None:
            # This will never be the minimum. Makes later code easier
            return max(self.box_size) + 1
          elif signs[i]:
            return abs(p[i] - (bounds[i] + self.box_size[i]))
          else:
            return abs(p[i] - bounds[i])

        # Find the shortest distances
        coords = [distance(i) for i in range(3)]
        index = coords.index(min(coords))

        return index, coords[index]

      # In crawl, we obtain the coordinate closests to an edge (index), and its absolute distance from that edge
      index, distance = closest(point)

      # The change is the line scaled so that the right coordinate changes the amount necessary to cross into the next box
      # This means that we scale it and also add a teeny bit so as to push it into the right box
      # This is the scaled version, exactly the distance we need to move
      move = helpers.scale(distance / abs(line[index]), line)
      # Here we scale the line again by epsilon/2. This is our push
      push = helpers.scale(variables.epsilon / 2, line)
      # The total change is the addition of these two
      change = helpers.sum_vectors(move,push)

      # make sure we are changing the right amount
      assert helpers.compare(abs(move[index]), distance)

      # The new initial coordinate in the next box
      new_point = helpers.sum_vectors(point,change)

      return new_point

    points, passed,temp = [coord2], False, coord1
    while not passed:
      points.append(temp)
      temp = crawl(temp)

      # Check the next coordinate to see if we have moved past the endpoint
      for i in range(3):
        if signs[i] != None:
          # Movings positively, so set to True if our new_point has a larger positive coordinate
          # Moving negatively, so set to True if our new_point has a smaller positive coordinate
          passed = temp[i] > coord2[i] + variables.epsilon / 2 if signs[i] else temp[i] < coord2[i] - variables.epsilon / 2

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
      return False

  def add_beam(self,p1,p2,name):
    ''' 
    Function to add the name and endpoint combination of a beam
    to all of the boxes that contain it. Returns the number of boxes (which should be at least 1)
    '''
    def addbeam(beam,p):
      '''
      Function to add an arbitrary beam to its respective box. Returns number of boxes changed.
      Also takes care of finding intersecting beams to the added beam and adding the joints to both
      beams. Uses the point p (which should be on the beam), to calculate the box it should be added to
      '''
      # Getting indeces
      xi,yi,zi = self.__get_indeces(p)

      # Getting the box and all of the other beams in the box
      try:
        box = self.model[xi][yi][zi]
      except IndexError:
        print ("Addbeam is incorrect. Accessing box not defined.")
        return False

      # Finding intersection points with other beams
      for key in box:
        point = helpers.intersection(box[key].endpoints, beam.endpoints)
        # If they intersect, add the joint to both beams
        if point != None:
          assert key == box[key].name
          if not beam.addjoint(point, box[key]):
            sys.exit("Could not add joint to {} at {}".format(beam.name, str(point)))
          if not box[key].addjoint(point, beam):
            sys.exit("Could not add joint to {} at {}".format(box[key].name, str(point)))

      # update the box
      self.model[xi][yi][zi] = box

      # Adding beam to boxes that contain it based on the point p.
      try:
        if beam.name in self.model[xi][yi][zi]:
          return 0
        else:
          self.model[xi][yi][zi][beam.name] = beam
          return 1
      except IndexError:
        raise OutofBox ("The coordinate {}, is not in the structure. Something went wront in addpoint()".format(p))

    # Create the beam
    new_beam = Beam(name,(p1,p2))

    # Add to all boxes it is located in
    total_boxes = 0
    try:
      for point in self.__path(p1, p2):
        total_boxes += addbeam(new_beam,point)
    except OutofBox as e:
      print (e)
      return False

    # If something went wrong, kill the program
    assert total_boxes > 0

    # Add a beam to the structure
    self.tubes += 1

    return total_boxes

  def remove_beam(self,name,point=None):
    '''
    This function removes the beam element referred to by the specified name from all the boxes that
    contained it. If a point contained by the element is given, then it makes the removal faster.
    Otherwise, the entire structure is searched for the name, and all references removed. Returns
    true if the removal is successfull, false otherwise (ie, cannot find the element)
    Furthermore, it removes itself from all of the beams with which it previously intersected.
    '''
    def remove_joints(beam):
      for coord in beam.joints:
        for other_beam in beam.joints[coord]:
          if not other_beam.removejoint(coord,beam):
            return False
      return True


    # no point given, so cycle through entire structure
    deleted = False
    if point == None:
      for wall in self.model:
        for column in wall:
          for box in column:
            if name in box:
              value = remove_joints(box[name])
              del box[name]
              deleted = value
      self.tubes -= 1
      return value

    # point is given, so no need to cycle. Just find endpoints.
    else:
      xi, yi, zi = self.__get_indeces(point)
      # found the beam, now get endpoints to find rest of it
      if name in self.model[xi][yi][zi]:
        beam = self.model[xi][yi][zi][name]
        p1,p2 = beam.endpoints

        # find the boxes it crosses
        for p in self.__path(p1,p2):
          x,y,z = self.__get_indeces(p)

          # check for the beam being in the box, otherwise raise an error
          if name in self.model[x][y][z]:
            del self.model[x][y][z][name]
            deleted = True
        self.tubes -= 1
        return remove_joints(beam)

      # the beam isn't located in the specified box
      else: 
        print ("The beam was not found with the specified point. Attempting to remove it anyway.")
        return remove_beam(name)

  def reset(self):
    # Reset the storage
    self.model =  [[[{} for k in range(self.num[0])] for j in range(self.num[1])] for i in range(self.num[2])]

    # Reset the tubes
    self.tubes = 0