import pdb
import traceback
import sys

from main import Simulation
from visualization import Visualization

# Variables (see Documentation for description)
view = True
seed = "F@st1#lAn3"
robot_number = 1
maxsteps = 10000
debug = 0 # begin debugging after this timestep. 0 turns off debugging
comment = ""

# Run the Simulation, input is the random seed
Sim = Simulation()
Sim.start(view,robot_number)

# wrapped in a try/except block to catch errors and immediately begin
# pdb at exception's location
try:
  Sim.run_simulation(view,maxsteps,debug,comment)
except:
  _, _, tb = sys.exc_info()
  traceback.print_exc()
  pdb.post_mortem(tb)

# Display the simulation
Sim.run_visualization()
