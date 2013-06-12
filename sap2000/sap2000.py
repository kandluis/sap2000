import win32com.client as win32
from sap2000.constants import UNITS
from sap2000.sap_groups import SapGroups
from sap2000.sap_areas import SapAreaObjects, SapAreaElements
from sap2000.sap_points import SapPointObjects, SapPointElements
from sap2000.sap_analysis import SapAnalysis


class Sap2000(object):
  def __init__(self):
    super(Sap2000, self).__init__()

    # create the Sap2000 COM-object
    sap_com_object = win32.gencache.EnsureDispatch("SAP2000v15.sapobject")
    self.sap_com_object = sap_com_object

    # Each of the following attributes represents an object of the SAP2000 type library.
    # Each attribute is an instance of a subclass of SapBase.
    self.groups = SapGroups(sap_com_object)
    self.area_elements = SapAreaElements(sap_com_object)
    self.point_elements = SapPointElements(sap_com_object)
    self.area_objects = SapAreaObjects(sap_com_object)
    self.point_objects = SapPointObjects(sap_com_object)
    self.analysis = SapAnalysis(sap_com_object)

  def start(self, units="kN_m_C", visible=True, filename=""):
    """
    Starts the Sap2000 application.

    When the model is not visible it does not appear on screen and it does
    not appear in the Windows task bar.  If no filename is specified, you
    can later open a model or create a model through the API.  The file name
    must have an .sdb, .$2k, .s2k, .xls, or .mdb extension. Files with .sdb
    extensions are opened as standard SAP2000 files. Files with .$2k and
    .s2k extensions are imported as text files. Files with .xls extensions
    are imported as Microsoft Excel files. Files with .mdb extensions are
    imported as Microsoft Access files.
    """
    units = UNITS[units]
    self.sap_com_object.ApplicationStart(units, visible, filename)

  def exit(self, save_file=False):
    """ If the model file is saved then it is saved with its current name. """
    self.sap_com_object.ApplicationExit(save_file)
    self.sap_com_object = None

  def hide(self):
    """
    This function hides the Sap2000 application. When the application is
    hidden it is not visible on the screen or on the Windows task bar.  If
    the application is already hidden calling this function returns an
    error.
    """
    self.sap_com_object.Hide()

  def show(self):
    """
    This function unhides the Sap2000 application, that is, it makes it
    visible.  When the application is hidden, it is not visible on the
    screen or on the Windows task bar.  If the application is already
    visible (not hidden) calling this function returns an error.
    """
    self.sap_com_object.Unhide()

  def open(self, filename):
    """
    This function opens an existing Sap2000 file.

    The file name must have an sdb, $2k, s2k, xlsx, xls, or mdb extension.
    Files with sdb extensions are opened as standard Sap2000 files. Files
    with $2k and s2k extensions are imported as text files. Files with xlsx
    and xls extensions are imported as Microsoft Excel files. Files with mdb
    extensions are imported as Microsoft Access files.
    """
    return_value = self.sap_com_object.SapModel.File.OpenFile(filename)
    assert return_value == 0        # Ensure that everything went as expected

  def save(self, filename=""):
    """
    If a file name is specified, it should have an .sdb extension. If no file name is specified,
    the file is saved using its current name. If there is no current name for the file (the file
    has not been saved previously) and this function is called with no file name specified, an
    error will be returned.
    """
    return_value = self.sap_com_object.SapModel.File.SaveFile(filename)
    assert return_value == 0        # Ensure that everything went as expected


if __name__=='__main__':
  sap = Sap2000()
  sap.start(filename="""C:/job/Elaiourgeio/SAP/yfistameno.sdb""")
  sap.hide()