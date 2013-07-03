from worker import Worker

class Swarm:
  def __init__(self,size, structure, program):
    # The number of robots in the swarm
    self.size = size

    # The location of the swarm.
    self.home = (0,0,0)

    # Access to the structure, so we can create workers
    self.structure = structure

    # Access to the program
    self.model = program

    # create workers
    self.workers = {}
    for i in range(size):
      name = "worker_" + str(i)

      # workers start at home
      location = (i,0,0) 
      self.workers[name] = Worker(structure,location,program)

  def decide(self):
    # Assert that the model has been analyzed
    if not self.model.model.GetModelIsLocked():
      self.model.model.SetModelIsLocked(True)

    # Tell each robot to make the decion
    for worker in self.workers:
      self.workers[worker].decide()

  def act(self):
    # Asser that the model is not locked!
    if self.model.model.GetModelIsLocked():
      self.model.model.SetModelIsLocked(False)

    # Tell each robot to act
    for worker in self.workers:
      self.workers[worker].do_action()

  def get_information(self):
    information = {}
    for name, worker in self.workers.items():
      information[name] = worker.current_state()

    return information

class ReactiveSwarm(Swarm):
  def __init__(self,size,structure,program):
    super(ReactiveSwarm, self).__init__(size,structure,program)

  def reset(self):
    '''
    Create a spanking new army of workers
    '''
    self.workers = {}
    for i in range(self.size):
      name = "worker_" + str(i)
      location = (i,0,0)
      self.workers[name] = Worker(self.structure,location,self.model)

  def on_ground(self):
    '''
    Returns whether or not all of the swarm is on the ground. If it is,
    no need to analyze the structure this time
    '''
    for worker in self.workers:
      if self.workers[worker].beam != None:
        return False

    return True