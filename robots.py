from sap2000.constants import EOBJECT_TYPES
import helpers, construction, variables

class Automaton:
  def __init__(self,program):
    self.__model = program.sap_com_object.SapModel
    self.__program = program

class Movable(Automaton):
  def __init__(self,structure,location,program):
    super(Movable, self).__init__(program)
    self.__structure = structure
    self.__step = variables.step_length
    self.__location = location
    self.at_top = False

    # The robots all initially move towards the centertower
    self.__ground_direction = helpers.make_vector(location,construction.construction_location)

    self.beam = None
    self.num_beams = variables.beam_capacity
    self.weight = variables.robot_load

  def __addload(beam,location,value):
    '''
    Adds a load of the specified value to the named beam at the specific location
    '''
    distance = helpers.distance(self.__location,location)
    ret = self.__model.FrameObj.SetLoadPoint(beam.name,variables.robot_load_case, myType=1, dir=10, dist=distance, val=value, relDist=False)
    assert ret == 0

  def __change_location_local(self,new_location, first_beam = None):
    '''
    Moves the robot about locally (ie, without worrying about the structure, except 
    for when it moves onto the first beam)
    '''
    # When we move onto our first beam, add the load
    if first_beam != None:
      self.beam = first_beam
      self.__addload(first_beam,new_location,self.weight)
    self.__location = new_location

    # Check that we are on the first octant
    assert self.__location[0] >= 0
    assert self.__location[1] >= 0

    # Verify that we are still on the xy plane
    assert self.__location[2] == 0

  def __change_location(self,new_location, new_beam):
    '''
    Function that takes care of changing the location of the robot on the
    SAP2000 program. Removes the current load from the previous location (ie,
    the previous beam), and shifts it to the new beam (specified by the new location)
    It also updates the current beam. If the robot moves off the structure, this also
    takes care of it.
    '''
    def removeload(location):
      '''
      Removes the load assigned to a specific location based on where the robot existed (assumes the robot is on a beam)
      '''
      # obtain current values.
      # values are encapsulated in a list as follows: ret, number_items, frame_names, loadpat_names, types, coordinates, directions, rel_dists, dists, loads
      data = self.__model.FrameObj.GetLoadPoint(self.beam.name)
      assert data[0] == 0 # Making sure everything went okay

      # Find location of load
      i, j = self.beam.endpoints
      curr_dist = helpers.distance(i,self.__location)

      # Loop through distances to find our load (the one in self.__location) and remove all reference to it
      # Additionally remove loads not related to our load patters
      indeces = []
      index = 0
      for ab_dist in data[8]:  # this provides acces to the absolute_distance from the i-point of the beam
        if helpers.compare(ab_dist,curr_dist) or variables.robot_load_case != data[3][index]:
          indeces.append(index)
        index += 1

      # add the loads we want back to the frame (automatically deletes all previous loads)
      for i in range(data[1]):
        if i not in indeces:
          ret = self.__model.FrameObj.SetLoadPoint(self.beam.name, variables.robot_load_case, myType=1, dir=10, dist=data[7][i], val=data[9][i])
          assert ret == 0

    # Move the load off the current location and to the new one (if still on beam), then change the locations
    removeload(self.__location)

    # Check to see if we will be moving off a beam and onto the ground (50% chance)
    if new_location[2] == 0 and random.randint(0,1) == 0:
      new_beam = None

    # Don't add the load if there is no beam
    if new_beam != None:
      self.__addload(new_beam, new_location, self.weight)

    self.__location = new_location
    self.beam = new_beam

  def __get_walkable_directions(self,box):
    '''
    Finds all of the beams in box which intersect the robots location or 
    to which the robot can walk onto. Returns delta x, delta y, and delta z
    of the change necessary to arrive at either the joint or to move along
    the current beam by current_step.
    '''
    # Get all joints within a time-step
    # Remember that beams DOES NOT include the current beam, only others
    crawlable = {}
    for joint in self.beam.joints:
      dist = helpers.distance(joint,self.__location)
      
      # If we are at the joint, return the possible directions of other beams
      if dist == 0:
        for beam in self.beam.joints[joint]:
      
          # The index error should never happen, but this provides nice error support
          try:
            e1, e2 = beam.endpoints
            crawlable[beam.name] = [helpers.make_vector(self.__location,e1), helpers.make_vector(self.__location,e2)]
          except IndexError:
            print ("The beam {} seems to have a joint with {}, but it is not in the box?".format(name,self.beam.name))
      
      # For all joints within the timestep, return a direction that is exactly the change from current to that point
      elif dist <= self.__step:
        if self.beam.name in crawlable:
          crawlable[self.beam.name].append(helpers.make_vector(self.__location,joint))
        else:
          crawlable[self.beam.name] = [helpers.make_vector(self.__location,joint)]

    # There are no joints nearby. This means we are either on a joint OR far from one. 
    # Therefore, we add the directions to the endpoint of our current beam to the current set of directions
    if self.beam.name not in crawlable:
      crawlable[self.beam.name] = [helpers.make_vector(self.__location,self.beam.endpoints.i), helpers.make_vector(self.__location,self.beam.endpoints.j)]

    return crawlable

  def get_location(self):
    '''
    Provides easy access to the location
    '''
    return self.__location

  def ground(self):
    '''
    This function finds the nearest beam to the robot that is connected 
    to the xy-place (ground). It returns that beam and its direction from the robot.
    '''
    box = self.__structure.get_box(self.__location)
    distances = {}
    vectors = {}
    for name in box:
      e1, e2 = box[name].endpoints # So e1 is in the form (x,y,z)
      # beam is lying on the ground (THIS IS NOT FUNCTIONAL)
      if e1[2] == 0 and e2[0] == 0:
        vectors[name] = helpers.vector_to_line(e1,e2,self.__location)
        distances[name] = helpers.length(vectors[name])
        assert 1 == 2
      # Only one point is on the ground
      elif e1[2] == 0:
        vectors[name] = helpers.make_vector(self.__location, e1)
        distances[name] = helpers.distance(e1, self.__location)
      elif e2[2] == 0:
        vectors[name] = helpers.make_vector(self.__location, e2)
        distances[name] = helpers.distances(e2, self.__location)

    # get name of beam at the minimum distance if one exists
    if distances == {}:
      return None

    # This retruns the key (ie, name) of the minimum value in distances
    name = min(distances, key=distances.get)

    return {  'beam'  : box[name],
              'distance' : distances[name],
              'direction' : vectors[name]}

  def get_ground_direction(self):
    ''' 
    In future classes, this function can be altered to return a preferred direction, 
    but currently it only returns a random feasable direction if no direction is assigned
    for the robot (self.__ground_direction)
    '''
    def random_direction():
      '''
      Returns a random, new location (direction)
      '''
      import random
      # obtain a random direction
      direction = (random.uniform(-1 * self.__step, self.__step), random.uniform(-1 * self.__step, self.__step), 0)

      # The they can't all be zero!
      if helpers.length(direction) == 0:
        return random_direction()
      else:
        step = helpers.scale(self.__step,helpers.make_unit(direction))
        predicted_location = helpers.sum_vectors(step, self.__location)
        if helpers.check_location(predicted_location):
          return direction
        else:
          return random_direction()

    # If we have a currently set direction, check to see if we will go out of bounds.
    if self.__ground_direction != None:
      step = helpers.scale(self.__step,helpers.make_unit(self.__ground_direction))
      predicted_location = helpers.sum_vectors(step, self.__location)
      # We are going out of bounds, so set the direction to none and call yourself again (to find a new location)
      if not helpers.check_location(predicted_location):
        self.__ground_direction = None
        return self.get_ground_direction()
      # Here, we return the right direction
      else:
        assert self.__ground_direction != None
        return self.__ground_direction
    # We don't have a direction, so pick a random one (it is checked when we pick it)
    else:
      self.__ground_direction = random_direction()
      return self.__ground_direction

  def wander(self):
    '''
    When a robot is not on a structure, it wanders around randomly. The wandering is
    restricted to the 1st octant in global coordinates. If the robot is near enough a beam
    to be on it in the next time step, it jumps on the beam. The robots have a tendency
    to scale the structure, per se, but are restricted to their immediate surroundings.
    '''
    # Check to see if robot is on a beam. If so, pick between moving on it or off it.
    result = self.ground()
    if result == None:
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.__location,helpers.scale(self.__step, helpers.make_unit(direction)))
      self.__change_location_local(new_location)
    else:
      dist, close_beam, direction = result['distance'], result['beam'], result['direction']
      if dist < self.__step:
        self.beam = close_beam
        self.move(direction,close_beam)
      else:
        direction = self.get_ground_direction()
        new_location = helpers.sum_vectors(self.__location,helpers.scale(self.__step, helpers.make_unit(direction)))
        self.__change_location_local(new_location)

  def move(self, direction, beam):
    '''
    Moves the robot in direction passed in and onto the beam specified
    '''
    length = helpers.length(direction)

    # The direction is smaller than the determined step, so move exactly by direction
    if length < self.__step:
      new_location = helpers.sum_vectors(self.__location, direction)
      self.__change_location(new_location, beam)

      # call do_action again since we still have some distance left, and update __step to reflect how much 
      # distance is left to cover
      self.__step = self.__step - length
      self.do_action()

    # The direction is larger than the usual step, so move only the step in the specified direction
    else:
      movement = helpers.scale(self.__step, helpers.make_unit(direction))
      new_location = helper.sum_vectors(self.__location, movement)
      self.__change_location(new_location, beam)

      # update the step back to the default
      self.__step = variables.step_length

  def get_directions_info(self):
    '''
    Returns a list of triplets with delta x, delta y, and delta z of the direction the robot can
    move in. These directions constitute the locations where beams currently exist. Additionally,
    it returns the "box of locality" to which the robot is restricted containing all of the beams
    nearby that the robot can detect (though, this should only be used for finding a connection,
    as the robot itself SHOULD only measure the stresses on its current beam)
    '''
    # Verify that the robot is on its beam and
    # correct if necessary. This is done so that floating-point arithmethic errors don't add up.
    (e1, e2) = self.beam.endpoints
    if not (helpers.on_line (e1,e2,self.__location)):
      self.__change_location(helpers.correct(e1,e2,self.__location), self.beam)

    # Obtain all local objects
    box = self.__structure.get_box(self.__location)

    # Find the beams and directions (ie, where can he walk?)
    directions_info = self.__get_walkable_directions(box)

    return {  'box'         : box,
              'directions'  : directions_info }

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. In this class, it simply picks a random
    direction (eventually, it will have a tendency to move upwards when carrying a beam
    and downwards when needing material for the structure). The direction 
    is also returned with it's corresponding beam in the following format (direction, beam).
    '''
    from random import choice

    info = self.get_directions_info()

    # Pick a random beam to walk on
    beam_name = choice(list(info['directions'].keys()))

    # From the beam, pick a random direction (really, 50/50)
    direction = choice(info['directions'][beam_name])

    return {  'beam'      : info['box'][beam_name],
              'direction' : direction }

  def on_structure(self):
    '''
    Returns whether or not the robot is on the structure
    '''
    return self.beam == None

  def do_action(self):
    '''
    In movable, simply moves the robot to another location.
    '''
    # We are not on a beam, so wander about aimlessly
    if self.beam == None:
      beam = self.wander()

    else:
      move_info = self.get_direction()
      self.move(move_info['direction'], move_info['beam'])