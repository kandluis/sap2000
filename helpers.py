import os
import errno

def path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def get_nearby(loc, points, count):
  for point in points:
    distance = distance(loc, point)

def distance((x1,y1,z1), (x2,y2,z2)):
	return sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)