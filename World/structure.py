'''
This file establishes the structure and keeps track of all beam elements added 
to it. This is done for the sake of efficiency, as we only want to query the 
SAP program when absolutely necessary. The following functions are all helpful'
'''
# Python libraries
import math
import sys
# allows easy implementation of Coord and EndPoints
from collections import namedtuple

# Importing helper functions
from Helpers import helpers
from Helpers.errors import OutofBox
# importing simulation constants
from variables import BEAM, MATERIAL, PROGRAM, VISUALIZATION, WORLD

# importing visualization library
import visual

# name the tuples - easily creating both a Coord Objects and an Endpoint Object
Coord = namedtuple("Coordinates", ["x", "y", "z"])
EndPoints = namedtuple("Endpoints", ["i","j"])

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Beam Object Definition
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class BeamBase(object):
  def __init__(self, name, endpoints,visual_model = None):
    # Each beam has two endpoints (i and j)
    self.endpoints = EndPoints(i=endpoints[0], j=endpoints[1])

    # Each beam keeps track of all its joints. This is a dictionary as follows:
    # {coord : list of beams}
    self.joints = {}

    # This is the name of the beam
    self.name = name

    # This is how much each beam weighs
    self.weight = MATERIAL['beam_load']

    self.visual_model = visual_model

  def current_state(self):
    '''
    Returns the current state
    '''
    joints = {}
    for coord, beams in self.joints.items():
      for beam in beams:
        if coord in joints:
          joints[coord].append(beam.name)
        else:
          joints[coord] = [beam.name]

    return {  'endpoints' : self.endpoints,
               'joints'    : joints,
              'weight'    : self.weight  }

  def addjoint(self, coord, beam):
    '''
    Adds a joint (at the specified coordinate), to the beam itself. The beam 
    variable defines the which crosses this one at the joint
    '''
    # Verify that the coordinate is on the beam based on endpoints
    if not helpers.on_line(self.endpoints.i, self.endpoints.j, coord):
      return False

    else:
      coord = Coord(x=coord[0],y=coord[1],z=coord[2])
      # We cycle manually so we can compare using our compare function
      for key, beams in self.joints.items():
        # We have a key and the beam isn't already there
        if helpers.compare_tuple(key,coord) and beam not in beams:
          self.joints[key].append(beam)
          return True

      self.joints[coord] = [beam]
      return True

  def removejoint(self,coord, beam):
    '''
    Removes a specified joint from this beam. Returns whether or not the removal
    was successful.
    '''
    coord = Coord(x=coord[0],y=coord[1],z=coord[2])
    # The joint is not on the beam
    if not coord in self.joints:
      return False

    else:
      # The beam is not at this joint
      if not beam in self.joints[coord]:
        return False
      else:
        self.joints[coord].remove(beam)

        # remove the coordinate if there are no beams there
        if self.joints[coord] == []:
          self.joints.pop(coord, None)
        return True

class Beam(BeamBase):
  '''
  This class keeps track of both the original design location of the tubes and 
  of the deflected location based on the analysis results
  '''
  def __init__(self, name, endpoints,endpoint_names, visual_model = None):
    super(Beam,self).__init__(name,endpoints,visual_model)

    self.endpoint_names = EndPoints(i=endpoint_names[0],j=endpoint_names[1])
    
    # Keeps track of the amoung of deflection
    self.deflection = None

    # Deflected enpoints
    self.deflected_enpoints = self.get_true_endpoints()

    # Keeps track of the deflected endpoint we last wrote out 
    # This makes a faster visualization (we only change the visualization) when
    # there's a change that will be noticeable.
    self.previous_write_endpoints = None

  def current_state(self):
    '''
    Adding deflected endpoints to state
    '''
    state = super(Beam,self).current_state()

    state.update({ 'deflected_enpoints'        : self.deflected_enpoints,
                  'deflection'                : self.deflection,
                  'previous_write_endpoints'  : self.previous_write_endpoints,
                  'endpoint_names'            : self.endpoint_names })

    return state

  def update_deflection(self,i_val,j_val):
    '''
    Updates the deflection using a named tupled
    '''
    # Update deflection
    self.deflection = EndPoints(i=i_val,j=j_val)

    # Update endpoints
    self.deflected_endpoints = self.get_true_endpoints()

    return (self.previous_write_endpoints is None or helpers.distance(
      self.deflected_endpoints.i,self.previous_write_endpoints.i) 
      >= VISUALIZATION['step'] or helpers.distance(
        self.deflected_endpoints.j,self.previous_write_endpoints.j) >=
      VISUALIZATION['step'])

  def global_default_axes(self):
    '''
    Returns the default local axes. Later on we might incorporate the ability to return
    rotated axes.
    '''
    axis_1 = helpers.make_unit(helpers.make_vector(self.endpoints.i,
      self.endpoints.j))
    vertical = (math.sin(math.radians(helpers.smallest_angle(axis_1,(0,0,1)))) 
      <= 0.001)

    # Break up axis_1 into unit component vectors on 1-2 plane, along with 
    # their maginitudes
    u1, u2 = (axis_1[0],axis_1[1],0),(0,0,axis_1[2])
    l1,l2 = helpers.length(u1), helpers.length(u2)
    u1 = helpers.make_unit(u1) if not helpers.compare(l1,0) else (1,1,0) 
    u2 = helpers.make_unit(u2) if not helpers.compare(l2,0) else (0,0,1)

    # Calculate axis_2 by negating and flipping componenet vectors of axis_1
    axis_2 = (1,0,0) if vertical else helpers.make_unit(helpers.sum_vectors(
      helpers.scale(-1 * l2,u1),helpers.scale(l1,u2)))

    # Make it have a positive z-component
    axis_2 = axis_2 if axis_2[2] > 0 else helpers.scale(-1,axis_2)

    # Calculate axis_3 by crossing axis 1 with axis 2 (according to right hand
    # rule)
    axis_3 = helpers.cross(axis_1,axis_2)
    axis_3 = helpers.make_unit((axis_3[0],axis_3[1],0)) if vertical else axis_3

    # Sanity checks
    # Unit length
    assert helpers.compare(helpers.length(axis_3),1)

    # On the x-y plane
    assert helpers.compare(axis_3[2],0)

    return axis_1,axis_2,axis_3

  def global_joint_axes(self):
    '''
    By default, 1,2,3 and the same as +x,+y,+z
    '''
    return (1,0,0),(0,1,0),(0,0,1)

  def get_true_endpoints(self):
    '''
    Takes into account the deflection and returns the true physical endpoints of
    the structure
    '''
    if self.deflection is None:
      return self.endpoints
    else:
      return EndPoints(i=helpers.sum_vectors(self.endpoints.i,self.deflection.i),
       j=helpers.sum_vectors(self.endpoints.j,self.deflection.j))

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Python Structure Object
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Structure(object):
  def __init__(self, visualization):

    super(Structure,self).__init__()

    # number of boxes
    self.num = WORLD['properties']['num_x'], WORLD['properties']['num_y'], WORLD['properties']['num_z']

    # size of each box
    self.box_size = (WORLD['properties']['dim_x'] / WORLD['properties']['num_x'], WORLD['properties']['dim_y'] / 
      WORLD['properties']['num_y'], WORLD['properties']['dim_y'] / WORLD['properties']['num_y'])

    self.origin = WORLD['properties']['origin']

    # size of the entire structure
    self.size = WORLD['properties']['dim_x'], WORLD['properties']['dim_y'], WORLD['properties']['dim_z']

    # Storage of information
    self.model =  ([[[{} for k in range(WORLD['properties']['num_z'])] for j in 
      range(WORLD['properties']['num_y'])] for i in range(WORLD['properties']['num_x'])])

    # Keeps track of how many tubes we have in the structure
    self.tubes = 0

    # Keeps track of whether the decesion to start it has occured
    self.started = False

    # Maximum height of the strucutre
    self.height = 0

    # Whether or not we should display the structure
    self.visualization = visualization

    # Keeps track of the visualization data
    self.visualization_data = ''

    # Keeps track of the colors of each beam based on its current max_moment
    self.color_data = ''

    # Stores information on the beams' max moments
    self.structure_data = []

  def __feasable_point(self,p):
    '''
    Checks whether or not a point lies within the defined limits of the 
    structure
    '''
    return helpers.within(self.origin,self.size,p)

  def __get_indeces(self,point):
    '''
    Returns the indeces of the box containing the specified point 
    '''
    def get_index(coord,axis):
      '''
      Returns index associated with the coord.
      '''
      return int(math.floor(coord / axis))

    x,y,z = point

    dim_x, dim_y, dim_z = self.box_size
    xi, yi, zi = get_index(x,dim_x), get_index(y,dim_y), get_index(z,dim_z)
    return xi, yi, zi

  def __path(self,coord1, coord2):
    '''
    Traverses the line formed between coord1 and coord2. Returns a list of 
    points on the line that lie in different boxes. This will NOT miss any 
    points that are in different boxes. The basic method is to find the 
    intersection of the line with one of the faces of the cube formed by the 
    box. There should not be multiple points, but this has not been proven. It 
    might return two points that are in the same box.
    '''
    def get_sign(n):
      '''
      Returns the sign of the number
      '''
      if n == 0:
        return None
      else:
        return n > 0

    # move from coord1 to coord2. Here, we determine the sign of the change 
    # (pos = True, neg = False, or None)
    signs = (get_sign(coord2[0] - coord1[0]), get_sign(coord2[1] - coord1[1]),
      get_sign(coord2[2] - coord1[2]))
    line = helpers.make_vector(coord1,coord2)

    def crawl(point):
      # get the current box boundaries (bottom left corner-(0,0,0) is starting)
      # and coordinates
      xi, yi, zi = self.__get_indeces(point)
      bounds = xi*self.box_size[0], yi*self.box_size[1], zi*self.box_size[2]

      # This is defined here to have access to the above signs and bounds
      def closest(p):
        '''
        Returns which coordinate in p is closest to the boundary of a box 
        (x = 0, y = 1, z = 2) if moving along the line, and the absolute change
        in that coordinate.
        '''
        def distance(i):
          '''
          i is 0,1,2 for x,y,z
          '''
          if signs[i] == None:
            # This will never be the minimum. Makes later code easier
            return None
          elif signs[i]:
            return abs(p[i] - (bounds[i] + self.box_size[i]))
          else:
            return abs(p[i] - bounds[i])

        # Find the shortest time distance (ie, distance/velocity)
        index = None
        for i in range(3):
          dist, vel = distance(i), abs(line[i])
          if dist is not None and vel != 0:
            if index is None:
              index = i
            else:
              min_time = distance(index) / abs(line[index])
              index = i if dist / vel < min_time else index

        return index, distance(index)

      # In crawl, we obtain the coordinate closests to an edge (index), and its 
      # absolute distance from that edge
      index, distance = closest(point)

      # The change is the line scaled so that the right coordinate changes the 
      # amount necessary to cross into the next box. This means that we scale it
      # and also add a teeny bit so as to push it into the right box. This is 
      # the scaled version, exactly the distance we need to move
      move = helpers.scale(distance / abs(line[index]), line)
      # Here we scale the line again by epsilon/2. This is our push
      push = helpers.scale(PROGRAM['epsilon'] / 2, line)
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
          # Movings positively, so set to True if our new_point has a larger 
          # positive coordinate
          # Moving negatively, so set to True if our new_point has a smaller 
          # positive coordinate
          passed = (temp[i] > coord2[i] + PROGRAM['epsilon'] / 2 if signs[i] 
            else temp[i] < coord2[i] - PROGRAM['epsilon'] / 2)

    return points

  def load_model(self,program):
    '''
    Loads the model from SapModel (model variable) into the structure. Simply
    mimicks constructing this model.
    '''
    frames = program.frame_objects
    points = program.point_objects

    # Get the names
    names = frames.get_names()

    # Cycle through names
    for name in names:
      # Get name of the endpoints for each beam, then the coordiantes of those 
      # points
      p1,p2 = frames.get_points(name)
      e1,e2 = points.get_cartesian(p1),points.get_cartesian(p2)
      # Add the beam to the structure
      if not self.add_beam(e1,e2,name):
        print("Could not add the beam {} at the points {}-{}. Maybe those \
          points are out of bounds?".format(name,str(e1),str(e2)))

    return 0

  def find_beam(self,beam):
    '''
    Cycles through the structure, looking for the beam specified by name
    '''
    for wall in self.model:
      for column in wall:
        for cell in column:
          if beam in cell:
            return cell[beam]

    return None

  def get_endpoints(self,beam_name,location,deflected=False):
    '''
    Returns the endpoints of the beam. It uses location to facilitate the 
    search. If not found, it looks for the beam the old fashion way. 
    '''
    beam = self.get_beam(beam_name,location)
    if beam is not None:
      endpoints = beam.deflected_endpoints if deflected else beam.endpoints
      return endpoints
    else:
      return None

  def get_beam(self,beam_name,location):
    '''
    Returns the beam object with the specified name. Uses location to quickly
    find the box that contains it. If it is not found in that box, None is 
    returned. This doesn't mean the beam doesn't exists, just that the location
    specified a box which does not contain the beam\
    '''
    box = self.get_box(location)

    for name,beam in box.items():
      if beam_name == name:
        return beam

    if self.find_beam(beam_name) is not None:
      return self.find_beam(beam_name)
    else:
      return None

  def get_box(self,point):
    '''
    Finds the box containing the specified point and returns a dictionary 
    containing the named and point coordinates of the objects for which any part
    is contained within the box
    '''
    xi, yi, zi = self.__get_indeces(point)
    num_x, num_y, num_z = self.num

    # Catch Errors 
    try:
      return (self.model[xi][yi][zi])
    except IndexError:
      print ("The coordinate, {}, is not in the structure and should never have\
        been. Please check the add function in structure.py".format(point))
      return None

  def get_boxes(self,location,radius=BEAM['length']):
    '''
    Returns all of the boxes that are within the sphere specified by location
    and radius
    '''
    def index_range(index):
      dim = self.box_size[index]
      num = math.ceil(radius/dim)
      ret = num / 2 if index != 2 else num
      return math.ceil(ret)

    boxes = []
    x,y,z = int(index_range(0)),int(index_range(1)),int(index_range(2))
    xi,yi,zi = self.__get_indeces(location)
    for i in range(-x,x+1):
      for j in range(-y,y+1):
        for k in range(0,z+1):
          ix,iy,iz = xi+i,yi+j,zi+k
          try:
            boxes.append(self.model[ix][iy][iz])
          except IndexError:
            pass

    return boxes

  def add_beam(self,p1,p1_name,p2,p2_name,name):
    ''' 
    Function to add the name and endpoint combination of a beam
    to all of the boxes that contain it. Returns the number of boxes (which 
    should be at least 1)
    '''
    def addbeam(beam,p):
      '''
      Function to add an arbitrary beam to its respective box. Returns number of
      boxes changed. Also takes care of finding intersecting beams to the added
      beam and adding the joints to both beams. Uses the point p (which should 
      be on the beam), to calculate the box it should be added to
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
            sys.exit("Could not add joint to {} at {}".format(beam.name,
              str(point)))
          if not box[key].addjoint(point, beam):
            sys.exit("Could not add joint to {} at {}".format(box[key].name,
              str(point)))

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
        raise OutofBox ("The coordinate {}, is not in the structure. Something\
          went wront in addpoint()".format(p))

    # Create the beam
    new_beam = Beam(name,(p1,p2),(p1_name,p2_name))

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

    # If showing the visualization, add the cylinder to the structure
    if self.visualization:
      temp = visual.cylinder(pos=p1,axis=helpers.make_vector(p1,p2),
        radius=MATERIAL['outside_diameter'])
      temp.color = (0,1,1)

    # Safe visualization data
    self.visualization_data += "{}:{}-{}<>".format(str(new_beam.name),str(
      helpers.round_tuple(p1,3)),str(helpers.round_tuple(p2,3)))

    # Add a beam to the structure count and increase height if necessary
    self.tubes += 1
    self.height = max(p1[2],p2[2],self.height)

    return total_boxes

  def remove_beam(self,name,point=None):
    '''
    This function removes the beam element referred to by the specified name 
    from all the boxes that contained it. If a point contained by the element is
    given, then it makes the removal faster. Otherwise, the entire structure is
    searched for the name, and all references removed. Returns true if the 
    removal is successfull, false otherwise (ie, cannot find the element) 
    Furthermore, it removes itself from all of the beams with which it 
    previously intersected.
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
        print ("The beam was not found with the specified point. Attempting to\
          remove it anyway.")
        return remove_beam(name)

  def available(self,e1,e2):
    '''
    Returns whether or not the location between e1 and e2 is available for 
    positioning a beam. 
    To be available, two requirements exist:
      1. The endpoints lie within the structure
      2. No beam exists in that location.
      3. No beam exists for part of that location (ie, no overlap)
    '''
    def box_available(box):
      for name, beam in box.items():
        e3,e4 = beam.endpoints
        # If all four points lie on the same line and one of the two points we 
        # are checking lies within the beam's endpoints
        # then the location for our points is not available
        if (helpers.collinear(e1,e2,e3) and helpers.collinear(e1,e2,e4) and 
          (helpers.between_points(e3,e4,e1,False) or 
            helpers.between_points(e3,e4,e2,False))):
          return False
      return True

    # Requirement 1
    if not self.__feasable_point(e1) or not self.__feasable_point(e2):
      return False
    # Requirement 2
    elif self.exists(e1,e2):
      return False
    # Check requirement 3
    else:
      # Get the box for e1 and check it
      xi1, yi1, zi1 = self.__get_indeces(e1)
      if not box_available(self.get_box(e1)):
        return False

      xi2, yi2, zi2 = self.__get_indeces(e2)
      # If the next box is not the same box, check it
      if xi1 != xi2 or yi1 != yi2 or zi1 != zi2:
        if not box_available(self.get_box(e2)):
          return False

      return True

  def exists(self,e1,e2):
    '''
    Returns whether or not the beam defined by the endpoints e1 -> e2 exists
    '''
    # Let's get the box
    xi, yi, zi = self.__get_indeces(e1)

    # Cycle through the box and compare endpoints
    for name in self.model[xi][yi][zi]:
      beam = self.model[xi][yi][zi][name]
      if ((helpers.compare_tuple(beam.endpoints.i,e1,0.5) and helpers.compare_tuple(
        beam.endpoints.j,e2,0.5)) or (helpers.compare_tuple(beam.endpoints.i,e2,0.5) and
        helpers.compare_tuple(beam.endpoints.j,e1,0.5))):
        return True
    return False

  def get_information(self):
    '''
    Returns the name of each beam along with it's endpoints
    '''
    beams = {}
    for wall in self.model:
      for column in wall:
        for box in column:
          for name, beam in box.items():
            if name not in beams:
              beams[name] = beam.current_state()

    return beams

  def reset(self):
    # Reset the storage
    self.model =  ([[[{} for k in range(self.num[0])] for j in 
      range(self.num[1])] for i in range(self.num[2])])

    # Reset the tubes
    self.tubes = 0

  def failed(self,program):
    '''
    Checks the entire SAP2000 structure for any possible structural errors.
    '''
    def get_max_moment(beam):
      '''
      Returns the largest moment along a beam
      '''
      results = program.model.Results.FrameForce(beam.name,0)
      if results[0] != 0:
        #pdb.set_trace()
        return 0

      def total(index):
        '''
        Calculates the total moment for a specified index
        '''
        m22 = results[13][index]
        m33 = results[14][index]
        return math.sqrt(m22**2 + m33**2)

      # Calculate individual moments, and from them choose maximum
      moments = [total(i) for i in range(results[1])]
      max_val = max(moments)

      # Store max value along with beam name 
      if (beam.name,max_val) not in self.structure_data[-1]:
        self.structure_data[-1].append((beam.name,max_val))

      # Calculate gradiant color and store
      ratio = round(max_val/PROGRAM['structure_check'],2)
      color = (ratio,round(max(1-ratio,0),2),0)
      try:
        self.color_data += "{}:{}<>".format(beam.name,str(color)) 
      except MemoryError:
        pass

      # Return maximum value
      return max_val

    def update_deflection(beam):
      '''
      Updates the deflection of the specified beam
      '''
      # Assert that the local axes are still the default
      results = program.model.FrameObj.GetLocalAxes(beam.name)
      if not (results[0] == 0 and results[1] == 0 and not results[2]):
        pdb.set_trace()
        return (0,0,0)

      # Obtain joint axes - these are, by default, the global axes
      axis_1,axis_2,axis_3 = beam.global_joint_axes()

      # Placed here for access to local axes
      def get_deflection(joint_name):
        '''
        Returns the correct displacement in absolute coordinates for the named
        joint
        '''
        # Get displacements
        results = program.model.Results.JointDisplAbs(joint_name,0)
        if results[0] != 0:
          #pdb.set_trace()
          return (0,0,0)
        u1,u2,u3 = results[7][0], results[8][0], results[9][0]

        # Return the total deflection based on the local axes
        return helpers.sum_vectors(helpers.scale(u1,axis_1),helpers.sum_vectors(
          helpers.scale(u2,axis_2),helpers.scale(u3,axis_3)))

      return beam.update_deflection(get_deflection(beam.endpoint_names.i),
        get_deflection(beam.endpoint_names.j))

    bool_data = False
    seen = []
    data = ''
    for wall in self.model:
      for column in wall:
        for cell in column:
          for name,beam in cell.items():
            # Only if this is the first time we are collecting data 
            if name not in seen:
              moment = get_max_moment(beam)
              if moment > PROGRAM['structure_check']:
                data += "Beam {} is structurally unstable with moment {}.\n".format(
                  name,str(moment))
                bool_data = True

              # Update deflection of beams :)
              if update_deflection(beam) and VISUALIZATION['deflection']:
                # Add the deflection data for the beam if it's changed significantly
                # since last time we updated it
                try:
                  self.visualization_data += "{}:{}-{}<>".format(str(name),str(
                    helpers.round_tuple(beam.deflected_endpoints.i,3)),str(
                    helpers.round_tuple(beam.deflected_endpoints.j,3)))
                except MemoryError:
                  pdb.set_trace()

                # Update the previous endpoints
                beam.previous_write_endpoints = beam.deflected_endpoints

              seen.append(name)

    if not bool_data:
      return bool_data
    else:
      return data
