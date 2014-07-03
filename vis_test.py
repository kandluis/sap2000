from visualization import Visualization

revisualize = 'C:\\SAP 2000\\2014-Jul\\Jul-03\\06_17_45\\'

vis = Visualization(revisualize)
vis.load_data()
vis.run(False,inverse_speed=.1)
