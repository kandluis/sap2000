def parseFolder(url):
# This function finds the file with the completed/most complete tower
    # Define initial variables
    potential_tower_files = []
    halfname = []
    towernumber = []
    # Check directory was entered correctly
    try:
        for root, dir, files in os.walk(url):
            root = root
            dir = dir
            files = files
    except TypeError:
        print('directory needs to be a string or no such directory exists')
        return 0

    # Find all .sdb files
    for index in range(1,len(files)):
        if re.search('.sdb', files[index-1]):
            potential_tower_files.append(files[index-1])

    for index in range(1,len(potential_tower_files)):
        halfname.append(potential_tower_files[index-1].split('tower-'))
        towernumber.append(halfname[index-1][1].split('.sdb')[0])

        #convert to integer and return max
        finaltowernumber = max(towernumber)

    # Return the path for the tower
    towerpath = 'tower-' + finaltowernumber + '.sdb'

    return towerpath
