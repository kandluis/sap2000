from main import Simulation
from visualization import Visualization

# Variables
view = True

# Run the Simulation, input is the random seed
sim = Simulation("F@st1#lAn3-test")
sim.start(view,1)
sim.run_simulation(view,10000)

# Display the simulation
sim.run_visualization()
