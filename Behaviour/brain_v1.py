# Python default libraries
from random import *
from math import *
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
  def __init__(self, Robot):
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
  def __init__(self, Robot):
    super().__init__(Robot)
    self.Body.addToMemory('decision',None)
    self.Body.addToMemory('location',self.Body.getLocation())
    self.Body.addToMemory('construction_angle',90)

  def performDecision(self):
    #pdb.set_trace()
    self.decide()

  def performAction(self):
    #pdb.set_trace()
    self.act()

  ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  Brain Helper functions
  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  def decide(self):
    pass

  def act(self):
    if self.Body.num_beams == 0 and helpers.compare(self.Body.getLocation()[2],0):
      self.pick_up_beam()
    elif self.Body.num_beams > 0 and helpers.compare(self.Body.getLocation()[2],0):
      self.go_to_construction_site() if random()*2 == 0 else self.move('NWSE')
    else:
      self.move('NWSE')

  # move in certain direction (random by default)
  def move(self, angle=random()*360):
    def random_NWSE():
      rand = int(random()*4)
      if rand == 0: return 90   #forward
      if rand == 1: return 180  #left
      if rand == 2: return 270  #backward
      if rand == 3: return 0    #right
    if angle == 'NWSE': 
      angle = random_NWSE()
    rad = radians(angle)
    direction = helpers.make_vector((0,0,0),(cos(rad),sin(rad),0))
    new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
      self.Body.step, helpers.make_unit(direction)))
    self.Body.changeLocalLocation(new_location)

  # Called whenever robot does not have a beam while on the ground.
  def pick_up_beam(self, num_beams = ROBOT['beam_capacity']):
    if not self.Body.atHome():
      direction_home = helpers.make_vector(self.Body.getLocation(), HOME['center'])
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(direction_home)))
      self.Body.changeLocalLocation(new_location)
    else: 
      self.Body.pickupBeams(num_beams)

  # Straight to construction site corner
  def go_to_construction_site(self):
    if not self.Body.atSite(): 
      direction_construction = helpers.make_vector(self.Body.getLocation(), CONSTRUCTION['center'])
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(direction_construction)))
      self.Body.changeLocalLocation(new_location)
    else:
      self.Body.discardBeams()

  # Called when robot is at construction site.
  def find_ground_beam(self):
    beam_location = self.Body.ground()


  def build(self):
    pass





















