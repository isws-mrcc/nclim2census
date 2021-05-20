# ---------------------------------------------------------------------------
# 2p5_CreateTestData.py
# Created in November 2020
# Revised through -
#   by Z. Zaloudek
# TOOK 2 minutes TO RUN ON 11/23/2020 for Champaign County IL
# TOOK 2 minutes TO RUN ON 11/23/2020 for State of Illinois
# ---------------------------------------------------------------------------

# Import things
print 'Starting up at...'
import datetime, arcpy
print datetime.datetime.today()


# Geoprocessing environment settings
arcpy.env.overwriteOutput = True

    
# Variables
Folder = r'\\SWSATLAS\CentersGIS\CAS\MRCC\AWR_CensusTracts'
inTracts = Folder + '\\USCensusTracts2010.gdb\\CensusTracts2010'
tractsstfldnm = 'STATEFP10'
tractscntyfldnm = 'COUNTYFP10'
inGridpts = Folder + '\\nClimGridPoints.gdb\\nClimGridPoints'
pointslatfldnm = 'Lat'
pointslonfldnm = 'Lon'
GDBnm = 'GISprocessing'
GDB = Folder+'\\'+GDBnm+'.gdb'


# Where clauses to select Champaign County IL
tractswclause = arcpy.AddFieldDelimiters(inTracts,tractsstfldnm)+" = '17' AND "+\
          arcpy.AddFieldDelimiters(inTracts,tractscntyfldnm)+" = '019'"
pointswclause = arcpy.AddFieldDelimiters(inGridpts,pointslatfldnm)+" >= 39.8542 AND "+\
          arcpy.AddFieldDelimiters(inGridpts,pointslonfldnm)+" >= -88.4792 AND "+\
          arcpy.AddFieldDelimiters(inGridpts,pointslatfldnm)+" <= 40.3958 AND "+\
          arcpy.AddFieldDelimiters(inGridpts,pointslonfldnm)+" <= -87.9375"

### Where clauses to select State of IL
##tractswclause = arcpy.AddFieldDelimiters(inTracts,tractsstfldnm)+" = '17'"
##pointswclause = arcpy.AddFieldDelimiters(inGridpts,pointslatfldnm)+" >= 36.9792 AND "+\
##          arcpy.AddFieldDelimiters(inGridpts,pointslonfldnm)+" >= -91.5208 AND "+\
##          arcpy.AddFieldDelimiters(inGridpts,pointslatfldnm)+" <= 42.5208 AND "+\
##          arcpy.AddFieldDelimiters(inGridpts,pointslonfldnm)+" <= -87.4792"


# Select out Champaign County IL tracts
outtracts = inTracts+'_forTEST'
print 'Selecting Tracts...'
arcpy.Select_analysis(inTracts, outtracts, tractswclause)

# Select out points over Champaign County IL
outpoints = inGridpts+'_forTEST'
print 'Selecting Points...'
arcpy.Select_analysis(inGridpts, outpoints, pointswclause)



print 'Cone done at', datetime.datetime.today()
