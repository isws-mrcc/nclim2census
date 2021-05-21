from netCDF4 import Dataset
import numpy as np
import pickle, math
import cenmod

## This source file will generate the deviation arrays (reverse mapping estimate - original gridded data).
## This needs the original netcdf nclimgrid-d gridded arrays as netcdf files, the census tract estimates
## generated from the estimation code and the c2g mapping file (pickle). The deviation arrays are output as numpy
## object files. See AWR Report for more details
##
## C. Travis Ashby
## 04/28/2021

# Set up directory and file names

map_dir = "..\\map_data\\"
output_dir = "..\\output\\"
output_err_dir = "..\\output\\err\\"
c2g_pickle_file = "C2G_Map.pickle"
logfilenm = output_dir + "errproc.log.txt"
c2g_tot_fname = output_dir + c2g_pickle_file

# Averaging times, etc.

# Note that end_year and end_month and start_year and start_month don't pair. In other words
# start_year = 2000, end_year = 2001, start_month = 1, end_month = 5 does NOT run the processing
# from Jan 2000 - May 2001. Rather it processes months 1-5 (Jan-May)in the years 2000 and 2001. This allows
# for extraction of specific months across years. This only processes on field at a time.

start_year = 1981
end_year = 1982
start_month = 7
end_month = 7
field2process = "tavg"



# Open census tract to gridpoint mapping file and load mapping dictionary cdict

indictfile = open(c2g_tot_fname, "rb")
cdict = pickle.load(indictfile)
indictfile.close()



# Keep track of number of days processed

days_processed = 0

# Set up dictionary for census tract input temperature data from txt file
cendict = {}

# Start year loop

for curr_year in range(start_year, end_year + 1):
    print("Processing year: ", curr_year)

    for curr_month in range(start_month, end_month + 1):
        print("Processing month: ", curr_month)
            
        indata_dir = "..\\ncei_data\\" + ("%4d\\" % curr_year) 


        if curr_year < 1970:
            pre_1970 = True  # Pre-1970, all three temperature fields are in one netcdf file. 1970 onward,
                             # they are in three separate files.
        else:
            pre_1970 = False

        if pre_1970:
            in_nc_file = indata_dir + "ncdd" + "-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                             + "-grd-scaled.nc"
        else:        
            in_nc_file = indata_dir + field2process + "-" + ("%4d" % (curr_year)) + ("%02d" % (curr_month)) \
                                 + "-grd-scaled.nc"

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

            print(input_nc_var[field2process])

            print("# of times = ", numtimes)
            print("# of lat values = ", numlat)
            print("# of lon values = ", numlon)

            # Instate and init. reverse estimate grid array

            testim = np.empty((numtimes, numlat, numlon))
            testim.fill(float('nan'))





            var_array = input_nc_var[field2process][:]  # Load variable into array
    #        print("VALUE!!! = %f\n" % (var_array[0][70][1010])) # Debug

     
            input_nc_var.close() 
            print("Input file %s is closed.\n" % (in_nc_file))
        

            #Input Netcdf file has been read. Close it.


            # Open input cen. tract data file and create data dictionary for the current day
            
            cdatafname = output_dir + ("%4d\\" % (curr_year)) + field2process + "-" + ("%4d%02d" % (curr_year, curr_month)) + \
                         "-census.txt"
    #        cdatafname = "tester.txt"                    
            cdatafile = open(cdatafname, "r")
            line = cdatafile.readline()        #Read in file header, discard
            line = cdatafile.readline()     #Read in first date line, discard

    # Loop thru input txt file retrieving each day
            monthday = 0
            for line in cdatafile:
                cleanline = line.strip()
                cfields = cleanline.split(",")

                if len(cfields) == 3:         #This is a data line otherwise it is a time/date line
                    tract_num = int(cfields[0])
                    cendict[tract_num] = float(cfields[1])
                    
                else:                        #New date line, process data from previous day
                    days_processed += 1
                    print("cendict days_processed: ", days_processed)
                    monthday += 1
                    print("Monthday = ", monthday)
                    cenmod.ct2grid(cdict, cendict, testim[monthday-1, :, :])

     # There is an implicit assumption in the code above: For every day the same census tracts
     # are listed in the input file. It turns out this is valid, but may need to be revisited when processing
     # the 1895+ data in case there is a change in the grid coverage and hence CT coverage.
     
    # Reached end of file, still need to process previous day so repeat code from above

            days_processed += 1
            print("cendict days_processed: ", days_processed)
            monthday += 1
            print("Monthday = ", monthday)
            cenmod.ct2grid(cdict, cendict, testim[monthday-1, :, :])

    # Compute deviation from original input

            deviat=np.empty((numtimes, numlat, numlon))
            deviat.fill(np.nan)

            # What is going on here is that outputting masked arrays is apparently
            # not supported, so the original grid is basically recast below as
            # a 'nan' filled array. Only became a problem for outputting .npy files
            # hence this workaround. It's due to the fact that the netcdf files
            # are considered masked arrays.
            
            var_array2 = np.ma.filled(var_array.astype(float), np.nan) 
            deviat = testim - var_array2

    #Technically we have what we need to compute basic error statistics. Output deviation array as numpy object
            
            outarray_fname = output_err_dir + "%4d%02d-" % (curr_year, curr_month) + field2process + "-dev.npy"
            np.save(outarray_fname, deviat)

    # Done with current input file (1 month). Close it
            cdatafile.close()


# For diagnostic purposes output text file        
##finout = open("finout.txt", "w")
##
##for i in range(numlon):
##    for j in range(numlat):
##        print(i, j, "%9.3f" % (deviat[4, j, i]), file=finout)

##finout.close()
##
## 
### for curr_key in cendict:
#    print("%14d,  %8.4f" % (curr_key, cendict[curr_key]), file=finout)

#finout.close()

            
# Done with generating deviation numpy array files        

