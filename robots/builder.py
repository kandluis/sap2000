from helpers import helpers
from robots.movable import Movable
import construction, math, operator, pdb, random, sys,variables

class Builder(Movable):
  def __init__(self,name,structure,location,program):
    super(Builder,self).__init__(name,structure,location,program)
    # The number of beams the robot is carrying
    self.num_beams = variables.beam_capacity

    # Whether or not we should start construction
    self.start_construction = False

    # Set the right weight
    self.weight = (variables.robot_load + variables.beam_load * 
      variables.beam_capacity)

    # Stores variables for construction algorithm (this is the robots memory)
    self.memory = {}

    # Climbing up or down
    self.memory['pos_z'] = None
    self.memory['dir_priority'] = [0]

    # Starting defaults
    self.memory['built'] = False

    # Keeps track of the direction we last moved in.
    self.memory['previous_direction'] = None

    # Stores information on beams that need repairing
    self.memory['broken'] = []

    # Stores whether or not we are constructing vertically or at an angle (for 
    # support)
    self.memory['construct_support'] = False

    # Stores direction of support beam (basically 2d)
    self.memory['repair_beam_direction'] = None

    self.repair_mode = False

  def at_joint(self):
    '''
    Returns whether or not the robot is at a joint
    '''
    if self.beam is not None:
      for joint in self.beam.joints:
        # If we're at a joint
        if helpers.compare(helpers.distance(self.location,joint),0):
          return True

    return False

  def current_state(self):
    state = super(Builder, self).current_state()
    memory = self.memory.copy()
    memory['broken'] = [(beam.name,beam.endpoints) for beam,direction in memory['broken']]
    state.update({  'num_beams'           : self.num_beams,
                    'start_construction'  : self.start_construction,
                    'next_direction_info' : self.next_direction_info,
                    'memory'              : memory,
                    'repair_mode'         : self.repair_mode})
    
    return state

  def climb_off(self,loc):
    if helpers.compare(loc[2],0) and (self.num_beams == 0 or self.repair_mode):
      direction = helpers.make_vector(self.location,construction.home)
      self.ground_direction = (direction if direction[2] == 0 else 
        self.ground_direction)

      # Reset the number of steps if we are repairing
      self.memory['new_beam_steps'] = (math.ceil((construction.beam['length'] 
        / 2) / variables.step_length) if self.repair_mode else 0)
      return True
    else:
      self.ground_direction = (None if not self.repair_mode else 
        self.ground_direction)
      return False

  def pickup_beams(self,num = variables.beam_capacity):
    '''
    Pickup beams by adding weight to the robot and by adding num to number 
    carried
    '''
    self.num_beams = self.num_beams + num
    self.weight = self.weight + variables.beam_load * num

    # Set the direction towards the structure
    self.ground_direction = helpers.make_vector(self.location,
      construction.construction_location)

  def discard_beams(self,num = 1):
    '''
    Get rid of the specified number of beams by decresing the weight and the 
    number carried
    '''
    self.num_beams = self.num_beams - num
    self.weight = self.weight - variables.beam_load * num

  def at_home(self):
    '''
    True if the robot is in the area designated as home (on the ground)
    '''
    return helpers.within(construction.home, construction.home_size,
      self.location)

  def at_site(self):
    '''
    True if the robot is in the area designated as the construction site 
    (on the ground)
    '''
    return helpers.within(construction.construction_location, 
      construction.construction_size, self.location)

  def pre_decision(self):
    '''
    Takes care of resetting appropriate values
    '''
    # We build almost never.
    self.start_construction = False
    self.step = variables.step_length

  # Model needs to have been analyzed before calling THIS function
  def decide(self):
    '''
    This functions decides what is going to be done next based on the analysis 
    results of the program. Therefore, this function should be the one that 
    decides whether to construct or move, based on the local conditions
    and then stores that information in the robot. The robot will then act 
    based on that information once the model has been unlocked. 
    '''
    self.pre_decision()

    # If we decide to construct, then we store that fact in a bool so action 
    # knows to wiggle the beam
    if self.construct():
      self.start_construction = True

    # Movement decisions
    else:
      super(Builder,self).decide()

  # Model needs to be unlocked before running this function! 
  def do_action(self):
    '''
    Overwriting the do_action functionality in order to have the robot move up 
    or downward (depending on whether he is carrying a beam or not), and making 
    sure that he gets a chance to build part of the structure if the situation 
    is suitable. This is also to store the decion made based on the analysis 
    results, so that THEN the model can be unlocked and changed.
    '''
    # Check to see if the robot decided to construct based on analysys results
    if self.start_construction:
      self.build()
      self.start_construction = False

    # Move around
    else:
      super(Builder,self).do_action()

  def filter_dict(self,dirs,new_dirs,comp_functions,priorities = []):
    '''
    Filters a dictinary of directions, taking out all directions not in the 
    correct directions based on the list of comp_functions (x,y,z).

    Edit: Now also filters on priority. If a direction has priority of 0, then
    it MUST be in that direction. The only way that it will ever return an empty
    dictionary is if none of the directions match the direction we want to move
    in for each coordinate with priority zero. Otherwise, we match as many low
    priorty numbers as possible. Same priorities must be matched at the same
    level.
    '''
    # Access the list of broken beam names
    broken = [beam.name for beam,direction in self.memory['broken']]

    # Access items
    for beam, vectors in dirs.items():
      # Access each directions
      for vector in vectors:
        coord_bool = True
        # Apply each function to the correct coordinates
        for function, coord in zip(comp_functions,vector):
          coord_bool = coord_bool and function(coord)

        # When repairing, we want to switch direction onto another beam but not
        # one that is broken
        if (coord_bool and not (self.repair_mode and self.at_joint() and 
          self.beam.name == beam and beam in broken)):
          if beam not in new_dirs:
            new_dirs[beam] = [vector]
          else:
            new_dirs[beam].append(vector)

    # Case is not matched, so obtain keys of max values and remove those
    # restraints if the value is not 0
    if new_dirs == {}:
      if priorities == []:
        # COPY the LIST
        priorities = list(self.memory['dir_priority'])
      
      max_val = max(priorities)
      max_indeces = [priorities.index(x) for x in priorities if x == max_val]
      # Set to -1 so we don't use them next time, and set comp_funs to True
      for index in max_indeces:
        priorities[index] = -1
        comp_functions[index] = lambda a : True

      if max_val <= 0:
        return new_dirs
      else:
        return self.filter_dict(dirs,new_dirs,comp_functions,priorities)

    else:
      return new_dirs

  def filter_directions(self,dirs):
    '''
    Filters the available directions and returns those that move us in the 
    desired direction. Should be overwritten to provide more robost 
    functionality.
    '''
    directions = {}
    base = [lambda x : True, lambda y : True]
    # Still have beams, so move upwards
    if self.num_beams > 0:
      directions = self.filter_dict(dirs, directions,
        (base.append(lambda z : z > 0)))
    # No more beams, so move downwards
    else:
      directions = self.filter_dict(dirs, directions,
        (base.append(lambda z : z < 0)))

    return directions

  def no_available_direction(self):
    '''
    This specifies what the robot should do if there are no directions available
    for travel. This basically means that no beams are appropriate to climb on.
    We pass here, because we just pick the directio randomly later on.
    '''
    pass

  def random_direction(self,directions):
    beam_name = random.choice(list(directions.keys()))
    direction = random.choice(directions[beam_name])

    self.memory['previous_direction'] = beam_name, direction

    return beam_name, direction

  def pick_direction(self,directions):
    '''
    Functions to pick a new direction once it is determined that we either have 
    no previous direction, we are at a joint, or the previous direction is 
    unacceptable)
    '''
    return self.random_direction(directions)

  def elect_direction(self,directions):
    '''
    Takes the filtered directions and elects the appropriate one. This function
    takes care of continuing in a specific direction whenever possible.
    '''
    def next_dict(item,dictionary):
      '''
      Returns whether or not the value (a direction vector) is found inside of 
      dictionary (ie, looks for parallel directions)
      '''
      key, value = item
      temp = {}
      for test_key,test_values in dictionary.items():
        # Keys are the same, vectors are parallel (point in same dir too)
        if key == test_key:
          for test_value in test_values:
            if (helpers.parallel(value,test_value) and 
              helpers.dot(value,test_value) > 0):
              if test_key in temp:
                temp[test_key].append(test_value)
              else:
                temp[test_key] = [test_value]
      
      # No values are parallel, so return None
      if temp == {}:
        return None

      # Pick a direction randomly from those that are parallel
      else:
        self.pick_direction(temp)

    # We are not at a joint and we have a previous direction
    if not self.at_joint() and self.memory['previous_direction'] is not None:

      # Pull a direction parallel to our current from the set of directions
      direction_info = next_dict(self.memory['previous_direction'],directions)

      if direction_info is not None:
        return direction_info

    # If we get to this point, either we are at a joint, we don't have a 
    # previous direction, or that previous direction is no longer acceptable
    return self.pick_direction(directions)

  def get_moment(self,name):
    '''
    Returns the moment for the beam specified by name at the point closest 
    to the robot itself
    '''
    # Format (ret[0], number_results[1], obj_names[2], i_end distances[3], 
    # elm_names[4], elm_dist[5], load_cases[6], step_types[7], step_nums[8],
    # Ps[9], V2s[10], V3s[11], Ts[12], M2s[13], M3s[14]
    results = self.model.Results.FrameForce(name,0)
    if results[0] != 0:
      pdb.set_trace()
      helpers.check(results[0],self,"getting frame forces",results=results,
        state=self.current_state())
      return 0

    # Find index of closest data_point
    close_index, i = 0, 0
    shortest_distance = None
    distances = results[3]
    for i_distance in distances:
      # Get beam endpoints to calculate global position of moment
      i_end,j_end = self.structure.get_endpoints(name,self.location)
      beam_direction = helpers.make_unit(helpers.make_vector(i_end,j_end))
      point = helpers.sum_vectors(i_end,helpers.scale(i_distance,
        beam_direction))
      distance = helpers.distance(self.location,point)

      # If closer than the current closes point, update information
      if shortest_distance is None or distance < shortest_distance:
        close_index = i
        shortest_distance = distance

      i += 1

    # Make sure index is indexiable
    assert close_index < results[1]

    # Now that we have the closest moment, calculate sqrt(m2^2+m3^2)
    m22 = results[13][close_index]
    m33 = results[14][close_index]
    total = math.sqrt(m22**2 + m33**2)

    return total


  def filter_feasable(self,dirs):
    '''
    Filters the set of dirs passed in to check that the beam can support a robot
    + beam load if the robot were to walk in the specified direction to the
    very tip of the beam.
    This function is only ever called if an analysis model exists.

    Additionally, this function stores information on the beams that need to be 
    repaired. This is stored in self.memory['broken'], which is originally set
    to none.
    '''
    # Sanity check
    assert self.model.GetModelIsLocked()

    results = {}
    # If at a joint, cycle through possible directions and check that the beams
    # meet the joint_limit. If they do, keep them. If not, discard them.
    if self.at_joint():
      for name, directions in dirs.items():
        moment = self.get_moment(name)
        # If the name is our beam, do a structural check instead of a joint check
        if ((self.beam.name == name and 
          moment < construction.beam['beam_limit']) or (moment < 
          construction.beam['joint_limit'])):
          results[name] = directions
        else:
          # Keep only the directions that take us down
          new_directions = ([direction for direction in directions if 
            helpers.compare(direction[2],0) or direction[2] < 0])
          if len(new_directions) > 0:
            results[name] = new_directions

          # Add beam to broken
          beam = self.structure.get_beam(name,self.location)
          if not any(beam in broken for broken in self.memory['broken']):
            self.memory['broken'].append((beam,moment))


    # Not at joint, so check own beam
    else:
      assert len(dirs) == 1
      moment = self.get_moment(self.beam.name)
      if moment < construction.beam['beam_limit']:
        results = dirs
      # Add the beam to the broken
      else:
        # Keep only the directions that take us down
        for name,directions in dirs.items():
          new_directions = ([direction for direction in directions if 
            helpers.compare(direction[2],0) or direction[2] < 0])
          if len(new_directions) > 0:
            results[name] = new_directions

        if not any(self.beam in broken for broken in self.memory['broken']):
          self.memory['broken'].append((self.beam,moment))

    return results

  def get_direction(self):
    ''' 
    Figures out which direction to move in. This means that if the robot is 
    carrying a beam, it wants to move upwards. If it is not, it wants to move 
    downwards. So basically the direction is picked by filtering by the 
    z-component
    '''
    # Get all the possible directions, as normal
    info = self.get_directions_info()

    # Filter out directions which are unfeasable
    if self.model.GetModelIsLocked():
      feasable_directions = self.filter_feasable(info['directions'])
    else:
      feasable_directions = info['directions']

    # Now filter on based where you want to go
    directions = self.filter_directions(feasable_directions)

    # This will only occur if no direction takes us where we want to go. If 
    # that's the case, then just a pick a random direction to go on and run the
    # routine for when no directions are available.
    if directions == {}:
      # No direction takes us exactly in the way we want to go, so check if we
      # might need to construct up or might want to repair
      self.no_available_direction()

      # Feasable is empty when our own beam is the one that doesn't support us
      if feasable_directions != {}:
        beam_name, direction = self.elect_direction(feasable_directions)
      # Refilter original directions (to travel down)
      else:
        beam_name,direction = self.elect_direction(self.filter_directions(
          info['directions']))

    # Otherwise we do have a set of directions taking us in the right place, so 
    # randomly pick any of them. We will change this later based on the analysis
    else:
      beam_name, direction = self.elect_direction(directions)

    return {  'beam'      : info['box'][beam_name],
              'direction' : direction }

  def wander(self):
    '''    
    When a robot is not on a structure, it wanders. The wandering in the working
    class works as follows. The robot moves around randomly with the following 
    restrictions:
      The robot moves towards the home location if it has no beams and 
        the home location is detected nearby.
      Otherwise, if it has beams for construction, it moves toward the base 
      specified construction site. If it finds another beam nearby, it has a 
      tendency to climb that beam instead.
    '''
    # Check to see if robot is at home location and has no beams
    if self.at_home() and self.num_beams == 0 :
      self.pickup_beams()

    # If we have no beams, set the ground direction to home (TEMP CODE)
    if self.num_beams == 0:
      self.ground_direction = helpers.make_vector(self.location,
        construction.home)

    # Find nearby beams to climb on
    result = self.ground()
    if result == None or self.repair_mode:
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.location,helpers.scale(self.step,
        helpers.make_unit(direction)))
      self.change_location_local(new_location)
    else:
      dist, close_beam, direction = (result['distance'], result['beam'],
        result['direction'])
      # If the beam is within steping distance, just jump on it
      if self.num_beams > 0 and dist <= self.step:
        # Set the ground direction to None (so we walk randomly if we do get off
        # the beam again)
        self.ground_direction = None

        # Then move on the beam
        self.move(direction, close_beam)

      # If we can "detect" a beam, change the ground direction to approach it
      elif self.num_beams > 0 and dist <= variables.local_radius:
        self.ground_direction = direction
        new_location = helpers.sum_vectors(self.location, helpers.scale(
          self.step,helpers.make_unit(direction)))
        self.change_location_local(new_location)
      else:
        direction = self.get_ground_direction()
        new_location = helpers.sum_vectors(self.location,helpers.scale(
          self.step,helpers.make_unit(direction)))
        self.change_location_local(new_location)

  def addbeam(self,p1,p2):
    '''
    Adds the beam to the SAP program and to the Python Structure. Might have to 
    add joints for the intersections here in the future too. Removes the beam 
    from the robot.
    '''
    def addpoint(p): 
      '''
      Adds a point object to our model. The object is retrained in all 
      directions if on the ground (including rotational and translational 
      motion. Returns the name of the added point.
      '''
      # Add to SAP Program
      name = self.program.point_objects.addcartesian(p)
      # Check Coordinates
      if helpers.compare(p[2], 0):
        DOF = (True,True,True,True,True,True)
        if self.program.point_objects.restraint(name,DOF):
          return name
        else:
          print("Something went wrong adding ground point {}.".format(str(p)))
      else:
        return name

    # Add points to SAP Program
    p1_name, p2_name = addpoint(p1), addpoint(p2)
    name = self.program.frame_objects.add(p1_name,p2_name,
      propName=variables.frame_property_name)

    # Get rid of one beam
    self.discard_beams()

    # Set to false if we were constructing support
    self.memory['construct_support'] = False

    # Successfully added to at least one box
    if self.structure.add_beam(p1,p2,name) > 0:
      box = self.structure.get_box(self.location)
      try:
        beam = box[name]
      except IndexError:
        print("Failed in addbeam. Adding beam {} at points {} and {} didn't \
          work.".format(name,str(p1),str(p2)))
        return False
      # Cycle through the joints and add the necessary points
      for coord in beam.joints:
        if coord != p1 and coord != p2:
          added = addpoint(coord)
      return True
    else:
      return False

  def get_ratio(self,string):
    '''
    Returns the appropriate ratios for support beam construction
    '''
    angle = construction.beam[string]
    angle = 90 - angle if self.beam is None else angle
    return helpers.ratio(angle)

  def get_ratios(self):
    mini,maxi = ((self.get_ratio('support_angle_min'), self.get_ratio(
      'support_angle_max'))
      if self.beam is not None else (self.get_ratio('support_angle_max'),
      self.get_ratio('support_angle_min')))

    return mini,maxi

  def support_beam_endpoint(self):
    '''
    Returns the endpoint for construction a support beam
    '''
    def non_zero_xydirection():
      '''
      Returns a non_zero list of random floats with zero z component
      '''
      tuple_list = ([random.uniform(-1,1),random.uniform(-1,1),
        random.uniform(-1,1)])
      if all(tuple_list):
        tuple_list[2] = 0
        return tuple(tuple_list)
      else:
        return non_zero_xydirection()

    # Sanity check
    assert self.memory['repair_beam_direction'] is not None

    # Add beam_directions plus vertical change based on angle ratio (tan)
    ratio = self.get_ratio('support_angle')
    vertical = helpers.scale(1/ratio,(0,0,1))

    # Check to see if direction is vertical
    if helpers.parallel(self.memory['repair_beam_direction'],vertical):
      xy_dir = non_zero_xydirection()
    else:
      xy_dir = self.memory['repair_beam_direction']
    xy_dir = helpers.make_unit(xy_dir)

    # Obtain construction direction
    direction = helpers.make_unit(helpers.sum_vectors(xy_dir,vertical))

    # Calculate endpoints
    endpoint = helpers.sum_vectors(self.location,helpers.scale(
      construction.beam['length'],direction))

    return endpoint

  def local_ratios(self,pivot,endpoint):
    '''
    Calculates the ratios of a beam if it were to intersect nearby beams. 
    Utilizes the line defined by pivot -> endpoint as the base for the ratios 
    '''
    # We place it here in order to have access to the pivot and to the vertical 
    # point
    if helpers.compare(pivot[0],816.1657) or helpers.compare(pivot[1],878.8637):
      pdb.set_trace()
      
    def add_ratios(box,dictionary):
      for name in box:
        # Ignore the beam you're on.
        if self.beam == None or self.beam.name != name:
          beam = box[name]
          # Get the closest points between the vertical and the beam
          points = helpers.closest_points(beam.endpoints,(pivot,endpoint))
          if points != None:
            # Endpoints (e1 is on a vertical beam, e2 is on the tilted one)
            e1,e2 = points
            # Let's do a sanity check. The shortest distance should have no 
            # change in z
            assert helpers.compare(e1[2],e2[2])
            # If we can actually reach the second point from vertical
            if helpers.distance(pivot,e2) <= variables.beam_length:
              # Distance between the two endpoints
              dist = helpers.distance(e1,e2)
              if dist != 0:
                # Change in z from vertical to one of the two poitns (we already
                # asserted their z value to be equal)
                delta_z = abs(e1[2] - pivot[2])
                ratio = dist / delta_z if delta_z != 0 else sys.float_info.max
                # Check to see if in the dictionary. If it is, associate point 
                # with ratio
                if e2 in dictionary:
                  assert helpers.compare(dictionary[e2],ratio)
                else:
                  dictionary[e2] = ratio

          # Get the points at which the beam intersects the sphere created by 
          # the vertical beam      
          sphere_points = helpers.sphere_intersection(beam.endpoints,pivot,
            variables.beam_length)
          if sphere_points != None:
            # Cycle through intersection points (really, should be two, though 
            # it is possible for it to be one, in
            # which case, we would have already taken care of this). Either way,
            # we just cycle
            for point in sphere_points:
              # The point is higher above.This way the robot only ever builds up
              if point[2] >= pivot[2]:
                projection = helpers.correct(pivot,endpoint,point)
                # Sanity check
                assert helpers.compare(projection[2],point[2])

                dist = helpers.distance(projection,point)
                delta_z = abs(point[2] - pivot[2])
                ratio = dist / delta_z
                if point in dictionary:
                  assert helpers.compare(dictionary[point],ratio)
                else:
                  dictionary[point] = ratio

      return dictionary

    # get all beams nearby (ie, all the beams in the current box and possible 
    # those further above)
    boxes = self.structure.get_boxes(self.location)
    '''
    Ratios contains the ratio dist / delta_z where dist is the shortest distance
    from the vertical beam segment to a beam nearby and delta_z is the 
    z-component change from the pivot point to the intersection point. Here, we 
    add to ratios those that arise from the intersection points of the beams 
    with the sphere. The dictionary is indexed by the point, and each point is 
    associated with one ratio
    '''
    ratios = {}
    for box in boxes:
      ratios = add_ratios(box,ratios)

    return sorted(ratios.items(), key = operator.itemgetter(1))

  def build(self):
    '''
    This functions sets down a beam. This means it "wiggles" it around in the 
    air until it finds a connection (programatically, it just finds the 
    connection which makes the smallest angle). Returns false if something went 
    wrong, true otherwise.
    '''
    def check(i,j):
      '''
      Checks the endpoints and returns two that don't already exist in the 
      structure. If they do already exist, then it returns two endpoints that 
      don't. It does this by changing the j-endpoint. This function also takes 
      into account making sure that the returned value is still within the 
      robot's tendency to build up. (ie, it does not return a beam which would 
      build below the limit angle_constraint)
      '''
      # There is already a beam here, so let's move our current beam slightly to
      # some side
      if not self.structure.available(i,j):
        limit = (math.tan(math.radians(construction.beam['angle_constraint'])) *
         construction.beam['length'] / 3)
        return check(i,(random.uniform(-1* limit, limit),random.uniform(
          -1 * limit,limit), j[2]))
      else:
        # Calculate the actual endpoint of the beam (now that we now direction 
        # vector)
        unit_direction = helpers.make_unit(helpers.make_vector(i,j))
        j = helpers.sum_vectors(i,helpers.scale(variables.beam_length,
          unit_direction))
        return i,j

    # Sanitiy check
    assert (self.num_beams > 0)

    # This is the i-end of the beam being placed. We pivot about this
    pivot = self.location

    # Default vertical endpoint (the ratios are measured from the line created 
    # by pivot -> vertical_endpoint)
    vertical_endpoint = helpers.sum_vectors(pivot,helpers.scale(
      variables.beam_length,
      helpers.make_unit(construction.beam['vertical_dir_set'])))

    # Get the ratios
    sorted_ratios = self.local_ratios(pivot,vertical_endpoint)

    # Find the most vertical position
    final_coord = self.find_nearby_beam_coord(sorted_ratios,pivot)

    # Obtain the default endpoints
    default_endpoint = self.get_default(final_coord,vertical_endpoint)
    i, j = check(pivot, default_endpoint)

    return self.addbeam(i,j)

  def find_nearby_beam_coord(self,sorted_ratios,pivot):
    '''
    Returns the coordinate of a nearby, reachable beam which results in the
    angle of construction with the most verticality
    '''
    # Limits
    constraining_ratio = helpers.ratio(construction.beam['angle_constraint'])
    min_support_ratio,max_support_ratio = self.get_ratios()

    # Cycle through the sorted ratios until we find the right coordinate to build
    for coord, ratio in sorted_ratios:

      # If building a support beam, we don't want it too vertical or horizontal
      if self.memory['construct_support'] and (ratio < min_support_ratio or
        ratio > max_support_ratio):
        pass

      # If the smallest ratio is larger than what we've specified as the limit, 
      # but larger than our tolerence, then build
      if ratio > constraining_ratio:
        return coord

      # The beam doesn't exist, so build it
      elif self.structure.available(pivot,coord):
        unit_direction = helpers.make_unit(helpers.make_vector(pivot,coord))
        coord = helpers.sum_vectors(pivot,helpers.scale(
          variables.beam_length,unit_direction))
        return coord

    return None

  def get_default(self,ratio_coord,vertical_coord):
    '''
    Returns the coordinate onto which the j-point of the beam to construct 
    should lie
    '''
    if self.memory['construct_support']:
      return self.support_beam_endpoint()
    elif ratio_coord is not None:
      return ratio_coord
    else:
      # Create disturbance
      disturbance = self.get_disturbance()
      
      # We add a bit of disturbance every onece in a while
      new_coord = vertical_coord if self.default_probability() else (
      helpers.sum_vectors(vertical_coord,disturbance))
      return new_coord

  def get_disturbance(self):
    '''
    Returns the disturbance level for adding a new beam at the tip (in this
    class, the disturbance is random at a level set in variables.random)
    '''
    change = variables.random
    return helpers.make_unit((random.uniform(-change,change),
      random.uniform(-change,change),0))

  def default_probability(self):
    '''
    Returns whether or not the disturbance should be applied to the current 
    contruction. Realistically, this should be a probabilistic function.

    True means that the disturbance is NOT applied
    False means that the disturbance is
    '''
    return (random.randint(0,4) == 1)

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build (in which case)
    ''' 
    if ((self.at_site()) and not self.memory['built'] and 
      self.num_beams > 0):
      self.memory['built'] = True
      self.memory['constructed'] += 1
      return True
    else:
      self.memory['built'] = False
      return False
