from main import Simulation
from visualization import Visualization

# Variables
view = True

# Run the Simulation
sim = Simulation("Consider this a test, Watson")
sim.start(view,1)
sim.run_simulation(view,4000)

# Display the simulation
sim.run_visualization()
