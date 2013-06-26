def run(timesteps = 10, robots = 10, debug = True, comment=""):
  from time import strftime
  from sap2000.constants import MATERIAL_TYPES, UNITS
  import helpers, commandline, variables

  outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\"
  outputfilename = "output.sdb"
  program, SapModel = commandline.run("",outputfolder + outputfilename)
  program.hide()

  # Make sure that the model is not locked so that we can change properties
  assert not SapModel.GetModelIsLocked()

  # define material property HERE
  ret = SapModel.PropMaterial.SetMaterial('PIPE',MATERIAL_TYPES[
  	'MATERIAL_STEEL'])
  assert ret == 0

  # switch to default units HERE
  ret = SapModel.SetPresentUnits(UNITS[variables.program_units])
  assert ret == 0

  # assign isotropic mechanical properties to material HERE

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

    # Run the analysis
    ret = SapModel.Analyze.RunAnalysis()
    if not ret:
      if debug:
        sap_failures.write("RunAnalysis failed! Value returned was {}".format(str(ret)))

    # Make sure that the model has been unlocked, and if not, unlock it
    if SapModel.GetModelIsLocked():
      SapModel.SetModelIsLocked(False)
      
    swarm.act()

  if debug:
    loc_text.close()
    sap_failures.close()

  return (program, structure, swarm)