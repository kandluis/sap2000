#!/usr/bin/env python

from sap2000.sap_base import SapBase

class SapLinesBase(SapBase):
  def __init__(self, sap_com_object, sap_object):
    super(SapLinesBase, self).__init__(sap_com_object, sap_object)

  def get_endpoints(self,name):
    """
    This function retrieves the names of the point elements at each end of a 
    specified line element. The function returns zero if the point names are 
    successfully retrieved, otherwise it returns a nonzero value.
    """
    return_value, iname, jname = self._obj.GetPoints(name)
    assert return_value == 0
    return iname, jname

  def get_allendpoints(self):
    return {name:self.get_endpoints(name) for name in self.get_names()}

class SapLineElements(SapLinesBase):
  def __init__(self, sap_com_object):
    super(SapLineElements, self).__init__(sap_com_object, sap_com_object.SapModel.LineElm)