from robots.repairer import Repairer

class DeflectionRepairer(Repairer):
  '''
  Attemps to build vertical beams such that they counter balance each Otherwise
  '''
  def __init__(self,name,structure,location,program):
    super(SmartRepairer,self).__init__(name,structure,location,program)
    
  def get_disturbance(self):
    '''
    Returns the disturbance level for adding a new beam at the tip. This is
    modified so that the disturbance compensates for the angle at which the
    current beam lies (using basic math)
    '''
    # TODO
    return super(Repairer,self).get_disturbance()

class SmartRepairer(Repairer):
  '''
  Repairs beams based on a sliding scale repair.
  '''
  def __init__(self,name,structure,location,program):
    super(SmartRepairer,self).__init__(name,structure,location,program)

  def beam_check(self,name):
    '''
    Checks a beam to see whether it is in a state that requires repair
    '''
    moment = self.get_moment(name)
    e1,e2 = self.structure.get_endpoints(name,self.location)
    xy_dist = helpers.distance((e1[0],e1[1],0),(e2[0],e2[1],0))
    limit = construction.beam['beam_limit'] + (
      xy_dist / construction.beam['length']) * construction.beam['horizontal_beam_limit']

    return (moment < limit or helpers.compare(moment,limit))

class LeanRepairer(Repairer):
  '''
  Instead of building directly up, this class builds at a specified angle
  from the ground. There are no perfectly vertical tubes, nor even those that
  are almost vertical
  '''
  def __init__(self,name,structure,location,program):
    super(SmartRepairer,self).__init__(name,structure,location,program)

  def get_default(self,ratio_coord,vertical_coord):
    '''
    Returns the coordinate onto which the j-point of the beam to construct 
    should lie
    '''
    # No vertical coordinate this time, since we will use a leaning one
    coord = super(LeanRepairer,self).get_default(ratio_coord,None)
    if coord is not None:
      return coord
    # We need to return one that leans
    else:
      xy_dir = self.non_zero_xydirection()
      scale = 1 / helpers.ratio(construction.beam['construction_angle'])
      vertical = helpers.scale(scale,construction.beam['vertical_dir_set'])
      direction = helpers.make_unit(helpers.sum_vectors(xy_dir,vertical))
      endpoint = helpers.sum_vectors(self.location,helpers.scale(
        construction.beam['length'],direction))

      return endpoint
