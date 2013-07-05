from main import Simulation

sim = Simulation()
path = sim.start(1)
sim.run_simulation(50,outputfolder=path)
