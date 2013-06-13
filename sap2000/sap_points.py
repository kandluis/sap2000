#!/usr/bin/env python

from sap2000.sap_base import SapBase

class SapPointsBase(SapBase):
  def __init__(self, sap_com_object, sap_object):
    super(SapPointsBase, self).__init__(sap_com_object, sap_object)

  def get_cartesian(self, name, csys="Global"):
    """
    Returns the x, y and z coordinates of the specified point object in the
    Present Units. The coordinates are reported in the coordinate system
    specified by Csys
    """
    return_value, x, y, z = self._obj.GetCoordCartesian(name, 1.0, 1.0, 1.0, csys)
    assert return_value == 0        # Ensure that everything went as expected
    return x, y, z

  def get_all(self):
    return {name:self.get_cartesian(name) for name in self.get_names()}


class SapPointObjects(SapPointsBase):
  def __init__(self, sap_com_object):
    super(SapPointObjects, self).__init__(sap_com_object, sap_com_object.SapModel.PointObj)


class SapPointElements(SapPointsBase):
  def __init__(self, sap_com_object):
    super(SapPointElements, self).__init__(sap_com_object, sap_com_object.SapModel.PointElm)