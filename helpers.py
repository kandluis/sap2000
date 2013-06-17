import os
import errno

def check(return_value, message):
  if return_value = 0:
    pass
  else:
    print message
    assert return_value == 0

def path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def get_nearby(loc, points, count):
  for point in points:
    distance = distance(loc, point)

def distance(p1,p2):
  x1,y1,z1 = p1
  x2,y2,z2 = p2
  dist = sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)*2)

  return dist
