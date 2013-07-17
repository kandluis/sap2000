from helpers import helpers
from visual import *
import construction, time, re, pdb, variables

class Visualization:
  def __init__(self,outputfolder):
    self.data = []
    self.folder = outputfolder
    self.workers = {}
    self.beams = {}

  def load_data(self,swarm='swarm_visualization.txt',
    structure='structure_visualization.txt',color_swarm='swarm_color_data.txt',
    color_structure='structure_color_data.txt'):
    '''
    Loads the data from the files specified
    '''
    def load_file(file_obj,two=True):
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
          if item_data != '\n' and item_data != '':

            # Now we split the item into the two data (there is a : between them)
            data_1,data_2 = re.split(":",item_data)

            # Read a float tuple if both, else set it as a string (leave a alone)
            #data_1 = (tuple(float(v) for v in re.findall("[-+]?[0-9]*\.?[0-9]+",
            #  data_1)) if both else data_1)
            if not two:
              # Read float tuple for color or location if not endpoints
              coords = [tuple(float(v) for v in re.findall("[-+]?[0-9]*\.?[0-9]+",
                data_2))]
            else:
              coords = []
              for coord in  re.split("-",data_2):
                coords.append(tuple(float(v) for v in re.findall("[-+]?[0-9]*\.?[0-9]+",
                  coord)))

            # Add data to timestep
            timestep_data.append((data_1,coords))

        # Add timestep to data
        timesteps.append(timestep_data)

      return timesteps

    # Open the files and load the data. Zip it up so that all the data is accessible in one timestep
    with open(self.folder + color_swarm, 'r') as sc_file, open(self.folder + color_structure, 'r') as stc_file, open(self.folder + swarm, 'r') as s_file, open(self.folder + structure, 'r') as st_file:
      swarm_loc = load_file(s_file,False)
      swarm_colors = load_file (sc_file,False)
      struct_loc = load_file(st_file,True)
      struct_color = load_file(stc_file,False)
      self.data = list(zip(swarm_loc,swarm_colors,struct_loc,struct_color))

  def setup_scene(self,fullscreen):
    '''
    Sets up the scene for the display output.
    '''
    # Set title and background color (white)
    scene = display(title="Robot Simulation",background=(1,1,1))
    # Automatically center
    scene.autocenter = True
    # Removing autoscale
    scene.autoscale = 0
    # Set whether the windows will take up entire screen or not
    scene.fullscreen = fullscreen
    # Size of the windows seen is the size of one beam (to begin)
    scene.range = (variables.beam_length,variables.beam_length,
      variables.beam_length)
    # The center of the windows exists at the construction location
    scene.center = helpers.scale(.5,helpers.sum_vectors(
      construction.construction_location,scene.range))
    # Vector from which the camera start
    scene.forward = (1,0,0)
    # Define up (used for lighting)
    scene.up = (0,0,1)
    # Defines whether or not we exit the program when we exit the screen
    # visualization
    scene.exit = False

    return scene

  def setup_base(self):
    '''
    Creates a visual for the ground, the construction area, and the home area
    '''
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

  def run(self,fullscreen = True, inverse_speed=.25):
    if self.data == []:
      print("No data has been loaded. Cannot run simulation.")
    else:
      # Setup the scene
      scene = self.setup_scene(fullscreen)

      # Setup basic
      self.setup_base()

      # Set up worker dictionary to keep track of objects
      timestep = 1
      for swarm_step, swarm_color,structure_step,struct_color in self.data:
        for name, locations in swarm_step:
          # Create the object
          if name not in self.workers:
            self.workers[name] = sphere(pos=locations[0],
              radius=variables.local_radius/2,make_trail=False)
            self.workers[name].color = (1,0,1)
          # Change the objects position
          else:
            self.workers[name].pos = locations[0]

        # Set the color
        for name, colors in swarm_color:
          self.workers[name].color = colors[0]

        # Add beams if any
        for name,coords in structure_step:
          i,j = coords
          self.beams[name] = cylinder(pos=i,axis=helpers.make_vector(coords[0],
            coords[1]),radius=variables.outside_diameter,color=(0,1,0))

          # Update window dimensions
          limit = max(j)
          if limit > max(scene.range):
            scene.range = (limit,limit,limit)
            scene.center = helpers.scale(.5,helpers.sum_vectors(
              construction.construction_location,scene.range))

        # Change the color of the beams
        for name,colors in struct_color:
          try:
            self.beams[name].color = colors[0]
          except IndexError:
            print("A nonexistant beam is beam is to be recolored!")

        # Check key_presses
        if scene.kb.keys:
          s = scene.kb.getkey()
          if len(s) == 1:
            # Move faster
            if s == 'f':
              inverse_speed /= 2
            # Move more slowly
            elif s == 's':
              inverse_speed *= 2
            # Pause or continue
            elif s == ' ':
              self.pause(scene)
            else:
              pass

        time.sleep(inverse_speed)
        timestep += 1

  def pause(self,scene):
    '''
    Pauses the program. Waits for the space_key to start it again
    '''
    while True:
      if scene.kb.keys:
        s = scene.kb.getkey()
        if len(s) == 1:
          # Continue execution
          if s == ' ':
            break

      time.sleep(0.01)
