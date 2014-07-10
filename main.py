# import python libraries
import os
import random
import sys
import pdb
import pprint
from time import strftime

# for data output to Excel File
from xlsxwriter.workbook import Workbook

# import local libraries
# Commandline provides access to functions for running simulation from commandline
from Helpers import commandline
from Helpers import helpers
# import simulation objects
#from oldCode.colony import SmartSwarm
from World.swarm import SmartSwarm
from World.structure import Structure
from SAP2000.constants import MATERIAL_TYPES, UNITS,STEEL_SUBTYPES, PLACEHOLDER
from variables import BEAM, MATERIAL, PROGRAM, WORLD, WIND
# import third party libraries
import visualization as Visual
from visualization import Visualization

# import entire libraries so we can extra data from them and export them
import variables
import construction
from Behaviour import constants as BConstants

class Simulation(object):
  def __init__(self,seed = None,template="C:\\SAP 2000\\template.sdb"):
    self.SapProgram = None
    self.SapModel = None
    self.Structure = None
    self.Swarm = None
    self.started = False
    self.folder = None
    self.run = False

    # Keeps track of the excel data since we can only write it in one go
    self.excel = {}
    self.excel['headers'] = []
    self.excel['data'] = [[]]

    # Seed the simulation
    self.seed = seed
    
    # Stores the template
    self.template = template

  def __setup_general(self):
    '''
    Function to setup the general settigns for the SAP2000 program
    '''
    # switch to default units HERE
    ret = self.SapModel.SetPresentUnits(UNITS[PROGRAM['units']])
    if ret:
      return False

    if not self.__setup_case("DEAD"):
      print("Failure setting up DEAD case.")
      return False

    return True

  def __setup_wind(self,name=PROGRAM['wind_case']):
    '''
    We initalize the wind based on the information in variables.python
    '''
    # Add loadpattern and case
    if not helpers.addloadpattern(self.SapModel,name,'LTYPE_WIND'):
      return False

    # Make static non-linear
    if not self.__setup_case(name):
      return False

  def __setup_case(self, name):
    # Initialize Non-linear
    ret = self.SapModel.LoadCases.StaticNonlinear.SetCase(name)
    if ret:
      return False
    # Set options (P-delta)
    ret = self.SapModel.LoadCases.StaticNonlinear.SetGeometricNonlinearity(name,
      1)
    if ret:
      return False

    ret,load_types,loads,scales = self.SapModel.LoadCases.StaticNonlinear.SetLoads(
      name,1,["Load"],[name],[1])

    if ret:
      return False

    return True

  def __setup_analysis(self):
    '''
    Funtion to set up the analysis model to the correct values
    '''
    # Set the degrees of Freedom
    DOF = (True,True,True,True,True,True)
    ret, DOF = self.SapModel.Analyze.SetActiveDOF(DOF)
    if ret:
      print("Failure with DOF.")
      return False

    # Set the cases to be analyzed (all cases)
    ret = self.SapModel.Analyze.SetRunCaseFlag("",False,True)
    if ret:
      print("Failure with run flag.")
      return False

    # Set the cases to be analyzed (all cases)
    ret = self.SapModel.Analyze.SetRunCaseFlag(PROGRAM['robot_load_case'],True,
      False)
    if ret:
      print("Failure with run flag.")
      return False

    # Set the cases to be analyzed (all cases)
    ret = self.SapModel.Analyze.SetRunCaseFlag("DEAD",True,False)
    if ret:
      print("Failure with run flag.")
      return False

    # Set the cases to be analyzed (all cases)
    ret = self.SapModel.Analyze.SetRunCaseFlag("Wind",True,False)
    if ret:
      print("Failure with setting the wind case to be analyzed.")

    # Set Solver Options (Multithreaded, Auto, 64bit, robot_load_case)
    ret = self.SapModel.Analyze.SetSolverOption_1(2,0,False,
      PROGRAM['robot_load_case'])
    if ret:
      print("Failure with solver options")
      return False

    return True

  def __setup_material(self):
    '''
    Sets up our beam materials
    '''
    # Defining our Scaffold Tube Material Property
    ret, name = self.SapModel.PropMaterial.AddQuick(MATERIAL['material_property'],
      MATERIAL_TYPES[MATERIAL['material_type']],
      STEEL_SUBTYPES[MATERIAL['material_subtype']],PLACEHOLDER,PLACEHOLDER,
      PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,MATERIAL['material_property'])
    if ret or name != MATERIAL['material_property']:
      return False

    # Defining the Frame Section. This is the Scaffold Tube
    ret = self.SapModel.PropFrame.SetPipe(MATERIAL['frame_property_name'],
      MATERIAL['material_property'],MATERIAL['outside_diameter'],
      MATERIAL['wall_thickness'])
    if ret:
      return False

    return True

  def __push_information(self,file_obj):
    '''
    Writes out the data from variables and construction
    '''
    # Pull the names of all the variables and use that to get their attributes 
    # and store them in a list of names, values
    variables_text = 'variables', ([(constant, getattr(variables, constant)) for
     constant in dir(variables) if '__' not in constant and '.' not in constant])
    construction_text = 'construction', ([(constant, getattr(construction,
      constant)) for constant in dir(construction) if '__' not in constant 
      and '.' not in constant])
    constants_text = 'behaviour', ([(constant, getattr(BConstants,
      constant)) for constant in dir(BConstants) if '__' not in constant 
      and '.' not in constant])
    
    # Cycle through both modules and store information the data
    data = ''
    for name, file_data in variables_text, construction_text, constants_text:
      data += 'Data from the file {}.\n\n'.format(name)
      for var_name, value in file_data:
        data += var_name + ' : ' + str(value) + '\n'
      data += '\n\n'

    # Write out the data and you are now done
    file_obj.write(data)

  def __push_data(self,data,file_obj,i):
    '''
    Writes a set of data to a data file in specified format
    '''
    to_write = "Data for Timestep: {}\n\n\n".format(str(i))
    for name, state in data.items():
      to_write += "{} = \n\n".format(name)
      for key, temp_data in state.items():
        to_write += "{} : {}\n".format(str(key),pprint.pformat(temp_data))
      to_write += "\n"
    file_obj.write(to_write + "\n")

  def __add_excel(self,data):
    '''
    Stores timestep data in the simulation
    '''
    timestep = []
    for name, state in data.items():

      # Add names to headers if not already there
      if name not in self.excel['headers']:
        self.excel['headers'].append(name)
        self.excel['headers'].append("{}-height".format(name))
        self.excel['headers'].append("{}-measured moment".format(name))

      # Add the location to a list
      timestep.append(state['location'])
      timestep.append(state['location'][2])
      timestep.append(state['read_moment'])

    # Add the location list to a list of rows
    self.excel['data'].append(timestep)


  def __push_excel(self,file_name):
    '''
    Writes a set of data to an excel file
    '''
    # Open work book
    workbook = Workbook(file_name)
    worksheet = workbook.add_worksheet()

    # start at top left corner and write headers
    row, col = 0, 0
    for header in self.excel['headers']:
      worksheet.write(row,col, str(header))
      col += 1

    # start in second row and write data
    row, col = 1, 0
    for row_data in self.excel['data']:
      for cell_data in row_data:
        worksheet.write(row, col, str(cell_data))
        col += 1
      row += 1
      col = 0

    workbook.close()

    # Empty memory (this usually happens every 4000 timesteps)
    self.excel['header'] = []
    self.excel['data'] = [[]]

  def makeOutputFolder(self,comment):
    return (PROGRAM['root_folder'] + "\\" + strftime("%Y-%b") + "\\" +
        strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\")

  def reset(self, comment = ""):
    '''
    Allows us to reset everything without exiting the SAP program
    '''
    if self.started:
      # Resetting the SAP Program (this saves the previous file)
      self.SapProgram.reset(template=self.template)

      # Creating new SAP Files
      outputfolder = self.makeOutputFolder(comment)
      outputfilename = "tower.sdb"
      outputfile = outputfolder + outputfilename

      # Create directory if necessary
      path = os.path.dirname(outputfile)
      helpers.path_exists(path)

      # Save to the new file
      ret = self.SapModel.File.Save(outputfolder + outputfilename)
      assert ret == 0

      # Reset the structure and the swarm
      self.Structure.reset()
      self.Swarm.reset()

      self.folder = outputfolder
      self.run = False

    else:
      print("The simulation is not started. Cannot reset.")

  def start(self, visualization = False, robots = 10, comment = "", 
    model="C:\\SAP 2000\\template.sdb"):
    '''
    This starts up the SAP 2000 Program and hides it. 
      visualization = should we display the simulation as it occurs?
      robots = number of robots in simulation
      comment = a comment attached to the name of the folder
      model = location of a file which contains a starting model
    '''
    outputfolder = ''
    if self.started:
      print("Simulation has already been started")
    else:
      outputfolder = self.makeOutputFolder(comment)
      outputfilename = "tower.sdb"
      self.SapProgram, self.SapModel = commandline.run(model,
        outputfolder + outputfilename)
      self.SapProgram.hide()
      self.started = True

    # Make python structure and start up the colony
    self.Structure = Structure(visualization)
    self.Swarm = SmartSwarm(robots, self.Structure, self.SapProgram)

    # If we started with a previous model, we have to add all of the beams 
    # to our own model in python
    if model != "":
      ret = self.Structure.load_model(self.SapProgram)
      assert ret == 0

    self.folder = outputfolder

  def stop(self):
    '''
    This stops the simulation gracefully
    '''
    if self.started:
      ret = self.SapProgram.exit()
      assert ret == 0
      self.started = False
      self.run = False
      self.folder = None
    else:
      print("No simulation started. Use Simulation.Start() to begin.")

  def go(self,visualization = False, robots = 10, timesteps = 10, debug = True, 
    comment = ""):
    '''
    Direct accesss
    '''
    outputfolder = ""
    if not self.started:
      outputfolder = self.start(visualization,robots,comment)
    self.folder = outputfolder
    self.run_simulation(visualization,timesteps,debug,comment)
    self.stop()

    # Run visualization
    self.run_visualization()

  def run_visualization(self,fullscreen=True,inverse_speed=.25):
    '''
    Displays the visualization if an outputfolder exist and the simulation has
    been run.
    '''
    if self.run:
      window = Visualization(self.folder)
      window.load_data()
      window.run(fullscreen,inverse_speed)
    else:
      print("The visualization cannot be started becase simulation has not run.")

  def run_simulation(self,visualization = False, timesteps = 10, debug = True,
    comment = "",writeOut=True):
    '''
    Runs the simulation according to the variables passed in.
    '''
    outputfolder = self.folder

    start_time = strftime("%H:%M:%S")
    # Make sure the simulation has been started. If not, exit.
    if not self.started:
      print("The simulation has not been started. Start it, then run it, or " +
        "simply Simulation.go()")
      sys.exit(1)

    # Make sure that the model is not locked so that we can change properties. 
    # Unlock it if it is
    if self.SapModel.GetModelIsLocked():
      self.SapModel.SetModelIsLocked(False)

    # Set everything up.
    if not self.__setup_general():
      sys.exit("General Setup Failed.")
    if not self.__setup_material():
      sys.exit("Material Setup Failed.")
    if not self.__setup_analysis():
      sys.exit("Analysis Setup Failed.")

    # Open files for writing if debugging
    with open(outputfolder + 'repair_info.txt', 'a') as repair_file, open(outputfolder + "robot_data.txt", 'a') as loc_text, open(outputfolder + "sap_failures.txt", 'a') as sap_failures, open(outputfolder + "run_data.txt", 'a') as run_text, open(outputfolder + "structure.txt", "a") as struct_data:
      loc_text.write("This file contains information on the robots at each" +
        " timestep if debugging.\n\n")
      sap_failures.write("This file contains messages created when SAP 2000 does"
       + " not complete a function successfully if debugging.\n\n")
      struct_data.write("This file contains the data about the Pythonic" +
        " structure.\n\nCurrently unused do to space issues.")
      run_text.write("This file contains the variables used in the run of the" +
        " simulation.\n\nTotal timesteps: " + str(timesteps) + "\nStart time of"
        + " simumation: " + start_time + "\nSeed:" + str(self.seed) + "\n\n")

      run_text.write("Folder: {}\n\n".format(str(self.folder)))

      # Write variables
      self.__push_information(run_text)

      if debug:
        print(PROGRAM['debug_message'])
      # setup a nice visual 
      if visualization:
        scene = Visual.setup_scene(False)
        Visual.setup_base()

      # Run the simulation!
      for i in range(timesteps):
        if visualization:
          self.Swarm.show()

        # Add number and new line to structure visualization data
        self.Structure.visualization_data += "\n"
        self.Structure.structure_data.append([])
        
        try:
          self.Structure.color_data += '\n'
        except MemoryError:
          self.Structure.color_data = ''


        # Save to a different filename every now and again
        try:
          if i % PROGRAM['analysis_timesteps'] == 0 and i != 0:
            filename = "tower-" + str(i) + ".sdb"
            self.SapModel.File.Save(outputfolder + filename)
        except:
          print("Simulation ended when saving output.")
          if writeOut:
            swarm_data = self.Swarm.get_information()
            self.__add_excel(swarm_data)
            self.__push_data(swarm_data,loc_text,i+1)
          self.exit(run_text)
          raise

        # Run the analysis if there is a structure to analyze and there are \
        # robots on it (ie, we actually need the information)
        if self.Structure.tubes > 0 and self.Swarm.need_data():
          try:
            sap_failures.write(helpers.run_analysis(self.SapModel))
          except:
            if writeOut:
              swarm_data = self.Swarm.get_information()
              self.__add_excel(swarm_data)
              self.__push_data(swarm_data,loc_text,i+1)
            self.exit(run_text)
            raise

          # Check the structure for stability
          failed = self.Structure.failed(self.SapProgram)
          if failed:
            print(failed)
            break

        # debuggin here for quick access to decide/act methods
        if debug <= i and debug:
          pdb.set_trace()

        # Make the decision based on analysis results
        try:
          self.Swarm.decide()
        except:
          print("Simulation ended at decision.")
          if writeOut:
            swarm_data = self.Swarm.get_information()
            self.__add_excel(swarm_data)
            self.__push_data(swarm_data,loc_text,i+1)
          self.exit(run_text)
          raise

        # Make sure that the model has been unlocked, and if not, unlock it
        if self.SapModel.GetModelIsLocked():
          self.SapModel.SetModelIsLocked(False)
          
        # Change the model based on decisions made (act on your decisions)
        try:
          self.Swarm.act()
        except:
          print("Simulation ended at act.")
          if writeOut:
            swarm_data = self.Swarm.get_information()
            self.__add_excel(swarm_data)
            self.__push_data(swarm_data,loc_text,i+1)
          self.exit(run_text)
          raise

        # Write out errors on movements
        errors = self.Swarm.get_errors()
        if errors != '':
          sap_failures.write("Errors that occurred in timestep {}. {}\n\n".format(
            str(i+1),errors))

        # Write out repair information
        repair_data = self.Swarm.get_repair_data()
        if repair_data != '':
            repair_file.write("Repairs for begun at timestep {}:\n {}\n".format(
              str(i+1),repair_data))

        # Give a status update if necessary
        commandline.status("Finished timestep {}.".format(str(i + 1)))
        print()

        # Sort beam data
        if self.Structure.structure_data[-1] != []:
          self.Structure.structure_data[-1].sort(key=lambda t: int(t[0]))

        # Check height of structure and break out if we will reach maximum
        if self.Structure.height > WORLD['properties']['dim_z'] - 2* BEAM['length']:
          break

        with open(self.folder + 'random_seed_results.txt', 'a') as rand_tex:
          rand_tex.write("{},".format(str(random.randint(0,i+1))))

        with open(self.folder + 'structure_height.txt', 'a') as str_height:
          str_height.write("{},\n".format(str(self.Structure.height)))

        # We run out of mememory is we don't do this every once in a while
        if i % 100 == 0 and i != 0:
          # Write out visualization data
          self.visualization_data()

          # Write out structure physics
          self.structure_physics()

        # We run out of memory for Excel information if we don't clean it out
        # everynow and again
        if i % 5000 == 0 and i != 0:
          self.__push_excel(self.folder + "locations-{}.xlsx".format(str(i)))

        # This section writes the robots decisions out to a file
        if writeOut:
          swarm_data = self.Swarm.get_information()
          self.__add_excel(swarm_data)
          self.__push_data(swarm_data,loc_text,i+1)
          
        # END OF LOOOP

      # Clean up
      self.exit(run_text)

  def exit(self,run_text):

    # Sort beam data
    if self.Structure.structure_data[-1] != []:
      self.Structure.structure_data[-1].sort(key=lambda t: int(t[0]))

    # Finish up run_data (add ending time and maximum height)
    run_data = ("\n\nStop time : " + strftime("%H:%M:%S") + 
      ".\n\n Total beams" + " on structure: " + str(self.Structure.tubes) 
      + ".")
    run_data += "\n\n Maximum height of structure : " +  str(
      self.Structure.height) + "."

    # Write out simulation data
    run_text.write(run_data)

    # Write out locations to excel
    self.__push_excel(self.folder + "locations-end.xlsx")

    # Write out visualization data
    self.visualization_data()

    # Write out structure moments
    self.structure_physics()

    self.run = True

  def visualization_data(self):
    '''
    Writes out the data for the visualization currently stored and clears the
    buffers
    '''
    # Write data
    with open(self.folder + 'structure_color_data.txt','a') as c_struct, open(self.folder + 'swarm_color_data.txt', 'a') as c_swarm, open(self.folder + 'swarm_visualization.txt', 'a') as v_swarm, open(self.folder + 'structure_visualization.txt','a') as v_struct:
      v_swarm.write(self.Swarm.visualization_data)
      c_swarm.write(self.Swarm.color_data)
      v_struct.write(self.Structure.visualization_data)
      c_struct.write(self.Structure.color_data)

    # Clear buffers
    self.Swarm.visualization_data = ''
    self.Swarm.color_data = ''
    self.Structure.visualization_data = ''
    self.Structure.color_data = ''

  def structure_physics(self):
    '''
    Writes out the physical data for the structure and clears the buffer.
    '''
    # Write data
    with open(self.folder + 'structure_physics.txt',"a") as struct_phys:
      for timestep in self.Structure.structure_data:
        for beam,moment in timestep:
          struct_phys.write("{},{},".format(beam,str(moment)))
        struct_phys.write("\n")

    # Clear buffers
    self.Structure.structure_data = []


