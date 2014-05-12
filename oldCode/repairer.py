from Helpers import helpers
from oldCode.worker import Worker
import math, pdb, random

from variables import BEAM, ROBOT
from construction import CONSTRUCTION

from Behaviour import constants as BConstants

#DONE
class DumbRepairer(Worker):
  def __init__(self,name,structure,location,program):
    super(DumbRepairer,self).__init__(name,structure,location,program)

    # Number of steps we spend searching for a support beam once we encounter a
    # new beam
    self.memory['new_beam_steps'] = 0

    # Same as above, but on the ground - since the ground is already a horizontal
    # support beam
    self.memory['new_beam_ground_steps'] = 0

    # Stores name of beam to be reinforced (so we know when we're no longer on it)
    self.memory['broken_beam_name'] = ''

    # Stores the previous beam we were on
    self.memory['previous_beam'] = None

    # Constains repair data so we can write it out to file in main.py
    self.repair_data = ''

# Done
  def current_state(self):
    state = super(DumbRepairer,self).current_state()
    return state

# DONE
  def repairing(self):
    '''
    This is run when repairing, so as to set the right values when filtering and
    when picking directions
    '''
    # If we are at a joint, we might move up but MUST move in right x and y
    if self.at_joint():

      # No longer care if we move up or down
      self.memory['pos_z'] = None
      self.memory['dir_priority'] = [1,1,1]
    else:

      # Want to move down
      self.memory['pos_z'] = False
      self.memory['dir_priority'] = [1,1,0]

# DONE
  def construction_mode(self):
    '''
    Resets the robot to go back into construction mode (leaves some variables
     - such as the repair_beam_direction and the broken_beam_name available)
    '''
    self.memory['new_beam_steps'] = 0
    self.memory['new_beam_ground_steps'] = 0
    self.memory['previous_beam'] = None
    self.memory['pos_z'] = True
    self.memory['pos_y'] = None
    self.memory['pos_x'] = None
    self.memory['dir_priority'] = [1,1,0]
    self.repair_mode = False
    self.search_mode = False

# DONE
  def add_support_mode(self):
    '''
    Sets up the construction of a support beam
    '''
    # Return to construct mode
    self.construction_mode()

    # But specify steps, and that we need to construct a support
    self.memory['broken'] = []
    self.memory['new_beam_steps'] = 1
    self.memory['new_beam_ground_steps'] = 1
    self.memory['construct_support'] = True

# DONE
  def ground_support(self):
    '''
    Looks for a support from the ground
    '''
    # We have run our course, so add the support
    if self.memory['new_beam_ground_steps'] == 0:
      self.add_support_mode()
      self.ground_direction = helpers.scale(-1,self.ground_direction)

    self.memory['new_beam_ground_steps'] -= 1

# DONE
  def find_support(self):
    '''
    Looks for a support beam on the structure
    '''
    # We did not find a beam in the number of steps we wanted (go back to build
    # mode, but with the condition to build in exactly one timestep)
    if self.memory['new_beam_steps'] == 0:
      self.add_support_mode()

    self.memory['new_beam_steps'] -= 1
    self.memory['new_beam_ground_steps'] -= 1

# DONE
  def decide(self):
    '''
    Overwritting to allow for repair work to take place
    '''
    if self.search_mode and self.repair_mode:
      self.pre_decision()

      # We have moved off the structure entirely, so wander
      if self.beam is None:
        self.ground_support()

      # We've moved off the beam, so run the search support routine
      elif (self.memory['broken_beam_name'] != self.beam.name and 
        self.search_mode and self.memory['broken_beam_name'] != ''):

        # Remember the beam we moved onto right after the broken one
        if self.memory['previous_beam'] is None:
          self.memory['previous_beam'] = self.beam.name

        # We have found a support beam, so return to construct mode (the support beam is vertical)
        if (self.memory['previous_beam'] != self.beam.name and (
          self.memory['previous_direction'] is None or 
          self.memory['previous_direction'][1][2] > 0 or helpers.compare(
            self.memory['previous_direction'][1][2],0))):
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
    elif self.repair_mode:
      if (helpers.compare(helpers.distance(self.location,
          self.beam.endpoints.j),self.step / 2)):
        self.start_contruction = True
        self.memory['broken'] = []

    # Build Mode
    else:
      super(DumbRepairer,self).decide()

# DONE
  def no_available_direction(self):
    '''
    No direction takes us where we want to go, so check to see if we need to 
      a) Construct
      b) Repair
    '''
    # Initialize repair mode if there are broken beams (and you can fix)
    if self.memory['broken'] != [] and self.num_beams > 0:
      beam, moment = max(self.memory['broken'],key=lambda t : t[1])

      # Print to console
      string = "{} is starting repair of beam {} which has moment {} at {}".format(
        self.name,beam.name,str(moment),str(self.location))

      # This is a special repair of the moment is zero
      if moment == 0:
        string += ". This repair occured due to special rules."
      print(string)

      # Store, to output into file later
      self.repair_data = string
      
      # switch to repair mode with the beam as the one being repaired
      self.start_repair(beam)

    else:

      # Do parent's work
      super(DumbRepairer,self).no_available_direction()

# DONE
  def get_preferred_direction(self,beam):
    '''
    Returns the preferred direction - this is the direction towards which the 
    robot wants to move when looking for an already set support tube.
    The direction is a unit vector
    '''
    # Calculate direction of repair (check 0 dist, which means it is perfectly
    # vertical!)
    i, j = beam.endpoints.i, beam.endpoints.j
    v1 = helpers.make_vector(self.location,j)
    v2 = helpers.make_vector(i,self.location)
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

# DONE
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
        self.memory[string] = None
      if coord > 0:
        self.memory[string] = True
      else:
        self.memory[string] = False

    angle_with_vertical = helpers.smallest_angle(helpers.make_vector(
      beam.endpoints.i,beam.endpoints.j),(0,0,1))

    # Get direction of travel
    self.memory['preferred_direction'] = self.get_preferred_direction(beam)

    # Get direction of travel if on the ground based on preferred direction on
    # the structure
    self.ground_direction = self.get_preferred_ground_direction(
      self.memory['preferred_direction'])

    # Travel down !
    self.memory['pos_z'] = False

    # Store name of repair beam
    self.memory['broken_beam_name'] = beam.name

    # Number of steps to search once we find a new beam that is close to
    # parallel to the beam we are repairing (going down, ie NOT support beam)
    length = BEAM['length'] * math.cos(
      math.radians(BConstants.beam['support_angle']))
    self.memory['new_beam_steps'] = math.floor(length/ROBOT['step_length'])+1
    self.memory['new_beam_ground_steps'] = (self.memory['new_beam_steps'] if
      self.ground_direction is None else self.memory['new_beam_steps'] - 1 + math.floor(
        math.sin(math.radians(angle_with_vertical)) * self.memory['new_beam_steps']))

    # So the entire robot knows that we are in repair mode
    self.repair_mode = True
    self.search_mode = True

# DONE
  def local_rules(self):
    '''
    Overriding so we can build support beam
    '''
    # If we ran our course with the support, construct it
    if (((self.beam is not None and self.memory['new_beam_steps'] == 0) or (
      helpers.compare(self.location[2],0) and 
      self.memory['new_beam_ground_steps'] == 0)) and 
      self.memory['construct_support']):
      return True

    # Local rules as before
    else:
      return super(DumbRepairer,self).local_rules()

class Repairer(DumbRepairer):
  '''
  Fixes the way that beams are constructed. This is the class where we clear up
  behavioural bugs
  '''
#DONE
  def __init__(self,name,structure,location,program):
    super(Repairer,self).__init__(name,structure,location,program)

    # Robots have a tendency to return to the previous area of repair
    self.memory['ground_tendencies'] = [None,None,None]

# DONE
  def pickup_beams(self):
    '''
    Resets the robot's broken settings. Might change this later
    '''
    self.memory['broken'] = []
    self.memory['broken_beam_name'] = ''

    super(Repairer,self).pickup_beams()

# DONE
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

      # Get the correct vector for the current beam
      # Remember - we travel in the opposite direction as normal when building
      # the support beam, so that's why this seems opposite of normal
      c_i,c_j = self.beam.endpoints
      current_vector = (helpers.make_vector(c_j,c_i) if 
        self.memory['previous_direction'][1][2] > 0 else helpers.make_vector(
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

# DONE
  def support_vertical_change(self):
    # Get vertical vector 
    change_vector = super(Repairer,self).support_vertical_change()

    # If we're on the ground, just return (no rotation necessary)
    if self.beam is None:
      return change_vector

    # Otherwise, rotate it based on our current beam
    else:
      # Debugging
      # pdb.set_trace()
      if self.memory['previous_direction'] is None:
        #pdb.set_trace()
        pass

      # Get the correct vector for the current beam
      i,j = self.beam.endpoints
      current_vector = helpers.make_vector(i,j)
      
      # Find rotation from vertical
      angle = helpers.smallest_angle((0,0,1),current_vector)
      rotation_angle = 180 - angle if angle > 90 else angle

      vertical_angle = abs(BConstants.beam['support_angle'] - rotation_angle)

      return super(Repairer,self).support_vertical_change(angle=vertical_angle)

# DONE
  def support_beam_endpoint(self):
    '''
    Returns the endpoint for a support beam
    '''
    #pdb.set_trace()
    # Get broken beam
    e1,e2 = self.structure.get_endpoints(self.memory['broken_beam_name'],
      self.location)

    # Direction
    v = helpers.make_unit(helpers.make_vector(e1,e2))

    # Get pivot and repair beam midpoint
    pivot = self.location
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
      if self.beam is None:
        return simple

      # On a beam, so check our support_angle_difference
      else:
        beam_vector = helpers.make_vector(self.beam.endpoints.i,
          self.beam.endpoints.j)
        support_vector = helpers.make_vector(self.location,coord)
        angle = helpers.smallest_angle(beam_vector,support_vector)
        real_angle = abs(90-angle) if angle > 90 else angle
        
        return simple and real_angle > BConstants.beam['support_angle_difference']

    return_coord = None
    for coord,angle in sorted_angles:
      if acceptable_support(angle,coord) and helpers.on_line(e1,e2,coord):
        self.memory['broken_beam_name'] = ''
        return coord
      elif acceptable_support(angle,coord):
        return_coord = coord

    if return_coord is not None:
      return return_coord
    else:  
      # Otherwise, do default behaviour
      return super(Repairer,self).support_beam_endpoint()

# DONE
  def remove_specific(self,dirs):
    '''
    We don't want to move UP along our own beam when we are repairing and at a
    joint.
    '''
    new_dirs = {}
    if self.at_joint() and self.repair_mode:
      # Access items
      for beam, vectors in dirs.items():
        # If the directions is about our beam, remove references to up.
        # Also do this for our broken beam (we don't want to get stuck climbing
        # onto it again and again in a cycle)
        if beam == self.beam.name or beam == self.memory['broken_beam_name']:
          vectors = [v for v in vectors if v[2] < 0 or helpers.compare(v[2],0)]
          if vectors != []:
            new_dirs[beam] = vectors
        else:
          new_dirs[beam] = vectors

      return super(Repairer,self).remove_specific(new_dirs)

    return super(Repairer,self).remove_specific(dirs)