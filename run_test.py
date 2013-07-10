from main import Simulation
from visualization import Visualization

# Variables
view = False

# Run the Simulation
sim = Simulation()
sim.start(view,2)
sim.run_simulation(view,500)

# Display the simulation
sim.run_visualization()
