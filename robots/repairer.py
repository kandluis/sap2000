from helpers import helpers
from robots.worker import Worker
import construction, math, pdb,variables, random

class DumbRepairer(Worker):
  def __init__(self,name,structure,location,program):
    super(DumbRepairer,self).__init__(name,structure,location,program)
    # Number of steps we spend searching for a support beam once we encounter a
    # new beam
    self.memory['new_beam_steps'] = 0

    # Stores name of beam to be reinforced (so we know when we're no longer on it)
    self.memory['broken_beam_name'] = ''

    # Stores the previous beam we were on
    self.memory['previous_beam'] = None

    # Constains repair data so we can write it out to file in main.py
    self.repair_data = ''

    # We are searching for a support beam (done and done)
    self.search_mode = True

  def current_state(self):
    state = super(DumbRepairer,self).current_state()
    state.update({  'search_mode' : self.search_mode})
    return state

  def repairing(self):
    '''
    This is run when repairing, so as to set the right values when filtering and
    when picking directions
    '''
    # If we are at a joint, we might move up but MUST move in right x and y
    if self.at_joint():
      self.memory['pos_z'] = True
      self.memory['dir_priority'] = [1,1,1]
    else:
      self.memory['pos_z'] = False
      self.memory['dir_priority'] = [1,1,0]

  def construction_mode(self):
    '''
    Resets the robot to go back into construction mode (leaves some variables
     - such as the repair_beam_direction and the broken_beam_name available)
    '''
    self.memory['new_beam_steps'] = 0
    self.memory['previous_beam'] = None
    self.memory['pos_z'] = True
    self.memory['pos_y'] = None
    self.memory['pos_x'] = None
    self.memory['dir_priority'] = [1,1,0]
    self.repair_mode = False
    self.search_mode = False

  def add_support_mode(self):
    '''
    Sets up the construction of a support beam
    '''
    # Return to construct mode
    self.construction_mode()

    # But specify steps, and that we need to construct a support
    self.memory['broken'] = []
    self.memory['new_beam_steps'] = 1
    self.memory['construct_support'] = True

  def ground_support(self):
    '''
    Looks for a support from the ground
    '''
    if self.memory['new_beam_steps'] == 0:
      self.add_support_mode()
      self.ground_direction = helpers.scale(-1,self.ground_direction)

    self.memory['new_beam_steps'] -= 1

  def find_support(self):
    '''
    Looks for a support beam on the structure
    '''
    # We did not find a beam in the number of steps we wanted (go back to build
    # mode, but with the condition to build in exactly one timestep)
    if self.memory['new_beam_steps'] == 0:
      self.add_support_mode()

    self.memory['new_beam_steps'] -= 1


  def decide(self):
    '''
    Overwritting to allow for repair work to take place
    '''
    # Repair Mode
    if self.repair_mode:
      self.pre_decision()

      # We have moved off the structure entirely, so wander
      if self.beam is None:
        self.ground_support()

      # We've moved off the beam, so run the search support routine
      elif (self.memory['broken_beam_name'] != self.beam.name and 
        self.search_mode and self.memory['broken_beam_name'] != ''):
        if self.memory['previous_beam'] is None:
          self.memory['previous_beam'] = self.beam.name

        # We have found a support beam, so return to construct mode (the support beam is vertical)
        if (self.memory['previous_beam'] != self.beam.name and (
          self.memory['previous_direction'] is None or 
          self.memory['previous_direction'][1][2] > 0 or helpers.compare(
            self.memory['previous_direction'][1][2],0))):
          self.construction_mode()

        self.find_support()

        # Move (don't check construction)
        self.movable_decide()

      # Simply move
      else:
        self.movable_decide()

    # Build Mode
    else:
      super(DumbRepairer,self).decide()

  def no_available_direction(self):
    '''
    No direction takes us where we want to go, so check to see if we need to 
      a) Construct
      b) Repair
    '''
    # Initialize repair mode if there are broken beams (and you can fix)
    if self.memory['broken'] != [] and self.num_beams > 0:
      beam, moment = max(self.memory['broken'],key=lambda t : t[1])
      string = "{} is starting repair of beam {} which has moment {} at {}".format(
        self.name,beam.name,str(moment),str(self.location))
      print(string)
      self.repair_data = string
      
      # Uncomment when ready!
      self.start_repair(beam)

    else:
      # Do parent's work
      super(DumbRepairer,self).no_available_direction()

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
      '''
      if helpers.compare(coord,0):
        self.memory[string] = None
      if coord > 0:
        self.memory[string] = True
      else:
        self.memory[string] = False

    # Calculate direction of repair (check 0 dist, which means it is perfectly
    # vertical!)
    j = beam.endpoints.j
    # This is the xy-change, basically
    direction = helpers.make_vector(self.location,(j[0],j[1],self.location[2]))
    # Check to make sure the direction is non-zero. 
    non_zero = not helpers.compare(helpers.length(direction),0)

    # If it is zero-length, then store (0,0,1) as direction. Otherwise, give a 
    # 180 degree approace
    direction = helpers.make_unit(direction) if non_zero else (0,0,1)
    disturbance = self.non_zero_xydirection()
    direction = helpers.make_unit(helpers.sum_vectors(disturbance,direction))
    self.memory['repair_beam_direction'] = direction

    # If vertical, give None so that it can choose a random direction. Otherwise,
    # pick a direction which within 180 degrees of the beam
    self.ground_direction = direction if non_zero else None
    
    # We want to climb down, and travel in 'direction' if possible
    set_dir('pos_x',direction[0])
    set_dir('pos_y',direction[1])
    self.memory['pos_z'] = False

    # Store name of repair beam
    self.memory['broken_beam_name'] = beam.name

    # Number of steps to search once we find a new beam that is close to
    # parallel to the beam we are repairing (going down, ie NOT support beam)
    length = construction.beam['length'] * math.cos(
      math.radians(construction.beam['support_angle']))
    self.memory['new_beam_steps'] = math.floor(length/variables.step_length)+1

    self.repair_mode = True
    self.search_mode = True

  def local_rules(self):
    '''
    Overriding so we can build support beam
    '''
    # If the program is not locked, there are no analysis results so True
    if not self.model.GetModelIsLocked():
      return False

    # Analysis results available
    elif self.memory['new_beam_steps'] == 0 and self.memory['construct_support']:
      return True
    
    return False

class Repairer(DumbRepairer):
  def __init__(self,name,structure,location,program):
    super(Repairer,self).__init__(name,structure,location,program)

    # Robots have a tendency to return to the previous area of repair
    self.memory['ground_tendencies'] = [None,None,None]

  def get_disturbance(self):
    '''
    Returns the disturbance level for adding a new beam at the tip. This is
    modified so that the disturbance compensates for the angle at which the
    current beam lies (using basic math)
    '''
    # TODO
    return super(Repairer,self).get_disturbance()

  def support_beam_endpoint(self):
    # Get broken beam
    e1,e2 = self.structure.get_endpoints(self.memory['broken_beam_name'],
      self.location)

    # Reset the broken beam name
    self.memory['broken_beam_name'] = ''

    if (helpers.compare(e1[2],0) or helpers.compare(e2[1],0) and 
      helpers.compare(self.location[2],0)):
      pivot = self.location
      vertical_endpoint = helpers.sum_vectors(pivot,helpers.scale(
        variables.beam_length,
        helpers.make_unit(construction.beam['vertical_dir_set'])))
      sorted_ratios = self.local_ratios(pivot,vertical_endpoint)
      # Cycle through ratios looking for one that lies on the beam we want
      for coord,ratio in sorted_ratios:
        if helpers.on_line(e1,e2,coord):
          midpoint = helpers.midpoint(e1,e2)
          if helpers.distance(pivot,midpoint) <= construction.beam['length']:
            return midpoint
          else:
            return coord

      # We didn't find an appropriate one, so return default enpoint
      self.memory['construct_support'] = False
      ratio = self.find_nearby_beam_coord(sorted_ratios,pivot)
      return self.get_default(ratio,vertical_endpoint)
      

    # Otherwise, do default behaviour
    return super(Repairer,self).support_beam_endpoint()

class SmartRepairer(Repairer):
  def __init__(self,name,structure,location,program):
    super(SmartRepairer,self).__init__(name,structure,location,program)

  def beam_check(self,name):
    moment = self.get_moment(name)
    e1,e2 = self.structure.get_endpoints(name,self.location)
    xy_dist = helpers.distance((e1[0],e1[1],0),(e2[0],e2[1],0))
    limit = construction.beam['beam_limit'] + (
      xy_dist / construction.beam['length']) * construction.beam['horizontal_beam_limit']

    return (moment < limit or helpers.compare(moment,limit))

  def support_beam_endpoint(self):
    # Get broken beam
    e1,e2 = self.structure.get_endpoints(self.memory['broken_beam_name'],
      self.location)
    # Get pivot and vertical
    pivot = self.location
    vertical_endpoint = helpers.sum_vectors(pivot,helpers.scale(
        variables.beam_length,
        helpers.make_unit(construction.beam['vertical_dir_set'])))

    # Get ratios
    sorted_ratios = self.local_ratios(pivot,vertical_endpoint)
    min_support_ratio,max_support_ratio = self.get_ratios()

    # Cycle through ratios looking for one that is above our limit (not too
    # vertical nor horizontal) that is on our broken beam
    for coord,ratio in sorted_ratios:
      # Build everywhere on the beam excep for the tips.
      if helpers.on_line(e1,e2,coord) and not (helpers.compare_tuple(e1,coord)
        or helpers.compare_tuple(e2,coord)):
        # We have an acceptable beam
        if not ((ratio < min_support_ratio or ratio > max_support_ratio) or 
          helpers.compare(ratio,0)):
          # Reset the broken beam name
          self.memory['broken_beam_name'] = ''
          return coord
      
    # Otherwise, do default behaviour
    return super(SmartRepairer,self).support_beam_endpoint()

class LeanRepairer(SmartRepairer):
  def __init__(self,name,structure,location,program):
    super(SmartRepairer,self).__init__(name,structure,location,program)

  def get_default(self,ratio_coord,vertical_coord):
    '''
    Returns the coordinate onto which the j-point of the beam to construct 
    should lie
    '''
    # No vertical coordinate this time, since we will use a leaning one
    coord = super(LeanRepairer,self).get_default(ratio_coord,None)
    if coord is not None:
      return coord
    # We need to return one that leans
    else:
      xy_dir = self.non_zero_xydirection()
      scale = 1 / helpers.ratio(construction.beam['construction_angle'])
      vertical = helpers.scale(scale,construction.beam['vertical_dir_set'])
      direction = helpers.make_unit(helpers.sum_vectors(xy_dir,vertical))
      endpoint = helpers.sum_vectors(self.location,helpers.scale(
        construction.beam['length'],direction))

      return endpoint
