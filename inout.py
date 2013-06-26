import os, variables
from sap2000 import sap2000
from sap2000.constants import UNITS
from helpers import path_exists

# temp
# from sap2000.constants import FRAME_TYPES

def io(inputfile = "", outputfile = "C:\SAP 2000\output.sdb"):
  """
  Opens the specified inputfile and outputfile. By default, it creates a new model
  if no inputfile is specified and saves it as the specified outputfile. If no outputfile
  is specified, the default location is "C:\SAP 2000\output.sdb". Returns the program and model.
  """
  # start program
  program = sap2000.Sap2000()
  program.start(filename=inputfile)

  # open model if specified
  if inputfile == "":
    model = program.initializeModel()
    return_value = model.File.NewBlank()
    assert return_value == 0

  else:
    model = program.sap_com_object.SapModel

  # save with new output file name (create directory if necessary)
  path = os.path.dirname(outputfile)
  path_exists(path)
  program.save(outputfile)

  # reset the correct units
  model.SetPresentUnits(UNITS[variables.program_units])

  return program, model
