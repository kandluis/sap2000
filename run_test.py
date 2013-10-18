from main import Simulation
from visualization import Visualization

# Variables
view = True

# Run the Simulation
sim = Simulation("Papyrus")
sim.start(view,1)
sim.run_simulation(view,10000)

# Display the simulation
sim.run_visualization()
