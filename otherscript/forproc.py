from netCDF4 import Dataset
import pickle, math
import numpy as np

# The input NCEI nClimgrid-d netcdf files need to be in the map_dir under subdirectories by year
# The output will also be organized this way in the output dir, so setup directories named by the
# 4 digit year before running
# As elsewhere this is going to run the range of months start_month -> end_month for each year in the
# year range. This allows for slicing of the years. If one doesn't want this, then simply
# run it from Jan - Dec for the middle years and then the specific month range for the first and last
# years respectively (set start_year and end_year to the year)


gen_txt_output = False
start_month = 1
end_month = 12
start_year = 1951
end_year = 2020

fields2process = ["tmax", "tmin", "tavg"]
#fields2process = ["tmax"]

# String constants for directories and whatnot


map_dir = "..\\map_data\\"
output_dir = "..\\output\\"
g2c_pickle_file = "G2C_Map.pickle"
logfilenm = output_dir + "forproc.log.txt"
g2c_tot_fname = output_dir + g2c_pickle_file


logfile = open(logfilenm, "w") #Log file for debugging if needed. Put write or print commands in code
                               #as needed

# Open up pickled dictionary that contains grid to tract mapping information and fields

indictfile = open(g2c_tot_fname, "rb")
mdict = pickle.load(indictfile)
indictfile.close()


# Start looping through years

for curr_year in range(start_year, end_year + 1):
                       
    indata_dir = "..\\ncei_data\\" + ("%4d\\" % curr_year) 
    if curr_year < 1970:
        pre_1970 = True  # Pre-1970, all three temperature fields are in one netcdf file. 1970 onward,
                         # they are in three separate files.
    else:
        pre_1970 = False

    # Begin month processing loop
    
    for curr_month in range(start_month, end_month + 1):

        # Begin field processing loop (tmax, tmin, tave)
        
        for field in fields2process:
            field_index = fields2process.index(field) + 1
            
            # Construct input and output filenames

            #input netcdf fname
            if pre_1970:
                in_nc_file = indata_dir + "ncdd" + "-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                         + "-grd-scaled.nc"
            else:        
                in_nc_file = indata_dir + field + "-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                             + "-grd-scaled.nc"

            #output text fname
            out_fname_txt = output_dir + ("%4d\\" % (curr_year)) + field + "-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                         + "-census.txt"

            #output pickle fname

            out_fname_pickle = output_dir + ("%4d\\" % (curr_year)) + "tall-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                         + "-census_g2c.pickle"

            
            #umatched census tract listing fname

            umatch_ct_fname = output_dir + ("%4d\\" % (curr_year)) + field + "-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                         + "-umatch_ct.txt"

            #open output text file and unmatched tracts file


            outfile = open(out_fname_txt, "w")


            umatchfile = open(umatch_ct_fname, "w")

            # Open netcdf file print out some meta info from file

            print("*****NETCDF FILE INFO****")
            print("\n\nOpening file: ", in_nc_file)

            
            input_nc_var = Dataset(in_nc_file, "r")
            print(input_nc_var.data_model)
            print(input_nc_var.dimensions)

            # Get dimensions of data file to use in later code

            numtimes = len(input_nc_var.dimensions["time"])
            numlat =  len(input_nc_var.dimensions["lat"])
            numlon = len(input_nc_var.dimensions["lon"])
            testdict =  input_nc_var.dimensions


            print(testdict)
            for var in input_nc_var.variables:
                print(var)

            print(input_nc_var[field])

            print("# of times = ", numtimes)
            print("# of lat values = ", numlat)
            print("# of lon values = ", numlon)





            var_array = input_nc_var[field][:]  # Load variable into array
    #        print("VALUE!!! = %f\n" % (var_array[0][70][1010])) # Debug
        

            #Input Netcdf file has been read. Close it.
            
            input_nc_var.close() 
            print("Input file %s is closed.\n" % (in_nc_file))
            
            # Input NETCDF file read and closed 

            
            outfile.write("GEOID,            %s\n" % (field))   


            # Process each census tract: Compute total area of contributing grid cells
            # Computed area weighted average of temperature variable.
            # Ensure that tract has temperature data input from grid
            # If not, take note.

            # Empty list of current field values from previous month

            for currkey in mdict:
                mdict[currkey][field_index] = []
        
            # Start the time loop

            for day in range(0, numtimes):
# Debug                print("Field: %s, Day: %2d\n" % (field, day + 1))
                outfile.write("%4d    %02d    %02d\n" % (curr_year, curr_month, day + 1))    
                missing_tracts = set()
                templistcopy = []
                sortkey = list(mdict.keys())
                sortkey.sort()
                
                # Process each census tract
                for currkey in sortkey:
                    tract_val = 0.0
                    tot_area = 0.0
                    gridpoints = mdict[currkey]
                    for gp in gridpoints[4:]:
                        i = gp[0][0]
                        j = gp[0][1]
                        gptemp = var_array[day, j, i]
                        # Make sure temperature is valid. If so,
                        # update total area and start computing

                        if ( not (math.isnan(gptemp))):
                            tract_val += gp[1]*gptemp  # weighted temperature
                            tot_area += gp[1]

                    if tot_area == 0.0:         #No valid temperature went into this computation
        #                logfile.write("Census Tract %d has no defined value\n" % (currkey))
                        missing_tracts.add(currkey)
                        gridpoints[0] = float('nan')
                        (gridpoints[field_index]).append(float('nan'))

                        
                    else:                      #At least one valid gridpoint temperature contributed
                        gridpoints[0] = tot_area
                        gridpoints[field_index].append(tract_val/tot_area) #Normalize and record
                        if gen_txt_output:
                            outfile.write("%011d, %12.3f,\n" % (currkey, gridpoints[field_index][day]))
                                


                umatchfile.write("%d Tracts total are completely missing data for field %s on day %2d\n" % (len(missing_tracts), field, day + 1))


            #Make sorted list of tracts that had no valid data at some point during the above time loop (a full month)
                
            templistcopy = list(missing_tracts)
            templistcopy.sort()
            for elem in templistcopy:
                print("%14d" % (elem), file=umatchfile)




        # All days in month have been processed
        # The current field is complete
        # Close unmatched list file and output value file

            outfile.close()
            umatchfile.close()

##        Output the pickle file for the month (or not). These files are huge if one does all 3 fields for
##        the whole month.
##        It's best to just output the text file above for each individual field, month and year
##        since that is the final product anyhow.

##        outpfile = open(out_fname_pickle, "wb")
##        pickle.dump(mdict, outpfile, 2)
##        outpfile.close()


logfile.close()
