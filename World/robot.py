# Basic class for any automatic object that needs access to the SAP program
class Body(object):
  def __init__(self,name,program,location,program):

    '''''''''''''''''''''''''''''
    SAP 2000 API Access Variables
    '''''''''''''''''''''''''''''
    # Access to the SAP 2000 Program
    self.program = program

    # Accesss to the SapModel from SAP 2000
    self.model = program.sap_com_object.SapModel

    # Storage of the sphere model
    self.simulation_model = None

    '''''''''''''''''''''''''''''
    Local Information Variables and Python Structure
    '''''''''''''''''''''''''''''
    # Access to my Python structure
    self.structure = structure

    # Robot name
    self.name = name

    # Number of steps left in movement
    self.step = ROBOT['step_length']

    # The current location of the robot on the designed structure
    self.location = location

    # The beam on which the robot currently is
    self.beam = None

    # Set the right weight
    self.weight = ROBOT['load']

    # The number of beams the robot is carrying
    self.num_beams = 0

    '''''''''''''''''''''''''''''''''
    Construction variables for robot body/Memory Storage
    '''''''''''''''''''''''''''''''''
    self.memory = {}

    '''''''''''''''''''''''''''''''''
    Output Data Storage
    '''''''''''''''''''''''''''''''''
    # Contains Errors from SAP 2000
    self.error_data = ''
    self.repar_data = ''


'''
Decision Making?
'''
    # The robots all initially move towards the centertower
    self.ground_direction = helpers.make_vector(location,
      CONSTRUCTION['corner'])

    # The direction in which we should move
    self.next_direction_info = None


  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  State gathering functions (for information purposes).
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def myType(self):
    return self.my_type()

  def my_type(self):
    '''
    Returns the class name.
    '''
    return self.__class__.name

  def currentState(self):
    return current_state()

  def current_state(self):
    '''
    Returns the current state of the robot. This is used when we write the 
    information to the logs
    '''
    # None if on the ground
    beam = self.beam.name if self.beam is not None else self.beam

    # Round location to prevent decimal runoff in Excel
    location = [round(coord,2) for coord in self.location]
    deflected_location = [round(coord,2) for coord in self.get_true_location()]
    
    # Copy the memory so that it is not modified
    memory = self.memory.copy()

    state = { 'name'              : self.name,
              'step'              : self.step,
              'location'          : location,
              'deflected_location': deflected_location,
              'ground_direction'  : self.ground_direction,
              'beam'              : beam,
              'weight'            : self.weight,
              'next_direction'    : self.next_direction_info,
              'num_beams'         : self.num_beams,
              'memory'            : memory }

    return state

  def needData(self):
    return need_data()

  def need_data(self):
    '''
    Returns whether or not this particular robot needs the structure to be analyzed
    '''
    return self.beam is not None and self.memory['pos_z']

  def getGenuineLocation(self):
    return get_true_location()

  def get_true_location(self):
    '''
    Returns the location of the robot on the current beam, accounting for the
    deflections that the beam has undergone. Uses the design location and the 
    deflection data from SAP to calculate this location.
    '''
    # Not on the structure, no deflection, or not recording deflection
    if not self.on_structure() or self.beam.deflection is None or not VISUALIZATION['deflection']:
      return self.location

    else:
      # Get deflections
      i_def, j_def = self.beam.deflection.i, self.beam.deflection.j

      # Obtain weight of each scale based on location on beam
      i_weight = 1 - (helpers.distance(self.location,self.beam.endpoints.i) / 
        BEAM['length'])
      j_weight = 1 - i_weight

      # Sum the two vectors to obtain general deflection
      # This sort of addition works under the assumption that the beam ITSELF 
      # does not deflect significantly
      deflection = helpers.sum_vectors(helpers.scale(i_weight,i_def),helpers.scale(
        j_weight,j_def))

      # Return true location
      return helpers.sum_vectors(self.location,deflection)

  def getLocation(self):
    return get_location

  def get_location(self):
    '''
    Provides easy access to the location.
    '''
    return self.location

  def onStructure(self):
    return on_structure()

  def on_structure(self):
    '''
    Returns whether or not the robot is on the structure
    '''
    return self.beam is not None

  def at_home(self):
    '''
    True if the robot is in the area designated as home (on the ground)
    '''
    return helpers.within(HOME['center'], HOME['size'],
      self.location)

  def at_site(self):
    '''
    True if the robot is in the area designated as the construction site 
    (on the ground)
    '''
    return helpers.within(CONSTRUCTION['corner'], 
      CONSTRUCTION['size'], self.location)

  def atTop(self):
    return self.at_top()
  def at_top(self):
    '''
    Returns if we really are at the top
    '''
    def below(beams):
      '''
      Returns whether all of the beams are below us
      '''
      for beam in beams:
        for endpoint in beam.endpoints:

          # If the beam is not close to us and it is greater than our location
          if (not helpers.compare(helpers.distance(self.location,endpoint),0)
            and endpoint[2] > self.location[2]):
            return False

      return True

    if self.beam is not None:
      if (helpers.compare(helpers.distance(self.location,self.beam.endpoints.i),0)
        and self.beam.endpoints.i[2] > self.beam.endpoints.j[2]):
        close = self.beam.endpoints.i
      elif (helpers.compare(helpers.distance(self.location,self.beam.endpoints.j),0)
        and self.beam.endpoints.j[2] > self.beam.endpoints.i[2]):
        close = self.beam.endpoints.j
      else:
        close = None

      if close is not None:
        try:
          beams = self.beam.joints[self.beam.endpoints.i]
          return below(beams)
        except KeyError:
          return True

    return False

  def addToMemory(self,key,value):
    '''
    Adds into the robot memory the information specified by value accessible 
    throught the key
    '''
    self.memory.update({key : value})
    return True

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Mobility functions for the robot body.
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def changeLocation(self,new_location):
    pass

  def change_location_local(self,new_location, first_beam = None):
    '''
    Moves the robot about locally (ie, without worrying about the structure, 
    except for when it moves onto the first beam)
    '''
    # When we move onto our first beam, add the load
    if first_beam != None:
      self.addload(first_beam,new_location,self.weight)
    self.location = new_location

    # Check that we are on the first octant
    assert self.location[0] >= 0
    assert self.location[1] >= 0

    # Verify that we are still on the xy plane
    if helpers.compare(self.location[2], 0):
      loc = list(self.location)
      loc[2] = 0
      self.location = tuple(loc)

  def change_location_structure(self,new_location, new_beam):
    '''
    Function that takes care of changing the location of the robot on the
    SAP2000 program. Removes the current load from the previous location (ie,
    the previous beam), and shifts it to the new beam (specified by the new 
    location). It also updates the current beam. If the robot moves off the 
    structure, this also takes care of it.
    '''
    def removeload(location):
      '''
      Removes the load assigned to a specific location based on where the robot 
      existed (assumes the robot is on a beams
      '''
      # Sanity check
      assert not self.model.GetModelIsLocked()

      # obtain current values.
      # values are encapsulated in a list as follows: ret, number_items, 
      # frame_names, loadpat_names, types, coordinates, directions, rel_dists, 
      # dists, loads
      data = self.model.FrameObj.GetLoadPoint(self.beam.name)
     
      # Sanity check with data
      assert data[0] == 0 
      if data[1] == 0:
        helpers.check(1,self,"getting loads",beam=self.beam.name,
          return_data=data,state=self.current_state())
        return;

      # Find location of load
      i, j = self.beam.endpoints
      curr_dist = helpers.distance(i,self.location)

      # Loop through distances to find our load (the one in self.location) and 
      # remove all reference to it. Additionally remove loads not related to our
      # load pattern
      indeces = []
      index = 0
      for ab_dist in data[8]:  # this provides acces to the absolute_distance 
        if ((helpers.compare(ab_dist,curr_dist) and PROGRAM['robot_load_case'] == 
          data[3][index]) or data[3][index] != PROGRAM['robot_load_case']):
          indeces.append(index)
        index += 1

      # Delete the loads off the beam
      ret = self.model.FrameObj.DeleteLoadPoint(self.beam.name,
        PROGRAM['robot_load_case'])
      helpers.check(ret,self,"deleting loads",return_val=ret,
        beam=self.beam.name,distance=curr_dist,previous_loads=data,
        state=self.current_state())

      # add the loads we want back to the frame (automatically deletes all 
      # previous loads)
      for i in range(data[1]):
        if i not in indeces:
          ret = self.model.FrameObj.SetLoadPoint(self.beam.name, 
            data[3][i], data[4][i], data[6][i], data[7][i], data[9][i],"Global",
            True,False)
          helpers.check(ret,self,"adding back loads",return_val=ret,
            beam=self.beam.name,load_pat=data[3][i],type=data[4][i],
            direction=data[6][i],rel_dist=data[7][i],load_val=data[9][i],
            state=self.current_state())

    # Move the load off the current location and to the new one (if still on 
    # beam), then change the locations
    if self.beam is not None:
      removeload(self.location)

    # Check to see if we will be moving off a beam and onto the ground
    if self.climb_off(new_location):
      new_beam = None

    # Don't add the load if there is no beam
    if new_beam is not None:
      self.addload(new_beam, new_location, self.weight)
    else:
      self.beam = new_beam


    # Update local location
    self.location = new_location

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Query functions about the structure and the local environment. Restricted
  to what the robot knows. These are like the sensors
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def atJoint(self):
    return self.at_joint()

  def at_joint(self):
    '''
    Returns whether or not the robot is at a joint
    '''
    if self.on_structure():

      for joint in self.beam.joints:
        # If we're at a joint to another beam
        if helpers.compare(helpers.distance(self.location,joint),0):
          return True

    return False

  def getMoment(self,name):
    return self.get_moment

  def get_moment(self,name):
    '''
    Returns the moment for the beam specified by name at the point closest 
    to the robot itself
    '''
    m11,m22,m33 = self.get_moment_magnitudes(name)

    # Find magnitude
    total = math.sqrt(m22**2 + m33**2)

    return total
  def getMomentMagnitudes(self,name,pivot=None):
    return self.get_moment_magnitudes(name,pivot)

  def get_moment_magnitudes(self,name,pivot = None):
    '''
    Returns the moment magnitudes (m11,m22,m33) for the local axes u1,u2,u3 at
    the output station closest to the pivot. If there is no pivot, it returns
    the values from the output station closest to the robot's location.
    '''
    # So we can modify the pivot whenever we call the fuction
    pivot = self.location if pivot is None else pivot

    # Format (ret[0], number_results[1], obj_names[2], i_end distances[3], 
    # elm_names[4], elm_dist[5], load_cases[6], step_types[7], step_nums[8],
    # Ps[9], V2s[10], V3s[11], Ts[12], M2s[13], M3s[14]
    results = self.model.Results.FrameForce(name,0)
    if results[0] != 0:
      # pdb.set_trace()
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
      distance = helpers.distance(pivot,point)

      # If closer than the current closes point, update information
      if shortest_distance is None or distance < shortest_distance:
        close_index = i
        shortest_distance = distance

      i += 1

    # Make sure index is indexable
    assert close_index < results[1]

    # Now that we have the closest moment, calculate sqrt(m2^2+m3^2)
    m11 = results[12][close_index]
    m22 = results[13][close_index]
    m33 = results[14][close_index]

    return m11,m22,m33

  def getAvailableDirection(self):
    return self.get_direction_info()

  def get_directions_info(self):
    '''
    Returns a list of triplets with delta x, delta y, and delta z of the 
    direction the robot can move in. These directions constitute the locations 
    where beams currently exist. Additionally, it returns the "box of locality" 
    to which the robot is restricted containing all of the beams nearby that the
    robot can detect (though, this should only be used for finding a connection,
    as the robot itself SHOULD only measure the stresses on its current beam)
    '''
    # Run analysys before deciding to get the next direction
    if not self.model.GetModelIsLocked() and self.need_data():
      errors = helpers.run_analysis(self.model)
      if errors != '':
        # pdb.set_trace()
        pass

    # Verify that the robot is on its beam and correct if necessary. 
    # This is done so that floating-point arithmethic errors don't add up.
    (e1, e2) = self.beam.endpoints
    if not (helpers.on_line (e1,e2,self.location)):
      self.change_location(helpers.correct(e1,e2,self.location), self.beam)

    # Obtain all local objects
    box = self.structure.get_box(self.location)

    # Debugging
    if box == {}:
      # pdb.set_trace()
      pass

    # Find the beams and directions (ie, where can he walk?)
    directions_info = self.get_walkable_directions(box)

    return {  'box'         : box,
              'directions'  : directions_info }

  def get_walkable_directions(self,box):
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
      dist = helpers.distance(self.location,joint)
      
      # If we are at the joint, return the possible directions of other beams
      if helpers.compare(dist,0):
        for beam in self.beam.joints[joint]:
      
          # The index error should never happen, but this provides nice error 
          # support
          try:
            # Get endpoints of beam and find direction vector to those endpoints
            e1, e2 = beam.endpoints
            v1, v2 = helpers.make_vector(self.location,e1), helpers.make_vector(
              self.location,e2)

            # We don't want to include zero-vectors
            bool_v1,bool_v2 = (not helpers.compare(helpers.length(v1),0),
              not helpers.compare(helpers.length(v2),0))

            # Checking for zero_vectors
            if bool_v1 and bool_v2:
              crawlable[beam.name] = ([helpers.make_vector(self.location,e1), 
                helpers.make_vector(self.location,e2)])
            elif bool_v1:
              crawlable[beam.name] = [helpers.make_vector(self.location,e1)]
            elif bool_v2:
              crawlable[beam.name] = [helpers.make_vector(self.location,e2)]
            else:
              raise Exception("All distances from beam were zero-length.")

            # Include distances to nearby joints (on the beam moving out from our
            # current joint)
            for coord in beam.joints:
              # Direction vecotrs
              v = helpers.make_vector(self.location,coord)
              length = helpers.length(v)

              # If further than our step, or zero, pass
              if ((length < self.step or helpers.compare(length, self.step))
                and not helpers.compare(length,0)):
                try:
                  # Only add if it is not already accounted for
                  if v not in crawlable[beam.name]:
                    crawlable[beam.name].append(v)
                except IndexError:
                  raise Exception("Adding nearby joints failed because \
                    endpoints were ignored.")

          except IndexError:
            print ("The beam {} seems to have a joint with {}, but it is not in\
              the box?".format(name,self.beam.name))
      
      # For all joints within the timestep, return a direction that is exactly 
      # the change from current to that point.
      elif dist <= self.step:
        if self.beam.name in crawlable:
          crawlable[self.beam.name].append(helpers.make_vector(self.location,
            joint))
        else:
          crawlable[self.beam.name] = [helpers.make_vector(self.location,joint)]
      # The joint is too far, so no point in considering it as a walkable direction
      else:
        pass

    # The joints never include our own beam, so now add directions pertaining to
    # our own beam
    v1, v2 = (helpers.make_vector(self.location,self.beam.endpoints.i), 
      helpers.make_vector(self.location,self.beam.endpoints.j))

    # Check to make sure directions are non-zero
    b_v1 = not helpers.compare(helpers.length(v1),0)
    b_v2 = not helpers.compare(helpers.length(v2),0)

    # If we haven't already accounted for our beam
    if self.beam.name not in crawlable:
      # Add the non-zero directions
      if b_v1 and b_v2:
        crawlable[self.beam.name] = [v1,v2]
      elif b_v1:
        crawlable[self.beam.name] = [v1]
      elif b_v2:
        crawlable[self.beam.name] = [v2]

    # Add directions that might not have been entered by joints
    else:
      bool_v1, bool_v2 = True, True
      for direct in crawlable[self.beam.name]:
        # Don't add directions which are basically the same.
        if helpers.parallel(direct,v1) and helpers.dot(direct,v1) > 0:
          bool_v1 = False
        if helpers.parallel(direct,v2) and helpers.dot(direct,v2) > 0:
          bool_v2 = False

      # Add the non-zero non-parallel direction
      if bool_v2 and b_v2:
        crawlable[self.beam.name].append(v2)
      if bool_v1 and b_v1:
        crawlable[self.beam.name].append(v1)

    return crawlable

  def nearestOnGround(self):
    return ground(self)

  def ground(self):
    '''
    This function finds the nearest beam to the robot that is connected 
    to the xy-plane (ground). It returns that beam and its direction from the 
    robot.
    '''
    # Get local boxes
    boxes = self.structure.get_boxes(self.location)

    # Initializations
    distances = {}
    vectors = {}

    # Cycle through boxes
    for box in boxes:
      # Cycle through beams in each box
      for name in box:

        # So e1 is in the form (x,y,z)
        e1, e2 = box[name].endpoints 
        # beam is lying on the ground (THIS IS NOT FUNCTIONAL)
        if helpers.compare(e1[2],0) and helpers.compare(e2[0],0):
          # pdb.set_trace()
          vectors[name] = helpers.vector_to_line(e1,e2,self.location)
          distances[name] = helpers.length(vectors[name])

        # Only one point is on the ground
        elif helpers.compare(e1[2],0):
          vectors[name] = helpers.make_vector(self.location, e1)
          distances[name] = helpers.distance(e1, self.location)
        elif helpers.compare(e2[2],0):
          vectors[name] = helpers.make_vector(self.location, e2)
          distances[name] = helpers.distances(e2, self.location)

        # No points on the ground
        else:
          pass

    # get name of beam at the minimum distance if one exists
    if distances == {}:
      return None
    else:
      # This returns the key (ie, name) of the minimum value in distances
      name = min(distances, key=distances.get)

      # So far away that we can't "see it"      
      if distances[name] > ROBOT['local_radius']:
        return None
      else:
        # All the same beans 
        beams = [box[name] for box in boxes if name in box]

        return {  'beam'  : beams[0],
                  'distance' : distances[name],
                  'direction' : vectors[name]}

  def move(self, direction, beam):
    '''
    Moves the robot in direction passed in and onto the beam specified
    '''
    length = helpers.length(direction)

    # The direction is smaller than the determined step, so move exactly by 
    # direction
    if length < self.step:
      new_location = helpers.sum_vectors(self.location, direction)
      self.change_location_structure(new_location, beam)

      # call do_action again since we still have some distance left, and update
      # step to reflect how much distance is left to cover
      self.step = self.step - length

      # Reset step in preparation for next timestep
      if helpers.compare(self.step,0):
        self.step == ROBOT['step_length']

      # We still have steps to go, so run an analysis if necessary
      elif self.beam is not None:
        # Run analysis before deciding to get the next direction
        if not self.model.GetModelIsLocked() and self.need_data():
          errors = helpers.run_analysis(self.model)
          if errors != '':
            # pdb.set_trace()
            pass

        # Get next direction
        self.next_direction_info = self.get_direction()

        # Unlock the results so that we can actually move
        if self.model.GetModelIsLocked():
          self.model.SetModelIsLocked(False)

        # Move
        self.do_action()

      # We climbed off
      else:
        assert not self.model.GetModelIsLocked()
        
        self.do_action()

    # The direction is larger than the usual step, so move only the step in the 
    # specified direction
    else:
      movement = helpers.scale(self.step, helpers.make_unit(direction))
      new_location = helpers.sum_vectors(self.location, movement)
      self.change_location(new_location, beam)


  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Action functions which affect the structure.
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def addLoad(self,beam,location,value):
    return self.addload(beam,location,value)

  def addload(self,beam,location,value):
    '''
    Adds a load of the specified value to the named beam at the specific 
    location
    '''
    # Sanity check
    assert not self.model.GetModelIsLocked()

    # Jump on beam
    self.beam = beam

    # Find distance and add load
    distance = helpers.distance(beam.endpoints.i,location)
    ret = self.model.FrameObj.SetLoadPoint(beam.name,PROGRAM['robot_load_case'],
      1,10,distance,value,"Global", False, True,0)
    helpers.check(ret,self,"adding new load",beam=beam.name,distance=distance,
      value=value,state=self.current_state())

  def addBeam(self,p1,p2):
    return self.addbeam(p1,p2)
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

    # Unlock the program if necessary
    if self.model.GetModelIsLocked():
      self.model.SetModelIsLocked(False)

    # Add points to SAP Program
    p1_name, p2_name = addpoint(p1), addpoint(p2)
    name = self.program.frame_objects.add(p1_name,p2_name,
      propName=MATERIAL['frame_property_name'])

    # Skip addition of beam
    if name == '':
      # Set to false if we were constructing support
      self.memory['construct_support'] = False
      return False

    # Set the output statios
    ret = self.model.FrameObj.SetOutputStations(name,2,1,10,False,False)
    if ret != 0:
      print("Could not set output stations for added beam.")
      return False

    # Get rid of one beam
    self.discard_beams()

    # Set to false if we were constructing support
    self.memory['construct_support'] = False

    # Successfully added at least one box
    if self.structure.add_beam(p1,p1_name,p2,p2_name,name) > 0:
      
      # Check to make sure the added element is near us 
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
          if added == '':
            print("Something went wrong when adding joint {} to SAP".format(str(
              coord)))
            return False

      return True

    else:
      print("Did not add beam to structure.")
      return False

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

        # Create a small disturbace
        lim = BEAM['random']
        f = random.uniform
        disturbance = (f(-1*lim,lim),f(-1*lim,lim),f(-1*lim,lim))

        # find the new j-point for the beam
        new_j = helpers.beam_endpoint(i,helpers.sum_vectors(j,disturbance))

        return check(i,new_j)

      else:

        # Calculate the actual endpoint of the beam (now that we now direction 
        # vector)
        return (i,helpers.beam_endpoint(i,j))

    # Sanitiy check
    assert (self.num_beams > 0)

    # Default pivot is our location
    pivot = self.location

    if self.beam is not None:

      # Obtain any nearby joints, and insert the i/j-end if needed
      all_joints = [coord for coord in self.beam.joints if not helpers.compare(
        coord[2],0)]
      if self.beam.endpoints.j not in all_joints and not helpers.compare(
        self.beam.endpoints.j[2],0):
        all_joints.append(self.beam.endpoints.j)
      if self.beam.endpoints.i not in all_joints and not helpers.compare(
        self.beam.endpoints.i[2],0):
        all_joints.append(self.beam.endpoints.i)

      # Find the nearest one
      joint_coord, dist = min([(coord, helpers.distance(self.location,coord)) for coord in all_joints], key = lambda t: t[1])
      
      # If the nearest joint is within our error, then use it as the pivot
      if dist <= BConstants.beam['joint_error']:
        pivot = joint_coord

    # Default vertical endpoint (the ratios are measured from the line created 
    # by pivot -> vertical_endpoint)
    vertical_endpoint = helpers.sum_vectors(pivot,helpers.scale(
      BEAM['length'],
      helpers.make_unit(BConstants.beam['vertical_dir_set'])))

    # Get the ratios
    sorted_angles = self.local_angles(pivot,vertical_endpoint)

    # Find the most vertical position
    final_coord = self.find_nearby_beam_coord(sorted_angles,pivot)

    # Obtain the default endpoints
    default_endpoint = self.get_default(final_coord,vertical_endpoint)
    i, j = check(pivot, default_endpoint)

    # Sanity check
    assert helpers.compare(helpers.distance(i,j),BConstants.beam['length'])

    return self.addbeam(i,j)

  def find_nearby_beam_coord(self,sorted_angles,pivot):
    '''
    Returns the coordinate of a nearby, reachable beam which results in the
    angle of construction with the most verticality
    '''
    # Limits
    min_constraining_angle, max_constraining_angle = self.get_angles(False)
    min_support_angle,max_support_angle = self.get_angles()

    # Cycle through the sorted angles until we find the right coordinate to build
    for coord, angle in sorted_angles:

      # If the smallest angle is larger than what we've specified as the limit, 
      # but larger than our tolerence, then build
      if min_constraining_angle <= angle and angle <= max_constraining_angle:
        return coord

    return None

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Actions performable by the robot body
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def pickup_beams(self,num = ROBOT['beam_capacity']):
    '''
    Pickup beams by adding weight to the robot and by adding num to number 
    carried
    '''
    self.num_beams = self.num_beams + num
    self.weight = self.weight + MATERIAL['beam_load'] * num

    # Set the direction towards the structure
    self.ground_direction = helpers.make_vector(self.location,
      CONSTRUCTION['center'])

  def discard_beams(self,num = 1):
    '''
    Get rid of the specified number of beams by decresing the weight and the 
    number carried
    '''
    self.num_beams = self.num_beams - num
    self.weight = self.weight - MATERIAL['beam_load'] * num



  def decide(self):
    '''
    Makes decisions based on available data
    '''
    pass

  def do_action(self):
    '''
    Acts based on decisions made
    '''
    pass