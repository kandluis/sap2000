# Python default libraries
import random
import math
import pdb
from abc import ABCMeta, abstractmethod

# Local imports
from Helpers import helpers
# constants for simulation
from variables import BEAM, ROBOT,PROGRAM, VISUALIZATION
# constants for construction
from construction import HOME,CONSTRUCTION
# constants for behaviour
from Behaviour import constants as BConstants

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Implementation of different robot brains. 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class BaseBrain(metaclass=ABCMeta):
  @abstractmethod
  def __init__(self,Robot):
    # access to the robot body; functions are detailed in the documentation file
    # Code for the robot can be found in /World/robot.py
    self.Body = Robot

  @abstractmethod
  def performDecision(self):
    '''
    This function is called during the simulation before the act function is called.
    The brain should perform the task of deciding what actions to perform next.

    In particular, note that self.Body.addToMemory(key,value) allows for storing 
    information in the Body. 
    '''
    pass

  @abstractmethod
  def performAction(self):
    '''
    Perform the action that should occur after each timestep. This actions should be 
    based on the information currently stored in memory, as the robot has to access
    to data from the structure. DO NOT ATTEMPT to access the SAP 2000 API; there
    are no results.
    '''
    pass


'''
Example brain model. Does some simple movements on the structure to demonstrate
how to access the API for the body. This implements a robot which moves.
'''
class MovingBrain(BaseBrain):
  def __init__(self,Robot):
    super(MovingBrain,self).__init__(Robot)


'''
Currently used brain class object. This is the final implementation of the summer
simulation that have here.
'''
class Brain(BaseBrain):
  def __init__(self,Robot):
    super(Brain,self).__init__(Robot)

    # Setup default values for memory storage
    self.Body.addToMemory('search_mode', False)
    self.Body.addToMemory('start_construction', False)
    self.Body.addToMemory('ground_direction', None)
    self.Body.addToMemory('ground_tendencies', [None, None, None])
    self.Body.addToMemory('new_beam_steps', 0)

    # Same as above, but on the ground - since the ground is already a horizontal
    # support beam
    self.Body.addToMemory('new_beam_ground_steps', 0)

    # Stores name of beam to be reinforced (so we know when we're no longer on it)
    self.Body.addToMemory('broken_beam_name','')

    # Stores the previous beam we were on
    self.Body.addToMemory('previous_beam',None)

    # Smaller number gives higher priority
    self.Body.addToMemory('dir_priority',[0,0,0])

    # Move further in the x-direction?
    self.Body.addToMemory('pos_x', None)

    # Move further in the y-direction?
    self.Body.addToMemory('pos_y', None)

    self.Body.addToMemory('start_construction', False)

    # Climbing up or down
    self.Body.addToMemory('pos_z', None)
    self.Body.addToMemory('dir_priority', [0])

    # Starting defaults
    self.Body.addToMemory('built', False)
    self.Body.addToMemory('constructed', 0)

    # Keeps track of the direction we last moved in.
    self.Body.addToMemory('previous_direction', None)

    # Stores information on beams that need repairing
    self.Body.addToMemory('broken', [])

    # Stores whether or not we are constructing vertically or at an angle (for 
    # support)
    self.Body.addToMemory('construct_support', False)

    # This is the direction towards which the robot looks when searching for a 
    # support tube.
    # This is in the form (x,y,z)
    self.Body.addToMemory('preferred_direction', None)

    # Modes for supporting structure
    # WILL GO IN MEMORY
    self.Body.addToMemory('search_mode', False)
    self.Body.addToMemory('repair_mode', False)

    # The robots all initially move towards the centertower
    self.Body.addToMemory('ground_direction', helpers.make_vector(self.Body.getLocation(),
      CONSTRUCTION['corner']))

    # The direction in which we should move
    self.Body.addToMemory('next_direction_info', None)

    # The robots all initially move towards the centertower
    self.Body.addToMemory('ground_direction', helpers.make_vector(self.Body.getLocation(),
      CONSTRUCTION['corner']))


  def performDecision(self):
    #pdb.set_trace()
    self.decide()

  def performAction(self):
    #pdb.set_trace()
    self.do_action()

  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Brain Helper functions
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def decide(self):
    '''
    Overwritting to allow for repair work to take place
    '''
    #pdb.set_trace()
    if self.Body.readFromMemory('search_mode') and self.Body.readFromMemory('repair_mode'):
      self.pre_decision()

      # We have moved off the structure entirely, so wander
      if self.Body.beam is None:
        self.ground_support()

      # We've moved off the beam, so run the search support routine
      elif (self.Body.readFromMemory('broken_beam_name') != self.Body.beam.name and 
        self.Body.readFromMemory('search_mode') and self.Body.readFromMemory('broken_beam_name') != ''):

        # Remember the beam we moved onto right after the broken one
        if self.Body.readFromMemory('previous_beam') is None:
          self.Body.addToMemory('previous_beam',self.Body.beam.name)

        # We have found a support beam, so return to construct mode (the support beam is vertical)
        if (self.Body.readFromMemory('previous_beam') != self.Body.beam.name and (
          self.Body.readFromMemory('previous_direction') is None or 
          self.Body.readFromMemory('previous_direction')[1][2] > 0 or helpers.compare(
            self.Body.readFromMemory('previous_direction')[1][2],0))):
          self.construction_mode()

          # Decide again since we're out of repair mode
          self.decide()

        else:
          self.find_support()
          # Move (don't check construction)
          self.movable_decide()

      # Simply move
      else:
        self.movable_decide()

    
    # We found a support beam and are on it, planning on construction. If 
    # we reach the endpoint of the beam (the support beam), then construct.
    elif self.Body.readFromMemory('repair_mode'):
      if (helpers.compare(helpers.distance(self.Body.getLocation(),
          self.Body.beam.endpoints.j),self.Body.step / 2)):
        self.Body.addToMemory('start_contruction', True)
        self.Body.addToMemory('broken',[])

    # Build Mode
    else:
      self.pre_decision()

      # If we decide to construct, then we store that fact in a bool so action 
      # knows to wiggle the beam
      if self.construct():
        self.Body.addToMemory('start_construction', True)

      # Movement decisions
      else:
        self.movable_decide()


  def beam_check(self,name):
    '''
    Checks a beam to see whether it is in a state that requires repair
    '''
    moment = self.Body.getMoment(name)

    ##### THIS SHOULDN"T BE HERE
    e1,e2 = self.Body.structure.get_endpoints(name,self.Body.getLocation())
    #####

    xy_dist = helpers.distance((e1[0],e1[1],0),(e2[0],e2[1],0))
    limit = BConstants.beam['beam_limit'] + (
      xy_dist / BConstants.beam['length']) * BConstants.beam['horizontal_beam_limit']

    return (moment < limit or helpers.compare(moment,limit))

  def pre_decision(self):
    '''
    Takes care of resetting appropriate values.
    '''
    # We build almost never.
    self.Body.addToMemory('start_construction', True)
    self.Body.step = ROBOT['step_length']
    self.Body.addToMemory('broken',[])

  def climb_off(self,loc):
    '''
    Returns whether or not the robot should climb off the structure. Additionally,
    sets some special variables
    '''
    # On the xy-plane with no beams OR repairing
    if helpers.compare(loc[2],0) and (self.Body.num_beams == 0 or 
      self.Body.readFromMemory('search_mode')):
      
      # Not repairing, so calculate direction
      if not self.Body.readFromMemory('search_mode'):
        direction = helpers.make_vector(self.Body.getLocation(),HOME['center'])
        direction = (direction[0],direction[1],0)
        self.Body.addToMemory('ground_direction', direction)

      return True
    
    else:

      # Resetting to None if not in search_mode
      groundirection = (None if not self.Body.readFromMemory('search_mode') 
        else self.Body.readFromMemory('ground_direction'))
      self.Body.addToMemory('ground_direction', groundirection)

      return False

  def get_ground_direction(self):
    ''' 
    In future classes, this function can be altered to return a preferred 
    direction,  but currently it only returns a random feasable direction if no
    direction is assigned for the robot (self.Body.readFromMemory('ground_direction'))
    '''
    def random_direction():
      '''
      Returns a random, new location (direction)
      '''
      # obtain a random direction
      direction = (random.uniform(-1 * self.Body.step, self.Body.step), random.uniform(
        -1 * self.Body.step, self.Body.step), 0)

      # The they can't all be zero!
      if helpers.compare(helpers.length(direction),0):
        return random_direction()
      else:
        step = helpers.scale(self.Body.step,helpers.make_unit(direction))
        predicted_location = helpers.sum_vectors(step, self.Body.getLocation())

        # Check the location
        if helpers.check_location(predicted_location):
          return direction
        else:
          return random_direction()

    # If we have a currently set direction, check to see if we will go out of 
    # bounds.
    if self.Body.readFromMemory('ground_direction') != None:
      step = helpers.scale(self.Body.step,helpers.make_unit(
        self.Body.readFromMemory('ground_direction')))
      predicted_location = helpers.sum_vectors(step, self.Body.getLocation())

      # We are going out of bounds, so set the direction to none and call 
      # yourself again (to find a new location)
      if not helpers.check_location(predicted_location):
        self.Body.addToMemory('ground_direction', None)
        return self.get_ground_direction()

      # Here, we return the right direction
      else:
        assert self.Body.readFromMemory('ground_direction') != None
        return self.Body.readFromMemory('ground_direction')

    # We don't have a direction, so pick a random one (it is checked when we 
    # pick it)
    else:
      self.Body.addToMemory('ground_direction',random_direction())
      return self.Body.readFromMemory('ground_direction')

  def pickup_beams(self,num = ROBOT['beam_capacity']):
    '''
    Adding ability to change memory
    '''

    # Set the direction towards the structure
    self.Body.addToMemory('ground_direction', helpers.make_vector(self.Body.getLocation(),
      CONSTRUCTION['center']))
    self.Body.addToMemory('broken', [])
    self.Body.addToMemory('broken_beam_name', '')

    # Move up when you pick one up
    self.Body.addToMemory('pos_z', True)

    self.Body.pickupBeams(num)

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
    if self.Body.atHome() and self.Body.num_beams == 0:
      self.pickup_beams()

    # If we have no beams, set the ground direction to home (TEMP CODE)
    if self.Body.num_beams == 0:
      vector = helpers.make_vector(self.Body.getLocation(),HOME['center'])
      self.Body.addToMemory('ground_direction', (vector if not helpers.compare(helpers.length(
        vector),0) else self.non_zero_xydirection())) 

    # Find nearby beams to climb on
    result = self.Body.ground()

    # Either there are no nearby beams, we are on repair_mode/search_mode, our beams are 0, or
    # we are constructing a support - so don't mess with direction
    if (result == None or self.Body.readFromMemory('repair_mode') or self.Body.readFromMemory('search_mode') or 
      self.Body.num_beams == 0 or self.Body.readFromMemory('construct_support')):
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.Body.getLocation(),helpers.scale(self.Body.step,
        helpers.make_unit(direction)))
      self.Body.changeLocalLocation(new_location)

    # Nearby beam, jump on it
    else:
      dist, close_beam, direction = (result['distance'], result['beam'],
        result['direction'])
      # If the beam is within steping distance, just jump on it
      if self.Body.num_beams > 0 and dist <= self.Body.step:
        # Set the ground direction to None (so we walk randomly if we do get off
        # the beam again)
        self.Body.addToMemory('ground_direction', None)

        # Then move on the beam
        self.move(direction, close_beam)

      # If we can "detect" a beam, change the ground direction to approach it
      elif self.Body.num_beams > 0 and dist <= ROBOT['local_radius']:
        self.Body.addToMemory('ground_direction', direction)
        new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale(
          self.Body.step,helpers.make_unit(direction)))
        self.Body.changeLocalLocation(new_location)
      
      # Local beams, but could not detect (this is redundant)
      else:
        direction = self.get_ground_direction()
        new_location = helpers.sum_vectors(self.Body.getLocation(),helpers.scale(
          self.Body.step,helpers.make_unit(direction)))
        self.Body.changeLocalLocation(new_location)

  def pre_decision(self):
    '''
    Takes care of resetting appropriate values
    '''
    self.Body.step = ROBOT['step_length']

  def movable_decide(self):
    '''
    Later classes need direct access to this method
    '''
    # If we're not on a beam, then we will wander on the ground
    if self.Body.beam is None:
      # reset steps
      self.Body.addToMemory('next_direction_info', None)

    # Otherwise, we are not on the ground and we decided not to build, so pick 
    # a direction and store that
    else:
      # Before we decide, we need to make sure that we have access to analysis
      # results. Therefore, check to see if the model is locked. If it is not,
      # then execute and analysis.
      if not self.Body.model.GetModelIsLocked() and self.Body.needData():
        errors = helpers.run_analysis(self.Body.model)
        assert errors == ''

      self.Body.addToMemory('next_direction_info', self.get_direction())

  # Model needs to have been analyzed before calling THIS function
  def decision_helper(self):
    '''
    This functions decides what is going to be done next based on the analysis 
    results of the program. Therefore, this function should be the one that 
    decides whether how to move, based on the local conditions
    and then stores that information in the robot. The robot will then act 
    based on that information once the model has been unlocked. 
    '''
    self.pre_decision()
    self.movable_decide()

  def do_action(self):
    '''
    Overwriting the do_action functionality in order to have the robot move up 
    or downward (depending on whether he is carrying a beam or not), and making 
    sure that he gets a chance to build part of the structure if the situation 
    is suitable. This is also to store the decion made based on the analysis 
    results, so that THEN the model can be unlocked and changed.
    '''
    # Check to see if the robot decided to construct based on analysys results
    if self.Body.readFromMemory('start_construction'):
      if not self.build():
        print("Could not build...")
      self.Body.addToMemory('start_construction', False)

    # Move around
    elif self.Body.beam is not None:
      assert self.Body.readFromMemory('next_direction_info') != None
      self.move(self.Body.readFromMemory('next_direction_info')['direction'],
        self.Body.readFromMemory('next_direction_info')['beam'])
      self.Body.addToMemory('next_direction_info', None)

    # We have climbed off, so wander about 
    else:
      self.wander()

  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Construction Decision Helper functions
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def support_xy_default(self):
    '''
    Returns the direction in which the support beam should be constructed
    '''
    # Check to see if direction is vertical
    default_direction = self.get_repair_beam_direction()

    # The beam was vertical
    if default_direction is None:
      xy_dir = self.non_zero_xydirection()

    # Use the default direction
    else:
      xy_dir = default_direction

    return helpers.make_unit(xy_dir)

  def support_vertical_default(self,angle=None):
    '''
    Returns the vertical change for the support endpoint locations
    '''
    # Add beam_directions plus vertical change based on angle ratio (tan)
    if angle is None:
      ratio = helpers.ratio(self.get_angle('support_angle'))

    # We changed the angle from the default  
    else:
      ratio = helpers.ratio(angle)

    # Calculate vertical based on assumption that xy-dir is unit
    vertical = helpers.scale(1/ratio,(0,0,1)) if ratio != 0 else None

    return vertical

  def support_beam_default(self):
    '''
    Returns the endpoint for construction of a support beam
    '''
    # Add beam_directions plus vertical change based on angle ratio (tan)
    ratio = helpers.ratio(self.get_angle('support_angle'))
    vertical = self.support_vertical_change()
    xy_dir = self.support_xy_direction()

    if xy_dir is None or vertical is None:
      direction = (0,0,1)
    else:
      xy_dir = helpers.make_unit(xy_dir)
      direction = helpers.make_unit(helpers.sum_vectors(xy_dir,vertical))

    # Calculate endpoints
    endpoint = helpers.sum_vectors(self.Body.getLocation(),helpers.scale(
      BConstants.beam['length'],direction))

    return endpoint

  def support_xy_direction(self):
    '''
    Improves the construction direction so that we take into account the angle
    at which our current beam is located, and the verticality of the beam we
    are attempting to reach. This returns a unit direction (always should!)
    '''
    # If we're on the ground, then continue doing as before
    if self.Body.beam is None:
      return self.support_xy_default()

    else:
      # Get repair beam vector
      b_i,b_j = self.Body.structure.get_endpoints(self.Body.readFromMemory('broken_beam_name'),
        self.Body.getLocation())
      repair_vector = helpers.make_vector(b_i,b_j)

      # Get the correct vector for the current beam
      # Remember - we travel in the opposite direction as normal when building
      # the support beam, so that's why this seems opposite of normal
      c_i,c_j = self.Body.beam.endpoints
      current_vector = (helpers.make_vector(c_j,c_i) if 
        self.Body.readFromMemory('previous_direction')[1][2] > 0 else helpers.make_vector(
          c_i,c_j))

      # 
      angle = helpers.smallest_angle(repair_vector,current_vector)

      # If below the specified angle, then place the beam directly upwards (no
      # change in xy)
      if angle < BConstants.beam['direct_repair_limit']:
        return None
      else:
        vertical = (0,0,1)
        v1,v2 = helpers.make_vector(b_i,c_i), helpers.make_vector(b_i,c_j)

        # We can't get a direction based on beam locations
        if helpers.parallel(vertical,v1) and helpers.parallel(vertical,v2):
          return self.support_xy_default()

        # We can use the current beam to decide the direction
        elif not helpers.parallel(vertical,current_vector):
          # pdb.set_trace()

          # Project onto the xy-plane and negate
          if current_vector[2] > 0:
            projection = helpers.make_unit(helpers.scale(-1,(current_vector[0],
              current_vector[1],0)))
          else:
            projection = helpers.make_unit((current_vector[0],current_vector[1],0))

          # Add some small disturbance
          disturbance = helpers.scale(random.uniform(-1,1),(-projection[1],
            projection[0],projection[2]))
          result = helpers.sum_vectors(projection,disturbance)

          # TODO
          return result

        elif not helpers.parallel(vertical,repair_vector):
          return self.support_xy_default()

        else:
          return self.support_xy_default()

  def support_vertical_change(self,angle=None):
    # Get vertical vector 
    change_vector = self.support_vertical_default()

    # If we're on the ground, just return (no rotation necessary)
    if self.Body.beam is None:
      return change_vector

    # Otherwise, rotate it based on our current beam
    else:
      # Debugging
      # pdb.set_trace()
      if self.Body.readFromMemory('previous_direction') is None:
        #pdb.set_trace()
        pass

      # Get the correct vector for the current beam
      i,j = self.Body.beam.endpoints
      current_vector = helpers.make_vector(i,j)
      
      # Find rotation from vertical
      angle = helpers.smallest_angle((0,0,1),current_vector)
      rotation_angle = 180 - angle if angle > 90 else angle

      vertical_angle = abs(BConstants.beam['support_angle'] - rotation_angle)

      return self.support_vertical_default(angle=vertical_angle)
  
  def support_beam_endpoint(self):
    '''
    Returns the endpoint for a support beam
    '''
    #pdb.set_trace()
    # Get broken beam
    e1,e2 = self.Body.structure.get_endpoints(self.Body.readFromMemory('broken_beam_name'),
      self.Body.getLocation())

    # Direction
    v = helpers.make_unit(helpers.make_vector(e1,e2))

    # Get pivot and repair beam midpoint
    pivot = self.Body.getLocation()
    midpoint1 = helpers.midpoint(e1,e2)

    # Upper midpoint to encourate upward building
    midpoint = helpers.midpoint(e2,midpoint1)

    # Add an offset to mimick inability to determine location exactly
    offset = helpers.scale(random.uniform(-1*BEAM['random'],BEAM['random']),v)
    midpoint = (helpers.sum_vectors(midpoint,offset) if random.randint(0,4) == 1
    else midpoint) 

    # Calculate starting beam_endpoint
    endpoint = helpers.beam_endpoint(pivot,midpoint)

    # Calculate angle from vertical
    angle_from_vertical = helpers.smallest_angle(helpers.make_vector(pivot,
      endpoint),(0,0,1))

    # Get angles
    sorted_angles = self.Body.localAngles(pivot,endpoint)
    min_support_angle,max_support_angle = self.get_angles()
    min_constraining_angle,max_constraining_angle = self.get_angles(
      support=False)

    # Defining here to have access to min,max, etc.
    def acceptable_support(angle,coord):
      # Find beam endpoints
      beam_endpoint = helpers.beam_endpoint(pivot,coord)

      # Calculate angle from vertical of beam we wish to construct based on the
      # information we've gathered
      from_vertical = (angle_from_vertical + angle if beam_endpoint[2] <= 
        endpoint[2] else angle_from_vertical - angle)

      simple = not (from_vertical < min_constraining_angle or from_vertical > 
        max_constraining_angle)

      # On the ground
      if self.Body.beam is None:
        return simple

      # On a beam, so check our support_angle_difference
      else:
        beam_vector = helpers.make_vector(self.Body.beam.endpoints.i,
          self.Body.beam.endpoints.j)
        support_vector = helpers.make_vector(self.Body.getLocation(),coord)
        angle = helpers.smallest_angle(beam_vector,support_vector)
        real_angle = abs(90-angle) if angle > 90 else angle
        
        return simple and real_angle > BConstants.beam['support_angle_difference']

    return_coord = None
    for coord,angle in sorted_angles:
      if acceptable_support(angle,coord) and helpers.on_line(e1,e2,coord):
        self.Body.addToMemory('broken_beam_name', '')
        return coord
      elif acceptable_support(angle,coord):
        return_coord = coord

    if return_coord is not None:
      return return_coord
    else:  
      # Otherwise, do default behaviour
      return self.support_beam_default()

  def remove_specific(self,dirs):
    '''
    We don't want to move UP along our own beam when we are repairing and at a
    joint.
    '''
    new_dirs = {}
    if self.Body.atJoint() and self.Body.readFromMemory('repair_mode'):
      # Access items
      for beam, vectors in dirs.items():
        # If the directions is about our beam, remove references to up.
        # Also do this for our broken beam (we don't want to get stuck climbing
        # onto it again and again in a cycle)
        if beam == self.Body.beam.name or beam == self.Body.readFromMemory('broken_beam_name'):
          vectors = [v for v in vectors if v[2] < 0 or helpers.compare(v[2],0)]
          if vectors != []:
            new_dirs[beam] = vectors
        else:
          new_dirs[beam] = vectors

      return new_dirs

    return dirs


  def local_rules(self):
    '''
    Overriding so we can build support beam
    '''
    # If we ran our course with the support, construct it
    if (((self.Body.beam is not None and self.Body.readFromMemory('new_beam_steps') == 0) or (
      helpers.compare(self.Body.getLocation()[2],0) and 
      self.Body.readFromMemory('new_beam_ground_steps') == 0)) and 
      self.Body.readFromMemory('construct_support')):
      return True

    # Local rules as before
    else:
      return False

  def get_preferred_ground_direction(self,direction):
    '''
    Returns the direction of preffered travel if we reach the ground when repairing
    '''
    if direction is not None:
      return (direction[0],direction[1],0)
    else:
      return None

  def start_repair(self,beam):
    '''
    Initializes the repair of the specified beam. Figures out which direction to
    travel in and stores it within the robot's memory, then tells it to climb
    down in a specific direction if necessary. Also sets the number of steps to
    climb down looking for a support beam.
    '''
    def set_dir(string,coord):
      '''
      Figures out what pos_var should be in order to travel in that direction
      
      NO LONGER USED

      '''
      if helpers.compare(coord,0):
        self.Body.addToMemory(string,None)
      if coord > 0:
        self.Body.addToMemory(string,True)
      else:
        self.Body.addToMemory(string,False)

    angle_with_vertical = helpers.smallest_angle(helpers.make_vector(
      beam.endpoints.i,beam.endpoints.j),(0,0,1))

    # Get direction of travel
    self.Body.addToMemory('preferred_direction',self.get_preferred_direction(beam))

    # Get direction of travel if on the ground based on preferred direction on
    # the structure
    self.Body.addToMemory('ground_direction',self.get_preferred_ground_direction(
      self.Body.readFromMemory('preferred_direction')))

    # Travel down !
    self.Body.addToMemory('pos_z',False)

    # Store name of repair beam
    self.Body.addToMemory('broken_beam_name',beam.name)

    # Number of steps to search once we find a new beam that is close to
    # parallel to the beam we are repairing (going down, ie NOT support beam)
    length = BEAM['length'] * math.cos(
      math.radians(BConstants.beam['support_angle']))
    self.Body.addToMemory('new_beam_steps',math.floor(length/ROBOT['step_length'])+1)
    groundsteps = (self.Body.readFromMemory('new_beam_steps') if
      self.Body.readFromMemory('ground_direction') is None else self.Body.readFromMemory(
        'new_beam_steps') - 1 + math.floor(math.sin(math.radians(
          angle_with_vertical)) * self.Body.readFromMemory('new_beam_steps')))
    self.Body.addToMemory('new_beam_ground_steps',groundsteps)

    # So the entire robot knows that we are in repair mode
    self.Body.addToMemory('repair_mode', True)
    self.Body.addToMemory('search_mode', True)

  def get_preferred_direction(self,beam):
    '''
    Returns the preferred direction - this is the direction towards which the 
    robot wants to move when looking for an already set support tube.
    The direction is a unit vector
    '''
    #pdb.set_trace()
    # Calculate direction of repair (check 0 dist, which means it is perfectly
    # vertical!)
    i, j = beam.endpoints.i, beam.endpoints.j
    v1 = helpers.make_vector(self.Body.getLocation(),j)
    v2 = helpers.make_vector(i,self.Body.getLocation())
    l1,l2 = helpers.length(v1), helpers.length(v2)

    # v1 is non-zero and it is not vertical
    if not (helpers.compare(l1,0) or helpers.is_vertical(v1)):
      return helpers.make_unit(v1)

    # v2 is non-zero and it is not vertical
    elif not (helpers.compare(l2,0) or helpers.is_vertical(v2)):
      return helpers.make_unit(v2)

    # No preferred direction because the beam is perfectly vertical
    else:
      return None

  def no_available_direction(self):
    '''
    No direction takes us where we want to go, so check to see if we need to 
      a) Construct
      b) Repair
    '''
    # Initialize repair mode if there are broken beams (and you can fix)
    if self.Body.readFromMemory('broken') != [] and self.Body.num_beams > 0:
      beam, moment = max(self.Body.readFromMemory('broken'),key=lambda t : t[1])

      # Print to console
      string = "{} is starting repair of beam {} which has moment {} at {}".format(
        self.Body.name,beam.name,str(moment),str(self.Body.getLocation()))

      # This is a special repair of the moment is zero
      if moment == 0:
        string += ". This repair occured due to special rules."
      print(string)

      # Store, to output into file later
      self.repair_data = string
      
      # switch to repair mode with the beam as the one being repaired
      self.start_repair(beam)

    elif self.Body.num_beams > 0 and self.Body.atTop():
      self.Body.addToMemory('start_construction', True)
      self.Body.addToMemory('broken', [])
    else:
      pass

  def add_support_mode(self):
    '''
    Sets up the construction of a support beam
    '''
    # Return to construct mode
    self.construction_mode()

    # But specify steps, and that we need to construct a support
    self.Body.addToMemory('broken', [])
    self.Body.addToMemory('new_beam_steps', 1)
    self.Body.addToMemory('new_beam_ground_steps', 1)
    self.Body.addToMemory('construct_support', True)

  def ground_support(self):
    '''
    Looks for a support from the ground
    '''
    # We have run our course, so add the support
    if self.Body.readFromMemory('new_beam_ground_steps') == 0:
      self.add_support_mode()
      self.Body.addToMemory('ground_direction',helpers.scale(
        -1,self.Body.readFromMemory('ground_direction')))

    self.Body.addToMemory('new_beam_ground_steps', self.Body.readFromMemory('new_beam_ground_steps') - 1)

  def find_support(self):
    '''
    Looks for a support beam on the structure
    '''
    # We did not find a beam in the number of steps we wanted (go back to build
    # mode, but with the condition to build in exactly one timestep)
    if self.Body.readFromMemory('new_beam_steps') == 0:
      self.add_support_mode()

    self.Body.addToMemory('new_beam_steps',self.Body.readFromMemory('new_beam_steps') - 1)
    self.Body.addToMemory('new_beam_ground_steps',self.Body.readFromMemory('new_beam_ground_steps') - 1)

  def construction_mode(self):
    '''
    Resets the robot to go back into construction mode (leaves some variables
     - such as the repair_beam_direction and the broken_beam_name available)
    '''
    self.Body.addToMemory('new_beam_steps', 0)
    self.Body.addToMemory('new_beam_ground_steps', 0)
    self.Body.addToMemory('previous_beam', None)
    self.Body.addToMemory('pos_z', True)
    self.Body.addToMemory('pos_y', None)
    self.Body.addToMemory('pos_x', None)
    self.Body.addToMemory('dir_priority', [1,1,0])

    self.Body.addToMemory('repair_mode', False)
    self.Body.addToMemory('search_mode', False)

  def repairing(self):
    '''
    This is run when repairing, so as to set the right values when filtering and
    when picking directions
    '''
    # If we are at a joint, we might move up but MUST move in right x and y
    if self.Body.atJoint():

      # No longer care if we move up or down
      self.Body.addToMemory('pos_z', None)
      self.Body.addToMemory('dir_priority', [1,1,1])
    else:

      # Want to move down
      self.Body.addToMemory('pos_z',False)
      self.Body.addToMemory('dir_priority', [1,1,0])

  def construct(self):
    '''
    Decides whether the robot should construct or not based on some local rules.
    '''
    return self.basic_rules() or self.local_rules()

  def basic_rules(self):
    '''
    Decides whether to build or not. Uses some relatively simple rules to decide.
    Here is the basic logic it is following.
    1.  a)  If we are at the top of a beam
        OR
        b)  i)  We are at the specified construction site
            AND
            ii) There is no beginning tube
    AND
    2.  Did not build in the previous timestep
    AND
    3.  Still carrying construction material
    '''

    if (((self.Body.atSite() and not self.Body.structure.started and not self.Body.readFromMemory('search_mode')
      )) and not self.Body.readFromMemory('built') and self.Body.num_beams > 0):

      self.Body.structure.started = True
      self.Body.addToMemory('built', True)
      return True
    else:
      self.Body.addToMemory('built', False)
      return False

  def pick_direction(self,directions):
    '''
    Overwritting to pick the direction of steepest descent when climbing down
    instead of just picking a direction randomly. Also takes into account that 
    we might want to travel upward when repairing.
    '''
    def min_max_dir(vs,get_min=True):
      unit_list = [helpers.make_unit(v) for v in vs]
      if get_min:
        val = min(unit_list,key=lambda t : t[2])
      else:
        val = max(unit_list,key=lambda t : t[2])

      index = unit_list.index(val)
      return index,val

    def pick_support(vs):
      '''
      Returns index, sorting_angle of vs.
      '''
      angle_list = [abs(helpers.smallest_angle((1,0,0),v) - 
        BConstants.beam['support_angle']) for v in vs]
      min_val = min(angle_list)
      index = angle_list.index(min_val)
      return index, min_val

    if self.Body.readFromMemory('search_mode') and not self.Body.readFromMemory('construct_support'):
      self.repairing()

    # Pick the closests direction to a support beam
    if self.Body.readFromMemory('search_mode') and self.Body.atJoint():
      #pdb.set_trace()
      beam, (index,angle) = min([(n, pick_support(vs)) for n,vs in directions.items()],
        key=lambda t: t[1][1])

    # Pick the smalles pos_z whether moving up or down (modification)
    else:
      beam, (index, unit_dir) = min([(n, min_max_dir(vs)) for n,vs in directions.items()],
        key=lambda t : t[1][1][2])

    # We want to return the original direction vector since it contains both
    # information on direction and on distance

    direction = beam, directions[beam][index]
    # Store direction
    self.Body.addToMemory('previous_direction', direction)
    
    return direction

  def preferred(self,vector):
    '''
    Returns True if vector is preferred, False if it is not
    '''
    xy = self.Body.readFromMemory('preferred_direction')
    xy = (xy[0],xy[1],0) 
    if (helpers.compare_tuple(xy,(0,0,0)) or helpers.compare_tuple((
      vector[0],vector[1],0),(0,0,0))):
      return True

    return (helpers.smallest_angle((vector[0],vector[1],0),xy) <= 
      BConstants.beam['direction_tolerance_angle'])

  def filter_preferred(self,v):
    '''
    Decided whether or not v is a preferred direction
    '''
    return True

  def filter_dict(self,dirs,new_dirs,comp_functions,preferenced,priorities=[]):
    '''
    Filters a dictinary of directions, taking out all directions not in the 
    correct directions based on the list of comp_functions (x,y,z).

    Edit: Now also filters on priority. If a direction has priority of 0, then
    it MUST be in that direction. The only way that it will ever return an empty
    dictionary is if none of the directions match the direction we want to move
    in for each coordinate with priority zero. Otherwise, we match as many low
    priorty numbers as possible. Same priorities must be matched at the same
    level. 

    Edit: Have done mostly away with priorities, though for compatibility, we
    still keep them in case we want to use them later. Will probably work on 
    removing them entirely. 

    Now, we have added a "preferenced" bool which checks to see if the direction
    is within a specified angle of preferred travel (the angle is dictated in 
    construction.py). The preference is set to True when we are searching for a
    support, otherwise to False. We want this direction, but if we can't find it,
    we reset the variable to False
    '''
    # Access items
    for beam, vectors in dirs.items():

      true_beam = self.Body.structure.get_beam(beam,self.Body.getLocation())

      # If the beam won't be a support beam, pass it..
      if (preferenced and true_beam.endpoints.j in true_beam.joints and 
        self.Body.readFromMemory('preferred_direction') is not None):
        pass 

      # Access each directions
      for vector in vectors:
        coord_bool = True

        # Apply each function to the correct coordinates
        for function, coord in zip(comp_functions,vector):
          coord_bool = coord_bool and function(coord)

        # Additionally, check the x-y direction if we have a preferenced direction
        if (preferenced and self.Body.readFromMemory('preferred_direction') is not None and
          not helpers.is_vertical(vector)):
          coord_bool = coord_bool and self.filter_preferred(vector)

        # Check to see if the direciton is acceptable and keep if it is
        if coord_bool:
          if beam not in new_dirs:
            new_dirs[beam] = [vector]
          else:
            new_dirs[beam].append(vector)

    # Special rules for travelling
    new_dirs = self.remove_specific(new_dirs)

    # Case is not matched, so obtain keys of max values and remove those
    # restraints if the value is not 0
    if new_dirs == {}:

      # We didn't take priorities into account, now we do
      if priorities == []:

        # COPY the LIST
        priorities = list(self.Body.readFromMemory('dir_priority'))
      
      max_val = max(priorities)

      # Set to -1 so we don't use them next time, and set comp_funs to True
      for i, val in enumerate(priorities):
        if val == max_val:
          priorities[i] = -1
          comp_functions[i] = lambda a : True

      # We ran out of priorities and we have no preference, so just return the
      # empty set
      if max_val <= 0 and not preferenced:
        return new_dirs

      # We have preference, and/or priorites
      else:
        return self.filter_dict(dirs,new_dirs,comp_functions,False,priorities)

    # Non-empty set
    else:
      return new_dirs

  def filter_directions(self,dirs):
    '''
    Filters the available directions and returns those that move us in the 
    desired direction. Overwritten to take into account the directions in
    which we want to move. When climbing down, it will take the steepest path.
    '''
    # Change stuff up, depending on whether we are in repair mode (but not 
    # construct support mode)
    if self.Body.readFromMemory('search_mode') and not self.Body.readFromMemory('construct_support'):
      self.repairing()

    def bool_fun(string):
      '''
      Returns the correct funtion depending on the information stored in memory
      '''
      if self.Body.readFromMemory(string):
        return (lambda a : a > 0)
      elif self.Body.readFromMemory(string) is not None:
        return (lambda a : a < 0)
      else:
        return (lambda a : True)

    # direction functions
    funs = [bool_fun('pos_x'), bool_fun('pos_y'), bool_fun('pos_z')]

    directions =  self.filter_dict(dirs, {}, funs,preferenced=self.Body.readFromMemory('search_mode'))

    return directions

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
      if not self.Body.structure.available(i,j):

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
    assert (self.Body.num_beams > 0)

    # Default pivot is our location
    pivot = self.Body.getLocation()

    if self.Body.beam is not None:

      # Obtain any nearby joints, and insert the i/j-end if needed
      all_joints = [coord for coord in self.Body.beam.joints if not helpers.compare(
        coord[2],0)]
      if self.Body.beam.endpoints.j not in all_joints and not helpers.compare(
        self.Body.beam.endpoints.j[2],0):
        all_joints.append(self.Body.beam.endpoints.j)
      if self.Body.beam.endpoints.i not in all_joints and not helpers.compare(
        self.Body.beam.endpoints.i[2],0):
        all_joints.append(self.Body.beam.endpoints.i)

      # Find the nearest one
      joint_coord, dist = min([(coord, helpers.distance(self.Body.getLocation(),coord)) for coord in all_joints], key = lambda t: t[1])
      
      # If the nearest joint is within our error, then use it as the pivot
      if dist <= BConstants.beam['joint_error']:
        pivot = joint_coord

    # Default vertical endpoint (the ratios are measured from the line created 
    # by pivot -> vertical_endpoint)
    vertical_endpoint = helpers.sum_vectors(pivot,helpers.scale(
      BEAM['length'],
      helpers.make_unit(BConstants.beam['vertical_dir_set'])))

    # Get the ratios
    sorted_angles = self.Body.localAngles(pivot,vertical_endpoint)

    # Find the most vertical position
    final_coord = self.find_nearby_beam_coord(sorted_angles,pivot)

    # Obtain the default endpoints
    default_endpoint = self.get_default(final_coord,vertical_endpoint)
    i, j = check(pivot, default_endpoint)

    # Sanity check
    assert helpers.compare(helpers.distance(i,j),BConstants.beam['length'])

    result = self.Body.addBeam(i,j)

    # Set to false if we were constructing support
    self.Body.addToMemory('construct_support', False)

    # no beams, we want to travel down
    if self.Body.num_beams == 0:
      self.Body.addToMemory('pos_z', False)

    return result

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

  def get_default(self,angle_coord,vertical_coord):
    '''
    Returns the coordinate onto which the j-point of the beam to construct 
    should lie
    '''
    # pdb.set_trace()
    if self.Body.readFromMemory('construct_support'):
      return self.support_beam_endpoint()

    elif angle_coord is not None and self.struck_coordinate():
      return angle_coord

    # Retunr the vertical coordinate
    else:
      # Create disturbance
      disturbance = self.get_disturbance()
      
      # We add a bit of disturbance every once in a while
      new_coord = vertical_coord if self.default_probability() else (
      helpers.sum_vectors(vertical_coord,disturbance))
      return new_coord

  def get_disturbance(self):
    '''
    Returns the disturbance level for adding a new beam at the tip (in this
    class, the disturbance is random at a level set in BEAM['random'])
    '''
    change = BEAM['random']
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

  def support_coordinate(self):
    '''
    Returns whether or not the beam being built should be done so as a support beam.
    '''
    return self.Body.readFromMemory('construct_support')

  def struck_coordinate(self):
    '''
    Returns whether the struck coordinate of a nearby beam should be used if found
    '''
    return True
 
  def non_zero_xydirection(self):
    '''
    Returns a non_zero list of random floats with zero z component.
    The direction returned is a unit vector.
    '''
    # Random list
    tuple_list = ([random.uniform(-1,1),random.uniform(-1,1),
      random.uniform(-1,1)])

    # All are non-zero
    if all(tuple_list):
      tuple_list[2] = 0
      return helpers.make_unit(tuple(tuple_list))

    # All are zero - try again
    else:
      return self.non_zero_xydirection()

  def get_repair_beam_direction(self):
    '''
    Returns the xy direction at which the support beam should be set (if none is
    found). Currently, we just add a bit of disturbace while remaining within 
    the range that the robot was set to search.
    '''
    #pdb.set_trace()
    direction = self.Body.readFromMemory('preferred_direction')

    # No preferred direction, so beam was vertically above use
    if direction is None:
      return None

    # Add a bit of disturbace
    else:

      # Project onto xy_plane and make_unit
      xy = helpers.make_unit((direction[0],direction[1],0))
      xy_perp = (-1 * xy[1],xy[0],0)

      # Obtain disturbance based on "search_angle"
      limit = helpers.ratio(BConstants.beam['direction_tolerance_angle'])
      scale = random.uniform(-1 * limit,limit)
      disturbance = helpers.scale(scale,xy_perp)

      return helpers.sum_vectors(disturbance,xy)

  def get_angles(self,support = True):
    if support:
      mini,maxi = (self.get_angle('support_angle_min'), self.get_angle(
        'support_angle_max'))
    else:
      mini,maxi = (self.get_angle('min_angle_constraint'), self.get_angle(
        'max_angle_constraint'))

    return mini,maxi

  def get_angle(self,string):
    '''
    Returns the appropriate ratios for support beam construction
    '''
    angle = BConstants.beam[string]
    return angle

  def move(self, direction, beam):
    '''
    Moves the robot in direction passed in and onto the beam specified
    '''
    length = helpers.length(direction)

    # The direction is smaller than the determined step, so move exactly by 
    # direction
    if length < self.Body.step:
      new_location = helpers.sum_vectors(self.Body.getLocation(), direction)
      # decide if we're climbing off the structure
      newbeam = None if self.climb_off(new_location) else beam
      self.Body.changeLocationOnStructure(new_location, newbeam)

      # call do_action again since we still have some distance left, and update
      # step to reflect how much distance is left to cover
      self.Body.step = self.Body.step - length

      # Reset step in preparation for next timestep
      if helpers.compare(self.Body.step,0):
        self.Body.step == ROBOT['step_length']

      # We still have steps to go, so run an analysis if necessary
      elif self.Body.beam is not None:
        # Run analysis before deciding to get the next direction
        if not self.Body.model.GetModelIsLocked() and self.Body.needData():
          errors = helpers.run_analysis(self.Body.model)
          if errors != '':
            # pdb.set_trace()
            pass

        # Get next direction
        self.Body.addToMemory('next_direction_info', self.get_direction())

        # Unlock the results so that we can actually move
        if self.Body.model.GetModelIsLocked():
          self.Body.model.SetModelIsLocked(False)

        # Move
        self.do_action()

      # We climbed off
      else:
        assert not self.Body.model.GetModelIsLocked()
        
        self.do_action()

    # The direction is larger than the usual step, so move only the step in the 
    # specified direction
    else:
      movement = helpers.scale(self.Body.step, helpers.make_unit(direction))
      new_location = helpers.sum_vectors(self.Body.getLocation(), movement)
      newbeam = None if self.climb_off(new_location) else beam
      self.Body.changeLocationOnStructure(new_location, newbeam)

  def get_direction(self):
    ''' 
    Figures out which direction to move in. This means that if the robot is 
    carrying a beam, it wants to move upwards. If it is not, it wants to move 
    downwards. So basically the direction is picked by filtering by the 
    z-component
    '''
    # Get all the possible directions, as normal
    info = self.Body.getAvailableDirections()

    # Filter out directions which are unfeasable if we have an analysis result
    # available
    if self.Body.model.GetModelIsLocked():
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
        directions = self.filter_directions(info['directions'])

        # We are on the structure
        if directions != {}:
          beam_name,direction = self.elect_direction(self.filter_directions(
            info['directions']))

        # This happens when we are climbing off the structure
        else:
          beam_name, direction = self.elect_direction(info['directions'])

    # Otherwise we do have a set of directions taking us in the right place, so 
    # randomly pick any of them. We will change this later based on the analysis
    else:
      beam_name, direction = self.elect_direction(directions)

    return {  'beam'      : info['box'][beam_name],
              'direction' : direction }

  def filter_feasable(self,dirs):
    '''
    Filters the set of dirs passed in to check that the beam can support a robot
    + beam load if the robot were to walk in the specified direction to the
    very tip of the beam.
    This function is only ever called if an analysis model exists.

    Additionally, this function stores information on the beams that need to be 
    repaired. This is stored in self.Body.addToMemory('broken'], which is originally set
    to none.
    '''
    # Sanity check
    assert self.Body.model.GetModelIsLocked()

    results = {}
    # If at a joint, cycle through possible directions and check that the beams
    # meet the joint_limit. If they do, keep them. If not, discard them.
    if self.Body.atJoint():
      
      # Cycle through directions
      for name, directions in dirs.items():

        # If the name is our beam and we can read moment from beams, 
        # do a structural check instead of a joint check
        if (ROBOT['read_beam'] and 
          ((self.Body.beam.name == name and self.beam_check(name)) or 
          (self.Body.beam.name != name and self.joint_check(name)))):
          results[name] = directions

        # Otherwise, do a joint_check for all beams
        elif self.joint_check(name):
          results[name] = directions

        # It joint check failed, only keep down directions
        else:

          # Keep only the directions that take us down
          new_directions = ([direction for direction in directions if 
            helpers.compare(direction[2],0) or direction[2] < 0])
          if len(new_directions) > 0:
            results[name] = new_directions

          # Add beam to broken
          beam = self.Body.structure.get_beam(name,self.Body.getLocation())
          if not any(beam in broken for broken in self.Body.readFromMemory('broken')):
            moment = self.Body.getMoment(name)
            lst = self.Body.readFromMemory('broken')
            lst.append((beam,moment))
            self.Body.addToMemory('broken', lst)

    # Not at joint, and can read beam moments
    elif ROBOT['read_beam']:

      # Sanity check (there should only be one beam in the set of directions if
      # We are not at a joint)
      assert len(dirs) == 1

      # Check beam
      if self.beam_check(self.Body.beam.name):
        results = dirs

      # Add the beam to the broken
      else:

        # Keep only the directions that take us down
        for name,directions in dirs.items():
          new_directions = ([direction for direction in directions if 
            helpers.compare(direction[2],0) or direction[2] < 0])
          if len(new_directions) > 0:
            results[name] = new_directions

        # Beam is not already in broken
        if not any(self.Body.beam in broken for broken in self.Body.readFromMemory('broken')):
          moment = self.Body.getMoment(name)
          lst = self.Body.readFromMemory('broken')
          lst.append((self.Body.beam,moment))
          self.Body.addToMemory('broken', lst)

    # We aren't reading beams, so we keep all the directions if not at a joint
    else:
      results = dirs

    return results

  def joint_check(self,name):
    moment = self.Body.getMoment(name)
    return moment < BConstants.beam['joint_limit']

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

      # Pick a direction from those that are parallel (so we continue moving)
      # in our preferred direction
      else:
        return self.pick_direction(temp)

    # We are not at a joint and we have a previous direction - keep direction
    if not self.Body.atJoint() and self.Body.readFromMemory('previous_direction') is not None:

      # Pull a direction parallel to our current from the set of directions
      direction_info = next_dict(self.Body.readFromMemory('previous_direction'),directions)

      if direction_info is not None:
        return direction_info

    # If we get to this point, either we are at a joint, we don't have a 
    # previous direction, or that previous direction is no longer acceptable
    return self.pick_direction(directions)