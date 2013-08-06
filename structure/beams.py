from helpers import helpers
from collections import namedtuple
import math, variables,pdb

Coord = namedtuple("Coordinates", ["x", "y", "z"])
EndPoints = namedtuple("Endpoints", ["i","j"])

class DumbBeam:
  def __init__(self, name, endpoints,visual_model = None):
    # Each beam has two endpoints (i and j)
    self.endpoints = EndPoints(i=endpoints[0], j=endpoints[1])

    # Each beam keeps track of all its joints. This is a dictionary as follows:
    # {coord : list of beams}
    self.joints = {}

    # This is the name of the beam
    self.name = name

    # This is how much each beam weighs
    self.weight = variables.beam_load

    self.visual_model = visual_model

  def current_state(self):
    '''
    Returns the current state
    '''
    joints = {}
    for coord, beams in self.joints.items():
      for beam in beams:
        if coord in joints:
          joints[coord].append(beam.name)
        else:
          joints[coord] = [beam.name]

    return {  'endpoints' : self.endpoints,
              'joints'    : joints,
              'weight'    : self.weight  }

  def addjoint(self, coord, beam):
    '''
    Adds a joint (at the specified coordinate), to the beam itself. The beam 
    variable defines the which crosses this one at the joint
    '''
    # Verify that the coordinate is on the beam based on endpoints
    if not helpers.on_line(self.endpoints.i, self.endpoints.j, coord):
      return False

    else:
      coord = Coord(x=coord[0],y=coord[1],z=coord[2])
      # We cycle manually so we can compare using our compare function
      for key, beams in self.joints.items():
        # We have a key and the beam isn't already there
        if helpers.compare_tuple(key,coord) and beam not in beams:
          self.joints[key].append(beam)
          return True

      self.joints[coord] = [beam]
      return True

  def removejoint(self,coord, beam):
    '''
    Removes a specified joint from this beam. Returns whether or not the removal
    was successful.
    '''
    coord = Coord(x=coord[0],y=coord[1],z=coord[2])
    # The joint is not on the beam
    if not coord in self.joints:
      return False

    else:
      # The beam is not at this joint
      if not beam in self.joints[coord]:
        return False
      else:
        self.joints[coord].remove(beam)

        # remove the coordinate if there are no beams there
        if self.joints[coord] == []:
          self.joints.pop(coord, None)
        return True

class Beam(DumbBeam):
  '''
  This class keeps track of both the original design location of the tubes and 
  of the deflected location based on the analysis results
  '''
  def __init__(self, name, endpoints,endpoint_names, visual_model = None):
    super(Beam,self).__init__(name,endpoints,visual_model)

    self.endpoint_names = EndPoints(i=endpoint_names[0],j=endpoint_names[1])
    
    # Keeps track of the amoung of deflection
    self.deflection = None

    # Deflected enpoints
    self.deflected_enpoints = self.get_true_endpoints()

    # Keeps track of the deflected endpoint we last wrote out 
    # This makes a faster visualization (we only change the visualization) when
    # there's a change that will be noticeable.
    self.previous_write_endpoints = None

  def current_state(self):
    '''
    Adding deflected endpoints to state
    '''
    state = super(Beam,self).current_state()

    state.update({ 'deflected_enpoints'        : self.deflected_enpoints,
                  'deflection'                : self.deflection,
                  'previous_write_endpoints'  : self.previous_write_endpoints,
                  'endpoint_names'            : self.endpoint_names })

    return state

  def update_deflection(self,i_val,j_val):
    '''
    Updates the deflection using a named tupled
    '''
    # Update deflection
    self.deflection = EndPoints(i=i_val,j=j_val)

    # Update endpoints
    self.deflected_endpoints = self.get_true_endpoints()

    return (self.previous_write_endpoints is None or helpers.distance(
      self.deflected_endpoints.i,self.previous_write_endpoints.i) 
      >= variables.visualization_step or helpers.distance(
        self.deflected_endpoints.j,self.previous_write_endpoints.j) >=
      variables.visualization_step)

  def global_default_axes(self):
    '''
    Returns the default local axes. Later on we might incorporate the ability to return
    rotated axes.
    '''
    axis_1 = helpers.make_unit(helpers.make_vector(self.endpoints.i,
      self.endpoints.j))
    vertical = (math.sin(math.radians(helpers.smallest_angle(axis_1,(0,0,1)))) 
      <= 0.001)

    # Break up axis_1 into unit component vectors on 1-2 plane, along with 
    # their maginitudes
    u1, u2 = (axis_1[0],axis_1[1],0),(0,0,axis_1[2])
    l1,l2 = helpers.length(u1), helpers.length(u2)
    u1 = helpers.make_unit(u1) if not helpers.compare(l1,0) else (1,1,0) 
    u2 = helpers.make_unit(u2) if not helpers.compare(l2,0) else (0,0,1)

    # Calculate axis_2 by negating and flipping componenet vectors of axis_1
    axis_2 = (1,0,0) if vertical else helpers.make_unit(helpers.sum_vectors(
      helpers.scale(-1 * l2,u1),helpers.scale(l1,u2)))

    # Calculate axis_3 by crossing axis 1 with axis 2 (according to right hand
    # rule)
    axis_3 = helpers.cross(axis_1,axis_2)
    axis_3 = helpers.make_unit((axis_3[0],axis_3[1],0)) if vertical else axis_3

    # Sanity checks
    # Unit length
    assert helpers.compare(helpers.length(axis_3),1)

    # On the x-y plane
    assert helpers.compare(axis_3[2],0)

    return axis_1,axis_2,axis_3

  def get_true_endpoints(self):
    '''
    Takes into account the deflection and returns the true physical endpoints of
    the structure
    '''
    if self.deflection is None:
      return self.endpoints
    else:
      return EndPoints(i=helpers.sum_vectors(self.endpoints.i,self.deflection.i),
       j=helpers.sum_vectors(self.endpoints.j,self.deflection.j))

