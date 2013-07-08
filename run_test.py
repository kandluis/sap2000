from main import Simulation
from visualization import Visualization
import cProfile

# Variables
view = False

# Run the Simulation
sim = Simulation()
path = sim.start(view,4)
sim.run_simulation(view,200,outputfolder=path)

# Display the simulation
window = Visualization(path)
window.load_data('swarm_visualization.txt','structure_visualization.txt')
window.run()
