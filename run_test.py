from main import Simulation
from visualization import Visualization

# Variables
view = True

# Run the Simulation
sim = Simulation("Trial")
sim.start(view,1)
sim.run_simulation(view,6000)

# Display the simulation
sim.run_visualization()
