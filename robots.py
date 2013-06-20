from sap2000 import variables
from sap2000.constants import EOBJECT_TYPES
import helpers

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
    self.beam = {}
    self.num_beams = variables.beam_capacity
    self.weight = variables.robot_load

  def __addload(beam,location,value):
    '''
    Adds a load of the specified value to the named beam at the specific location
    '''
    distance = helpers.distance(self.__location,location)
    self.__model.FrameObj.SetLoadPoint(beam['beam'],variables.robot_load_case, myType=1, dir=10, dist=distance, val=value, relDist=False)

  def __change_location_local(self,new_location, first_beam = {}):
    '''
    Moves the robot about locally (ie, without worrying about the structure, except 
    for when it moves onto the first beam)
    '''
    # When we move onto our first beam, add the load
    if first_beam != {}:
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
      data = self.__model.FrameObj.GetLoadPoint(self.beam['beam'])
      assert data[0] == 0 # Making sure everything went okay

      # Find location of load
      i, j = self.beam['endpoints']
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
          self.__model.FrameObj.SetLoadPoint(self.beam['beam'], variables.robot_load_case, myType=1, dir=10, dist=data[7][i], val=data[9][i])

    # Move the load off the current location and to the new one (if still on beam), then change the locations
    removeload(self.__location)

    # Check to see if we will be moving off a beam and onto the ground
    if new_location[2] == 0 and random.randint(0,1) == 1:
      new_beam = {}

    # Don't add the load if there is no beam
    if new_beam != {}:
      self.__addload(new_beam, new_location, self.weight)

    self.__location = new_location
    self.beam = new_beam

  def __get_walkable(self,beams):
    '''
    Returns all of the beams in beams which intersect the robots location
    '''
    crawlable = {}
    for beam, (e1,e2) in beams:
      if helpers.on_line(e1,e2,self.__location):
        crawlable[beam] = (e1,e2)

    return crawlable

  def get_location(self):
    '''
    Provides easy access to the location
    '''
    return self.__location

  def ground(self):
    '''
    This function finds the nearest beam to the robot that is connected 
    to the xy-place (ground). It returns that beam and its distance from the robot.
    '''
    box = self.__structure.get_box(self.__location)
    grounded = {}
    for beam, (e1,e2) in box:
      # beam is lying on the ground (THIS IS NOT FUNCTIONAL)
      if e1[2] == 0 and e2[0] == 0:
        grounded[beam] = helpers.distance_to_line(e1,e2,self.__location)
        assert 1 == 2
      # Only one point is on the ground
      else:
        if e1[2] == 0:
          grounded[beam] = helpers.distance(e1, self.__location)
        elif e2[2] == 0:
          grounded[beam] = helpers.distances(e2, self.__location)

    # get name of beam at the minimum distance
    if grounded == {}:
      return None

    name = min(grounded, key=grounded.get)

    return grounded[name], {  'beam'  : name,
                              'endpoints' : box[name]}

  def wander(self):
    '''
    When a robot is not on a structure, it wanders around randomly. The wandering is
    restricted to the 1st octant in global coordinates. If the robot is near enough a beam
    to be on it in the next time step, it jumps on the beam. The robots have a tendency
    to scale the structure, per se, but are restricted to their immediate surroundings.
    '''
    import random

    def random_direction():
      ''' 
      Returns direction which will move the robot the right number of steps and keep it
      inside the first octant(and within the bounds of the box)
      '''
      # obtain a random direction
      direction = (random.uniform(-1 * self.__step, self.__step), random.uniform(-1 * self.__step, self.__step), 0)

      # The they can't all be zero!
      if helpers.length(direction) == 0:
        return random_direction()
      else:
        direction = helpers.scale(self.__step,helpers.make_unit(direction))
        predicted_location = helpers.sum_vectors(direction, self.__location)
        if helpers.check_location(predicted_location):
          return direction
        else:
          return random_direction()

    # Check to see if robot is on a beam. If so, pick between moving on it or off it.
    result = self.ground()
    if result == None:
      direction = random_direction()
      self.__change_location_local(direction)
    else:
      dist, close_beam = result
      if dist < self.__step:
        rand = random.randint(0,1)
        # Move randomly
        if rand == 0:
          direction = random_direction()
          self.__change_location_local(direction)
        # Move onto the beam
        else:
          if dist == 0:
            self.beam = close_beam
          else:
            e1, e2 = close_beam['endpoints']
            if e1[2] == 0:
              self.move(helpers.make_vector(self.__location,e1), close_beam)
            else:
              self.move(helpers.make_vector(self.__location,e2), close_beam)


  def do_action(self):
    '''
    In movable, simply moves the robot to another location.
    '''
    # We are not on a beam, so wander about aimlessly
    if self.beam == {}:
      beam = self.wander()

    else:
      move_info = self.get_direction()
      self.move(move_info['direction'], { 'beam'  : move_info['beam'],
                                          'endpoints' : move_info['endpoints']})

  def move(self, direction, beam):
    '''
    Moves the robot in direction passed in and onto the beam specified
    '''
    length = helpers.length(direction)

    # The direction is smaller than the usual step, so move exactly by direction
    if length < self.__step:
      new_location = helpers.sum_vectors(self.__location, direction)
      self.__change_location(new_location, beam)

    # The direction is larger than the usual step, so move only the usual step in the specified direction
    else:
      movement = helpers.scale(self.__step, helpers.make_unit(direction))
      new_location = helper.sum_vectors(self.__location, movement)
      self.__change_location(new_location, beam)

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
    (e1, e2) = self.beam['endpoints']
    if not (helpers.on_line (e1,e2,self.__location)):
      self.__change_location(helpers.correct (e1,e2,self.__location), self.beam)

    # Obtain all local objects
    box = self.__structure.get_box(self.__location)

    # Find beams in the box which intersect the robot's location (ie, where can he walk?)
    crawlable = self.__get_walkable(box)

    directions_info = []
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
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)
    self.beams = variables.beam_capacity

  def move(self):
    '''
    Overwrite the move functionality of Movable to provide the chance to build in a timestep
    instead of moving to another space.
    '''
    if contruct():
      self.build()
    else:
      super(Worker,self).move()

  def build(self):
    pass

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build (in which case)
    It returns the two points that should be connected, or we should continue moving 
    (in which case, it returns None)
    ''' 
    return False