from helpers import helpers
from robots.modifications import SmartRepairer, LeanRepairer, DeflectionRepairer, RandomUpwardRepairer
from visual import *
import construction, variables

class Swarm:
  def __init__(self,size, structure, program):
    # The number of robots in the swarm
    self.size = size

    # The location of the swarm.
    self.home = construction.home

    # Access to the structure, so we can create repairers
    self.structure = structure

    # Access to the program
    self.model = program

    # create repairers
    self.repairers = {}
    for i in range(size):
      name = "smartrepairer_" + str(i)

      # repairers start at home
      location = helpers.sum_vectors(self.home,(i,0,0)) 
      self.repairers[name] = self.create(name,structure,location,program)

    # Keeps track of visualization data
    self.visualization_data = ''

    # Keeps track of the color each robot should be at each timestep
    self.color_data = ''

  def create(self,name,structure,location,program):
    return RandomUpwardRepairer(name,structure,location,program)

  def decide(self):
    # Tell each robot to make the decion
    for repairer in self.repairers:
      self.repairers[repairer].decide()

      # Add location data
      loc = self.repairers[repairer].location
      location = (loc[0], loc[1], 0) if helpers.compare(loc[2],0) else loc
      self.visualization_data += "{}:{}<>".format(repairer,str(
        helpers.round_tuple(location,3)))

      # Get color data based on what the robot is doing
      color = (1,0,1) if not self.repairers[repairer].repair_mode else (0,1,0)
      self.color_data += "{}:{}<>".format(repairer,str(color))

    self.visualization_data += "\n"
    self.color_data += "\n"

  def act(self):
    # Tell each robot to act
    for repairer in self.repairers:
      self.repairers[repairer].do_action()

  def get_information(self):
    information = {}
    for name, repairer in self.repairers.items():
      information[name] = repairer.current_state()

    return information

  def get_errors(self):
    data = ''
    for name,repairer in self.repairers.items():
      if repairer.error_data != '':
        data += "{}\n".format(repairer.error_data)
        repairer.error_data = ''
    return data

  def get_repair_data(self):
    data = ''
    for name,repairer in self.repairers.items():
      if repairer.repair_data != '':
        data += "{},".format(repairer.repair_data)
        repairer.repair_data = ''
    return data

class ReactiveSwarm(Swarm):
  def __init__(self,size,structure,program):
    super(ReactiveSwarm, self).__init__(size,structure,program)
    # Keeps track of how many robots we have created (in order to keep the 
    # names different)
    self.num_created = size
    self.original_size = size

  def show(self):
    '''
    Renders the colony in 3D. Each time this function is called, the colony is
    rendered.
    '''
    # Cycle through repairers
    for smartrepairer_name, repairer in self.repairers.items():
      # If model exists, move it to new location
      if repairer.simulation_model is not None:
        repairer.simulation_model.pos = repairer.location
    
      # Otherwise create a new model for the robot at the current location
      else:
        repairer.simulation_model = sphere(pos=repairer.location,
          radius=variables.local_radius,make_trail=False)
        repairer.simulation_model.color = (1,0,1)

  def reset(self):
    '''
    Create a spanking new army of repairers the size of the original army!
    '''
    self.repairers = {}
    for i in range(self.original_size):
      name = "smartrepairer_" + str(i)
      location = helpers.sum_vectors(self.home,(i,0,0)) 
      self.repairers[name] = self.create(name,self.structure,location,self.model)

  def need_data(self):
    '''
    Returns whether or not the robots will need to data in order to make 
    decisions. This basically checks to see if they are moving down. If so, then
    they don't need data.
    '''
    for name, repairer in self.repairers.items():
      if (repairer.memory['pos_z'] == True or repairer.memory['pos_z'] == None
        or repairer.beam is not None):
      #if not (repairer.memory['pos_z'] != True or repairer.beam is None):
        return True

    return False

  def new_robots(self, num = 1):
    '''
    Creates new robots at the home location. They line up along the positive
    x-axis. The names are a continuation of the size of the swarm.
    '''
    for i in range(self.num_created, self.num_created + num):
      name = "smartrepairer_" + str(i)
      location = helpers.sum_vectors(self.home,(i - num, 0, 0))
      self.repairers[name] = self.create(name,self.structure,location,self.model)

    self.size += num
    self.num_created += num

  def delete_robot(self, name):
    '''
    Deletes the specified robot from the swarm if it exists
    '''
    if name in self.repairers:
      self.repairers[name].change_location(construction.home, None)
      del(self.repairers[name])
      self.size -= 1
      return True
    else:
      return False

  def delete_random_robot(self):
    '''
    Deletes a random robot from the swarm.
    '''
    # Pick a random repairer
    from random import choice
    smartrepairer_name = choice(self.repairers.keys())

    return self.delete_robot(smartrepairer_name)

  def delete_random_robots(self,num = 1):
    '''
    Deletes the specified number of robots from the swarm. They are selected
    at random. Returns the number of robots successfully deleted.
    '''
    deleted = 0
    for i in range(num):
      if self.size > 0:
        if self.delete_random_robot():
          deleted += 1

    return deleted

  def delete_robots(self, names = []):
    '''
    Deletes the specified robots from the swarm (if found). If no name is passed
    in, it deletes nothing. Returns the number of robots successfully deleted.
    '''
    deleted = 0
    for name in names:
      if delete_robot(name):
        deleted += 1

    return deleted

class SmartSwarm(ReactiveSwarm):
  def __init__(self,size,structure,program):
    super(SmartSwarm, self).__init__(size,structure,program)