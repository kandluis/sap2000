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
    super(SapAreaProperties, self).__init__(sap_com_object,
      sap_com_object.SapModel.PropArea)