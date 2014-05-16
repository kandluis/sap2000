from visualization import Visualization

one_thousand = 'C:\\SAP 2000\\Jul-08\\14_53_17\\'
four_robots = "C:\\SAP 2000\\Jul-08\\17_55_09\\"
ten_robots = 'C:\\SAP 2000\\Jul-08\\18_09_43\\'

to_test = 'C:\\SAP 2000\\Aug-15\\19_39_21\\'
latest = 'C:\\SAP 2000\\Aug-16\\15_33_11\\'

spring = 'C:\\SAP 2000\\Apr-25\\00_03_58\\'

new_brain = 'C:\\SAP 2000\\2014-May\\May-14\\12_56_07\\'

vis = Visualization(new_brain)
vis.load_data()
vis.run(False,inverse_speed=.1)
