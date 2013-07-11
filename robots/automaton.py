# Basic class for any automatic object that needs access to the SAP program
class Automaton:
  def __init__(self,name,program):
    # Accesss to the SapModel from SAP 2000
    self.model = program.sap_com_object.SapModel

    # Access to the SAP 2000 Program
    self.program = program

    # Storage of the sphere model
    self.simulation_model = None

    # Robot name
    self.name = name

  def current_state(self):
    return {  'name'  : self.name }

  def decide(self):
    pass

  def do_action(self):
    pass