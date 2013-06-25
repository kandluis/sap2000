from sap2000 import variables
from robots import Movable
import helpers, construction

class Worker(Movable):
  def __init__(self,structure,location,program):
    super(Worker,self).__init__(structure,location,program)
    self.num_beams = variables.beam_capacity
    self.at_top = False
    self.upwards = False
    self.steps_to_construct = construction.steps_to_start

  def __pickup_beams(num = variables.beam_capacity):
    self.num_beam = self.num_beams + num
    self.weight = self.weight + variables.beam_load * num

  def __discard_beams(num = 1):
    self.num_beam = self.num_beam - num
    self.weight = self.weight - variables.beam_load * num

  def do_action(self):
    '''
    Overwriting the do_action functionality in order to have the robot move up or downward
    (depending on whether he is carrying a beam or not), and making sure that he gets a chance
    to build part of the structure if the situation is suitable.
    '''
    # If we can't construct here, then move
    if not self.construct():
      super(Worker,self).do_action()

    # Otherwise crawl somewhere else
    else:
      super(Worker,self).do_action()

  def get_direction(directions):
    ''' 
    Figures out which direction to move in. This means that if the robot is carrying a beam,
    it wants to move upwards. If it is not, it wants to move downwards. So basically the direction
    is picked by filtering by the z-component
    '''
    def filter_dict(dirs, new_dirs, comp_f):
      '''
      Filters a dictinary, taking out all directions not in the correct z-direction
      '''
      for beam, vectors in info['directions'].items():
        for vector in vectors:
          # vector[2] = the z-component
          if comt_f(vector[2]):
            new_dirs[beam] = vector
      return new_dirs

    # Get all the possible directions, as normal
    info = self.get_directions_info()

    # Still have beams, so move upwards
    directions = {}
    if self.num_beams > 0 or self.upwards:
      directions = filter_dict(info['directions'], directions, lambda z : z > 0)
    # No more beams, so move downwards
    else:
      directions = filter_dict(info['directions'], directions, lambda z : z < 0)

    from random import choice

    # This will only occur if no direction changes our vertical height. If this is the case, get directions as before
    if directions == {}:
      beam_name = choice(list(info['directions'].keys()))
      direction = choice(info['directions'][beam_name])
    # Otherwise we do have a set of directions taking us in the right place, so randomly pick any of them
    else:
      beam_name = choice(list(diretions.keys()))
      direction = directions[beam_name]

    return {  'beam'      : info['box'][beam_name],
              'direction' : direction }

  def wander(self):
    '''    
    When a robot is not on a structure, it wanders. The wandering in the working class
    works as follows. The robot moves around randomly with the following restrictions:
      The robot moves towards the home location if it has no beams and 
        the home location is detected nearby.
      Otherwise, if it has beams for construction, it moves toward the base specified construction
      site. If it finds another beam nearby, it has a tendency to climb that beam instead.
    '''
    def at_home():
      return within(construction.home, construction.home_size, self.__location)

    # Check to see if robot is at home location and has no beams
    if at_home() and self.num_beams == 0 :
      self.__pickup_beams(variables.beam_capacity)

    # Check to see if robot should build based on steps taken
    # This has been removed
    '''
    if self.steps_to_construct == 0:
      self.build()
    '''

    # Find nearby beams to climb on
    result = self.ground()
    if result == None:
      direction = self.get_ground_direction()
      new_location = helpers.sum_vectors(self.__location,helpers.scale(self.__step, helpers.make_unit(direction)))
      self.__change_location_local(new_location)
      # self.steps_to_construct -= 1
    else:
      dist, close_beam, direction = result['distance'], result['beam'], result['direction']

      # If the beam is within steping distance, just jump on it
      if self.num_beams > 0 and dist <= self.__step:
        # Set the beam as the current one, and set the ground direction to None (so we walk randomly if we do get off the beam again)
        self.beam = close_beam
        self.__ground_direction = None

        # Then move on the beam
        self.move(direction, close_beam)

      # If we can "detect" a beam, change the ground direction to approach it
      elif self.num_beams > 0 and dist <= variables.local_radius:
        self.__ground_direction = direction
        new_location = helpers.sum_vectors(self.__location, helpers.scale(self.__step, helpers.make_unit(direction)))
        self.__change_location_local(new_location)
      else:
        direction = self.get_ground_direction()
        new_location = helpers.sum_vectors(self.__location,helpers.scale(self.__step, helpers.make_unit(direction)))
        self.__change_location_local(new_location)
        # self.steps_to_construct -= 1


  def build(self):
    '''
    This functions sets down a beam. This means it "wiggles" it around in the air until
    it finds a connection (programatically, it just finds the connection which makes the smallest
    angle). Returns false if something went wrong, true otherwise.
    '''
    # This is the i-end of the beam being placed. We pivot about this
    pivot = self.__location

    # This is the j-end of the beam (if directly vertical)
    vertical_point = helpers.sum_vectors(self.__location,(0,0,variables.beam_length))

    # get all beams nearby (ie, all the beams in the current box and possible those further above)
    local_box = self.__structure.get_box(self.__location)
    top_box = self.__structure.get_box(vertical_point)

    # Ratios contains the ratio dist / delta_z where dist is the shortest distance from the vertical beam
    # segment to a beam nearby and delta_z is the z-component change from the pivot point to the intersection point
    ratios = {}
    for name in local_box:
      beam = local_box[name]
      intersection_point = helpers.intersection((beam.endpoints.i,beam.endpoints.j),(pivot, vertical_point))
      if intersection_point != None:
        # calculate the distance to the point, the change in z, and use that to calculate the ration
        vector = helpers.vector_to_line(beam.endpoints.i,beam.endpoints.j,intersection_point)
        if name in angles:
        intersection_point = helpers.intersection(())
        assert compare(ratios[name], helpers.)


  def construct(self):
    '''
    Decides whether the local conditions dictate we should build (in which case)
    It returns the two points that should be connected, or we should continue moving 
    (in which case, it returns None)
    ''' 
    return False