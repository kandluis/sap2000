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
how to access the API for the body. 
'''
class SimpleBrain(BaseBrain):
  def __init__(self,Robot):
    super(ExampleBrain,self).__init__(Robot)


'''
Currently used brain class object.
'''
class Brain(objec):
  def __init__(self):
    pass

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
      self.decision_helper();

  def performAction(self):
    self.do_action()


  '''
  Brain Helper functions
  '''

  def pre_decision(self):
    '''
    Takes care of resetting appropriate values.
    '''
    # We build almost never.
    self.start_construction = False
    self.step = ROBOT['step_length']
    self.memory['broken'] = []

  def climb_off(self,loc):
    '''
    Returns whether or not the robot should climb off the structure. Additionally,
    sets some special variables
    '''
    # On the xy-plane with no beams OR repairing
    if helpers.compare(loc[2],0) and (self.num_beams == 0 or self.search_mode):
      
      # Not repairing, so calculate direction
      if not self.search_mode:
        direction = helpers.make_vector(self.location,HOME['center'])
        direction = (direction[0],direction[1],0)
        self.ground_direction = direction

      return True
    
    else:

      # Resetting to None if not in search_mode
      self.ground_direction = (None if not self.search_mode else 
        self.ground_direction)

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
      direction = (random.uniform(-1 * self.step, self.step), random.uniform(
        -1 * self.step, self.step), 0)

      # The they can't all be zero!
      if helpers.compare(helpers.length(direction),0):
        return random_direction()
      else:
        step = helpers.scale(self.step,helpers.make_unit(direction))
        predicted_location = helpers.sum_vectors(step, self.location)

        # Check the location
        if helpers.check_location(predicted_location):
          return direction
        else:
          return random_direction()

    # If we have a currently set direction, check to see if we will go out of 
    # bounds.
    if self.ground_direction != None:
      step = helpers.scale(self.step,helpers.make_unit(self.ground_direction))
      predicted_location = helpers.sum_vectors(step, self.location)

      # We are going out of bounds, so set the direction to none and call 
      # yourself again (to find a new location)
      if not helpers.check_location(predicted_location):
        self.ground_direction = None
        return self.get_ground_direction()

      # Here, we return the right direction
      else:
        assert self.ground_direction != None
        return self.ground_direction

    # We don't have a direction, so pick a random one (it is checked when we 
    # pick it)
    else:
      self.ground_direction = random_direction()
      return self.ground_direction

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
      new_location = helpers.sum_vectors(self.location,helpers.scale(self.step,
        helpers.make_unit(direction)))

      # Move
      self.change_location_local(new_location)

    # A beam is nearby
    else:
      dist, close_beam, direction = (result['distance'], result['beam'],
        result['direction'])

      # If close enough, just jump on it
      if dist < self.step:
        self.move(direction,close_beam)

      # Otherwise, walk towards it
      else:
        # Scale direction to be step_size
        direction = helpers.scale(self.step,helpers.make_unit(direction))
        new_location = helpers.sum_vectors(self.location,helpers.scale(
          self.step, helpers.make_unit(direction)))

        # Move
        self.change_location_local(new_location)

    def pre_decision(self):
    '''
    Takes care of resetting appropriate values
    '''
    self.step = ROBOT['step_length']

  def movable_decide(self):
    '''
    Later classes need direct access to this method
    '''
    # If we're not on a beam, then we will wander on the ground
    if self.beam is None:
      # reset steps
      self.next_direction_info = None

    # Otherwise, we are not on the ground and we decided not to build, so pick 
    # a direction and store that
    else:
      # Before we decide, we need to make sure that we have access to analysis
      # results. Therefore, check to see if the model is locked. If it is not,
      # then execute and analysis.
      if not self.model.GetModelIsLocked() and self.need_data():
        errors = helpers.run_analysis(self.model)
        assert errors == ''

      self.next_direction_info = self.get_direction()

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
    if self.beam is not None:
      assert self.next_direction_info != None
      self.move(self.next_direction_info['direction'],
        self.next_direction_info['beam'])
      self.next_direction_info = None

    # We have climbed off, so wander about 
    else:
      self.wander()
