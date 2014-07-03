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
    print(self.Body.name, self.Body.num_beams)
    if self.Body.num_beams == 0:
      if helpers.compare(self.Body.getLocation()[2],0):
        self.pick_up_beam()
      else:
        self.climb_down()
    
    elif self.Body.num_beams > 0 and self.Body.beam != None:
      self.climb_up() #or add new beam to current beam

    elif self.Body.num_beams > 0 and helpers.compare(self.Body.getLocation()[2],0):
      if self.Body.ground() != None:
        self.go_to_beam() if random() <= 0.5 else self.move('NWSE')
      else: 
        BASE_RADIUS = 60
        vector_to_site = helpers.make_vector(self.Body.getLocation(), CONSTRUCTION['center'])
        if helpers.length(vector_to_site) <= BASE_RADIUS: 
          self.build_base() if random() <= 0.5 else self.move('NWSE')
        else:
          self.go_to_construction_site() if random() <= 0.75 else self.move('NWSE')
    
    else:
      print('Hmm, what to do?')

  # move in certain direction (random by default) for ground movement only
  def move(self, angle=random()*360):
    def random_NWSE():
      rand = int(random()*4)
      if rand == 0: return 90   #forward
      if rand == 1: return 180  #left
      if rand == 2: return 270  #backward
      if rand == 3: return 0    #right
    if angle == 'NWSE': angle = random_NWSE()
    rad = radians(angle)
    direction = helpers.make_vector((0,0,0),(cos(rad),sin(rad),0))
    new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
      self.Body.step, helpers.make_unit(direction)))
    self.Body.changeLocalLocation(new_location)

  # move on structure
  def climb(self, location, beam):
    length = helpers.length(location)
    if length < self.Body.step:
      new_location = helpers.sum_vectors(self.Body.getLocation(), location)
    else:
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(location)))
    if self.Body.model.GetModelIsLocked():
          self.Body.model.SetModelIsLocked(False)
    self.Body.changeLocationOnStructure(new_location, beam)

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

  # Called when robot decides to climb a certain ground beam.
  # Robot is moved to base of beam in one step
  def go_to_beam(self):
    beam_info = self.Body.ground()
    beam, distance, direction = beam_info['beam'], beam_info['distance'], beam_info['direction']
    #self.move(direction, beam)
    new_location = helpers.sum_vectors(self.Body.getLocation(), direction)
    self.Body.changeLocationOnStructure(new_location, beam)

  def build_base(self):
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
        # Calculate the actual endpoint of the beam (now that we know direction 
        # vector)
        return (i,helpers.beam_endpoint(i,j))
    pivot = self.Body.getLocation()
    ground_angle = radians(BConstants.beam['ground_angle'])
    random_angle = radians(random()*360)
    height = sin(ground_angle)
    radius = cos(ground_angle)
    x, y, z = radius*cos(random_angle), radius*sin(random_angle), height
    end_coordinates = (x,y,z)
    endpoint = helpers.sum_vectors(pivot,helpers.scale(BEAM['length'],\
                 helpers.make_unit(end_coordinates)))
    i, j = check(pivot, endpoint)
    self.Body.addBeam(i,j)
  
  def climb_down(self):
    # We want to go in available direction with largest negative delta z 
    info = self.Body.getAvailableDirections()
    direction = (0,0,0)
    beam = self.Body.beam
    steepest = float('Inf')
    for beam_name, loc in info['directions'].items():
      (x,y,z) = (loc[0][0], loc[0][1], loc[0][2])
      if z < steepest: 
        direction = (x,y,z)
        steepest = z
        beam = beam_name
    self.climb(direction,beam)
    
  def climb_up(self):
    # We want to go in available direction with largest positive delta z 
    info = self.Body.getAvailableDirections()
    direction = (0,0,0)
    beam = self.Body.beam
    steepest = -float('Inf')
    print(info['directions'])
    for beam_name, loc in info['directions'].items():
      (x,y,z) = (loc[0][0], loc[0][1], loc[0][2])
      if z > steepest: 
        direction = (x,y,z)
        steepest = z
        beam = beam_name
    self.climb(direction,beam)
    if random() <= 0.1: self.Body.discardBeams()

















