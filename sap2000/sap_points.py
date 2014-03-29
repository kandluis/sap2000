#!/usr/bin/env python

try:
    from sap_base import SapBase
except:
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
    return_value, x, y, z = self._obj.GetCoordCartesian(name,1.0,1.0,1.0,csys)
    assert return_value == 0        # Ensure that everything went as expected
    return x, y, z

  def get_cylindrical(self, name, csys="Global"):
    '''
    The function returns zero if the coordinates are successfully returned; 
    otherwise it returns nonzero. If successful, the function returns the r, 
    theta and z coordinates of the specified point object/element in the Present
    Units. The coordinates are reported in the coordinate system specified by 
    CSys
    '''
    return_value, r, theta, z = self._obj.GetCoordCylindrical(name, csys=csys)
    assert return_value == 0
    return r, theta, z

  def get_spherical(self, name, csys="Global"):
    '''
    The function returns zero if the coordinates are successfully returned; 
    otherwise it returns nonzero. If successful, the function returns the r, 
    theta and z coordinates of the specified point object/element in the Present
    Units. The coordinates are reported in the coordinate system specified by 
    CSys
    '''
    return_value, r, a, b = self._obj.GetCoordSpherical(name, csys=csys)
    assert return_value == 0
    return r, a, b

  def get_all(self, format):
    '''
    The function returns zero if the coordinates are successfully returned; 
    otherwise it returns nonzero. If successful, the function returns a 
    dictionary containing the name of all the objects/elements along with their 
    coordinates in the specified format. The default format is Cartesian.
    '''
    if format == "Cylindrical":
      return {name:self.get_cylindrical(name) for name in self.get_names()}
    elif format == "Spherical":
      return {name:self.get_spherical(name) for name in self.get_names()}
    else:
      return {name:self.get_cartesian(name) for name in self.get_names()}


class SapPointObjects(SapPointsBase):
  def __init__(self, sap_com_object):
    super(SapPointObjects, self).__init__(sap_com_object,
        sap_com_object.SapModel.PointObj)

  def addcartesian(self,pos,name = "1", csys = "Global", mergeOff = False,
    mergeNumber = 0):
    '''
    This function adds a point object to a model. The added point object will be
    tagged as a Special Point except if it was merged with another point object.
    Special points are allowed to exist in the model with no objects connected 
    to them. The function returns zero if the point object is successfully added
    or merged, otherwise it returns a nonzero value.
    '''
    x,y,z = pos
    return_value, name = self._obj.AddCartesian(x,y,z,name,name,csys, mergeOff,
        mergeNumber)
    assert return_value == 0
    return name

  def addcylindrical(self,pos,name = "1", csys = "Global", mergeOff = False,
    mergeNumber = 0):
    '''
    Same as addcartesian but in Cylindrical Coordinates instead. Therefore pos 
    should be in theform (r, theta, z)
    '''
    r, theta ,z = pos
    return_value, name = self._obj.AddCylindrical(x,theta,z,name,name,csys, 
      mergeOff, mergeNumber)
    assert return_value == 0
    return name

  def addspherical(self,pos,name = "1", csys = "Global", mergeOff = False,
    mergeNumber = 0):
    '''
    Similar to addcartesian and addcylindrical but in Spherical Coordinates 
    instead. Therefore, pos should be in form (r, a, b) where a is the angle on
    the xy-plane and 
    '''
    r, a, b = pos
    return_value, name = self._obj.AddSpherical(x,y,z,name,name,csys,mergeOff,
      mergeNumber)
    assert return_value == 0
    return name

  def restraint(self,name,DOF):
    return_value, DOF = self._obj.SetRestraint(name,DOF)
    return return_value == 0


class SapPointElements(SapPointsBase):
  def __init__(self, sap_com_object):
    super(SapPointElements, self).__init__(sap_com_object,
      sap_com_object.SapModel.PointElm)