from visualization import Visualization

one_thousand = 'C:\\SAP 2000\\Jul-08\\14_53_17\\'
four_robots = "C:\\SAP 2000\\Jul-08\\17_55_09\\"
ten_robots = 'C:\\SAP 2000\\Jul-08\\18_09_43\\'

vis = Visualization('C:\\SAP 2000\\Jul-09\\10_48_32\\')
vis.load_data('swarm_visualization.txt','structure_visualization.txt')
vis.run(inverse_speed=.5)
