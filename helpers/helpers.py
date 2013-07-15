from sap2000.constants import LOAD_PATTERN_TYPES
from helpers.vectors import *
import errno, math, os, pdb, variables

def ratio(deg):
  return math.tan(math.radians(deg))

def check(return_value, robot, error, **data):
  '''
  Used to check that the return value of the SAP2000 functions is zero. Provides
  nice failure in case it's not.
  '''
  if return_value != 0:
    if error == "getting loads":
      message = "Warning. Was not able to retrieve loads."
    else:
      message = "Error occured when {}.".format(error)
    for name, item in data.items():
      message += "\n{}::{}".format(name,str(item))
    robot.error_data += message

def path_exists(path):
  '''
  Checks to see if a directory exists, and if it does not, creates it
  '''
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise 

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
  formed by l1,l2. The line is a segment.
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

  # Find distance from l1 to intersetion by projecting
  scalar_projection = dot(a,unit)

  # Checking. If its negative, it means that the point of intersection is before
  # l1. For our purposes, this means that the vector to the line_segment is the 
  # vector p -> l1
  if scalar_projection < 0:
    return make_vector(p,l1)

  intersection = sum_vectors(l1,scale(dot(a,unit),unit))

  # Checking. If the intersection is not between the endpoints, then p is closer
  # to l2. Since we already checked the closeness to l1.
  if not between_points(l1,l2,intersection):
    return make_vector(p,l2)

  # If we get here, the point closes to p is the point of intersection
  return sub_vectors(intersection,p)

def check_location(p):
  '''
  Returns whether or not all elements in p are positive and are inside the 
  restricted coordinates
  '''
  x,y,z = p
  return ((x > 0 or compare(x,0)) and (y > 0 or compare(y,0) and (z >= 0 or 
    compare(z,0)) and x < variables.dim_x and y < variables.dim_y and (z < 
    variables.dim_z)))

def on_line(l1,l2,point,segment = True):
  '''
  Returns whether the point lies close the line l1 -> l2. The error allowed is 
  epsilon
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

  return (compare(length(cross(v1,v2)),0) and (between(lx1,lx2,x) and 
    between(ly1,ly2,y) and between(lz1, lz2, z) or not segment))

def between_points(p1,p2,p3, inclusive = True):
  '''
  Returns whether the point p3 is between the points p1 and p2. inclusive.
  '''
  return_value = True
  for i in range(3):
    return_value = return_value and between(p1[i],p2[i],p3[i], inclusive)

  return return_value 

def between(c1,c2,c3, inclusive = True):
  '''
  Returns whether or not c3 is between c1 and c2, inclusive.
  '''
  compare = (lambda x,y: x <= y) if inclusive else (
    lambda x,y : x < y)
  if c1 < c2:
    return compare(c1,c3) and compare(c3,c2)
  else:
    return compare(c2,c3) and compare(c3,c1)

def within(origin,size,point):
  '''
  Returns whether or not point is within the area designated by origin and size
  '''
  value = True
  for i in range(3):
    value = value and origin[i] <= point[i] and origin[i] + size[i] >= point[i] 
 
  return value

def collinear(p1,p2,p3):
  '''
  Returns whether or not the three points are collinear.
  '''
  v1 = make_vector(p1,p2)
  v2 = make_vector(p1,p3)
  normal = cross(v1,v2)
  return compare(length(normal),0)

def correct(l1,l2,point):
  '''
  Returns the corrected version of 'point' so that it is within the line spanned
  by l1, l2
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

def compare_tuple(v1,v2):
  '''
  Comapres two floats using our compare function
  '''
  return all([compare(x,y) for x,y in zip(v1,v2)])

'''
Helper functions pertaining to the SAP program
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
    ret = model.LoadPatterns.Add(name,LOAD_PATTERN_TYPES[myType],
      selfWTMultiplier,AddLoadCase)
    if ret == 0:
      return True
    else:
      return False


'''
Helper functions pertaining to the beams (especially intersections)
'''
def intersection(l1, l2, segment = True):
  '''
  Finds as quickly as possible whether two line segments intersect, 
  returning their point of intersection if they do intersect.
  Using the suggestion found here: http://mathforum.org/library/drmath/view/
  62814.html. Also, even if the two lines would intersect (if stretched 
  infinitely), the function still returns None if the intersection point is 
  not within both line SEGMENTS
  '''
  def same_direction(v1,v2):
    ''' 
    Returns whether or not two known to be parallel vectors point in the same 
    direction
    '''
    return dot(v1,v2) > 0

  # Get out coordinates
  p1, ep1 = l1
  p2, ep2 = l2

  # Obtain direction vectors
  v1 = make_vector(p1,ep1)
  v2 = make_vector(p2,ep2)

  # Cross v1 and v2, and cross (p2 - p1) and v2 and check whether or not they 
  # are parallel. Basically checks whether the two lines are coplanar 
  # (must be true if they intersect!)
  norm1 = cross(v1,v2)
  norm2 = cross(sub_vectors(p2,p1),v2)

  # norm1 and norm2 must be parallel (coplanar) but norm2 must be non-zero 
  # (not parallel)
  if not parallel(norm1,norm2) or length(norm1) == 0:
    if (p1 == p2 and ep1 != ep2) or (p1 == ep2 and ep1 != p2):
      return p1
    elif (ep1 == ep2 and p1 != p2 or ep1 == p2 and p1 != ep2):
      return ep1
    else:
      return None
      
  # Obtain the distance along line1 travelled
  unsigned_a = length(norm2) / length(norm1)
  a = unsigned_a if same_direction(norm1, norm2) else -1 * unsigned_a

  # Get intersetion point
  intersection_point = sum_vectors(p1,scale(a,v1))

  # Verify that the point is in both line segments (ie, between the endpoints 
  # since we already know it is on both lines)
  if segment and (not between_points(p1,ep1,intersection_point) or 
    not between_points(p2,ep2,intersection_point)):
    return None

  return sum_vectors(p1,scale(a,v1))

def distance_between_lines(l1,l2):
  '''
  Calculates the distance between the lines l1 and l2
  '''
  # Direction vectors
  v1,v2 = make_vector(l1[0],l1[1]), make_vector(l2[0],l2[1])

  # If parallel, pick a point and return the distance to the other line
  if parallel(v1,v2):
    return distance_to_line(l1[0],l1[1],l2[0])

  # Find normal and diagonal vector
  normal = make_unit(cross(v1,v2))
  diagonal = make_vector(l1[0],l2[1])

  #return length of projection onto normal
  return abs(dot(diagonal,normal))

def closest_points(l1,l2, segment = True):
  '''
  Calculates the closests points between the line l1 and l2
  '''
  def endpoints(line1, line2):
    '''
    Returns one endpoint of line1 or line2 (which ever has a feasable projection
    onto the other line)
    '''
    points = []
    for endpoint in line1:
      point = correct(line2[0],line2[1],endpoint)
      dist = distance(point,endpoint)
      if between(line2[0],line2[1],point) and dist != 0:
        points.append(((point,endpoint),dist))

    return min(points,key=lambda t : t[1])

  def intersection_shift(line1,line2,shift,normal):
    '''
    Especialized function that shifts line2 by a set amount along the specified
    normal and attempts to find that line's intersection with line1
    '''
    # Positive and negative shift
    unit_normal = make_unit(normal)
    v_shift,vn_shift = scale(shift,unit_normal),scale(-1*shift,unit_normal)
    shift_i,shift_j,nshift_i,nshift_j = (sum_vectors(line2[0],v_shift),
      sum_vectors(line2[1],v_shift),sum_vectors(line2[0],vn_shift),
      sum_vectors(line2[1],vn_shift))

    # Get intersection points
    point1,point2 = intersection(line1,(shift_i,shift_j)),intersection(line1,(
      nshift_j,nshift_j))
    if point1 is not None and point2 is not None:
      raise Exception("Shifting created two intersections!?")
    elif point1 is not None:
      return point1
    elif point2 is not None:
      return point2
    else:
      return None


  # Get coordinates
  i1,j1 =  l1
  i2,j2 = l2

  # get direction vectors
  v1 = make_vector(i1,j1)
  v2 = make_vector(i2,j2)

  # Find normal
  normal = cross(v1,v2)

  # If the two are parallel, infinite points, so return None
  if length(normal) == 0:
    return None

  # Find the distance between the two lines
  travel = distance_between_lines(l1,l2)

  # Shift until we find an interesection point (coplanar)
  intersection_point = intersection_shift((i1,j1),(i2,j2),travel,normal)
  if intersection_point == None:
    # This means that the two lines segments don't intersect, so return the two
    # endpoints (whichever are closests to one another)
    return endpoints(l1,l2)

  # Now, find the intersection point between the original lines by moving the 
  # intersection point up until it meets the projected line. We pass in false 
  # because this new line needs to extend infinitely
  true_intersect_point = intersection((i2,j2),(intersection_point,sum_vectors(
    intersection_point,normal)),False)
  # This means that they are parallel, which should never happen.
  if true_intersect_point == None:
    raise Exception("Finding intersection point failed.")

  # Do a sanity check to make sure that the point is on the line we want
  assert on_line(l2[0],l2[1],true_intersect_point)

  # Now we verify the intersection point to make sure it is within the original 
  # l2.
  if not between_points(l2[0],l2[1],true_intersect_point) and segment:
    return None

  # Now return the two points.
  return (intersection_point, true_intersect_point)

def sphere_intersection(line, center, radius, segment = True):
  '''
  Calculates the intersection points a line/line segment (as defined by two 
  points) and a sphere as defined by a center point and a radius. 

  Possible return values -> None, One Point, Two Points
  Uses the algorithm described here: http://en.wikipedia.org/wiki/Line%E2%80%93
  sphere_intersection
  '''
  line_origin = line[0]
  unit_line_direction = make_unit(make_vector(line[0],line[1]))

  dif = sub_vectors(line_origin,center)
  discriminant = dot(unit_line_direction,dif)**2 - dot(dif,dif) + radius**2
  # Value under the square root is negative, so this line does not intersect 
  # the sphere
  if discriminant < 0:
    return None
  else:
    neg_b = -1 * dot(unit_line_direction,dif)
    # There is only one interesection point
    if discriminant == 0:
      p = sum_vectors(line_origin,scale(neg_b,unit_line_direction))
      # verify it is on the line segment
      if segment:
        if on_line(line[0],line[1],p):
          return p
        else:
          return None
      else:
        return p
    # Two solutions. We need to return only the ones in the segment
    else:
      p1 = sum_vectors(line_origin,scale(neg_b + discriminant,
        unit_line_direction))
      p2 = sum_vectors(line_origin,scale(neg_b - discriminant,
        unit_line_direction))
      if not segment:
        return p1,p2
      else:
        p1_bool, p2_bool = on_line(line[0],line[1],p1),on_line(line[0],line[1],
          p2)
        if p1_bool and p2_bool:
          return p1,p2
        elif p1_bool:
          return p1
        elif p2_bool:
          return p2
        else:
          return None
