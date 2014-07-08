from variables import WORLD, PROGRAM

# home location
HOME = {
  # corner of home 
  'corner'  : (WORLD['properties']['dim_x'] * 0.4, WORLD['properties']['dim_y'] * 0.4,0),

  # Size of home, measured from the home location along the +x, +y, and +z axes
  'size'    : (40, 40, 0)#PROGRAM['epsilon'])
}

HOME.update({
  # The exact center of the defined home square
  'center'  : tuple([h_coord + size_coord / 2 for h_coord, size_coord in 
      zip(HOME['corner'], HOME['size'])])
})

# WORLD['propert']['are s']imilar to the above
CONSTRUCTION = {
  'corner'  : (WORLD['properties']['dim_x'] * 0.5, WORLD['properties']['dim_y'] * 0.5,0),
  'size'    : (40,40, 0)#PROGRAM['epsilon'])
}

CONSTRUCTION.update({
  'center'  : tuple([h_coord + size_coord / 2 for h_coord, size_coord in 
      zip(CONSTRUCTION['corner'],CONSTRUCTION['size'])])
})
