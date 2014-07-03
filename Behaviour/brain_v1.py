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
        BASE_RADIUS = 120
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
  def move(self, location, beam):
    length = helpers.length(direction)
    if length < self.Body.step:
      new_location = helpers.sum_vectors(self.Body.getLocation(), location)
    else:
      new_location = helpers.sum_vectors(self.Body.getLocation(), helpers.scale( \
                     self.Body.step, helpers.make_unit(location)))
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
    for beam_name, (x,y,z) in info['directions'].items():
      if z < steepest: 
        direction = (x,y,z)
        steepest = z
        beam = beam_name
    move(direction,beam)
    
  def climb_up(self):
    # We want to go in available direction with largest positive delta z 
    info = self.Body.getAvailableDirections()
    direction = (0,0,0)
    beam = self.Body.beam
    steepest = -float('Inf')
    for beam_name, (x,y,z) in info['directions'].items():
      if z > steepest: 
        direction = (x,y,z)
        steepest = z
        beam = beam_name
    move(direction,beam)
    if random() <= 0.1: self.Body.discardBeams()
  
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
    repaired. This is stored in self.Body.addToMemory('broken'), which is originally set
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

        # If joint check failed, only keep down directions
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


  def filter_directions(self,dirs):
    '''
    Filters the available directions and returns those that move us in the 
    desired direction. Overwritten to take into account the directions in
    which we want to move. When climbing down, it will take the steepest path.
    '''
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
  
  def move2(self, direction, beam):
    '''
    Moves the robot in direction passed in and onto the beam specified
    '''
    length = helpers.length(direction)
    print(self.Body.name + str(direction))
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
  '''

















