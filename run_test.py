import pdb
import traceback
import sys
import random

from main import Simulation
from visualization import Visualization

# Variables (see Documentation for description)
view = True
# To turn on/off the use of SAP, go to Helpers/helpers.py and change the
# global variable "SAP_PHYSICS" (defined after the import statements) to True/False.
seed = "r@nd0M2"
robot_number = 10
maxsteps = 10000
debug = 0 # begin debugging AFTER this timestep. 0 turns off debugging, change to 1 to debug w/ PDB
comment = seed

# seeding the simulation: turn this on to remove randomness in brain (for debugging)
# behavior between runs will be identical.
#random.seed(seed)

# Run the Simulation, input is the random seed
Sim = Simulation()
Sim.start(view, robot_number)

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
#SAP 2000 templates.sdb
