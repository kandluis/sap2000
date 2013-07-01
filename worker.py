from robots import Movable
import helpers, construction, variables

class Worker(Movable):
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)
    # The number of beams the robot is carrying
    self.num_beams = variables.beam_capacity

    # Whether we should move or upwards
    self.upwards = False

    # Whether or not we should start construction
    self.start_construction = False

    # The direction in which we should move
    self.next_direction_info = None

    # Set the right weight
    self.weight = variables.robot_load + variables.beam_load * variables.beam_capacity

    # Stores variables for construction algorithm (this is the robots memory)
    self.memory = {}

    # Starting defaults
    self.memory['built'] = False

  def __pickup_beams(self,num = variables.beam_capacity):
    self.num_beams = self.num_beams + num
    self.weight = self.weight + variables.beam_load * num

  def __discard_beams(self,num = 1):
    self.num_beams = self.num_beams - num
    self.weight = self.weight - variables.beam_load * num

  # Model needs to have been analyzed before calling THIS function
  def decide(self):
    '''
    This functions decides what is going to be done next based on the analysis results of the program.
    Therefore, this function should be the one that decides whether to construct or move, based on the local conditions
    and then stores that information in the robot. The robot will then act based on that information
    once the model has been unlocked. 
    '''
    # If we decide to construct, then we store that fact in a bool so action knows to wiggle the beam
    if self.construct():
      self.start_construction = True

    # Otherwise, if we're not on a beam, then we will wander on the ground
    elif self.beam == None:
      self.next_direction_info = None

    # Otherwise, we are not on the ground and we decided not to build, so pick a direction and store that
    else:
      self.next_direction_info = self.get_direction()

  # Model needs to be unlocked before running this function! 
  def do_action(self):
    '''
    Overwriting the do_action functionality in order to have the robot move up or downward
    (depending on whether he is carrying a beam or not), and making sure that he gets a chance
    to build part of the structure if the situation is suitable. This is also to store the decion 
    made based on the analysis results, so that THEN the model can be unlocked and changed.
    '''
    # Check to see if the robot decided to construct based on analysys results
    if self.start_construction:
      self.build()
      self.start_construction = False

    # Otherwise, we're on a beam but decided not to build, so get direction we decided to move in,
    # and move.
    elif self.beam != None:
      assert self.next_direction_info != None
      self.move(self.next_direction_info['direction'], self.next_direction_info['beam'])
      self.next_direction_info = None

    # We're still on the ground, so wander
    else:
      self.wander()

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. This means that if the robot is carrying a beam,
    it wants to move upwards. If it is not, it wants to move downwards. So basically the direction
    is picked by filtering by the z-component
    '''
    def filter_dict(dirs, new_dirs, comp_f):
      '''
      Filters a dictinary, taking out all directions not in the correct z-direction
      '''
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
      directions = filter_dict(info['directions'], directions, (lambda z : z > 0))
    # No more beams, so move downwards
    else:
      directions = filter_dict(info['directions'], directions, (lambda z : z < 0))

    from random import choice

    # This will only occur if no direction changes our vertical height. If this is the case, get directions as before
    if directions == {} and not self.at_top:
      beam_name = choice(list(info['directions'].keys()))
      direction = choice(info['directions'][beam_name])
      self.at_top = True

    # Otherwise we do have a set of directions taking us in the right place, so randomly pick any of them
    # We will change this later based on the analysis results from the program.
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
      Otherwise, if it has beams for construction, it moves toward the base specified construction
      site. If it finds another beam nearby, it has a tendency to climb that beam instead.
    '''
    def at_home():
      return helpers.within(construction.home, construction.home_size, self.location)

    # Check to see if robot is at home location and has no beams
    if at_home() and self.num_beams == 0 :
      self.__pickup_beams()

    # Check to see if robot should build based on steps taken
    # This has been removed
    '''
    if self.steps_to_construct == 0:
      self.build()
    '''

    # Find nearby beams to climb on
    result = self.ground()
    if result == None:
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.location,helpers.scale(self.step, helpers.make_unit(direction)))
      self.change_location_local(new_location)
    else:
      dist, close_beam, direction = result['distance'], result['beam'], result['direction']

      # If the beam is within steping distance, just jump on it
      if self.num_beams > 0 and dist <= self.step:
        # Set the ground direction to None (so we walk randomly if we do get off the beam again)
        self.ground_direction = None

        # Then move on the beam
        self.move(direction, close_beam)

      # If we can "detect" a beam, change the ground direction to approach it
      elif self.num_beams > 0 and dist <= variables.local_radius:
        self.ground_direction = direction
        new_location = helpers.sum_vectors(self.location, helpers.scale(self.step, helpers.make_unit(direction)))
        self.change_location_local(new_location)
      else:
        direction = self.get_ground_direction()
        new_location = helpers.sum_vectors(self.location,helpers.scale(self.step, helpers.make_unit(direction)))
        self.change_location_local(new_location)

  def addbeam(self,p1,p2):
    '''
    Adds the beam to the SAP program and to the Python Structure. Might have to add joints 
    for the intersections here in the future too. Removes the beam from the robot.
    '''
    def addpoint(p): 
      '''
      Adds a point object to our model. The object is retrained in all to rotational
      motion only. Returns the name of the added point.
      '''
      # Add to SAP Program
      name = self.program.point_objects.addcartesian(p)
      # Check Coordinates
      if p[2] == 0:
        DOF = (True,True,True,False,False,False)
        if self.program.point_objects.restraint(name,DOF):
          return name
        else:
          print("Something went wrong adding ground point {}.".format(str(p)))
      else:
        return name

    # Add points to SAP Program
    p1_name, p2_name = addpoint(p1), addpoint(p2)
    name = self.program.frame_objects.add(p1_name,p2_name,propName=variables.frame_property_name)

    # Get rid of one beam
    self.__discard_beams()

    # Successfully added to at least one box
    if self.structure.add_beam(p1,p2,name) > 0:
      box = self.structure.get_box(self.location)
      try:
        beam = box[name]
      except IndexError:
        print("Failed in addbeam. Adding beam {} at points {} and {} didn't work.".format(name,str(p1),str(p2)))
        return False
      # Cycle through the joints and add the necessary points
      for coord in beam.joints:
        if coord != p1 and coord != p2:
          added = addpoint(coord)
      return True
    else:
      return False

  def build(self):
    '''
    This functions sets down a beam. This means it "wiggles" it around in the air until
    it finds a connection (programatically, it just finds the connection which makes the smallest
    angle). Returns false if something went wrong, true otherwise.
    '''
    # This is the i-end of the beam being placed. We pivot about this
    pivot = self.location

    # This is the j-end of the beam (if directly vertical)
    vertical_point = helpers.sum_vectors(self.location,(0,0,variables.beam_length))

    # We place it here in order to have access to the pivot and to the vertical point
    def add_ratios(box,dictionary):
      '''
      Returns the 'verticality' that the beams in the box allow according to distance.
      It also calculates the ratio according to the intersection points of the beam
      with the sphere. 
      '''
      for name in box:
        # Ignore the beam you're on.
        if self.beam.name != name:
          beam = box[name]
          # Get the closest points between the vertical and the beam
          points = helpers.closest_points(beam.endpoints,(pivot,vertical_point))
          if points != None:
            # Endpoints
            e1,e2 = points
            # Let's do a sanity check. The shortest distance should have no change in z
            assert e1[2] == e2[2]
            # If we can actually reach the second point from vertical
            if helpers.distance(pivot,e2) <= variables.beam_length:
              # Distance between the two endpoints
              dist = helpers.distance(e1,e2)
              # Change in z from vertical to one of the two poitns (we already asserted their z value to be equal)
              delta_z = abs(e1[2] - vertical_point[2])
              ratio = dist / delta_z
              # Check to see if in the dictionary. If it is, associate point with ration
              if e2 in dictionary:
                assert(dictionary[e2] == ratio)
              else:
                dictionary[e2] = ratio

          # Get the points at which the beam intersects the sphere created by the vertical beam      
          sphere_points = helpers.sphere_intersection(beam.endpoints,pivot,variables.beam_length)
          if sphere_points != None:
            # Cycle through intersection points (really, should be two, though it is possible for it to be one, in
            # which case, we would have already taken care of this). Either way, we just cycle
            for point in sphere_points:
              # The point is higher above. This way the robot only ever builds up
              if point[2] >= pivot[2]:
                projection = helpers.correct(pivot,vertical_point,point)
                # Sanity check
                assert(projection[2] == point[2])

                dist = helpers.distance(projection,point)
                delta_z = abs(point[2] - vertical_point[2])
                ratio = dist / delta_z
                if point in dictionary:
                  assert(dictionary[point] == ratio)
                else:
                  dictionary[point] = ratio

      return dictionary

    # get all beams nearby (ie, all the beams in the current box and possible those further above)
    local_box = self.structure.get_box(self.location)
    top_box = self.structure.get_box(vertical_point)
    ratios = {}

    # Ratios contains the ratio dist / delta_z where dist is the shortest distance from the vertical beam
    # segment to a beam nearby and delta_z is the z-component change from the pivot point to the intersection point
    # Here, we add to ratios those that arise from the intersection points of the beams with the sphere.
    # The dictionary is indexed by the point, and each point is associated with one ratio
    ratios = add_ratios(local_box,add_ratios(top_box,ratios))

    # No ratios found, so just build vertically
    default_endpoint = helpers.sum_vectors(pivot,helpers.scale(variables.beam_length,helpers.make_unit(construction.beam['vertical_dir_set'])))
    if ratios == {}:
      return self.addbeam(pivot,default_endpoint)

    import math
    point = min(ratios, key=ratios.get)

    # If the smallest ratio is larger than what we've specified as the limit, then build vertically
    if ratios[point] > math.tan(math.radians(construction.beam['angle_constraint'])):
      return self.addbeam(pivot,default_endpoint)

    # Calculate the actual endpoint of the beam (now that we now direction vector)
    unit_direction = helpers.make_unit(helpers.make_vector(pivot,point))
    endpoint = helpers.sum_vectors(pivot,helpers.scale(variables.beam_length,unit_direction))

    # Construct the beammm! :))))
    return self.addbeam(pivot,endpoint)

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build (in which case)
    It returns the two points that should be connected, or we should continue moving 
    (in which case, it returns None)
    ''' 
    location = self.get_location()
    if (self.at_top or helpers.distance(location,construction.construction_location) <= construction.construction_radius) and not self.memory['built'] and self.num_beams > 0:
      self.at_top = False
       
      return True
    else:
      return False