from sap2000.constants import MATERIAL_TYPES, UNITS,STEEL_SUBTYPES, PLACEHOLDER
import helpers, commandline, variables, sys

def setup_general(Model):
  '''
  Function to setup the general settigns for the SAP2000 program
  '''
  # switch to default units HERE
  ret = Model.SetPresentUnits(UNITS[variables.program_units])
  if ret:
    return False

  # add load patterns HERE, which by default also defines a Load Case
  if not helpers.addloadpattern(Model, variables.robot_load_case, 'LTYPE_DEAD'):
    print ("Failure when adding the loadpattern {}".format(variables.robot_load_case))
    return False

  if not setup_case(Model.LoadCases,variables.robot_load_case):
    print ("Failure when setting-up load case {}.".format(variables.robot_load_case))
    return False
  if not setup_case(Model.LoadCases,"DEAD"):
    print("Failure setting up DEAD case.")
    return False

  return True

def setup_case(LoadCases, name):
  # Initialize Non-linear
  ret = LoadCases.StaticNonlinear.SetCase(name)
  if ret:
    return False
  # Set options (P-delta)
  ret = LoadCases.StaticNonlinear.SetGeometricNonlinearity(name,1)
  if ret:
    return False

  # Set loads
  if name == "DEAD":
    ret, load_types, loads, scales = LoadCases.StaticNonlinear.SetLoads(name,1,["Load"],[name],[1])
  else:
    ret, load_types, loads, scales = LoadCases.StaticNonlinear.SetLoads(name,2,["Load","Load"],[name,"DEAD"],[1,1])

  if ret:
    return False

  return True

def setup_analysis(Analysis):
  '''
  Funtion to set up the analysis model to the correct values
  '''
  # Set the degrees of Freedom
  DOF = (True,True,True,True,True,True)
  ret, DOF = Analysis.SetActiveDOF(DOF)
  if ret:
    print("Failure with DOF.")
    return False

  # Set the cases to be analyzed (all cases)
  ret = Analysis.SetRunCaseFlag("",True,True)
  if ret:
    print("Failure with run flag.")
    return False

  # Set Solver Options (Multithreaded, Auto, 64bit, robot_load_case)
  ret = Analysis.SetSolverOption_1(2,0,False,variables.robot_load_case)
  if ret:
    print("Failure with sovler options")
    return False

  return True

def setup_material(Model):
  '''
  Setups our beam materials
  '''
  # Defining our Scaffold Tube Material Property
  ret, name = Model.PropMaterial.AddQuick(variables.material_property,MATERIAL_TYPES[variables.material_type],STEEL_SUBTYPES[variables.material_subtype],PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,variables.material_property)
  if ret or name != variables.material_property:
    return False

  # Defining the Frame Section. This is the Scaffold Tube
  ret = Model.PropFrame.SetPipe(variables.frame_property_name,variables.material_property,variables.outside_diameter,variables.wall_thickness)
  if ret:
    return False

  return True

def run(timesteps = 10, robots = 5, debug = True, comment=""):
  from time import strftime

  outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\"
  outputfilename = "tower.sdb"
  program, SapModel = commandline.run("",outputfolder + outputfilename)
  program.hide()

  # Make sure that the model is not locked so that we can change properties. Unlock it if it is
  if SapModel.GetModelIsLocked():
    SapModel.SetModelIsLocked(False)

  # Setup
  if not setup_general(SapModel):
    sys.exit("General Setup Failed.")
  if not setup_material(SapModel):
    sys.exit("Material Setup Failed.")
  if not setup_analysis(SapModel.Analyze):
    sys.exit("Analysis Setup Failed.")

  # Make python structure and start up the colony
  from colony import ReactiveSwarm
  from structure import Structure

  structure = Structure()
  swarm = ReactiveSwarm(robots, structure, program)

  # Open files for writing if debugging
  if debug:
    loc_text = open(outputfolder + "locations.txt", 'w+')
    loc_text.write("This file contains the locations of the robots at each timestep.\n\n")
    sap_failures = open(outputfolder + "sap_failures.txt", 'w+')
    sap_failures.write("This file contains messages created when SAP 2000 does not complete a function successfully.\n\n")

  # Run the program the specified number of timesteps
  for i in range(timesteps):

    # This section is to assert that all functions work as expected, from a surface level
    if debug:
      loc_text.write("Timestep: " + str(i) + "\n\n")
      locations = swarm.get_locations()
      for worker in locations:
        loc_text.write(str(worker) + " : " + str(locations[worker]) + "\n")
      loc_text.write("\n")

    # Run the analysis if there is a structure to analyze
    if structure.tubes > 0:
      # Save to a different filename every now and again
      if i % variables.analysis_timesteps == 0:
        filename = "tower-" + str(timesteps) + ".sdb"
        SapModel.File.Save(outputfolder + filename)

      ret = SapModel.Analyze.RunAnalysis()
      # When ret is not 0 debug is on, write out that it failed.
      if ret and debug:
        sap_failures.write("RunAnalysis failed! Value returned was {}".format(str(ret)))

      # Deselect all outputs
      ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
      if ret and debug:
        sap_failures.write("Deselecting Cases failed! Value returned was {}".format(str(ret)))

      # Select just the Robot Load Case for Output
      ret = SapModel.Results.Setup.SetCaseSelectedForOutput(variables.robot_load_case)

    # Make the decision based on analysis results
    swarm.decide()

    # Make sure that the model has been unlocked, and if not, unlock it
    if SapModel.GetModelIsLocked():
      SapModel.SetModelIsLocked(False)
      
    # Change the model based on decisions made
    swarm.act()

    # Give a status update if necessary
    if i % 25 == 0 or i % 25 == 5 or (i * 5) % 7 == 3:
      print("Currently on timestep {}".format(str(i)))

  if debug:
    loc_text.close()
    sap_failures.close()

  return (program, structure, swarm)