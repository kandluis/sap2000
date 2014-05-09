import math

# TODO - Go through code and fix references
WORLD = {
  # The size of the division of space into blocks. 
  # x,y,z gives the number of blocks along the x axix, the y axis, and the z axis
  # dim_var gives the limit of the structure on the axis indicated by var. 
  # Keep in mind that the origin is the bottom-left part of this structure
  'properties'  : {
    'origin' : (0,0,0),
    'num_x' : 10,
    'num_y' : 10,
    'num_z' : 100,
    'dim_x' : 1700, # 100 ft
    'dim_y' : 1700,
    'dim_z' : 170000
  },
  'origin' : (0,0,0),
  'num_x' : 10,
  'num_y' : 10,
  'num_z' : 100,
  'dim_x' : 1700, # 100 ft
  'dim_y' : 1700,
  'dim_z' : 170000
}

ROBOT = {
  # This is a switch as to whether the robot can read moments along a beam (True)
  # or not (False)
  'read_beam' : True,

  # The number of beams that each robot carries (ie, how many elements can
  # construct before travelling off the structure)
  'beam_capacity' : 1,

  # If true, then we record data when moving down the structure. This slows down
  # the simulation significantly.
  'collect_data'  : True,

  # This defines the mass of each robot in the units specified by program_units
  'load'  : 0.035, # kip
  
  # Radius of "locality" (how far can a robot obtain information about 
  # the structure from where it is located. In units specified by program_units
  'local_radius' : 36, # 3 ft

  # The size of a step that the robot can take. This is expressed in the specified
  # program units.
  'step_length' : 10 # inches
}

BEAM = {
  # Length of each beam (in the units specified by program_units)
  'length' : 120, # 10ft or 120in
}

BEAM.update({
  # This dictates the maximum randomness when setting a new beam
  'random' : BEAM['length'] / 25,

  # percent of randomness for the beam
  'random_percentage' : 0.33
})

# Name of the material property defined for the beams
MATERIAL = {
  'frame_property_name' : "Scaffold Tube",
  'material_property'  : "A500GrB42",
  'outside_diameter' : 3.0, # inches(1.9)
  'wall_thickness' : 0.188, # inches (0.144)
  'steel_density' : 490,

  'material_type' : "MATERIAL_STEEL",
  'material_subtype' : "MATERIAL_STEEL_SUBTYPE_ASTM_A500GrB_Fy42",

  'steel_yield' : 42 #ksi
}

MATERIAL.update({
  'density' : MATERIAL['steel_density'] / (12**3), # pci
  'cross_sect_area' : math.pi * ((MATERIAL['outside_diameter'] / 2)**2 - 
    (MATERIAL['outside_diameter'] / 2 - MATERIAL['wall_thickness'])**2), # in*in
  'moment_of_intertia' : math.pi * ((MATERIAL['outside_diameter']/2)**4 - 
    (MATERIAL['outside_diameter'] / 2 - MATERIAL['wall_thickness'])**4) / 4
})

MATERIAL.update({
  'beam_load' : MATERIAL['cross_sect_area'] * BEAM['length'] * 
    MATERIAL['density'] / 1000 # kip
})
#####################################################

PROGRAM = {
  # Units for starting the program
  'units' : "kip_in_F",

  # This defines how sensitive the program is to accepting errors within the beam 
  # structure
  'epsilon' : 0.0001,

  # Name of the load case for the robots
  'robot_load_case' : "DEAD",
  'wind_case' : "Wind",
  'wind_combo'  : "D+W",

  'structure_check' : MATERIAL['steel_yield'] * MATERIAL['moment_of_intertia'] /
    (MATERIAL['outside_diameter'] / 2),

  # The number of timesteps before an analysis model is saved.
  'analysis_timesteps' : 200

  # the output folder for saving files
  'root_folder' : 'C:\SAP 2000\\'
}


# This dictactes what is considered a significant length in the visualization
# We only record events that occur at a length higher than this
VISUALIZATION = { 
  # anything above this is considered 'significant'
  'step'        : 1, #in

  # scaling factor for visualization
  'scaling'     : 1, # in

  # radius of robot 'ball' during visualization
  'robot_size'  : 18,  # in

  # should the visualization record data for deflection?
  'deflection' : True,
} 

# This stores information for the simulation - for example, output folder

######################################################


# Wind pattern settings (NOT WORKING)
WIND = {
  '''
  THESE SETTINGS ARE NOW TAKEN CARE OF MANUALLY THROUGH A TEMPLATE LOCATED In
  C:\SAP 2000\ template.sbd

  exposureFrom indicated the source of the wind exposure
  1 = From extents of rigid diaphragms
  2 = From area objects
  3 = From frame objeccs (open structure)
  4 = From area objects and frame objects (open structure)
  '''
  'exposureFrom' : 3,

  '''
  dirAngle is the direction angle of the wind load. This
  only applies when exposureFrom is 1
  '''
  'dirAngle' : 0,

  # Windward coefficient (exposureFrom must be 1)
  'cpw' : 1,

  # Leeward coefficient (exposureFrom must be 1)
  'cpl' : 1,

  # Indicated the desired case from ASCE7-05 (exposureFrom must be 1)
  'asceCase ' : 1,
  'ascee1 ' : 1,
  'ascee2 ' : 1,

  '''
  This item is True if the top and bottom elevations of the wind load are user 
  specified. It is False if the elevations are determined by the program.

  topZ and bottomZ only appy when userZ is set to True
  '''
  'userZ' : False,
  'topZ ' : 1,
  'bottomZ' : 1,

  # The wind speed in mph
  'windSpeed' : 90,

  '''
  exposureType indicating the exposure Category
  1 = B
  2 = C
  3 = D
  '''
  'exposureType'  : 2,

  'importanceFactor'  : 1,

  # The topological factor
  'kzt' : 1,

  'gustFactor'  : .85,

  # The directionality factor
  'kd'  : .85,

  '''
  solidGrossRatio is the solid area divided by gross area ratio for open frame
  structure loading.

  This only applies when exposureFrom is 3 or 4
  '''
  'solidGrossRatio' : .2,

  'userExposure' : False
}

######################################################
