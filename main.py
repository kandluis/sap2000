from helpers import commandline, helpers
from robots.colony import ReactiveSwarm
from structure.structure import Structure
from sap2000.constants import MATERIAL_TYPES, UNITS,STEEL_SUBTYPES, PLACEHOLDER
from time import strftime
from visual import *
from visualization import Visualization
from xlsxwriter.workbook import Workbook
import construction, os, random,sys, variables

class Simulation:
  def __init__(self,seed = None):
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
    random.seed(seed)

  def __setup_general(self):
    '''
    Function to setup the general settigns for the SAP2000 program
    '''
    # switch to default units HERE
    ret = self.SapModel.SetPresentUnits(UNITS[variables.program_units])
    if ret:
      return False

    # add load patterns HERE, which by default also defines a Load Case
    '''
    if not helpers.addloadpattern(self.SapModel, variables.robot_load_case, 
      'LTYPE_DEAD'):
      print ("Failure when adding the loadpattern {}".format(
        variables.robot_load_case))
      return False

    if not self.__setup_case(variables.robot_load_case):
      print ("Failure when setting-up load case {}.".format(
        variables.robot_load_case))
      return False
    '''
    if not self.__setup_case("DEAD"):
      print("Failure setting up DEAD case.")
      return False

    return True

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

    # Set loads
    if name == "DEAD":
      ret,load_types,loads,scales = self.SapModel.LoadCases.StaticNonlinear.SetLoads(
        name,1,["Load"],[name],[1])
    else:
      ret,load_types,loads,scales = self.SapModel.LoadCases.StaticNonlinear.SetLoads(
        name,2,["Load","Load"],[name,"DEAD"],[1,1])

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
    ret = self.SapModel.Analyze.SetRunCaseFlag(variables.robot_load_case,True,
      False)
    if ret:
      print("Failure with run flag.")
      return False

    # Set the cases to be analyzed (all cases)
    ret = self.SapModel.Analyze.SetRunCaseFlag("DEAD",True,False)
    if ret:
      print("Failure with run flag.")
      return False

    # Set Solver Options (Multithreaded, Auto, 64bit, robot_load_case)
    ret = self.SapModel.Analyze.SetSolverOption_1(2,0,False,
      variables.robot_load_case)
    if ret:
      print("Failure with sovler options")
      return False

    return True

  def __setup_material(self):
    '''
    Sets up our beam materials
    '''
    # Defining our Scaffold Tube Material Property
    ret, name = self.SapModel.PropMaterial.AddQuick(variables.material_property,
      MATERIAL_TYPES[variables.material_type],
      STEEL_SUBTYPES[variables.material_subtype],PLACEHOLDER,PLACEHOLDER,
      PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,variables.material_property)
    if ret or name != variables.material_property:
      return False

    # Defining the Frame Section. This is the Scaffold Tube
    ret = self.SapModel.PropFrame.SetPipe(variables.frame_property_name,
      variables.material_property,variables.outside_diameter,
      variables.wall_thickness)
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
    
    # Cycle through both modules and store information the data
    data = ''
    for name, file_data in variables_text, construction_text:
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
        to_write += "{} : {}\n".format(str(key),str(temp_data))
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

      # Add the location to a list
      timestep.append(state['location'])
      timsptep.append(state['location'][2])

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


  def reset(self, comment = ""):
    '''
    Allows us to reset everything without exiting the SAP program
    '''
    if self.started:
      # Resetting the SAP Program (this saves the previous file)
      self.SapProgram.reset()

      # Creating new SAP Files
      outputfolder = ('C:\SAP 2000\\' +strftime("%b-%d") + "\\" + 
        strftime("%H_%M_%S") + comment + "\\")
      outputfilename = "tower.sdb"
      outputfile = outputfolder + outputfilename

      # Create a new blank moder
      ret = self.SapModel.File.NewBlank()
      assert ret == 0

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

  def start(self, visualization = False, robots = 10, comment = "", model=""):
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
      outputfolder = ('C:\SAP 2000\\' +strftime("%b-%d") + "\\" + 
        strftime("%H_%M_%S") + comment + "\\")
      outputfilename = "tower.sdb"
      self.SapProgram, self.SapModel = commandline.run(model,
        outputfolder + outputfilename)
      self.SapProgram.hide()
      self.started = True

    # Make python structure and start up the colony
    self.Structure = Structure(visualization)
    self.Swarm = ReactiveSwarm(robots, self.Structure, self.SapProgram)

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
    comment = ""):
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
    with open(outputfolder + 'repair_info.txt', 'w+') as repair_file, open(outputfolder + "robot_data.txt", 'w+') as loc_text, open(outputfolder + "sap_failures.txt", 'w+') as sap_failures, open(outputfolder + "run_data.txt", 'w+') as run_text, open(outputfolder + "structure.txt", "w+") as struct_data:
      loc_text.write("This file contains information on the robots at each" +
        " timestep if debugging.\n\n")
      sap_failures.write("This file contains messages created when SAP 2000 does"
       + " not complete a function successfully if debugging.\n\n")
      struct_data.write("This file contains the data about the Pythonic" +
        " structure.\n\n")
      run_text.write("This file contains the variables used in the run of the" +
        " simulation.\n\nTotal timesteps: " + str(timesteps) + "\nStart time of"
        + " simumation: " + start_time + "\nSeed:" + str(self.seed) + "\n\n")

      run_text.write("Folder: {}\n\n".format(str(self.folder)))

      # Write variables
      self.__push_information(run_text)

      # Run the simulation!
      for i in range(timesteps):

        # Display the swarm if specified
        if visualization:
          self.Swarm.show()

        # Add number and new line to structure visualization data
        self.Structure.visualization_data += "\n"
        self.Structure.color_data += '\n'
        self.Structure.structure_data.append([])

        # Save to a different filename every now and again
        try:
          if i % variables.analysis_timesteps == 0 and i != 0:
            filename = "tower-" + str(i) + ".sdb"
            self.SapModel.File.Save(outputfolder + filename)
        except:
          print("Simulation ended when saving output.")
          self.exit(run_text)
          raise

        # Run the analysis if there is a structure to analyze and there are \
        # robots on it (ie, we actually need the information)
        if self.Structure.tubes > 0 and self.Swarm.need_data():
          try:
            ret = self.SapModel.Analyze.RunAnalysis()
            # When ret is not 0 debug is on, write out that it failed.
            if ret and debug:
              sap_failures.write("RunAnalysis failed! Value returned was" + 
                " {}".format(str(ret)))
          except:
            print("Simulation ended when analyzing model.")
            self.exit(run_text)
            raise

          # Deselect all outputs
          try:
            ret = self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
            if ret and debug:
              sap_failures.write("Deselecting Cases failed! Value returned was " +
                "{}".format(str(ret)))

            # Select just the Robot Load Case for Output
            ret = self.SapModel.Results.Setup.SetCaseSelectedForOutput(
              variables.robot_load_case)
          except:
            print("Simulation ended when setting up output cases.")
            self.exit(run_text)
            raise

          # Check the structure for stability
          failed = self.Structure.failed(self.SapProgram)
          if failed:
            print(failed)
            break

        # Make the decision based on analysis results
        try:
          self.Swarm.decide()
        except:
          print("Simulation ended at decision.")
          self.s(run_text)
          raise

        # Make sure that the model has been unlocked, and if not, unlock it
        if self.SapModel.GetModelIsLocked():
          self.SapModel.SetModelIsLocked(False)

        # This section writes the robots decisions out to a file
        if debug:
          swarm_data = self.Swarm.get_information()
          beam_data = self.Structure.get_information()
          self.__add_excel(swarm_data)
          self.__push_data(swarm_data,loc_text,i+1)
          self.__push_data(beam_data,struct_data,i+1)
          
        # Change the model based on decisions made (act on your decisions)
        try:
          self.Swarm.act()
        except:
          print("Simulation ended at act.")
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
        print("Finished timestep {}\r".format(str(i + 1)))

        # Sort beam data
        if self.Structure.structure_data[-1] != []:
          self.Structure.structure_data[-1].sort(key=lambda t: t[0])

        # Check height of structure and break out if we will reach maximum
        if self.Structure.height > variables.dim_z - 2* construction.beam['length']:
          break

        with open(self.folder + 'random_seed_results.txt', 'a') as rand_tex:
          rand_tex.write("{},".format(str(random.randint(0,i+1))))

        # END OF LOOOP

      # Clean up
      self.exit(run_text)

  def exit(self,run_text):

    # Finish up run_data (add ending time and maximum height)
    run_data = ("\n\nStop time : " + strftime("%H:%M:%S") + 
      ".\n\n Total beams" + " on structure: " + str(self.Structure.tubes) 
      + ".")
    run_data += "\n\n Maximum height of structure : " +  str(
      self.Structure.height) + "."

    # Write out simulation data
    run_text.write(run_data)

    # Write out locations
    self.__push_excel(self.folder + "locations.xlsx")

    # Write out visualization data
    with open(self.folder + 'structure_color_data.txt','w+') as c_struct, open(self.folder + 'swarm_color_data.txt', 'w+') as c_swarm, open(self.folder + 'swarm_visualization.txt', 'w+') as v_swarm, open(self.folder + 'structure_visualization.txt','w+') as v_struct:
      v_swarm.write(self.Swarm.visualization_data)
      c_swarm.write(self.Swarm.color_data)
      v_struct.write(self.Structure.visualization_data)
      c_struct.write(self.Structure.color_data)

    with open(self.folder + 'structure_physics.txt',"w+") as struct_phys:
      for timestep in self.Structure.structure_data:
        for beam,moment in timestep:
          struct_phys.write("{},{},".format(beam,str(moment)))
      struct_phys.write("\n")

    self.run = True

