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
Implementation of robot brain. 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class BaseBrain:
  __metaclass__=ABCMeta
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

class Brain(BaseBrain):
  def __init__(self,Robot):
    super().__init__(Robot)

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
    pass

  def do_action(self):
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


    















