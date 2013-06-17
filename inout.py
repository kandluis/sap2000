import os
from sap2000 import sap2000
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

    '''
    Temp test code below
    ret = model.File.New2DFrame(FRAME_TYPES["PortalFrame"],3,124,3,200)
    assert ret == 0
    '''
  else:
    model = program.sap_com_object.SapModel

  # save with new output file name (create directory if necessary)
  path = os.path.dirname(outputfile)
  path_exists(path)
  program.save(outputfile)

  return program, model
