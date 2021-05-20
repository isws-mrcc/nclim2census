## cenmod.py
## Modules used in census tract remap AWR

import numpy as np

def ct2grid(cdict, cendict, a):
    # cdict is the dictionary containing the mapping information using contributing areas
    # cendict is the dictionary containing the census tract temperature estimates
    # a is the array in which  the reverse estimate will be stored (should be prefilled with nans)
    # Because this is going to be compared to the netcdf array which has shape (numlat, numlon) we
    # need to transpose (last statement before 'return' does this implicitly)
    
    for gpij in cdict:
        arri = gpij[0]
        arrj = gpij[1]
        totarea = 0.0
        restimate = 0.0
        for ct in cdict[gpij][4:]:
            if ct[0] in cendict:
                totarea += ct[1]
                restimate += cendict[ct[0]] * ct[1]

        # Remember, some census tracts that intersect grid cells don't have temperature estimates
        # We account for this above by checking that ct[0] is in cendict and act accordingly

        if totarea == 0.0:     # No CT contributed to this GP
            restimate = np.nan
        else:                  # At least one CT contributed to this GP
            restimate /= totarea

        a[arrj, arri] = restimate
        
    return


            
