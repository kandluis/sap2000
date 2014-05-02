def is_vertical(v):
  '''
  Returns whether we consider the vector v to be vertical. This error angle is
  defined in variables.py
  '''
  angle = smallest_angle(v,(0,0,1))
  angle = angle if angle <= 90 else 180 - angle

  return angle <= construction.beam['verticality_angle']