# This script will generate the c2g mapping. In other words, in each gridpoint dictionary entry,
# contributing census tracts are stored. It's assumed that the output_dir already exists.
# The resulting pickle file is used in devcomp.py as it is needed for the reverse mapping from
# census tracts to gridpoints.


import pickle



output_dir = "..\\output\\"
map_dir = "..\\map_data\\"
combo_fname = "Combinations_Union.csv" 
#combo_fname = "testcomboshort.txt"
map_fname = output_dir + "C2G_Map.pickle"
unmatched_fname = output_dir + "umatch_c2g.txt"

Combofile = map_dir + combo_fname

cdict = {}

cfile = open(Combofile, "r"); 
umatch = open(unmatched_fname, "w")
umatchset = set()
line = cfile.readline()

cfields = []
for line in cfile:
    
    
    cleanline = line.strip()
    cfields = cleanline.split(",") 


    
    if cfields[5]: # Make sure there is a gridpoint for this input line
        if cfields[0]: # Make sure there is a census tract for this input line
            currkey = (int(cfields[5]), int(cfields[6])) # Set key to i, j tuple
            if currkey in cdict:          #Append this CT to the list
                cdict[currkey].append([int(cfields[0]), float(cfields[2])])

            else:        # GP isn't in the dictionary, add it
                cdict[currkey] = [None, [], [], [], [int(cfields[0]), float(cfields[2])]]
        else:
            umatchset.add((int(cfields[5]), int(cfields[6]))) # GP line has no census tract

# At this point cdict contains the gridpoints (as key) that have at least one
# census tract contributing to the gridpoint. Grid points without contributing census
# tracts are not in the dictionary


print("*****i,j's with missing GEOID lines*****\n", file=umatch)
print(umatchset, file=umatch)
copy_umatchset = umatchset.copy()

for ijid in copy_umatchset:
    if ijid in cdict:        # GP may have been added when a line with census tract was found
        umatchset.remove(ijid)
    
print("******i,j's actually missing from cdict*****\n", file=umatch)
print(umatchset, file=umatch)
cfile.close()
umatch.close()


#Output the mapping file to a pickle file to be used in later computations

mapfile = open(map_fname, "wb")
pickle.dump(cdict, mapfile, 2);
mapfile.close()






