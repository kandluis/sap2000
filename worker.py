from builder import Builder

class Worker(Builder):
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)

  def current_state(self):
    state = super(Worker,self).current_state()
    return state

  def construct(self):
    '''
    Decides whether the local conditions dictate we should build.
    Here is the basic logic it is following.
    1.  a)  If we are at the top of a beam
        OR
        b)  i)  We are at the specified construction site
            AND
            ii) There is no beginning tube
    AND
    2.  Did not build in the previous timestep
    AND
    3.  Still carrying construction material
    '''
    if ((self.at_top or (self.at_site() and self.structure.tubes == 0)) and not 
      self.memory['built'] and 
      self.num_beams > 0):
      self.at_top = False
      self.memory['built'] = True
      self.memory['construct'] += 1
      return True
    else:
      self.memory['built'] = False
      return False
