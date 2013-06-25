import os, errno, math
from sap2000 import variables
from sap2000.constants import LOAD_PATTERN_TYPES

def check(return_value, message):
  '''
  Used to check that the return value of the SAP2000 functions is zero. Provides nice failure in
  case it's not.
  '''
  if return_value == 0:
    pass
  else:
    print(message)
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
  dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

  return dist

def distance_to_line(l1,l2,p):
  '''
  Calculates the distance from the line (l1 -> l2) to the point (p)
  '''
  xl1, yl1, zl1 = l1
  xl2, yl2, xl2 = l2
  x, y , z = p

  # vector from one endpoint of line to p
  a = (x - xl1, y - yl1, z - zl1)
  # unit line vector
  length = distance(l1,l2)
  assert length > 0
  v = (xl2 - xl1 / length, yl2 - yl1 / length, zl2 - zl1 / length)

  # cross the two and return the magnitude of result (this is the distance)
  return length(cross(a,v))

def vector_to_line(l1,l2,p):
  '''
  Calculates the vector from the point p to the nearest location on the line
  formed by l1,l2
  '''
  # Unit line vector
  xl1, yl1, zl1 = l1
  xl2, yl2, xl2 = l2
  x, y , z = p

  # vector from one endpoint of line to p
  a = (x - xl1, y - yl1, z - zl1)
  # unit line vector
  length = distance(l1,l2)
  assert length > 0
  v = (xl2 - xl1 / length, yl2 - yl1 / length, zl2 - zl1 / length)

  intersection = sum_vectors(l1,scale(dot(a,unit),unit))

  return sub_vectors(intersection,p)

def check_location(p):
  '''
  Returns whether or not all elements in p are positive and are inside the restricted coordinates
  '''
  x,y,z = p
  return (x >=0 and y >= 0 and z >= 0 and x < variables.dim_x and y < variables.dim_y and z < variables.dim_z)

def on_line(l1,l2,point):
  '''
  Returns whether the point lies close the line l1 -> l2. The error allowed is epsilon
  '''

  lx1,ly1,lz1 = l1
  lx2, ly2, lz2 = l2
  x, y, z = point
  dist1, dist2 = distance(l1,l2), distance(l1,point)
  
  # Taking care of the point being an endpoint
  if dist2 == 0:
    return True

  # creating two vectors
  v1 = (lx2 - lx1), (ly2 - ly1), (lz2 - lz1)
  v2 = (x - lx1), (y - ly1), (z - lz1)

  return compare(length(cross(v1,v2)),0) and between(lx1,lx2,x) and between(ly1,ly2,y) and between(lz1, lz2, z)

def between(c1,c2,c3):
  '''
  Returns whether or not c3 is between c1 and c2
  '''
  if c1 < c2:
    return c1 <= c3 and c3 <= c2
  else:
    return c2 <= c3 and c3 <= c1

def within(origin,size,point):
  '''
  Returns whether or not point is within the area designated by origin and size
  '''
  value = True
  for i in range(3):
    value = value and origin[i] <= point[i] and origin[i] + size[i] >= point[i] 
 
  return value

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
  return (abs(x - y) < variables.epsilon)

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

'''
Helper functions for vector operations when keeping track of the structure in Python
'''

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

def make_unit(v):
  ''' 
  Returns a unit vector in the same direction as v
  '''
  dist = length(v)
  return tuple(x / dist for x in v)

def sub_vectors(v1,v2):
  '''
  Subtracts the second vector from the first
  '''
  return tuple([x - y for x, y in zip(v1,v2)])

def length(v):
  return distance(v,(0,0,0))

def cross(v1,v2):
  '''
  Calculates the cross product between two vectors, v1 and v2
  '''
  x1, y1, z1 = v1
  x2, y2, z2 = v2

  return (y1 * z2 - y2 * z1, z1 * x2 - z2 * x1, x1 * y2 - x2* y1)

'''
Helper functions pertaining to the sap program
'''

def addloadpattern(model,name,myType,selfWTMultiplier = 0, AddLoadCase = True):
  '''
  Adds the specified load pattern to the defined model,
  checking to see if it exists first. If added successfully,
  returns true, otherwise false
  '''
  ret, number, names = model.LoadPatterns.GetNameList()

  # load case is already defined
  if name in names:
    return False

  # defining for the first time  
  else:
    ret = model.LoadPatterns.Add(name,LOAD_PATTERN_TYPES[myType],selfWTMultiplier,AddLoadCase)
    if ret == 0:
      return True
    else:
      return False

'''
Helper functions pertaining to the beams (especially intersections)
'''
def intersection(l1, l2):
  '''
  Finds as quickly as possible whether two line segments intersect, 
  returning their point of intersection if they do intersect.
  Using the suggestion found here: http://mathforum.org/library/drmath/view/62814.html
  '''
  def same_direction(v1,v2):
    ''' 
    Returns whether or not two known to be parallel vectors point in the same direction
    '''
    return dot(v1,v2) > 0

  # Get out coordinates
  p1, ep1 = l1
  p2, ep2 = l2

  # Obtain direction vectors
  v1 = make_vector(p1,ep1)
  v2 = make_vector(p2,ep2)

  # Cross v1 and v2, and cross (p2 - p1) and v2 and check whether or not they are parallel
  # Basically checks whether the two lines are coplanar (must be true if they intersect!)
  norm1 = cross(v1,v2)
  norm2 = cross(sub_vectors(p2,p1),v2)

  # norm1 and norm2 must be parallel (coplanar) but norm2 must be non-zero (not parallel)
  if not parallel(norm1,norm2) or length(norm1) == 0:
    return None

  # Obtain the distance along line1 travelled
  unsigned_a = length(norm2) / length(norm1)
  a = unsigned_a if same_direction(norm1, norm2) else -1 * unsigned_a

  return sum_vectors(p1,scale(a,v1))


def parallel(v1,v2):
  '''
  Returns whether or not two vectors are parallel
  '''
  return length(cross(v1,v2)) == 0