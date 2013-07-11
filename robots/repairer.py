from helpers import helpers
from robots.worker import Worker
import construction, math, pdb,variables

class Repairer(Worker):
  def __init__(self,name,structure,location,program):
    super(Repairer,self).__init__(name,structure,location,program)
    # Number of steps we spend searching for a support beam once we encounter a
    # new beam
    self.memory['new_beam_steps'] = 0

    # Stores name of beam to be reinforced (so we know when we're no longer on it)
    self.memory['broken_beam_name'] = ''

    # Repair mode switch
    self.repair_mode = False

  def decide(self):
    '''
    Overwritting to allow for repair work to take place
    '''
    # Repair Mode
    if self.repair_mode:
      self.pre_decision()
      # We've moved off the beam, so run the 
      if self.memory['broken_beam_name'] != self.beam.name:

    super(Repairer,self).decide()

  def no_available_direction(self):
    '''
    No direction takes us where we want to go, so check to see if we need to 
      a) Construct
      b) Repair
    '''
    # Initialize repair mode if there are broken beams
    if self.memory['broken'] != []:
      beam, moment = max(self.memory['broken'],key=lambda t : t[1])
      print("{} is starting repair of {} which has moment {} at {}".format(
        self.name,beam.name,str(moment),str(self.location)))
      
      # Uncomment when ready!
      self.start_repair(beam)

    else:
      # Do parent's work
      super(Repairer,self).no_available_direction()

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
    direction = helpers.make_vector(self.location,j[0])
    self.memory['repair_beam_direction'] = helpers.make_unit(
      helpers.make_vector(self.location,(j[0],j[1],self.location[2])))
    
    # We want to climb down, and travel in 'direction' if possible
    set_dir('pos_x',direction[0])
    set_dir('pos_y',direction[1])
    self.memory['pos_z'] = False

    # Store name of repair beam
    self.memory['broken_beam_name'] = beam.name

    # Number of steps to search once we find a new beam that is close to
    # parallel to the beam we are repairing (going down, ie NOT support beam)
    length = construction.beam['length'] * math.cos(
      construction.beam['support_angle'])
    self.memory['new_beam_steps'] = math.floor(length/variables.step_length)+1

    self.repair_mode = True