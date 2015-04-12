import numpy, os, re

# pyWin file
import win32com.client as win32

from SAP2000.constants import UNITS

# Import OAPI
sap_com_object = win32.Dispatch("SAP2000v15.SapObject")

# This function will take a directory and return a score for the tallest tower found
# in the given folder
def scorer(base_directory):
    # Test directories
    ##'C:\\SAP 2000\\2014-Jul\\Jul-17\\23_15_10\\'
    ##'C:\\SAP 2000\\2014-Jul\\Jul-14\\18_16_29\\'
    ##'C:\\SAP 2000\\2014-Jun\\Jun-17\\12_11_39\\'
    
    # Initialize variables
    count = 0
    towername = parseFolder(base_directory)
    filename = base_directory + towername
    ##print(towername)

    # Ideals for each variable present in the score (subject to change)
    height_ideal = 3000       # [ft]
    foot_per_beams_ideal = 1.25
    density_ideal = 2
    buckling_factor_ideal = 2
    sbeam_ideal = 1

    # Weight each factor has on the score (subject to change)
    height_weight = 0.3
    foot_per_beams_weight = 0.05
    density_weight = 0.05
    buckling_weight = 0.25
    sbeam_weight = 0.35

    # Open a file in SAP
    model = sap_com_object.SapModel
    ret = model.File.OpenFile(filename)
    assert ret == 0
    
    # Define Design Combinations
    DesignSteel = True
    DesignConcrete = False
    DesignAluminum = False
    DesignColdFormed = False

    ret = model.RespCombo.AddDesignDefaultCombos(DesignSteel, DesignConcrete, \
                                                 DesignAluminum, DesignColdFormed)
    assert ret == 0

    # Add a strength combination
    ret = model.DesignSteel.SetComboStrength('D+W', True)
    assert ret == 0

    # Variables for buckling case
    LoadType = ('Load', 'Load')
    LoadName = ('DEAD' , 'WIND')
    MySF = (1.0, 0)

    # Set a buckling load case
    model.LoadCases.Buckling.SetCase('Buckling')
    model.LoadCases.Buckling.SetInitialCase('Buckling', 'DEAD')
    model.LoadCases.Buckling.SetLoads('Buckling', 2, LoadType, LoadName, MySF)
    model.Results.Setup.SetOptionBucklingMode(False, False, True)

    # Lock model
    ret = model.SetModelIsLocked(True)
    assert ret == 0

    # Set cases to run
    model.Results.Setup.SetCaseSelectedForOutput('Buckling', True)
    model.Results.Setup.SetCaseSelectedForOutput('DEAD', True)
    model.Results.Setup.SetCaseSelectedForOutput('WIND', True)

    # Set and run analysis of model
    model.Analyze.CreateAnalysisModel()

    # Run selected cases
    model.Analyze.RunAnalysis()

    # Find parameters required to calculate the score of the structure

    # Find maximum height of tower.
    heightfilename = base_directory + 'structure_height.txt'

    heightdata = open(heightfilename, 'r')
    linevalue = heightdata.readlines()[-1]
    height = linevalue[0:(len(linevalue) - 2)]  # this value is inches we must convert to feet
    height = float(height)/12
    heightdata.close() #########
    
    # Find the number of beams per foot of tower
    beam_count = model.LineElm.Count()
    foot_per_beams = height/beam_count

    # Find "density" of the structure
    joints = model.PointElm.Count()
    density = joints/(beam_count)

    # Determine buckling factor
    [ret, num_modes,load_case,step_type,step_num,factor]=model.Results.BucklingFactor(6, ('Buckling','Buckling'), ('Mode','Mode'),(1,2,3,4,5,6), ())
    assert ret == 0

    # Solve for percentage of beams stressed between 50% and 80% of total capacity
    # Return list of frame names
    MyName = ()
    frameobjs = model.FrameObj.Count()
    [ret, FrameCount, FrameNames] = model.FrameObj.GetNameList(frameobjs, MyName)

    # Set other variables
    Ratio = []
    RatioType = []
    Location = []
    ComboName = []
    ErrorSum = []
    WarningSum = []
    ItemType = 1
    for i in range(1, model.FrameObj.Count()+1):
        if len(RatioType) == 0:
            RatioType = [1]
        else:
            RatioType.append(1)

    # Select correct group for analysis
    model.DesignSteel.SetGroup('ALL', True)
    model.DesignSteel.SetComboStrength('D+W', True)
    model.DesignSteel.StartDesign()

    # Get design results summary
    [ret, count, frame_names, ratio, ratiotype, location, combo, errmsg, warnmsg] = \
            model.DesignSteel.GetSummaryResults('ALL', FrameCount, FrameNames, \
                                                Ratio, RatioType, Location, \
                                                ComboName, ErrorSum, WarningSum, ItemType)

    # Find percent of beams experiencing the correct range of stress
    for index in range(1,model.FrameObj.Count()):
        if ratio[index-1]>0.3 and ratio[index-1]<0.5:
            count = count + 1
        sbeam = count/FrameCount

    # Normalize variables
    normalized_height = height/height_ideal
    normalized_foot_per_beams = foot_per_beams/foot_per_beams_ideal
    normalized_density = density/density_ideal
    normalized_buckling = factor[0]/buckling_factor_ideal   # Onlyconcerned with first mode of failure
    normalized_sbeam = sbeam/sbeam_ideal

    # Return score of structure
    score = normalized_height*height_weight + normalized_foot_per_beams*foot_per_beams_weight + \
            normalized_density*density_weight + normalized_buckling*buckling_weight + \
            normalized_sbeam*sbeam_weight
    return score

def parseFolder(url):
# This function finds the file with the completed/most complete tower
    # Define initial variables
    potential_tower_files = []
    halfname = []
    towernumber = []
    
    # Check directory was entered correctly
    try:
        for root, direc, files in os.walk(url):
            pass
##            root = root
##            direc = direc
##            files = files
    except TypeError:
        print('directory needs to be a string or no such directory exists')
        return 0

    # Find all .sdb files
    for index in range(0,len(files)):
        if re.search('.sdb', files[index]):
            potential_tower_files.append(files[index])
            
    for index in range(0,len(potential_tower_files)):
        halfname.append(potential_tower_files[index].split('tower-'))
        del halfname[index][0]
        if halfname[index] == []:
            halfname[index] = '0'
        towernumber.append(halfname[index][0].split('.sdb')[0])

        # Temporarily convert to an integer
        towernumber[index] = int(towernumber[index])
                    
    # Return max
    finaltowernumber = max(towernumber)

    # Check if only tower.sdb exists
    if finaltowernumber == 0:
        towerpath = 'tower.sdb'
    else:   # Return the path for the tower (after return value to a string)
        finaltowernumber = str(finaltowernumber)
        towerpath = 'tower-' + finaltowernumber + '.sdb'

    return towerpath
