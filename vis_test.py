from visualization import Visualization

one_thousand = 'C:\\SAP 2000\\Jul-08\\14_53_17\\'
four_robots = "C:\\SAP 2000\\Jul-08\\17_55_09\\"
ten_robots = 'C:\\SAP 2000\\Jul-08\\18_09_43\\'

to_test = 'C:\\SAP 2000\\Jul-26\\17_06_16\\'

vis = Visualization(to_test)
vis.load_data()
vis.run(False,inverse_speed=.1)
