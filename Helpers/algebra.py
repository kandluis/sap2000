'''
Helper functions for vector operations when keeping track of the structure in 
Python. Basically a small, self contained linear algebra package for the simulation
which contains many helpful functions such as:

normalize()
'''
# Default Python libraries
import math

# Constants for the simulation are stored in this file
from variables import PROGRAM

def normalize(v,max_val):
  '''
  Normalizes the vector v. If the magnide of v is max_val, then v becomes a unit
  vector in the original direction of v. Otherwise, it is a scalar multiple based
  on the ratio maginute_of_v/max_val. v must be non-zero
  '''
  assert not compare(length(v),0)

  # Obtain unit direction and scale factor
  unit = make_unit(v)
  scalar = length(v) / max_val

  # Return normalized vectors
  return scale(scalar,unit)

def compare(x,y,e=PROGRAM['epsilon']):
  '''
  Compares two int/floats by taking into account "epsilon"
  '''
  return (abs(x - y) < e)

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
  assert not compare(dist,0)
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
  return compare(length(cross(v1,v2)),0,0.01)


# MATRIX OPERATIONS

def addMatrices(a,b):
  '''
  Takes in two lists of lists (i.e. matrices) of equal dimensions and adds them.
  '''
  res = []
  for i in range(len(a)):
      row = []
      for j in range(len(a[0])):
          row.append(a[i][j]+b[i][j])
      res.append(row)
  return res

def multiplyMatrices(A, B):
  '''
  Takes in two lists of lists (i.e. matrices) with appropriate dimensions 
  and multiplies them.
  '''
  rows_A = len(A)
  cols_A = len(A[0])
  rows_B = len(B)
  cols_B = len(B[0])
  if cols_A != rows_B:
    print("Cannot multiply the two matrices. Incorrect dimensions.")
    return
  # Create the result matrix
  # Dimensions would be rows_A x cols_B
  C = [[0 for row in range(cols_B)] for col in range(rows_A)]
  #print(C)
  for i in range(rows_A):
      for j in range(cols_B):
          for k in range(cols_A):
              C[i][j] += A[i][k] * B[k][j]
  return C

def multiplyScalar(A, c):
  return tuple(scale(c,row) for row in A)