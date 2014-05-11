import os
from visualization import Visualization

class Open(object):
  def __init__(self,folder):
    self.folder = folder
    self.trials = sorted([name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder,name))])

  def run_trial(self,trial_num,fullscreen=True):
    '''
    Runs the visualization for the specified file number and returns the 
    visualization object.
    '''
    folder = os.path.join(self.folder,self.trials[trial_num-1]) + os.path.sep
    vis = Visualization(folder)
    vis.load_data()
    vis.run(fullscreen,inverse_speed=.25)

    return vis
