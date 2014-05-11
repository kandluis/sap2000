# Basic class for any automatic object that needs access to the SAP program
class Automaton(object):
  def __init__(self,name,program):
    # Accesss to the SapModel from SAP 2000
    self.model = program.sap_com_object.SapModel

    # Access to the SAP 2000 Program
    self.program = program

    # Storage of the sphere model
    self.simulation_model = None

    # Robot name
    self.name = name

  def my_type(self):
    '''
    Returns the class name.
    '''
    return self.__class__.name

  def current_state(self):
    '''
    Returns the state of the robot at the moment the function is called
    '''
    return {  'name'  : self.name }

  def decide(self):
    '''
    Makes decisions based on available data
    '''
    pass

  def do_action(self):
    '''
    Acts based on decisions made
    '''
    pass