# ---------------------------------------------------------------------------
# 2_CreateGISPointsFromTXTfile.py
# Created in January 2021
# Revised through -
#   by Z. Zaloudek
# TOOK 2 minutes TO RUN ON 1/13/2021
# ---------------------------------------------------------------------------

# Import things
print 'Starting up at...'
import datetime, arcpy
print datetime.datetime.today()

# Geoprocessing environment settings
##NAD83_GCS = arcpy.SpatialReference(4269)
WGS84_GCS = arcpy.SpatialReference(4326)
arcpy.env.overwriteOutput = True

    
# Variables
Folder = r'\\SWSATLAS\CentersGIS\CAS\MRCC\AWR_CensusTracts'
inputfolder = Folder + '\\orig_data\\fromTravis'
pntfile = inputfolder + '\\latlon_ji.txt'
colbrks = [10,24,32,40] # location of column breaks in textfile line
cellsize = 0.04166666666666666666666666666667
GDBnm = 'nClimGridPoints'
GDB = Folder+'\\'+GDBnm+'.gdb'
FCnm = 'nClimGridPoints'
FC = GDB + '\\' + FCnm
fields = [
        ['Lat','DOUBLE',None],
        ['Lon','DOUBLE',None],
        ['UID_LL','TEXT',24],
        ['I','SHORT',None],
        ['J','SHORT',None],
        ['UID_IJ','TEXT',24],
    ]
fieldnms = []


# Create GDB if needed
if not arcpy.Exists(GDB):
    arcpy.CreateFileGDB_management(Folder, GDBnm)
    print 'Created GDB'

# Create Feature Class within GDB
print 'Creating blank feature class...'
arcpy.CreateFeatureclass_management(GDB, FCnm, 'POINT', '', 'DISABLED', 'DISABLED', WGS84_GCS)
print 'Adding fields...'
for fld in fields:
    arcpy.AddField_management(FC, fld[0], fld[1], '', '', fld[2])
    fieldnms.append(fld[0])
    print ' ',fld[0]
print 'Made new blank feature class'

# Set up insert cursor
fieldnms.append('SHAPE@XY')
icursor = arcpy.da.InsertCursor(FC, fieldnms)

# Go through pntfile1, add points to Feature Class
print 'Adding points...'
f = open(pntfile, 'r')
f.readline() # skip header
for line in f:
    # Get lat/lon and I,J from file
    lat = float(((str(line))[:colbrks[0]]).strip())
    lon = float(((str(line))[colbrks[0]:colbrks[1]]).strip())
    j = ((str(line))[colbrks[1]:colbrks[2]]).strip()
    i = ((str(line))[colbrks[2]:colbrks[3]]).strip()
    # Calculate UID based on lat/lon
    uidLL = str(lat)+'_'+str(lon)
    uidLL = uidLL.replace('.','p')
    # Calculate UID based on I,J
    uidIJ = str(i)+'_'+str(j)
    # Add to point feature class
    point = (float(lon),float(lat))
    icursor.insertRow([lat,lon,uidLL,i,j,uidIJ,point])
del icursor
f.close()
print 'Added points'


print 'Cone done at', datetime.datetime.today()
