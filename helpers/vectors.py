'''
Helper functions for vector operations when keeping track of the structure in 
Python
'''
import math

def distance(p1,p2):
  '''
  Returns the distance between p1 and p2
  '''
  x1,y1,z1 = p1
  x2,y2,z2 = p2
  dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

  return dist
  
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

def make_unit(v):
  ''' 
  Returns a unit vector in the same direction as v
  '''
  dist = length(v)
  assert dist != 0
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

def parallel(v1,v2):
  '''
  Returns whether or not two vectors are parallel
  '''
  return length(cross(v1,v2)) == 0
