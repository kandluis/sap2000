#!/usr/bin/env python

from sap2000.sap_base import SapBase


class SapFramesBase(SapBase):
  def __init__(self, sap_com_object, sap_object):
    super(SapFramesBase, self).__init__(sap_com_object, sap_object)

  def get_points(self, name):
    """
    Returns the names of the point elements/objects that define an area
    element/object.
    """
    return_value, i_end, j_end = self._obj.GetPoints(name, 1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return (i_end, j_end)

class SapFrameObjects(SapFramesBase):
  def __init__(self, sap_com_object):
    super(SapFrameObjects, self).__init__(sap_com_object, sap_com_object.SapModel.FrameObj)

  def get_frame_elements(self, frame_object_name):
    """
    Returns the names of the frame elements (analysis model area) associated
    with a specified frame object in the object-based model.
    """
    return_value, number_of_elements, elements = self._obj.GetElm(frame_object_name, 1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return elements

  def add(self, p1, p2, name="", propName = "Default"):
    '''
    This function adds a new frame object whose end points are specified by name.
    The function returns zero if the frame object is successfully added, otherwise 
    it returns a nonzero value.
    '''
    return_value, name = self._obj.AddByPoint(p1,p2,name,propName,name)
    assert return_value == 0
    return name

  def addbycoord(self,p1,p2,name, propName = "Default"):
    '''
    This function adds a new frame object whose end points are specified by coordinate.
    The function returns zero if the frame object is successfully added, otherwise 
    it returns a nonzero value.
    '''
    x1,y1,z1 = p1
    x2,y2,z2 = p2
    return_value, name = self._obj.AddByCoord(x1,y1,z1,x2,y2,z2,name, propName,name)
    assert return_value == 0
    return name

