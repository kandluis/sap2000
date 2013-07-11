from main import Simulation
from visualization import Visualization

# Variables
view = False

# Run the Simulation
sim = Simulation()
sim.start(view,20)
sim.run_simulation(view,4000)

# Display the simulation
sim.run_visualization()
