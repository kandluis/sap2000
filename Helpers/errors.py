'''''''''''''''
Custom Simulation Errors
'''''''''''''''
class OutofBox(Exception):
  '''
  Indicates that the simulation has attempted to access areas outside the defined
  space.
  '''
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class InvalidMemory(Exception):
  '''
  Raised if the item that is being searched for is not in the robot's memory
  '''
  def __init__(self,value):
    self.value = value
  def __str__(self):
    return repr(self.value)