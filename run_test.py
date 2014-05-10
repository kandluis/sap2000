from main import Simulation
from visualization import Visualization

# Variables (see Documentation for description)
view = True
seed = "F@st1#lAn3"
robot_number = 1
maxsteps = 10000

# Run the Simulation, input is the random seed
sim = Simulation()
sim.start(view,robot_number)
sim.run_simulation(view,maxsteps)

# Display the simulation
sim.run_visualization()
