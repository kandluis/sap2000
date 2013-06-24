from worker import Worker

class Swarm:
  def __init__(self,size, structure, program):
    self.size = size
    self.home = (0,0,0)
    self.__structure = structure
    self.__model = program

    # create workers
    self.workers = {}
    for i in range(size):
      name = "worker_" + str(i)

      # workers line up along the positive x axis
      location = (i,0,0)
      self.workers[name] = Worker(structure,location,program)

  def act(self):
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