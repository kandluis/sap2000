from robots import Worker

class Swarm:
	def __init__(self,size, structure, model):
		self.size = size
    self.home = (0,0,0)
    self.__structure = structure
    self.__model = model

		# create workers
		self.workers ={}
    	for i in range(size):
        name = "worker" + i
        location = (i,0,0)
        self.workers[name] = Worker(location,structure,model)

  def act(self):
    for worker in self.workers:
      worker.move()

class ReactiveSwarm(Swarm):
  def __init__(self,size,structure,model):
    super(ReactiveSwarm, self).__init__(size,structure,model)