#!/usr/bin/env python

class SapAnalysis(object):
  def __init__(self, sap_com_object):
    super(SapAnalysis, self).__init__()

    self._sap = sap_com_object
    self._obj = sap_com_object.SapModel.Analyze

  def run(self):
    """
    Run the analysis. The analysis model is automatically created as part of
    this function.

    Your model must have a file path defined before running the analysis. If
    the model is opened from an existing file, a file path is defined. If
    the model is created from scratch, the File.Save function must be called
    with a file name before running the analysis. Saving the file creates
    the file path.
    """
    print('ANALYSIS WAS RUN')
    return_value = self._obj.RunAnalysis()
    assert return_value == 0        # Ensure that everything went as expected

  def delete_all(self):
    """ Delete results for every load case. """
    return_value = self._obj.DeleteResults(Name="", All=True)
    assert return_value == 0        # Ensure that everything went as expected
