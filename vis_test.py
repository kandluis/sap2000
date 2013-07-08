from visualization import Visualization

folder = 'C:\\SAP 2000\\Jul-08\\10_47_14\\'
vis = Visualization(folder)
vis.load_data('swarm_visualization.txt','structure_visualization.txt')
vis.run(False)
