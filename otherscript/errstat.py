import numpy as np
import cenmod

# Months and years to process. Will process start_month to end_month in each year in
# start_year to end_year. Different from and does NOT process start_mo,start_year --> end_mo,end_year.
# It is expected that the devcomp.py script has been run for the appropriate time period.
# This script will process the month range for each year. Fields must be processed one at time
# unless a field loop is put in. With only 3 fields, this isn't a big deal.

start_year = 1981     
end_year = 2010
start_month = 7
end_month = 7
field2process = "tavg"

# Dir's

output_err_dir = "..\\output\\err\\" # Location of numpy arrays from devcomp.py
output_stats_dir = "..\\output\\err\\stats\\"

# Loop over years
# Number of statistical elements

stat_elem = 0
for curr_year in range(start_year, end_year +1):
    print("Processing year: ", curr_year)
    #Loop over months

    for curr_month in range(start_month, end_month + 1):
        print("month: ", curr_month)
        # Retrieve deviation array

        dev_fname = output_err_dir + "%4d%02d-" % (curr_year,  curr_month) + field2process + "-dev.npy"
        in_array = np.load(dev_fname)
        iashape = np.shape(in_array)
        numtimes = iashape[0]
        print("%02d days\n" % (numtimes))
        
        #Do whatever needs to be done in terms of computation with this array

        #If first time into outerloop declare and initialize arrays
        if stat_elem == 0:
            mean_dev = np.zeros((iashape[1], iashape[2]))
            mean_sqdev = np.zeros((iashape[1], iashape[2]))

        for ntime in range(numtimes):
            mean_dev = mean_dev + in_array[ntime, :, :]
            mean_sqdev = mean_sqdev + in_array[ntime, :, :] * in_array[ntime, :, :]

        stat_elem += iashape[0]  # Increase stat_elem by number of times in array

# Done with summing over years and months, normalize by stat_elem

print(np.shape(in_array[ntime-1, :, :]))
mean_dev = mean_dev / stat_elem
mean_sqdev = mean_sqdev / stat_elem
rms_dev = np.sqrt(mean_sqdev)
        
# Output numpy arrays

mdfile_fname = output_stats_dir + field2process + ".meandev.%02d-%02d.%4d-%4d.npy"   \
               % (start_month, end_month, start_year, end_year)
msfile_fname = output_stats_dir + field2process + ".meansqdev.%02d-%02d.%4d-%4d.npy"  \
               % (start_month, end_month, start_year, end_year)
rmsfile_fname = output_stats_dir + field2process + ".rtmeansqdev.%02d-%02d.%4d-%4d.npy" \
                % (start_month, end_month, start_year, end_year)

print("Stat arrays done. Outputting arrays.")

np.save(mdfile_fname, mean_dev)
np.save(msfile_fname, mean_sqdev)
np.save(rmsfile_fname, rms_dev)
