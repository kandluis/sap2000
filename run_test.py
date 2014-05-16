import pdb
import traceback
import sys
import random

from main import Simulation
from visualization import Visualization

# Variables (see Documentation for description)
view = True
seed = "r@nd0M2"
robot_number = 2
maxsteps = 10000
debug = 1 # begin debugging after this timestep. 0 turns off debugging
comment = seed

# seeding the simulation
random.seed(seed)

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
