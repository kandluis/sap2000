#!/usr/bin/env python

try:
    from sap_base import SapBase
except:
    from sap2000.sap_base import SapBase

class SapAreasBase(SapBase):
  def __init__(self, sap_com_object, sap_object):
    super(SapAreasBase, self).__init__(sap_com_object, sap_object)

  def get_property(self, name):
    """ Returns the area property assigned to an area object. """
    return_value, section_name = self._obj.GetPoints(name, 1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return points

  def get_points(self, name):
    """
    Returns the names of the point elements/objects that define an area
    element/object.
    """
    return_value, number_of_points, points = self._obj.GetPoints(name, 1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return points


class SapAreaElements(SapAreasBase):
  def __init__(self, sap_com_object):
    super(SapAreaElements, self).__init__(sap_com_object, 
        sap_com_object.SapModel.AreaElm)

  def get_area_object(self, area_element_name):
    """
    Returns the name of the area object from which an area element was
    created.
    """
    return_value, area_object_name = self._obj.GetObj(area_element_name, "")
    assert return_value == 0        # Ensure that everything went as expected
    return area_object_name


class SapAreaObjects(SapAreasBase):
  def __init__(self, sap_com_object):
    super(SapAreaObjects, self).__init__(sap_com_object, 
        sap_com_object.SapModel.AreaObj)

  def get_area_elements(self, area_object_name):
    """
    Returns the names of the area elements (analysis model area) associated
    with a specified area object in the object-based model.
    """
    return_value, number_of_elements, elements = self._obj.GetElm(
        area_object_name, 1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return elements