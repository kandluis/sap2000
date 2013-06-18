import os, errno
from sap2000 import variables

def check(return_value, message):
  '''
  Used to check that the return value of the SAP2000 functions is zero. Provides nice failure in
  case it's not.
  '''
  if return_value = 0:
    pass
  else:
    print message
    assert return_value == 0

def path_exists(path):
  '''
  Checks to see if a directory exists, and if it does not, creates it
  '''
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise

def distance(p1,p2):
  '''
  Returns the distance between p1 and p2
  '''
  x1,y1,z1 = p1
  x2,y2,z2 = p2
  dist = sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)*2)

  return dist

def on_line(l1,l2,point):
  '''
  Returns whether or not the point is located on the line specified by l1 and l2
  '''

  lx1,ly1,lz1 = l1
  lx2, ly2, lz2 = l2
  x, y, z = point
  dist1, dist2 = distance(l1,l2), distance(l1,point)

  # creating two vectors
  s1,s2,s3 = (lx2 - lx1) / dist1, (ly2 - ly1) / dist1, (lz2 - lz1) / dist1
  s11,s22,s33 = (x - lx1) / dist2, (y - ly1) / dist2, (z - lz1) / dist2
  
  ret1, ret2, ret3= compare(s1,s11), compare(s2,s22), compare(s3,s33)
  if ret1 == ret2 == ret3:
    return ret1
  else:
    return false

def correct(l1,l2,point):
  '''
  Returns the corrected version of 'point' so that it is within the line spanned by l1, l2
  '''
  # split up necessary data
  lx1,ly1,lz1 = l1
  lx2, ly2, lz2 = l2
  x, y, z = point
  dist = distance(l1,l2)

  # create vectors
  v1 = (lx2 - lx1) / dist, (ly2 - ly1) / dist, (lz2 - lz1) / dist
  v2 = (x - lx1), (y - ly1), (z - lz1)

  # use formula to calculate new vector
  point = sum_vectors(scale(dot(v1,v2),v1),l1)

  return point



def compare(x,y):
  '''
  Compares two int/floats by taking into account "epsilon"
  '''
  return (abs(x - y) < epsilon)

def dot(v1,v2):
  '''
  Dots two vectors
  '''
  loc1, dot = 0, 0
  for coord1 in v1:
    loc1 += 1
    loc2 = 0
    for coord2 in v2:
      loc2 += 1
      if loc1 == loc2:
        dot += coord1 * coord2

  # checking the lenght of the tuples
  assert (loc1 == loc2)

  return dot

def sum_vectors(v1,v2):
  '''
  Sums two vectors
  '''
  return tuple([x + y for x, y in zip(v1,v2)])

def scale(k,v):
  '''
  Scales the vector v by k
  '''
  return tuple(k * x for x in v)

def make_vector(p1,p2):
  '''
  Returns the vector between two points. P2 is the head, p1 the origin
  '''
  return sub_vectors(p2,p1)

def sub_vectors(v1,v2):
  '''
  Subtracts the second vector from the first
  '''
  return tuple([x - y for x, y in zip(v1,v2)])

def length(v):
  distace(v,(0,0,0))