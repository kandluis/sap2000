from visualization import Visualization

revisualize = 'C:\\SAP 2000\\2014-Jul\\Jul-03\\16_42_37\\'
# 16_42_37
# 17_01_07

vis = Visualization(revisualize)
vis.load_data()
vis.run(False,inverse_speed=.1)
