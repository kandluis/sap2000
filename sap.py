import numpy

# pyWin file
import win32com.client as win32

##from SAP2000 import sap2000, analysis, elements
##
from SAP2000.constants import UNITS
##from SAP2000.elements import SapGroups, SapAreaObjects, SapAreaElements, SapLineElements, SapFrameObjects, SapPointObjects, SapPointElements
##from SAP2000.analysis import SapAnalysis

# Import OAPI
sap_com_object = win32.Dispatch("SAP2000v15.SapObject")

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

# Initialize variables
count = 0

# Variables for buckling case
LoadType = ('Load', 'Accel')
LoadName = ('DEAD' , 'UZ')
MySF = (1.0, 0)

# Start SAP and open a file
filename = 'C:\\SAP 2000\\2014-Jun\\Jun-17\\12_11_39\\tower-2800 - Copy.sdb'
units = UNITS["kip_in_F"]
visible = True
sap_com_object.ApplicationStart(units, visible, filename)
model = sap_com_object.SapModel

# Define load patterns
Name = 'DEAD'
MyType = 1
SelfWTMultiplier = 1
AddLoadCase = True

ret = model.LoadPatterns.Add(Name, MyType, SelfWTMultiplier, AddLoadCase)
ret = model.LoadCases.StaticNonlinear.SetCase(Name)
assert ret == 0

Name = 'WIND'
MyType = 6
SelfWTMultiplier = 0
ret = model.LoadPatterns.Add(Name, MyType, SelfWTMultiplier, AddLoadCase)
ret = model.LoadCases.StaticNonlinear.SetCase(Name)
assert ret == 0

# Add Load Combination
Name = 'D+W'
ComboType = 0

ret = model.RespCombo.Add(Name, ComboType)

# Define Design Combinations
DesignSteel = True
DesignConcrete = False
DesignAluminum = False
DesignColdFormed = False

ret = model.RespCombo.AddDesignDefaultCombos(DesignSteel, DesignConcrete, DesignAluminum, DesignColdFormed)
assert ret == 0

# Add a strength combination
Selected = True

ret = model.DesignSteel.SetComboStrength(Name, Selected)
assert ret == 0

# Set a buckling load case
model.LoadCases.Buckling.SetCase('Buckling')
model.LoadCases.Buckling.SetInitialCase('Buckling', 'DEAD')
model.LoadCases.Buckling.SetLoads('Buckling', 2, LoadType, LoadName, MySF)
model.Results.Setup.SetOptionBucklingMode(False, False, True)

# Lock model
model.SetModelIsLocked(True)

# Set and run analysis of model
model.Analyze.CreateAnalysisModel()

# Set cases to run
model.Results.Setup.SetCaseSelectedForOutput('Buckling', True)
##model.Results.Setup.SetCaseSelectedForOutput('DEAD', True)
##model.Results.Setup.SetCaseSelectedForOutput('Wind', True)
model.Analyze.RunAnalysis()

# Establish number of beams used to create structure
beam_count = model.FrameObj.Count()

# Find maximum height of tower.  I assume this will take place through 
# calling an excel file.
heightfilename = 'C:\\SAP 2000\\2014-Jul\\Jul-16\\09_13_13\\structure_height.txt'
heightdata = open(heightfilename, 'r')
linevalue = heightdata.readlines()[-1]
height = linevalue[0:(len(linevalue) - 2)]

# Find "density" of the structure
joints = model.PointElm.Count()
density = joints/(2*beam_count)

### Determine buckling factor
##buckling =
[a,b,c,d,e,f]=model.Results.BucklingFactor(6,('Buckling','Buckling'), ('Mode','Mode'),(1,2,3,4,5,6), ())
##print(buckling)



# Determine the number of percent of beams stressed beyond 50% (arbitrary)

model.RespCombo.AddDesignDefaultCombos(True, False, False, False)
model.DesignSteel.SetComboStrength('D+W', True)
model.DesignSteel.StartDesign()

#construct arrays
FrameNames = []
Ratio = []
RatioType = []
Location = []
ComboName = []
ErrorSum = []
WarningSum = []
ItemType = 0
for i in range(1, model.FrameObj.Count()):
    if len(FrameNames) == 0:
        FrameNames = [i]
        Ratio = [0.5]
        RatioType = [1]
        Location = [0]
        ComboName = ['D+W']
        ErrorSum = ['No Messages']
        WarningSum = ['No Messages']
    else:
        FrameNames.append(i)
        Ratio.append(0.5)
        RatioType.append(1)
        Location.append(0)
        ComboName.append('D+W')
        ErrorSum.append('No Messages')
        WarningSum.append('No Messages')

# Solve for percentage of beams stressed between 50% and 80% of total capacity
for index in range(1,model.FrameObj.Count()):
    stress_ratio = model.DesignSteel.GetSummaryResults(str(index), model.FrameObj.Count() , FrameNames , Ratio,RatioType , Location, ComboName, ErrorSum, WarningSum,ItemType)
    if stress_ratio[3][0]>0.5 and stress_ratio[3][0]<0.8:
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



