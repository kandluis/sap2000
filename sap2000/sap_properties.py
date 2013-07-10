#!/usr/bin/env python

from sap2000.sap_base import SapBase

class SapPropertiesBase(SapBase):
  def __init__(self, sap_com_object, sap_object):
    super(SapPropertiesBase, self).__init__(sap_com_object,sap_object)


class SapAreaProperties(SapPropertiesBase):
  def __init__(self, sap_com_object):
    super(SapAreaProperties, self).__init__(sap_com_object,
      sap_com_object.SapModel.PropArea)
