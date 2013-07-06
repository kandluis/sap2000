from main import Simulation
import cProfile

view = False

sim = Simulation()
path = sim.start(view,1)
sim.run_simulation(view,100,outputfolder=path)
