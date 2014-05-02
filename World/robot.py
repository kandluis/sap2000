# Basic class for any automatic object that needs access to the SAP program
class Body(object):
  def __init__(self,name,program,location,program):

    # Access to the SAP 2000 Program
    self.program = program

    # Accesss to the SapModel from SAP 2000
    self.model = program.sap_com_object.SapModel

    # Storage of the sphere model
    self.simulation_model = None

    # Robot name
    self.name = name

    # Access to my Python structure
    self.structure = structure

    # Number of steps left in movement
    self.step = ROBOT['step_length']

    # The current location of the robot on the designed structure
    self.location = location

    # The beam on which the robot currently is
    self.beam = None

    # The weight of the robot
    self.weight = ROBOT['load']

    # Contains Errors from SAP 2000
    self.error_data = ''


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

    state = super(DumbMovable,self).current_state()

    # Round location to prevent decimal runoff in Excel
    location = [round(coord,2) for coord in self.location]
    deflected_location = [round(coord,2) for coord in self.get_true_location()]
    
    state.update({  'step'              : self.step,
                    'location'          : location,
                    'deflected_location': deflected_location,
                    'ground_direction'  : self.ground_direction,
                    'beam'              : beam,
                    'weight'            : self.weight,
                    'next_direction'    : self.next_direction_info })

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
    Returns the location of the robot.
    '''
    return self.location

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