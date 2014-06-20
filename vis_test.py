from visualization import Visualization

revisualize = 'C:\\SAP 2000\\2014-Jun\\Jun-19\\18_39_10\\'

vis = Visualization(revisualize)
vis.load_data()
vis.run(False,inverse_speed=.1)
