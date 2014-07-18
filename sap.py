import numpy

# pyWin file
import win32com.client as win32

##from SAP2000 import sap2000, analysis, elements
##
from SAP2000.constants import UNITS
##from SAP2000.elements import SapGroups, SapAreaObjects, SapAreaElements, SapLineElements, SapFrameObjects, SapPointObjects, SapPointElements
##from SAP2000.analysis import SapAnalysis

# Import OAPI
sap_com_object = win32.Dispatch("SAP2000v15.sapobject")

# Initialize dicitionaries
LISTVARIABLES = {
	'beamcount': [0],

	'totalheight': [0],

	'density': [0],

	'sbeamcount': [0],

	'scorecard': [0]
}

NORMALIZEDVARIABLES = {
	'normalbeams': 0,		# number of beams used in the structure

	'maximumheight': 0,		# maximum height of the structure
 
	'density': 0,	# number of extraneous beams (beams with only one connection)

	'stressedbeams': 0		# number of beams stressed beyond 50% (arbitrary)
}

#initialize variables
count = 0


# Start SAP and open a file
filename = 'C:\\SAP 2000\\2014-Jul\\Jul-16\\09_13_13\\tower-9800.sdb'
units = UNITS["kip_in_F"]
visible = True
sap_com_object.ApplicationStart(units, visible, filename)
model = sap_com_object.SapModel

# Set a buckling load case
model.LoadCases.Buckling.SetCase('Buckling1')
model.LoadCases.Buckling.SetInitialCase('Buckling1', 'DEAD')
model.LoadCases.Buckling.SetLoads('Buckling1' , 1 , 'Load' , 'DEAD',1)
model.Results.Setup.SetOptionBucklingMode(False, False, True)

# Set and run analysis of model
model.Analyze.RunAnalysis

# Establish number of beams used to create structure
beam_count = model.LineElm.Count()

# Find maximum height of tower.  I assume this will take place through 
# calling an excel file.
heightfilename = 'C:\\SAP 2000\\2014-Jul\\Jul-16\\09_13_13\\structure_height.txt'
heightdata = open(heightfilename, 'r')
linevalue = heightdata.readlines()[-1]
height = linevalue[0:(len(linevalue) - 2)]

# Find "density" of the structure
joints = model.PointElm.Count()
density = joints/(2*beam_count)

# Determine buckling factor
##buckling = model.Results.BucklingFactor()
##print(buckling)



# Determine the number of percent of beams stressed beyond 50% (arbitrary)

model.RespCombo.AddDesignDefaultCombos(True, False, False, False)
model.DesignSteel.SetComboStrength('D+W', True)
model.DesignSteel.StartDesign()

###construct array of FrameNames
##for i in range(1:beam_count):
##    FrameNames[i - 1] = i
##
##ret = model.DesignSteel.GetSummaryResults('D+W', 1 , FrameNames , 1 , 1

# Solve for percentage of beams stressed between 50% and 80% of total capacity
for line in ret:
    if ret(line)>0.5 and ret(line)<0.8:
        count = count + 1
        sbeam = count/beam_count

### Exit model
##sap_com_object.ApplicationExit(True)

# Store all values to a dictionary before nomalizing (if first run through, do not append)
if len(LISTVARIABLES['beamcount']) == 1:
       LISTVARIABLES['beamcount'] = [beam_count]
       LISTVARIABLES['totalheight'] = [height]
       LISTVARIABLES['density'] = [density]
       LISTVARIABLES['sbeamcount'] = [sbeam_count]
else:
        LISTVARIABLES['beamcount'].append(beam_count)
        LISTVARIABLES['totalheight'].append(height)
        LISTVARIABLES['density'].append(density)
        LISTVARIABLES['sbeamcount'].append(sbeam_count)

# Normalize all values if not first run.
if len(LISTVARIABLES['beamcount']) == 1:
        NORMALIZEDVARIABLES = {
            'totalbeams': beam_count,
               
            'maximumheight': height,
                
            'density': density,
                
            'stressedbeams':sbeam,
            }

else:
    for line in LISTVARIABLES['beamcount']:
        NORMALIZEDVARIABLES = {
            'totalbeams': (LISTVARIABLES['beamcount'][line] - numpy.mean(LISTVARIABLES['beamcount'])) / numpy.std(LISTVARIABLES['beamcount']),

            'maximumheight': (LISTVARIABLES['totalheight'][line] - numpy.mean(LISTVARIABLES['totalheight'])) / numpy.std(LISTVARIABLES['totalheight']),

            'density': (LISTVARIABLES['density'][line] - numpy.mean(LISTVARIABLES['density'])) / numpy.std(LISTVARIABLES['density']),

            'stressedbeams': (LISTVARIABLES['sbeamcount'][line] - numpy.mean(LISTVARIABLES['sbeamcount'])) / numpy.std(LISTVARIABLES['sbeamcount']),
            }
    

# Calculate overall score for structure
score = NORMALIZEDVARIABLES['totalbeams'] * 0.15 + NORMALIZEDVARIABLES['maximumheight'] * 0.5 + NORMALIZEDVARIABLES['density'] * 0.05 + NORMALIZEDVARIABLES['stressedbeams'] * 0.3
LISTVARIABLES['scorecard'].append(score)
'''def returnranking(query):	#query is a list element containing the score and corresponding name of a file: [score, name]
# Sort the scorecard and return ranking'''
LISTVARIABLES['scorecard'].sort()
##print(LISTVARIABLES['scorecard'].index(query))



