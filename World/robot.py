# Python default libraries
import operator
import math
from random import *
from abc import ABCMeta, abstractmethod

# import errors
from Helpers.errors import InvalidMemory
from Helpers import helpers

# import constants
from variables import BEAM, MATERIAL, PROGRAM, ROBOT, VISUALIZATION
from construction import HOME, CONSTRUCTION

class BaseBody:
  __metaclass__=ABCMeta
  '''
  These are the methods that need to be implemented in order for the
  current brains to continue functioning correctly. Look at comments on
  implementation of Body below or take a look at the documentation for more
  information on what each of these functions does
  '''
  @abstractmethod
  def __init__(self,Robot):
    pass

  @abstractmethod
  def currentState(self):
    pass

  @abstractmethod
  def needData(self):
    pass

  @abstractmethod
  def getGenuineLocation(self):
    pass

  @abstractmethod
  def getLocation(self):
    pass

  @abstractmethod
  def onStructure(self):
    pass

  @abstractmethod
  def atHome(self):
    pass

  @abstractmethod
  def atSite(self):
    pass

  @abstractmethod
  def atTop(self):
    pass

  @abstractmethod
  def addToMemory(self,key,value):
    pass

  @abstractmethod
  def popFromMemory(self,key):
    pass

  @abstractmethod
  def readFromMemory(self,key):
    pass

  @abstractmethod
  def changeLocalLocation(self,new_location,first_beam = None):
    pass

  @abstractmethod
  def changeLocationOnStructure(self,new_location,new_beam):
    pass

  @abstractmethod
  def atJoint(self):
    pass

  @abstractmethod
  def getMoment(self,name):
    pass

  @abstractmethod
  def getAvailableDirections(self):
   pass

  @abstractmethod
  def ground(self):
    pass

  @abstractmethod
  def addBeam(self,p1,p2):
    pass

  @abstractmethod
  def pickupBeams(self,num=ROBOT['beam_capacity']):
    pass

  @abstractmethod
  def discardBeams(self,num=1):
    pass

  @abstractmethod
  def localAngles(self,pivot,endpoint):
    pass

# Basic class for any automatic object that needs access to the SAP program
class Body(BaseBody):
  def __init__(self,name,structure,location,program):

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
    self.repair_data = ''
    self.read_moment = 0

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  State gathering functions (for information purposes).
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def myType(self):
    '''
    Returns the class name.
    '''
    return self.__class__.name

  def currentState(self):
    '''
    Returns the current state of the robot. This is used when we write the 
    information to the logs
    '''
    # None if on the ground
    beam = self.beam.name if self.beam is not None else self.beam

    # Round location to prevent decimal runoff in Excel
    location = [round(coord,2) for coord in self.location]
    deflected_location = [round(coord,2) for coord in self.getGenuineLocation()]
    
    # Copy the memory so that it is not modified
    memory = self.memory.copy()

    state = { 'name'              : self.name,
              'step'              : self.step,
              'location'          : location,
              'deflected_location': deflected_location,
              'beam'              : beam,
              'weight'            : self.weight,
              'num_beams'         : self.num_beams,
              'read_moment'       : self.read_moment,
              'memory'            : memory }

    return state

  def needData(self):
    '''
    Returns whether or not this particular robot needs the structure to be analyzed
    '''
    return self.onStructure()

  def getGenuineLocation(self):
    '''
    Returns the location of the robot on the current beam, accounting for the
    deflections that the beam has undergone. Uses the design location and the 
    deflection data from SAP to calculate this location.
    '''
    # Not on the structure, no deflection, or not recording deflection
    if not self.onStructure() or self.beam.deflection is None or not VISUALIZATION['deflection']:
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
    '''
    Provides easy access to the location.
    '''
    return self.location

  def onStructure(self):
    '''
    Returns whether or not the robot is on the structure
    '''
    return self.beam is not None

  def atHome(self):
    '''
    True if the robot is in the area designated as home (on the ground)
    '''
    return helpers.within(HOME['corner'], HOME['size'],
      self.location)

  def atSite(self):
    '''
    True if the robot is in the area designated as the construction site 
    (on the ground)
    '''
    return helpers.within(CONSTRUCTION['corner'], 
      CONSTRUCTION['size'], self.location)

  def atTop(self):
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

  def addToMemory(self,key,value,mult={}):
    '''
    Adds into the robot memory the information specified by value accessible 
    throught the key. If the key already exists, it simply replaces the value.
    '''
    mult.update({key : value})
    self.memory.update(mult)
    return True

  def popFromMemory(self,key):
    '''
    Returns the value associated with the key from memory and removes it from 
    memory. If no value is associated with key, raises a InvalidMemory(key)
    '''
    try:
      val = self.memory[key]
      del(self.memory[key])
      return val
    except KeyError:
      raise InvalidMemory(key)

  def readFromMemory(self,key):
    '''
    Returns the value associated with key from memory. If no value is associated
    with key, raises a InvalidMemory(key)
    '''
    try:
      return self.memory[key]
    except KeyError:
      raise InvalidMemory(key)

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Mobility functions for the robot body.
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def changeLocalLocation(self,new_location, first_beam = None):
    '''
    Moves the robot about locally (ie, without worrying about the structure, 
    except for when it moves onto the first beam)
    '''
    # When we move onto our first beam, add the load
    if first_beam != None:
      # Jump on beam
      self.beam = first_beam
      self.addLoad(first_beam,new_location,self.weight)
    self.location = new_location

    # Check that we are on the first octant
    assert self.location[0] >= 0
    assert self.location[1] >= 0

    # Verify that we are still on the xy plane
    if helpers.compare(self.location[2], 0):
      loc = list(self.location)
      loc[2] = 0
      self.location = tuple(loc)

  def changeLocationOnStructure(self,new_location, new_beam):
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
      existed (assumes the robot is on a beam)
      '''
      # Sanity check
      #assert not self.model.GetModelIsLocked() FIX (should work uncommented)

      # obtain current values.
      # values are encapsulated in a list as follows: ret, number_items, 
      # frame_names, loadpat_names, types, coordinates, directions, rel_dists, 
      # dists, loads
      data = self.model.FrameObj.GetLoadPoint(self.beam.name)
     
      # Sanity check with data
      assert data[0] == 0 
      if data[1] == 0:
        helpers.check(1,self,"getting loads",beam=self.beam.name,
          return_data=data,state=self.currentState())
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
        state=self.currentState())

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
            state=self.currentState())

    # Move the load off the current location and to the new one (if still on 
    # beam), then change the locations
    if self.beam is not None:
      removeload(self.location)

    # Don't add the load if there is no beam
    if new_beam is not None:
      # Jump on beam
      self.beam = new_beam
      self.addLoad(new_beam, new_location, self.weight)
    else:
      self.beam = new_beam


    # Update local location
    self.location = new_location

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Query functions about the structure and the local environment. Restricted
  to what the robot knows. These are like the sensors
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def atJoint(self):
    '''
    Returns whether or not the robot is at a joint
    '''
    if self.onStructure() and helpers.compare(self.location[2],0):
      return True

    # super section
    elif self.onStructure():

      for joint in self.beam.joints:
        # If we're at a joint to another beam
        if helpers.compare(helpers.distance(self.location,joint),0):
          return True
      
      return helpers.compare(self.location[2],0)
    
    else:
      return False

  def getMoment(self,name):
    '''
    Returns the moment for the beam specified by name at the point closest 
    to the robot itself
    '''
    m11,m22,m33 = self.getMomentMagnitudes(name)

    # Find magnitude
    total = math.sqrt(m22**2 + m33**2)

    # Store it to read out every timestep
    self.read_moment = total

    return total

  def getMomentMagnitudes(self,name,pivot=None):
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
        state=self.currentState())
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

  def getAvailableDirections(self):
    '''
    Returns a list of triplets with delta x, delta y, and delta z of the 
    direction the robot can move in. These directions constitute the locations 
    where beams currently exist. Additionally, it returns the "box of locality" 
    to which the robot is restricted containing all of the beams nearby that the
    robot can detect (though, this should only be used for finding a connection,
    as the robot itself SHOULD only measure the stresses on its current beam)
    '''
    # Run analysis before deciding to get the next direction
    if not self.model.GetModelIsLocked() and self.needData():
      errors = helpers.run_analysis(self.model)
      if errors != '':
        self.error_data += "getAvailableDirections(): " + errors + "\n"

    # Verify that the robot is on its beam and correct if necessary. 
    # This is done so that floating-point arithmethic errors don't add up.
    (e1, e2) = self.beam.endpoints
    if not (helpers.on_line (e1,e2,self.location)):
      self.changeLocationOnStructure(helpers.correct(e1,e2,self.location), self.beam)

    # Obtain all local objects
    box = self.structure.get_box(self.location)

    # Debugging
    if box == {}:
      #pdb.set_trace() FIX
      pass

    # Find the beams and directions (ie, where can he walk?)
    directions_info = self.getWalkableDirections(box)

    return {  'box'         : box,
              'directions'  : directions_info }

  def getWalkableDirections(self,box):
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
            raise Exception("The beam {} seems to have a joint with {}, but it is not in\
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

  def ground(self,random=False):
    '''
    This function finds the nearest beam to the robot that is connected 
    to the xy-plane (ground). It returns that beam and its direction from the 
    robot. If random = True, the function picks a random beam from those connected
    to the xy-plane.
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
      # Random key
      if random: name = choice(list(distances.keys()))
      # This returns the key (ie, name) of the minimum value in distances
      else: name = min(distances, key=distances.get)

      # So far away that we can't "see it"      
      if distances[name] > ROBOT['local_radius']:
        return None
      else:
        # All the same beans 
        beams = [box[name] for box in boxes if name in box]

        return {  'beam'  : beams[0],
                  'distance' : distances[name],
                  'direction' : vectors[name]}


  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Action functions which affect the structure.
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def addLoad(self,beam,location,value):
    '''
    Adds a load of the specified value to the named beam at the specific 
    location
    '''
    # Sanity check
    #assert not self.model.GetModelIsLocked() FIX

    # Find distance and add load
    distance = helpers.distance(beam.endpoints.i,location)
    ret = self.model.FrameObj.SetLoadPoint(beam.name,PROGRAM['robot_load_case'],
      1,10,distance,value,"Global", False, True,0)
    helpers.check(ret,self,"adding new load",beam=beam.name,distance=distance,
      value=value,state=self.currentState())

  def addBeam(self,p1,p2):
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
      return False

    # Set the output statios
    ret = self.model.FrameObj.SetOutputStations(name,2,1,10,False,False)
    if ret != 0:
      print("Could not set output stations for added beam.")
      return False

    # Get rid of one beam
    self.discardBeams()

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

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Actions performable by the robot body
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def pickupBeams(self,num = ROBOT['beam_capacity']):
    '''
    Pickup beams by adding weight to the robot and by adding num to number 
    carried
    '''
    self.num_beams = self.num_beams + num
    self.weight = self.weight + MATERIAL['beam_load'] * num

  def discardBeams(self,num = 1):
    '''
    Get rid of the specified number of beams by decresing the weight and the 
    number carried
    '''
    self.num_beams = self.num_beams - num
    self.weight = self.weight - MATERIAL['beam_load'] * num

  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Helper functions for construction
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def localAngles(self,pivot,endpoint):
    '''
    Calculates the ratios of a beam if it were to intersect nearby beams. 
    Utilizes the line defined by pivot -> endpoint as the base for the ratios 
    '''
    # We place it here in order to have access to the pivot and to the vertical 
    # point

    def add_angles(box,dictionary):
      for name, beam in box.items():

        # Ignore the beam you're on.
        if self.beam == None or self.beam.name != name:

          # Base vector (from which angles are measured)
          base_vector = helpers.make_vector(pivot,endpoint)

          # Get the closest points between the beam we want to construct and the
          # current beam
          points = helpers.closest_points(beam.endpoints,(pivot,endpoint))
          if points != None:

            # Endpoints (e1 is on a vertical beam, e2 is on the tilted one)
            e1,e2 = points

            # If we can actually reach the second point from vertical
            if (not helpers.compare(helpers.distance(pivot,e2),0) and 
              helpers.distance(pivot,e2) <= BEAM['length']):

              # Distance between the two endpoints
              dist = helpers.distance(e1,e2)

              # Vector of beam we want to construct and angle from base_vector
              construction_vector = helpers.make_vector(pivot,e2)
              angle = helpers.smallest_angle(base_vector,construction_vector)

              # Add to dictionary
              if e2 in dictionary:
                assert helpers.compare(dictionary[e2],angle)
              else:
                dictionary[e2] = angle

          # Get the points at which the beam intersects the sphere created by 
          # the vertical beam      
          sphere_points = helpers.sphere_intersection(beam.endpoints,pivot,
            BEAM['length'])
          if sphere_points != None:

            # Cycle through intersection points (really, should be two, though 
            # it is possible for it to be one, in
            # which case, we would have already taken care of this). Either way,
            # we just cycle
            for point in sphere_points:

              # Vector to the beam we want to construct
              construction_vector = helpers.make_vector(pivot,point)
              angle = helpers.smallest_angle(base_vector,construction_vector)

              # Add to dictionary
              if point in dictionary:
                assert helpers.compare(dictionary[point],angle)
              else:
                dictionary[point] = angle

          # Endpoints are also included
          for e in beam.endpoints:
            v = helpers.make_vector(pivot,e)
            l = helpers.length(v)
            if (e not in dictionary and not helpers.compare(l,0) and (
              helpers.compare(l,BEAM['length']) or l < BEAM['length'])):
              angle = helpers.smallest_angle(base_vector,v)
              dictionary[e] = angle

      return dictionary

    # get all beams nearby (ie, all the beams in the current box and possible 
    # those further above)
    boxes = self.structure.get_boxes(self.location)
    '''
    The dictionary is indexed by the point, and each point is 
    associated with one angle. The angle is measured from the pivot->endpoint
    line passed into the function.
    '''
    angles = {}
    for box in boxes:
      angles = add_angles(box,angles)

    return sorted(angles.items(), key = operator.itemgetter(1))
