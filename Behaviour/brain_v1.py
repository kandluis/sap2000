# Python default libraries
from random import *
from math import *
import pdb
from abc import ABCMeta, abstractmethod

# Local imports
from Helpers import helpers
# constants for simulation
from variables import BEAM, ROBOT, PROGRAM, VISUALIZATION
# constants for construction
from construction import HOME, CONSTRUCTION
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
    Called during the simulation before the act function is called.
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
    self.Body.addToMemory('wandering', -1)

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
    print('>> ' + str(self.Body.name) + ': beams=' + str(self.Body.num_beams))
    if self.Body.num_beams == 0:
      if helpers.compare(self.Body.getLocation()[2],0):
        self.pick_up_beam()
      else:
        self.climb_down()
    
    elif self.Body.num_beams > 0 and self.Body.beam != None:
      if self.Body.atTop(): 
        print('At TOP of beam', self.Body.beam.name)
        self.place_beam('center')  
      else:
        self.climb_up() if random() <= 0.95 else self.place_beam('center')

    elif self.Body.num_beams > 0 and helpers.compare(self.Body.getLocation()[2],0):
      wandering = self.Body.readFromMemory('wandering')
      if not self.Body.atSite() and wandering == -1:
        self.go_to_construction_site()
      else:
        if self.Body.readFromMemory('wandering') < 20:
          wandering+=1
          self.Body.addToMemory('wandering', wandering)
          self.move()
        elif self.Body.ground() != None:
          self.go_to_beam()
        else:
          self.build_base() if random() <= 0.1 else self.move()
    
    else:
      print('Hmm, what to do?')

  # move in certain direction (random by default) for ground movement only
  def move(self, angle='random'):
    def random_NWSE():
      rand = randint(0,3)
      if rand == 0: return 90   #forward
      if rand == 1: return 180  #left
      if rand == 2: return 270  #backward
      if rand == 3: return 0    #right
    if angle == 'NWSE': angle = random_NWSE()
    if angle == 'random': angle = random()*360
    rad = radians(angle)
    direction = helpers.make_vector((0,0,0),(cos(rad),sin(rad),0))
    new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
      self.Body.step, helpers.make_unit(direction)))
    self.Body.changeLocalLocation(new_location)
    return True

  # Called whenever robot does not have a beam while on the ground.
  def pick_up_beam(self, num_beams = ROBOT['beam_capacity']):
    if not self.Body.atHome():
      direction_home = helpers.make_vector(self.Body.getLocation(), HOME['center'])
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(direction_home)))
      self.Body.changeLocalLocation(new_location)
    else: 
      self.Body.pickupBeams(num_beams)
      self.Body.addToMemory('wandering',-1)
    return True

  # Straight to construction site center
  def go_to_construction_site(self):
    vector_to_site = helpers.make_vector(self.Body.getLocation(), CONSTRUCTION['center'])
    if helpers.length(vector_to_site) != 0: 
      direction_construction = helpers.make_vector(self.Body.getLocation(), CONSTRUCTION['center'])
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(direction_construction)))
      self.Body.changeLocalLocation(new_location)
    return True

  # Called when robot decides to climb a certain ground beam.
  # Robot is moved to base of beam in one step
  def go_to_beam(self):
    beam_info = self.Body.ground()
    beam, distance, direction = beam_info['beam'], beam_info['distance'], beam_info['direction']
    #self.move(direction, beam)
    new_location = helpers.sum_vectors(self.Body.getLocation(), direction)
    self.Body.changeLocationOnStructure(new_location, beam)
    return True

  def build_base(self):
    pivot = self.Body.getLocation()
    ground_angle = radians(BConstants.beam['ground_angle'])
    random_angle = radians(random()*360)
    height = sin(ground_angle)
    radius = cos(ground_angle)
    x, y, z = radius*cos(random_angle), radius*sin(random_angle), height
    end_coordinates = (x,y,z) #directional unit vector
    endpoint = helpers.sum_vectors(pivot,helpers.scale(BEAM['length'],\
                 helpers.make_unit(end_coordinates)))
    #try to connect to already present beam
    self.Body.addBeam(pivot,endpoint)
    return True

  def climb_down(self):
    # We want to go in available direction with largest negative delta z 
    # self.Body.model.SetModelIsLocked(False)
    info = self.Body.getAvailableDirections()
    direction = (0,0,0)
    beam = None
    steepest = float('Inf')
    for beam_name, loc in info['directions'].items():
      for (x,y,z) in loc:
        if z < steepest: 
          direction = (x,y,z)
          steepest = z
          beam = self.Body.structure.find_beam(beam_name) 
    self.climb(direction,beam)
    return True
    
  def climb_up(self):
    # We want to go in available direction with largest positive delta z 
    # self.Body.model.SetModelIsLocked(False)
    info = self.Body.getAvailableDirections()
    direction = (0,0,0)
    beam = None
    steepest = -float('Inf')
    #print(info['directions'])
    for beam_name, loc in info['directions'].items():
      for (x,y,z) in loc:
        if z > steepest: 
          direction = (x,y,z)
          steepest = z
          beam = self.Body.structure.find_beam(beam_name)
    self.climb(direction,beam)
    return True

  '''
  To move on structure; method called from either climb_up() or climb_down()
  '''
  def climb(self, location, beam):
    length = helpers.length(location)
    if length <= self.Body.step:
      new_location = helpers.sum_vectors(self.Body.getLocation(), location)
      if new_location[2] == 0: 
        beam = None
        print('climbing beam',None)
      else: print('climbing beam',beam.name)
    else:
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(location)))
      print('climbing beam',beam.name)
    self.Body.model.SetModelIsLocked(False)
    self.Body.changeLocationOnStructure(new_location, beam)
    return True

  '''
  Returns coordinates of where to place beam, given direction/location you want
  to build towards.
  '''
  def get_build_vector(self, build_angle, direction):
    current_beam_direction = self.Body.beam.global_default_axes()[0]
    (x_dir, y_dir, z_dir) = current_beam_direction

    if direction == None:
      random_angle = radians(random()*360)
      height = sin(build_angle)
      radius = cos(build_angle)
      x, y, z = radius*cos(random_angle), radius*sin(random_angle), height
      return (x, y, z)

    if direction == 'center': 
      height = sin(build_angle)
      radius = cos(build_angle)
      position_center = CONSTRUCTION['center']
      position_center = (position_center[0], \
        position_center[1], self.Body.getLocation()[2])
      direction_construction = helpers.make_vector(self.Body.getLocation(), position_center_relative)
      endpoint = helpers.scale(radius, helpers.make_unit(direction_construction))
      x, y, z = endpoint[0]+x_dir, endpoint[1]+y_dir, height+z_dir
      return (x, y, z)
    return False

  '''
  Note: This is omniscient information that the robot needs a sensor for in reality
  '''
  def get_structure_density(self, location, raidus=BEAM['length']):
    boxes = self.Body.structure.get_boxes(location, radius)
    nearby_beams = []
    #print(boxes)
    for box in boxes:
      for beam_name in box.keys():
        if beam_name not in nearby_beams:
          nearby_beams.append(beam_name)
    num_beams = len(nearby_beams)
    return num_beams

  # For building by placing beam on another beam
  def place_beam(self, direction=None):
    # don't make triple joints
    if self.Body.atJoint(): return False
    
    pivot = self.Body.getLocation()
    # don't place beams with a 2 ft. radius from each other
    if self.get_structure_density(pivot, 24) > 1: return False

    build_angle = radians(BConstants.beam['beam_angle'])
    end_coordinates = self.get_build_vector(build_angle, direction)
    print(end_coordinates)
    endpoint = helpers.sum_vectors(pivot,helpers.scale(BEAM['length'],\
                 helpers.make_unit(end_coordinates)))
    # try to connect to already present beam
    
    density = self.get_structure_density(endpoint)
    # location at end of beam you are about to place is too dense,
    # so do not place it.
    if density > BConstants.beam['max_beam_density']: return False
    self.Body.addBeam(pivot,endpoint)
    return True

















