#!/usr/bin/env python

from collections import namedtuple
import win32com.client as win32
from sap2000.constants import UNITS


class SapBase(object):
  def __init__(self, sap_com_object, sap_object):
    super(SapBase, self).__init__()

    self._sap = sap_com_object
    self._obj = sap_object

  def get_names(self):
    """ Returns the names of all defined elements/objects. """
    return_value, number_of_names, names = self._obj.GetNameList(1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return names

  def count(self):
    """ Returns a count of all the defined elements/objects. """
    return self._obj.Count()


class SapPropertiesBase(SapBase):
  def __init__(self, sap_com_object, sap_object):
    super(SapPropertiesBase, self).__init__(sap_com_object, sap_object)


class SapAreaProperties(SapPropertiesBase):
  def __init__(self, sap_com_object):
    super(SapAreaProperties, self).__init__(sap_com_object, sap_com_object.SapModel.PropArea)


class SapAnalysis(SapBase):
  def __init__(self, sap_com_object):
    super(SapAnalysis, self).__init__(sap_com_object, sap_com_object.SapModel.Analyze)

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
    return_value = self._obj.RunAnalysis()
    assert return_value == 0        # Ensure that everything went as expected

  def delete_all(self):
    """ Delete results for every load case. """
    return_value = self._obj.DeleteResults(Name="", All=True)
    assert return_value == 0        # Ensure that everything went as expected

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
    super(SapAreaElements, self).__init__(sap_com_object, sap_com_object.SapModel.AreaElm)

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
    super(SapAreaObjects, self).__init__(sap_com_object, sap_com_object.SapModel.AreaObj)


class SapGroups(SapBase):
  def __init__(self, sap_com_object):
    super(SapGroups, self).__init__(sap_com_object, sap_com_object.SapModel.GroupDef)

  def get_one(self, group_name):
    return_value, number_of_items, object_types, object_names = self._obj.GetAssignments(group_name, 1, [], [])
    assert return_value == 0    # Ensure that everything went as expected

    group = Group(group_name, set(), set(), set(), set(), set(), set(), set())
    for i in range(number_of_items):
      group[object_types[i]].add(object_names[i])

    return group

    def get_all(self):
        return [self.get_one(name) for name in self.get_names()]

if __name__=='__main__':
    sap= Sap2000()
    sap.start(filename="""D:/job/Elaiourgeio/SAP/yfistameno.sdb""")
    sap.hide()

    # sap.area_elements.get_names()
    # sap.area_elements.count()
    # sap.area_elements.get_points("1-1")
    # print(1)

    # sap.area_objects.get_names()
    # sap.area_objects.count()
    # sap.area_objects.get_points("1")
    # print(2)

    # sap.groups.get_names()
    # sap.groups.count()
    # sap.groups.validate_all()
    # print(3)
    # sap.groups.get_assignments("points_diafragma")
    #
    #sap.exit_application(False)