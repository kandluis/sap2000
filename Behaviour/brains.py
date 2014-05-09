from Helpers import helpers
from robots.automaton import Automaton
from SAP2000.constants import EOBJECT_TYPES
import pdb, random

from variables import BEAM, ROBOT,PROGRAM, VISUALIZATION
from construction import CONSTRUCTION

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Implementation of different robot brains. 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class BaseBrain(object):
  def __init__(self,Robot):
    # access to the robot body; functions are detailed in the documentation file
    # Code for the robot can be found in /World/robot.py
    self.Body = Robot


class ExampleBrain(BaseBrain):
  def __init__(self,Robot):
    super(ExampleBrain,self).__init__(Robot)

  def decide(self):
    '''
    This function is called during the simulation before the act function is called.
    The brain should perform the task of deciding what actions to perform next.

    In particular, note that self.Body.addToMemory(key,value) allows for storing 
    information in the Body. 
    '''
    pass

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
    super(ExampleBrain,self).__init__(Robot)


'''
Currently used brain class object. This is the final implementation of the summer
simulation that have here.
'''
class Brain(BaseBrain):
  def __init__(selfm,Robot):
    super(Brain,self).__init__(Robot)

    # Setup default values for memory storage
    self.Body.addToMemory('search_mode', False)
    self.Body.addToMemory('start_construction', False)
    self.Body.addToMemory('ground_direction', None)
    self.Body.addToMemory('ground_tendencies', [None, None, None])

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
      self.Body.addToMemory('start_construction', True)

    # Movement decisions
    else:
      self.decision_helper()

  def performAction(self):
    self.do_action()

  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Brain Helper functions
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def beam_check(self,name):
    '''
    Checks a beam to see whether it is in a state that requires repair
    '''
    moment = self.Body.getMoment(name)

    ##### THIS SHOULDN"T BE HERE
    e1,e2 = self.Body.structure.get_endpoints(name,self.Body.location)
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
        direction = helpers.make_vector(self.Body.location,HOME['center'])
        direction = (direction[0],direction[1],0)
        self.Body.addToMemory('ground_direction', direction)

      return True
    
    else:

      # Resetting to None if not in search_mode
      groundirection = None if not self.Body.readFromMemory('search_mode')
       else self.Body.readFromMemory('ground_direction')
      self.Body.addToMemory('ground_direction', groundirection)

      return False

  def get_ground_direction(self):
    ''' 
    In future classes, this function can be altered to return a preferred 
    direction,  but currently it only returns a random feasable direction if no
    direction is assigned for the robot (self.ground_direction)
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
        predicted_location = helpers.sum_vectors(step, self.Body.location)

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
      predicted_location = helpers.sum_vectors(step, self.Body.location)

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

  def wander(self):
    '''
    When a robot is not on a structure, it wanders around randomly. The 
    wandering is restricted to the 1st octant in global coordinates. If the 
    robot is near enough a beam to be on it in the next time step, it jumps on 
    the beam. The robots have a tendency to scale the structure, per se, but are
    restricted to their immediate surroundings.
    '''
    # Check to see if robot is on a beam. If so, pick between moving on it or 
    # off it.
    result = self.ground()

    # Nothign nearby
    if result is None:
      # Get direction
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.Body.location,helpers.scale(self.Body.step,
        helpers.make_unit(direction)))

      # Move
      self.change_location_local(new_location)

    # A beam is nearby
    else:
      dist, close_beam, direction = (result['distance'], result['beam'],
        result['direction'])

      # If close enough, just jump on it
      if dist < self.Body.step:
        self.move(direction,close_beam)

      # Otherwise, walk towards it
      else:
        # Scale direction to be step_size
        direction = helpers.scale(self.Body.step,helpers.make_unit(direction))
        new_location = helpers.sum_vectors(self.Body.location,helpers.scale(
          self.Body.step, helpers.make_unit(direction)))

        # Move
        self.Body.change_location_local(new_location)

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
      if not self.model.GetModelIsLocked() and self.Body.need_data():
        errors = helpers.run_analysis(self.model)
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
    In movable, simply moves the robot to another location.
    '''
    # We're on a beam but decided not to build, so get direction we 
    # decided to move in, and move.
    if self.Body.beam is not None:
      next_direction_info = self.Body.readFromMemory('next_direction_info')
      assert next_direction_info != None
      self.move(next_direction_info['direction'],
        next_direction_info['beam'])
      self.Body.addToMemory('next_direction_info', None)

    # We have climbed off, so wander about 
    else:
      self.wander()

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Construction Decision Helper functions
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  def support_xy_direction(self):
    '''
    Improves the construction direction so that we take into account the angle
    at which our current beam is located, and the verticality of the beam we
    are attempting to reach. This returns a unit direction (always should!)
    '''
    # If we're on the ground, then continue doing as before
    if self.Body.beam is None:
      return super(Repairer,self).support_xy_direction()

    else:
      # Get repair beam vector
      b_i,b_j = self.Body.structure.get_endpoints(self.Body.readFromMemory('broken_beam_name'),
        self.Body.location)
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
          return super(Repairer,self).support_xy_direction()

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
          return super(Repairer,self).support_xy_direction()

        else:
          return super(Repairer,self).support_xy_direction()

  def support_vertical_change(self):
    # Get vertical vector 
    change_vector = super(Repairer,self).support_vertical_change()

    # If we're on the ground, just return (no rotation necessary)
    if self.Body.beam is None:
      return change_vector

    # Otherwise, rotate it based on our current beam
    else:
      # Debugging
      # pdb.set_trace()
      if self.readFromMemory('previous_direction') is None:
        #pdb.set_trace()
        pass

      # Get the correct vector for the current beam
      i,j = self.Body.beam.endpoints
      current_vector = helpers.make_vector(i,j)
      
      # Find rotation from vertical
      angle = helpers.smallest_angle((0,0,1),current_vector)
      rotation_angle = 180 - angle if angle > 90 else angle

      vertical_angle = abs(BConstants.beam['support_angle'] - rotation_angle)

      return super(Repairer,self).support_vertical_change(angle=vertical_angle)
  
  def support_beam_endpoint(self):
    '''
    Returns the endpoint for a support beam
    '''
    #pdb.set_trace()
    # Get broken beam
    e1,e2 = self.Body.structure.get_endpoints(self.Body.readFromMemory('broken_beam_name'),
      self.Body.location)

    # Direction
    v = helpers.make_unit(helpers.make_vector(e1,e2))

    # Get pivot and repair beam midpoint
    pivot = self.Body.location
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
    sorted_angles = self.local_angles(pivot,endpoint)
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
        support_vector = helpers.make_vector(self.Body.location,coord)
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
      return super(Repairer,self).support_beam_endpoint()

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

      return super(Repairer,self).remove_specific(new_dirs)

    return super(Repairer,self).remove_specific(dirs)


  def local_rules(self):
    '''
    Overriding so we can build support beam
    '''
    # If we ran our course with the support, construct it
    if (((self.Body.beam is not None and self.Body.readFromMemory('new_beam_steps') == 0) or (
      helpers.compare(self.Body.location[2],0) and 
      self.Body.readFromMemory('new_beam_ground_steps') == 0)) and 
      self.Body.readFromMemory('construct_support')):
      return True

    # Local rules as before
    else:
      return super(DumbRepairer,self).local_rules()

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
    self.Body.addToMemory('ground_direction',self.get_preferred_direction(
      self.readFromMemory('preferred_direction')))

    # Travel down !
    self.Body.addToMemory('pos_z',False)

    # Store name of repair beam
    self.Body.addToMemory('broken_beam_name',beam.name)

    # Number of steps to search once we find a new beam that is close to
    # parallel to the beam we are repairing (going down, ie NOT support beam)
    length = BEAM['length'] * math.cos(
      math.radians(BConstants.beam['support_angle']))
    self.Body.addToMemory('new_beam_steps',math.floor(length/ROBOT['step_length'])+1)
    groundsteps = self.Body.readFromMemory('new_beam_steps') if
      self.ground_direction is None else self.memory['new_beam_steps'] - 1 + math.floor(
        math.sin(math.radians(angle_with_vertical)) * self.memory['new_beam_steps']))
    self.Body.addToMemory('new_beam_ground_steps',groundsteps)

    # So the entire robot knows that we are in repair mode
    self.repair_mode = True
    self.search_mode = True
