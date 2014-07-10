from visualization import Visualization

revisualize = 'C:\\SAP 2000\\2014-Jul\\Jul-10\\00_10_25\\'
#'C:\\SAP 2000\\2014-Jul\\Jul-03\\ \\'
# 16_42_37
# 17_01_07
# 17_24_31
#'C:\\SAP 2000\\2014-Jul\\Jul-08\\ \\'
# 13_47_27
#'C:\\SAP 2000\\2014-Jul\\Jul-10\\ \\'
# 00_10_25

vis = Visualization(revisualize)
vis.load_data()
vis.run(False,inverse_speed=.1)
