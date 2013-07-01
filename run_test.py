from main import Simulation

sim = Simulation()
path = sim.start(1)
sim.run_simulation(40,outputfolder=path)
