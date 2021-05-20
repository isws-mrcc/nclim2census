# ---------------------------------------------------------------------------
# 1_DownloadAndAggregate_CensusTracts.py
# Created in October 2020
# Revised through April 2021
#   by Z. Zaloudek
# TOOK 10 minutes TO RUN ON 11/23/2020
# TOOK 6 minutes TO RUN ON 3/18/2020
# ---------------------------------------------------------------------------

# Import things
print 'Starting up at...'
import os, glob, datetime, urllib, ssl, zipfile, arcpy
print datetime.datetime.today()

# Geoprocessing environment settings
arcpy.env.overwriteOutput = True

    
# Variables
Folder = r'\\SWSATLAS\CentersGIS\CAS\MRCC\AWR_CensusTracts'
folder = Folder+'\\orig_data\UScensus_2020'
baseurl = 'https://www2.census.gov/geo/tiger/TIGER2020/TRACT/'
GDBnm = 'USCensusTracts2020'
GDB = Folder+'\\'+GDBnm+'.gdb'
FCnm = 'CensusTracts2020'
FC = GDB + '\\' + FCnm
skipfields = ['FID','Shape']

### Used for 2010 US Census Tracts
##baseurl = 'https://www2.census.gov/geo/pvs/tiger2010st/'
##GDBnm = 'USCensusTracts2010'
##FCnm = 'CensusTracts2010'


states = (
    ['Alabama', 'AL', '01'],
##    ['Alaska', 'AK', '02'],
    ['Arizona', 'AZ', '04'],
    ['Arkansas', 'AR', '05'],
    ['California', 'CA', '06'],
    ['Colorado', 'CO', '08'],
    ['Connecticut', 'CT', '09'],
    ['Delaware', 'DE', '10'],
    ['Florida', 'FL', '12'],
    ['Georgia', 'GA', '13'],
##    ['Hawaii', 'HI', '15'],
    ['Idaho', 'ID', '16'],
    ['Illinois', 'IL', '17'],
    ['Indiana', 'IN', '18'],
    ['Iowa', 'IA', '19'],
    ['Kansas', 'KS', '20'],
    ['Kentucky', 'KY', '21'],
    ['Louisiana', 'LA', '22'],
    ['Maine', 'ME', '23'],
    ['Maryland', 'MD', '24'],
    ['Massachusetts', 'MA', '25'],
    ['Michigan', 'MI', '26'],
    ['Minnesota', 'MN', '27'],
    ['Mississippi', 'MS', '28'],
    ['Missouri', 'MO', '29'],
    ['Montana', 'MT', '30'],
    ['Nebraska', 'NE', '31'],
    ['Nevada', 'NV', '32'],
    ['New Hampshire', 'NH', '33'],
    ['New Jersey', 'NJ', '34'],
    ['New Mexico', 'NM', '35'],
    ['New York', 'NY', '36'],
    ['North Carolina', 'NC', '37'],
    ['North Dakota', 'ND', '38'],
    ['Ohio', 'OH', '39'],
    ['Oklahoma', 'OK', '40'],
    ['Oregon', 'OR', '41'],
    ['Pennsylvania', 'PA', '42'],
    ['Rhode Island', 'RI', '44'],
    ['South Carolina', 'SC', '45'],
    ['South Dakota', 'SD', '46'],
    ['Tennessee', 'TN', '47'],
    ['Texas', 'TX', '48'],
    ['Utah', 'UT', '49'],
    ['Vermont', 'VT', '50'],
    ['Virginia', 'VA', '51'],
    ['Washington', 'WA', '53'],
    ['West Virginia', 'WV', '54'],
    ['Wisconsin', 'WI', '55'],
    ['Wyoming', 'WY', '56'],
    )


# Had to add this line to get around 500 Internal Server Error when downloading
ssl._create_default_https_context = ssl._create_unverified_context

# Get Census Tracts data for each state
shps = []
for s in states:
    print s
    state = (s[0]).replace(' ','_')
    
    # Download zipfile
    url = baseurl+'/tl_2020_'+s[2]+'_tract.zip'
    dlfile = folder+'\\tract2020_'+s[2]+'.zip'
    
##    # Used for 2010 US Census Tracts
##    url = baseurl+s[2]+'_'+state+'/'+s[2]+'/tl_2010_'+s[2]+'_tract10.zip'
##    dlfile = folder+'\\tract2010_'+s[2]+'.zip'
    
    print ' url',url
    urllib.urlopen(url)
    urllib.URLopener().retrieve(url, dlfile)
    
    # Unzip file
    zipfl = zipfile.ZipFile(dlfile,'r')
    zipfl.extractall(folder)
    zipfl.close()

    # Add shapefile to shps list
    for shpfile in glob.glob( os.path.join( folder, ('*.shp') ) ):
        if shpfile not in shps:
            shps.append(shpfile)
##print 'shps',shps

# Create GDB if needed
if not arcpy.Exists(GDB):
    arcpy.CreateFileGDB_management(Folder, GDBnm)
    print 'Created GDB'

# Get info from first shapefile in shps list
shp = shps[0]
desc = arcpy.Describe(shp)

# Create Feature Class within GDB
print ' Creating blank feature class...'
arcpy.CreateFeatureclass_management(GDB, FCnm, 'POLYGON', '', 'DISABLED', 'DISABLED', desc.spatialReference)
print ' Adding fields...'
for fld in desc.fields:
    if fld.name not in skipfields:
        arcpy.AddField_management(FC, fld.name, fld.type, '', '', fld.length)
        print ' ',fld.name

# Aggregate Census Tracts for each state into one feature class
print 'Appending GIS data...'
arcpy.Append_management(shps, FC, 'NO_TEST')

# Delete shapefiles (keep zipfiles)
for shp in shps:
    arcpy.Delete_management(shp)
print 'Deleted individual shapefiles'

# Calculate Total Area from ALAND and AWATER fields
arcpy.AddField_management(FC, 'AREATOTAL', 'DOUBLE', '', '', None)
with arcpy.da.UpdateCursor(FC, ['ALAND','AWATER','AREATOTAL']) as cursor:
    for row in cursor:
        row[2] = row[0]+row[1]
        cursor.updateRow(row)
del cursor


print 'Cone done at', datetime.datetime.today()
