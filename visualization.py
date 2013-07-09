from helpers import helpers
from visual import *
import construction, time, re, variables

class Visualization:
  def __init__(self,outputfolder):
    self.data = []
    self.folder = outputfolder

  def load_data(self,swarm,structure):
    '''
    Loads the data from the files specified
    '''
    def load_file(file_obj,both=True):
      '''
      Loads the date from one file. If the bool both is true, then it loads two
      parts of data as tuples. If it is not, then it loads data_1 as text and 
      data_2 as a tuple.
      '''
      timesteps = []

      # For each line in the file
      for timestep in file_obj:
        timestep_data = []

        # For each item in the line (all items are split by <>)
        # Each item is either a (robot,location) or a (i-end,j-end)
        for item_data in re.split("<>",timestep):

          # We skip the new line character
          if item_data != '\n':

            # Now we split the item into the two data (there is a : between them)
            data_1,data_2 = re.split(":",item_data)

            # Read a float tuple if both, else set it as a string (leave a alone)
            data_1 = (tuple(float(v) for v in re.findall("[-+]?[0-9]*\.?[0-9]+",
              data_1)) if both else data_1)

            # Read float tuple
            data_2 = tuple(float(v) for v in re.findall("[-+]?[0-9]*\.?[0-9]+",
              data_2))

            # Add data to timestep
            timestep_data.append((data_1,data_2))

        # Add timestep to data
        timesteps.append(timestep_data)

      return timesteps

    with open(self.folder + swarm, 'r') as s_file, open(self.folder + structure, 'r') as st_file:
      self.data = zip(load_file(s_file,False),load_file(st_file,True))

  def run(self,fullscreen = True, inverse_speed=.25):
    if self.data == []:
      print("No data has been loaded. Cannot run simulation.")
    else:
      # Setup the scene
      scene = display(title="Robot Simulation",background=(1,1,1))
      scene.autocenter = True
      scene.fullscreen = fullscreen
      scene.range = (variables.beam_length,variables.beam_length,variables.beam_length)
      scene.center = helpers.scale(.5,helpers.sum_vectors(
        construction.construction_location,scene.range))
      scene.forward = (1,0,0)
      scene.up = (0,0,1)
      scene.exit = False

      # Setup the ground
      dim = variables.dim_x,variables.dim_y,variables.epsilon/2
      center = tuple([v/2 for v in dim])
      temp = box(pos=center,length=dim[0],height=dim[1],width=0.05)
      temp.color = (1,1,1)

      # Setup the Home Plate
      dim = construction.home_size
      center = tuple([h_coord + size_coord / 2 for h_coord, size_coord in 
        zip(construction.home,dim)])
      temp = box(pos=center,length=dim[0],height=dim[1],width=0.1)
      temp.color = (1,0,0)

      # Setup the construction plate
      dim = construction.construction_size
      center = tuple([c_coord + size_coord / 2 for c_coord, size_coord in
        zip(construction.construction_location,dim)])
      temp = box(pos=center, length=dim[0],height=dim[1],width=0.1)
      temp.color = (0,1,0)
      
      # Set up worker dictionary to keep track of objects
      workers = {}
      timestep = 1
      for swarm_step, structure_step in self.data:
        for name, location in swarm_step:
          # Create the object
          if name not in workers:
            workers[name] = sphere(pos=location,radius=variables.local_radius/2,
              make_trail=False)
            workers[name].color = (1,0,1)
          # Change the objects position
          else:
            workers[name].pos = location

        for i,j in structure_step:
          temp = cylinder(pos=i,axis=helpers.make_vector(i,j),
            radius=variables.outside_diameter)
          temp.color = (.5,1,.1)

          # Update window dimensions
          limit = max(j)
          if limit > max(scene.range):
            scene.range = (limit,limit,limit)
            scene.center = helpers.scale(.5,helpers.sum_vectors(
              construction.construction_location,scene.range))

        time.sleep(inverse_speed)
        timestep += 1
