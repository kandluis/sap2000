from sap2000.constants import MATERIAL_TYPES, UNITS,STEEL_SUBTYPES, PLACEHOLDER
from time import strftime
from colony import ReactiveSwarm
from structure import Structure
import helpers, commandline, variables, sys

class Simulation:
  def __init__(self):
    self.SapProgram = None
    self.SapModel = None
    self.Structure = None
    self.Swarm = None
    self.started = False

  def __setup_general(self):
    '''
    Function to setup the general settigns for the SAP2000 program
    '''
    # switch to default units HERE
    ret = self.SapModel.SetPresentUnits(UNITS[variables.program_units])
    if ret:
      return False

    # add load patterns HERE, which by default also defines a Load Case
    if not helpers.addloadpattern(self.SapModel, variables.robot_load_case, 'LTYPE_DEAD'):
      print ("Failure when adding the loadpattern {}".format(variables.robot_load_case))
      return False

    if not self.__setup_case(self.SapModel.LoadCases,variables.robot_load_case):
      print ("Failure when setting-up load case {}.".format(variables.robot_load_case))
      return False
    if not self.__setup_case(self.SapModel.LoadCases,"DEAD"):
      print("Failure setting up DEAD case.")
      return False

    return True

  def __setup_case(self, name):
    # Initialize Non-linear
    ret = self.SapModel.LoadCases.StaticNonlinear.SetCase(name)
    if ret:
      return False
    # Set options (P-delta)
    ret = self.SapModel.LoadCases.StaticNonlinear.SetGeometricNonlinearity(name,1)
    if ret:
      return False

    # Set loads
    if name == "DEAD":
      ret, load_types, loads, scales = self.SapModel.LoadCases.StaticNonlinear.SetLoads(name,1,["Load"],[name],[1])
    else:
      ret, load_types, loads, scales = self.SapModel.LoadCases.StaticNonlinear.SetLoads(name,2,["Load","Load"],[name,"DEAD"],[1,1])

    if ret:
      return False

    return True

  def __setup_analysis(self):
    '''
    Funtion to set up the analysis model to the correct values
    '''
    # Set the degrees of Freedom
    DOF = (True,True,True,True,True,True)
    ret, DOF = self.SapModel.Analysis.SetActiveDOF(DOF)
    if ret:
      print("Failure with DOF.")
      return False

    # Set the cases to be analyzed (all cases)
    ret = self.SapModel.Analysis.SetRunCaseFlag("",True,True)
    if ret:
      print("Failure with run flag.")
      return False

    # Set Solver Options (Multithreaded, Auto, 64bit, robot_load_case)
    ret = self.SapModel.Analysis.SetSolverOption_1(2,0,False,variables.robot_load_case)
    if ret:
      print("Failure with sovler options")
      return False

    return True

  def __setup_material(self):
    '''
    Sets up our beam materials
    '''
    # Defining our Scaffold Tube Material Property
    ret, name = self.SapModel.PropMaterial.AddQuick(variables.material_property,MATERIAL_TYPES[variables.material_type],STEEL_SUBTYPES[variables.material_subtype],PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,variables.material_property)
    if ret or name != variables.material_property:
      return False

    # Defining the Frame Section. This is the Scaffold Tube
    ret = self.SapModel.PropFrame.SetPipe(variables.frame_property_name,variables.material_property,variables.outside_diameter,variables.wall_thickness)
    if ret:
      return False

    return True

  def reset(self, comment = ""):
    '''
    Allows us to reset everything without exiting the SAP program
    '''
    if self.started:
      # Resetting the SAP Program (this saves the previous file)
      self.SapProgram.reset()

      # Creating new SAP Files
      outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\"
      outputfilename = "tower.sdb"
      outputfile = outputfolder + outputfilename

      # Create a new blank moder
      ret = self.SapModel.File.NewBlank()
      assert ret == 0

      # Create directory of necessary
      path = os.path.dirname(outputfile)
      helpers.path_exists(path)

      # Save to the new file
      ret = self.SapModel.File.Save(outputfolder + outputfilename)
      assert ret == 0

    else:
      print("The simulation is not started. Cannot reset.")

  def start(self,comment = ""):
    '''
    This starts up the SAP 2000 Program and hides it.
    '''
    outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\"
    outputfilename = "tower.sdb"
    self.SapProgram, self.SapModel = commandline.run("",outputfolder + outputfilename)
    self.SapProgram.hide()
    self.started = True

  def stop(self):
    '''
    This stops the simulation gracefully
    '''
    if not self.started:
      self.SapProgram.exit()
      self.started = False
    else:
      print("No simulation started. Use Simulation.Start() to begin.")

  def run(timesteps = 10, robots = 5, debug = True, comment=""):
    '''
    Runs the simulation according to the variables passed in.
    '''
    # Make sure the simulation has been started. If not, start it. Otherwise, reset everything.
    if self.started:
      self.reset(comment=comment)
    else:
      self.start(comment=comment)

    # Make sure that the model is not locked so that we can change properties. Unlock it if it is
    if self.SapModel.GetModelIsLocked():
      self.SapModel.SetModelIsLocked(False)

    # Set everything up.
    if not self.__setup_general():
      sys.exit("General Setup Failed.")
    if not self.__setup_material():
      sys.exit("Material Setup Failed.")
    if not self.__setup_analysis():
      sys.exit("Analysis Setup Failed.")

    # Make python structure and start up the colony
    self.Structure = Structure()
    self.Swarm = ReactiveSwarm(robots, self.Structure, self.SapProgram)

    # Open files for writing if debugging
    if debug:
      loc_text = open(outputfolder + "locations.txt", 'w+')
      loc_text.write("This file contains the locations of the robots at each timestep.\n\n")
      sap_failures = open(outputfolder + "sap_failures.txt", 'w+')
      sap_failures.write("This file contains messages created when SAP 2000 does not complete a function successfully.\n\n")

    # Run the simulation!
    for i in range(timesteps):

      # This section is to assert that all functions work as expected, from a surface level
      if debug:
        loc_text.write("Timestep: " + str(i) + "\n\n")
        locations = swarm.get_locations()
        for worker in locations:
          loc_text.write(str(worker) + " : " + str(locations[worker]) + "\n")
        loc_text.write("\n")

      # Run the analysis if there is a structure to analyze
      if self.Structure.tubes > 0:
        # Save to a different filename every now and again
        if i % variables.analysis_timesteps == 0:
          filename = "tower-" + str(timesteps) + ".sdb"
          self.SapModel.File.Save(outputfolder + filename)

        ret = self.SapModel.Analyze.RunAnalysis()
        # When ret is not 0 debug is on, write out that it failed.
        if ret and debug:
          sap_failures.write("RunAnalysis failed! Value returned was {}".format(str(ret)))

        # Deselect all outputs
        ret = self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        if ret and debug:
          sap_failures.write("Deselecting Cases failed! Value returned was {}".format(str(ret)))

        # Select just the Robot Load Case for Output
        ret = self.SapModel.Results.Setup.SetCaseSelectedForOutput(variables.robot_load_case)

      # Make the decision based on analysis results
      swarm.decide()

      # Make sure that the model has been unlocked, and if not, unlock it
      if self.SapModel.GetModelIsLocked():
        self.SapModel.SetModelIsLocked(False)
        
      # Change the model based on decisions made
      swarm.act()

      # Give a status update if necessary
      if i % 25 == 0 or i % 25 == 5 or (i * 5) % 7 == 3:
        print("Currently on timestep {}".format(str(i)))

    if debug:
      loc_text.close()
      sap_failures.close()

'''
if __name__ == "__main__":
  simulation = Simulation()
  simulation.start()
'''