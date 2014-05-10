#!/usr/bin/env python
'''
Importing Necessary Modules.
  collections - used for namedtuple, comes default with Python 27 Installation.
  Also used by the Groups Elements of SAP 2000

  win32com.client used to call on SAP 200 API directly. Pywin32 must be installed.
  See Journal for clarification on procedure.

  constants - mappings from SAP API terminology to actual sap2000 function paramenters
  See the OAPI for SAP from more clarification, though most variables are self
  explanatory. 
'''
import win32com.client as win32
try:
  from constants import UNITS
except:
  from SAP2000.constants import UNITS

# allows easy creation of Endpoints and Coordinates data type
from collections import namedtuple

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Base Structure for SAP Element API access. This is the base class for wrappers
around the SAP 2000 OPIA for functions that are commently used to access elements
in the SAP2000 structure model.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
SAP Points. These structures are useful to keep track of both location (robots
  are just points with specific loads assigned to them), as well as 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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

  def get_cylindricsal(self, name, csys="Global"):
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


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Area and AreaElement from the SAP OAPI. There wil be useful for implementations
of 3D structures (as opposed to current strut based models (04/16/2014))
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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
    return_value, area_name = self._obj.GetProperty(name,[])
    assert return_value == 0        # Ensure that everything went as expected
    return area_name


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


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Line Elements are used as a foundation for both Frames and Area Elements, though
neither needs to be explicitly related in the code. This class provides direct access
to those elements. 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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
    super(SapLineElements, self).__init__(sap_com_object,
      sap_com_object.SapModel.LineElm)


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Frame and FrameElements. These are used throughout the code; most of the current
structure relies on Frame Elements.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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
    super(SapFrameObjects, self).__init__(sap_com_object,
      sap_com_object.SapModel.FrameObj)

  def get_frame_elements(self, frame_object_name):
    """
    Returns the names of the frame elements (analysis model area) associated
    with a specified frame object in the object-based model.
    """
    return_value, number_of_elements, elements = self._obj.GetElm(
      frame_object_name, 1, [])
    assert return_value == 0        # Ensure that everything went as expected
    return elements

  def add(self, p1, p2, name="", propName = "Default"):
    '''
    This function adds a new frame object whose end points are specified by 
    name. The function returns zero if the frame object is successfully added, 
    otherwise it returns a nonzero value.
    '''
    return_value, name = self._obj.AddByPoint(p1,p2,name,propName,name)
    if return_value != 0:
      print("Adding beam from {} to {} failed. Code in sap_frames.py".format(
        str(p1),str(p2)))
    return name

  def addbycoord(self,p1,p2,name="", propName = "Default"):
    '''
    This function adds a new frame object whose end points are specified by 
    coordinate. The function returns zero if the frame object is successfully 
    added, otherwise it returns a nonzero value.
    '''
    x1,y1,z1 = p1
    x2,y2,z2 = p2
    return_value, name = self._obj.AddByCoord(x1,y1,z1,x2,y2,z2,name,
      propName,name)
    if return_value != 0:
      print ("Adding beam at points {} - {} failed.".format(str(p1),str(p2)))
      
    return name


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Group Elements; still not used in current implementations of simulation, but 
will come in handy when creating joint structure (frams + area elements, etc)
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Group = namedtuple("Group",
  "name, points, frames, cables, tendons, areas, solids, links")
Shell = namedtuple("Shell",
  "name type drilling material angle membrane bending color notes guid")


class SapGroups(SapBase):
  def __init__(self, sap_com_object):
    super(SapGroups, self).__init__(sap_com_object,
      sap_com_object.SapModel.GroupDef)

  def get_one(self, group_name):
    return_value, number_of_items, object_types,
    object_names = self._obj.GetAssignments(group_name, 1, [], [])
    assert return_value == 0    # Ensure that everything went as expected

    group = Group(group_name, set(), set(), set(), set(), set(), set(), set())
    for i in range(number_of_items):
      group[object_types[i]].add(object_names[i])

    return group

  def get_all(self):
    return [self.get_one(name) for name in self.get_names()]