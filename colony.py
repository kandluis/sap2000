from worker import Worker

class Swarm:
  def __init__(self,size, structure, program):
    # The number of robots in the swarm
    self.size = size

    # The location of the swarm.
    self.home = (0,0,0)

    # Access to the structure, so we can create workers
    self.__structure = structure

    # Access to the program
    self.__model = program

    # create workers
    self.workers = {}
    for i in range(size):
      name = "worker_" + str(i)

      # workers line up along the positive x axis
      location = (i,0,0)
      self.workers[name] = Worker(structure,location,program)

  def decide(self):
    # Assert that the model has been analyzed
    assert program.model.GetModelIsLocked()

    # Tell each robot to make the decion
    for worker in self.workers:
      self.workers[worker].decide()

  def act(self):
    # Asser that the model is not locked!
    assert not program.model.GetModelIsLocked()

    # Tell each robot to act
    for worker in self.workers:
      self.workers[worker].do_action()

  def get_locations(self):
    locations = {}
    for name in self.workers:
      locations[name] = self.workers[name].get_location()

    return locations

class ReactiveSwarm(Swarm):
  def __init__(self,size,structure,program):
    super(ReactiveSwarm, self).__init__(size,structure,program)