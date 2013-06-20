def run(runs = 10, debug = True, comment=""):
  from time import strftime
  from sap2000.constants import MATERIAL_TYPES, UNITS
  from sap2000 import variables
  import helpers, commandline

  outputfolder = 'C:\SAP 2000\\' +strftime("%b-%d") + "\\" + strftime("%H_%M_%S") + comment + "\\"
  outputfilename = "output.sdb"
  program, SapModel = commandline.run("",outputfolder + outputfilename)
  program.hide()

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

  from robots import Worker
  from structure import Structure

  structure = Structure()
  worker = Worker(structure,(0,0,0),program)

  # This section is to assert that all functions work as expected, from a surface level
  if debug:
    pass

  with open(outputfolder + "locations.txt", 'w+') as loc_text:
    for i in range(runs):
      worker.do_action()
      loc_text.write(str(worker.get_location()) + "\n")

  return (program, structure, worker)