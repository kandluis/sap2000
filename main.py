def run(timesteps = 10, robots = 5, debug = True, comment=""):
  from time import strftime
  from sap2000.constants import MATERIAL_TYPES, UNITS,STEEL_SUBTYPES, PLACEHOLDER
  import helpers, commandline, variables

  outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\"
  outputfilename = "output.sdb"
  program, SapModel = commandline.run("",outputfolder + outputfilename)
  program.hide()

  # Make sure that the model is not locked so that we can change properties. Unlock it if it is
  if SapModel.GetModelIsLocked():
    SapModel.SetModelIsLocked(False)

  # switch to default units HERE
  ret = SapModel.SetPresentUnits(UNITS[variables.program_units])
  assert ret == 0


  # Defining our Scaffold Tube Material Property
  ret, name = SapModel.PropMaterial.AddQuick(variables.material_property,MATERIAL_TYPES[variables.material_type],STEEL_SUBTYPES[variables.material_subtype],PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,PLACEHOLDER,variables.material_property)
  assert ret == 0
  assert name == variables.material_property

  # Defining the Frame Section. This is the Scaffold Tube
  ret = SapModel.PropFrame.SetPipe(variables.frame_property_name,variables.material_property,variables.outside_diameter,variables.wall_thickness)
  assert ret == 0

  # add load patterns HERE, which by default also defines a Load Case
  if not helpers.addloadpattern(SapModel, variables.robot_load_case, 'LTYPE_DEAD'):
    print ("Failure when adding the loadpattern {}".format(variables.robot_load_case))
    assert 1 == 2

  # Make python structure and start up the colony
  from colony import ReactiveSwarm
  from structure import Structure

  structure = Structure()
  swarm = ReactiveSwarm(robots, structure, program)

  # Open files for writing
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
      ret = SapModel.Analyze.RunAnalysis()
      # When ret is not 0 debug is on, write out that it failed.
      if ret and debug:
        sap_failures.write("RunAnalysis failed! Value returned was {}".format(str(ret)))

    # Make the decision based on analysis results
    swarm.decide()

    # Make sure that the model has been unlocked, and if not, unlock it
    if SapModel.GetModelIsLocked():
      SapModel.SetModelIsLocked(False)
      
    # Change the model based on decisions made
    swarm.act()

  if debug:
    loc_text.close()
    sap_failures.close()

  return (program, structure, swarm)