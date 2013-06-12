from collections import namedtuple
from sap2000.sap_base import SapBase


Group = namedtuple("Group", "name, points, frames, cables, tendons, areas, solids, links")
Shell = namedtuple("Shell", "name type drilling material angle membrane bending color notes guid")


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