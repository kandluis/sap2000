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
    # 180 degree approah
    direction = helpers.make_unit(direction) if non_zero else (0,0,1)
    disturbance = self.non_zero_xydirection()
    direction = helpers.make_unit(helpers.sum_vectors(disturbance,direction))
    self.memory['repair_beam_direction'] = direction

    # If vertical, give None so that it can choose a random direction. Otherwise,
    # pick a direction which within 180 degrees of the beam
    ground_direction = direction if random.randint(0,2) != 1 else helpers.scale(
      -1,direction)
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
  '''
  Fixes the way that beams are constructed. This is the class where we clear up
  behavioural bugs
  '''
  def __init__(self,name,structure,location,program):
    super(Repairer,self).__init__(name,structure,location,program)

    # Robots have a tendency to return to the previous area of repair
    self.memory['ground_tendencies'] = [None,None,None]

  def support_xy_direction(self):
    '''
    Improves the construction direction so that we take into account the angle
    at which our current beam is located, and the verticality of the beam we
    are attempting to reach. This returns a unit direction (always should!)
    '''
    # If we're on the ground, then continue doing as before
    if self.beam is None:
      return super(Repairer,self).support_xy_direction()

    else:
      # Get repair beam vector
      b_i,b_j = self.structure.get_endpoints(self.memory['broken_beam_name'],
        self.location)
      repair_vector = helpers.make_vector(b_i,b_j)

      # Debugging
      if self.memory['previous_direction'] is None:
        pdb.set_trace()

      # Get the correct vector for the current beam
      c_i,c_j = self.beam.endpoints
      current_vector = (helpers.make_vector(c_j,c_i) if 
        self.memory['previous_direction'][1][2] > 0 else helpers.make_vector(
          b_i,b_j))

      angle = helpers.smallest_angle(repair_vector,current_vector)

      # If below the specified angle, then place the beam directly upwards (no
      # change in xy)
      if angle < construction.beam['direct_repair_limit']:
        return None
      else:
        vertical = (0,0,1)
        v1,v2 = helpers.make_vector(b_i,c_i), helpers.make_vector(b_i,c_j)

        # We can't get a direction based on beam locations
        if helpers.parallel(vertical,v1) and helpers.parallel(vertical,v2):
          return super(Repairer,self).support_xy_direction()

        # We can use the current beam to decide the direction
        elif not helpers.parallel(vertical,current_vector):
          # Project onto the xy-plane and negate
          if current_vector[2] < 0:
            projection = helpers.make_unit(helpers.scale(-1,(current_vector[0],
              current_vector[1],0)))
          else:
            projection = helpers.make_unit(current_vector[0],current_vector[1],0)
          disturbance = helpers.scale(random.uniform(-1,1),(-projection[1],
            projection[0],projection[2]))
          results = helpers.sum_vectors(projection,disturbance)

          # TODO
          return projection

        elif not helpers.parallel(vertical,repair_vector):
          return super(Repairer,self).support_xy_direction()
        else:
          raise Exception("?")

  def support_vertical_change(self):
    # TODO
    return super(Repairer,self).support_vertical_change()


  def support_beam_endpoint(self):
    '''
    Returns the endpoint for a support beam
    '''
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
        pdb.set_trace()
        # We have an acceptable beam
        if not ((ratio < min_support_ratio or ratio > max_support_ratio) or 
          helpers.compare(ratio,0)):
          # Reset the broken beam name
          self.memory['broken_beam_name'] = ''
          return coord
      
    # Otherwise, do default behaviour
    return super(Repairer,self).support_beam_endpoint()
  '''
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
  '''