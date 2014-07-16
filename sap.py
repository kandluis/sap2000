import numpy
from SAP2000 import sap2000, analysis, elements

# This file will call on sap2000.py and run and algorithm
# that will give a grade to a structure allowing a learning
# algorithm to work properly

# Initialize lists

beam_count_list = [0]
height_list = [0]
ebeam_count_list = [0]
sbeam_count_list = [0]
# Initialize dicitionaries
LISTVARIABLES = {
	'beamcount': [0],

	'totalheight': [0],

	'ebeamcount': [0],

	'sbeamcount': [0],

	'scorecard': [0]
}

NORMALIZEDVARIABLES = {
	'normalbeams': 0,		# number of beams used in the structure

	'maximumheight': 0,		# maximum height of the structure

	'extraneousbeams': 0,	# number of extraneous beams (beams with only one connection)

	'stressedbeams': 0		# number of beams stressed beyond 50% (arbitrary)
}

# Initialize variable
count = 0	# to establish how often the program is called??

filename = 'C:\\SAP 2000\\2014-Jul\\Jul-16\\09_13_13\\tower-9800.sdb'
count = count + 1
# Start SAP and open a file
model = sap2000.Sap2000()
model.start()
model.open(filename)

# Set and run analysis of model

model.Analyze()

# In here we will magic some exports and use that data to run through the algorithm

# Establish number of beams used to create structure
total_elements = elements.count
robot_count = run_test.robot_number 
beam_count = total_elements - robot_count

# Find maximum height of tower.  I assume this will take place through 
# calling an excel file.

height = 500 #[ft] arbitrary number
#structure_heights.txt pulled from c://sap2000/2014/-Jul/July-"date" all files

# Determine the number of extraneous beams present in the simulation

# Determine the number of percent of beams stressed beyond 50% (arbitrary)

# Store all values to a dictionary before nomalizing
LISTVARIABLES['beamcount'].append(beam_count)
LISTVARIABLES['totalheight'].append(height)
LISTVARIABLES['ebeamcount'].append(ebeam_count)
LISTVARIABLES['sbeamcount'].append(sbeam_count)

# Store all values to a dictionary and normalize
NORMALIZEDVARIABLES = {
        'totalbeams': numpy.mean(beam_count_list) / numpy.std(beam_count_list),

        'maximumheight': numpy.mean(height_list) / numpy.std(height_list),

        'extraneousbeams': numpy.mean(ebeam_count_list) / numpy.std(ebeam_count_list),

        'stressedbeams': numpy.mean(sbeam_count_list) / numpy.std(sbeam_count_list),
}

# Calculate overall score for structure
score = CALCULATIONVARIABLES['totalbeams'] * 0.15 + CALCULATIONVARIABLES['maximumheight'] * 0.5 + CALCULATIONVARIABLES['extraneousbeams'] * 0.05 + CALCULATIONVARIABLES['stressedbeams'] * 0.3
LISTVARIABLES['scorecard'].append(score)
'''def returnranking(query):	#query is a list element containing the score and corresponding name of a file: [score, name]
# Sort the scorecard and return ranking'''
LISTVARIABLES['scorecard'].sort()
print(LISTVARIABLES['scorecard'].index(query))

