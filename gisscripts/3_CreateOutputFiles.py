# ---------------------------------------------------------------------------
# 3_CreateOutputFiles.py
# Created in November 2020
# Revised through March 2021
#   by Z. Zaloudek
# TOOK 2 minutes TO RUN ON 11/23/2020 for Champaign County IL
# TOOK 25 minutes TO RUN ON 1/13/2021 for Full CONUS Extent
# TOOK 25 minutes TO RUN ON 3/18/2021 for Full CONUS Extent
# ---------------------------------------------------------------------------

# Import things
print 'Starting up at...'
import datetime, arcpy, csv
print datetime.datetime.today()

# Check out any necessary ESRI licenses
from arcpy.sa import *
arcpy.CheckOutExtension('Spatial')

# Geoprocessing environment settings
NAD83_GCS = arcpy.SpatialReference(4269)
WGS84_GCS = arcpy.SpatialReference(4326)
AEAC_USGS = arcpy.SpatialReference(102039)
arcpy.env.overwriteOutput = True

    
# Variables
Folder = r'\\SWSATLAS\CentersGIS\CAS\MRCC\AWR_CensusTracts'
inTracts = Folder + '\\USCensusTracts2020.gdb\\CensusTracts2020'
##inTracts = Folder + '\\USCensusTracts2010.gdb\\CensusTracts2010_ForTest'
tractsuidfldnm = 'GEOID'
tractsalndfldnm = 'ALAND'
tractsawtrfldnm = 'AWATER'
tractsattlfldnm = 'AREATOTAL'
inGridpts = Folder + '\\nClimGridPoints.gdb\\nClimGridPoints'
##inGridpts = Folder + '\\nClimGridPoints.gdb\\nClimGridPoints_ForTest'
pointsuidLLfldnm = 'UID_LL'
pointslatfldnm = 'Lat'
pointslonfldnm = 'Lon'
pointsuidIJfldnm = 'UID_IJ'
pointsifldnm = 'I'
pointsjfldnm = 'J'
cellsize = 0.04166666666666666666666666666667 # decimal degrees
GDBnm = 'GISprocessing'
GDB = Folder+'\\'+GDBnm+'.gdb'
collength = 18
outfileTracts = Folder + '\\Tracts.csv'
outfileGridCells = Folder + '\\GridCells.csv'
outfileCombinations = Folder + '\\Combinations.csv'


# Function for finding geographic transformation method
def geoTransMethod(inSR,outSR):
    indatumname = inSR.GCS.datumName
    outdatumname = outSR.GCS.datumName
    transform_method = ''
    if ('WGS_1984' in indatumname and ('NAD_1983' in outdatumname or 'North_American_1983' in outdatumname)) or \
       (('NAD_1983' in indatumname or 'North_American_1983' in indatumname) and 'WGS_1984' in outdatumname):
        if ('2011' in indatumname and '2011' not in outdatumname) or \
           ('2011' not in indatumname and '2011' in outdatumname):
            transform_method = 'WGS_1984_(ITRF00)_To_NAD_1983_2011'
        else:
            transform_method = 'NAD_1983_To_WGS_1984_5' # Use for CONUS
##            transform_method = 'NAD_1983_To_WGS_1984_1' # Use for North America (not CONUS)
    return transform_method


# Create GDB if needed
if not arcpy.Exists(GDB):
    arcpy.CreateFileGDB_management(Folder, GDBnm)
    print 'Created GDB'

# Project input Census Tracts into working projection if needed
tracts = GDB + '\\_0_CensusTractsReprojected'
if arcpy.Describe(inTracts).spatialReference.name != AEAC_USGS.name:
    # Find geographic transformation method between NAD83 and Structures FC spatial reference
    geotransmthd = geoTransMethod(arcpy.Describe(inTracts).spatialReference,AEAC_USGS)
    # Project input data into working projection
    print 'Projecting Census Tracts...'
    arcpy.Project_management(inTracts, tracts, AEAC_USGS, geotransmthd, None, 'PRESERVE_SHAPE')
else:
    # Just copy the input data to the GDB
    print 'Copying Census Tracts...'
    arcpy.Copy_management(inTracts, tracts)

# Get all values from lat & lon fields in the input grid points
lats = []
lons = []
fields = [pointslatfldnm,pointslonfldnm]
with arcpy.da.SearchCursor(inGridpts, fields) as cursor:
    for row in cursor:
        lats.append(row[0])
        lons.append(row[1])
del cursor

# Set extent based on lat/lons
minx = min(lons)-(cellsize/2)
maxx = max(lons)+(cellsize/2)
miny = min(lats)-(cellsize/2)
maxy = max(lats)+(cellsize/2)
arcpy.env.Extent = (minx,miny,maxx,maxy)

# Create a rater grid from the grid points
gridras = GDB + '\\_1_RasterFromGridpoints'
print 'Creating raster grid from grid points...'
arcpy.PointToRaster_conversion(inGridpts, pointsuidIJfldnm, gridras, None, None, cellsize)

# Convert the grid raster to polygons
gridpolys = GDB + '\\_2_GridPolygons'
print 'Creating polygons from raster grid...'
arcpy.RasterToPolygon_conversion(gridras, gridpolys, 'NO_SIMPLIFY', pointsuidIJfldnm, 'SINGLE_OUTER_PART', None)

# Project input Grid Polygons into working projection if needed
gridpys = GDB + '\\_3_GridPolygonsReprojected'
if arcpy.Describe(inGridpts).spatialReference.name != AEAC_USGS.name:
    # Find geographic transformation method between NAD83 and Structures FC spatial reference
    geotransmthd = geoTransMethod(arcpy.Describe(inGridpts).spatialReference,AEAC_USGS)
    # Project input data into working projection
    print 'Projecting Grid Polygons...'
    arcpy.Project_management(gridpolys, gridpys, AEAC_USGS, geotransmthd, None, 'PRESERVE_SHAPE')
else:
    # Just copy the grid polygons to the GDB
    print 'Copying Grid Polygons...'
    arcpy.Copy_management(gridpolys, gridpys)



# Run one of the following three tools to determine overlapping between tracts and grid cell polygons

# Run Union tool (keeps all pieces, including where tracts & grid cells don't overlap)
outfileCombinations = outfileCombinations[:-4] + '_Union' + outfileCombinations[-4:]
overlap = GDB + '\\_4_Overlap_Union'
print 'Running Union...'
arcpy.Union_analysis([tracts,gridpys], overlap, 'ALL', None, 'GAPS')

### Run Identity tool (only keeps pieces where a tract exists)
##outfileCombinations = outfileCombinations[:-4] + '_Identity' + outfileCombinations[-4:]
##overlap = GDB + '\\_4_Overlap_Identity'
##print 'Running Identity...'
##arcpy.Identity_analysis(tracts, gridpys, overlap, 'ALL', None, 'NO_RELATIONSHIPS')

### Run Intersect tool (only keeps pieces where tracts & grid cells overlap)
##outfileCombinations = outfileCombinations[:-4] + '_Intersect' + outfileCombinations[-4:]
##overlap = GDB + '\\_4_Overlap_Intersect'
##print 'Running Intersect...'
##arcpy.Intersect_analysis([tracts,gridpys], overlap, 'ALL', None, 'INPUT')



# Function to pad a value with spaces on left side
def padvalue(val):
    v = str(val)
    while len(v) < collength:
        v = ' '+v
    return v

    
# Create a file with total area for each tract
print 'Making Tracts CSV...'
with open(outfileTracts, 'wb') as csvfile:
    fieldnms = [tractsuidfldnm,tractsattlfldnm,'Area_SqM']
    for fldnm in fieldnms:
        v = padvalue(fldnm)
        fieldnms[fieldnms.index(fldnm)] = v
    writer = csv.DictWriter(csvfile, fieldnames=fieldnms)
    writer.writeheader()
    # Use Search Cursor to go through each tract
    fields = [tractsuidfldnm,tractsattlfldnm,'SHAPE@AREA']
    with arcpy.da.SearchCursor(tracts, fields) as cursor:
        for row in cursor:
            linedict = {}
            for fldnm in fieldnms:
                val = row[fieldnms.index(fldnm)]
                if fields[fieldnms.index(fldnm)] == 'SHAPE@AREA' or \
                   fields[fieldnms.index(fldnm)] == tractsattlfldnm:
                    # Round GIS-derived area value to whole number
                    val = int(round((row[fieldnms.index(fldnm)]),0))
                linedict[fldnm] = padvalue(val)
            writer.writerow(linedict)
    del cursor
print ' Made Tracts CSV'


# Create a file with total area for each grid cell
print 'Making GridCells CSV...'
with open(outfileGridCells, 'wb') as csvfile:
    fieldnms = [pointsuidIJfldnm,'Area_SqM']
    for fldnm in fieldnms:
        v = padvalue(fldnm)
        fieldnms[fieldnms.index(fldnm)] = v
    writer = csv.DictWriter(csvfile, fieldnames=fieldnms)
    writer.writeheader()
    # Use Search Cursor to go through each grid cell polygon
    with arcpy.da.SearchCursor(gridpys, [pointsuidIJfldnm,'SHAPE@AREA']) as cursor:
        for row in cursor:
            linedict = {}
            for fldnm in fieldnms:
                val = row[fieldnms.index(fldnm)]
                if fields[fieldnms.index(fldnm)] == 'SHAPE@AREA':
                    # Round GIS-derived area value to whole number
                    val = int(round((row[fieldnms.index(fldnm)]),0))
                linedict[fldnm] = padvalue(val)
            writer.writerow(linedict)
    del cursor
print ' Made GridCells CSV'


# Get lat/lon & I,J values from the Grid Points (include a null entry)
lldict = {'':(None,None,None,None)}
print 'Gathering lat/lon values from Grid Points...'
fields = [pointsuidIJfldnm,pointslatfldnm,pointslonfldnm,pointsifldnm,pointsjfldnm]
with arcpy.da.SearchCursor(inGridpts, fields) as cursor:
    for row in cursor:
        lldict[row[0]] = (row[1],row[2],row[3],row[4])
del cursor


# Create a file with area of each tract/cell intersection
print 'Making Combinations CSV...'
with open(outfileCombinations, 'wb') as csvfile:
    fieldnms = [tractsuidfldnm,pointsuidIJfldnm,'Area_SqM',pointslatfldnm,pointslonfldnm,pointsifldnm,pointsjfldnm]
    for fldnm in fieldnms:
        v = padvalue(fldnm)
        fieldnms[fieldnms.index(fldnm)] = v
    writer = csv.DictWriter(csvfile, fieldnames=fieldnms)
    writer.writeheader()
    # Use Search Cursor to go through each piece of the overlap polygons
    with arcpy.da.SearchCursor(overlap, [tractsuidfldnm,pointsuidIJfldnm,'SHAPE@AREA']) as cursor:
        for row in cursor:
            linedict = {}
            # Get some values into CSV
            for fldnm in fieldnms[:3]:
                val = row[fieldnms.index(fldnm)]
                if fields[fieldnms.index(fldnm)] == 'SHAPE@AREA':
                    # Round GIS-derived area value to whole number
                    val = int(round((row[fieldnms.index(fldnm)]),0))
                linedict[fldnm] = padvalue(val)
            # Get lat/lon & I,J from lldict
            for fldnm in fieldnms[3:]:
                linedict[fldnm] = (lldict[row[1]])[fieldnms.index(fldnm)-3]
            writer.writerow(linedict)
    del cursor
print ' Made Combinations CSV'


### =============  Other things that could be done...  =============
##
### Make a list of grid cells that intersect each tract?
##
### Make a list of tracts that intersect each grid cell?
##
### Calculate the area of each tract covered by each grid cell?
### Calculate the % area of each tract covered by each grid cell?
##


print 'Cone done at', datetime.datetime.today()
