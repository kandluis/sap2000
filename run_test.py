from main import Simulation
import cProfile

sim = Simulation()
path = sim.start(1)
sim.run_simulation(50,outputfolder=path)
