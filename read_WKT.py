# -*- coding: utf-8 -*-

'''******************************************************************
Name: read_WKT
Description: This script reads the WKT geometry.
******************************************************************'''

import arcpy
import os
import argparse

parser = argparse.ArgumentParser(description = "This script takes multipatch files from a folder and encloses them. Then calculates volume of the features.")
parser.add_argument('-d', '--input_data', type = str, metavar = '', required = True, help = 'Folder, where the inputs are stored. It can be stored in sub-folders.')
args = parser.parse_args()

print ('Message: Parameters valid, starting the script.')

arcpy.env.overwriteOutput = 1


for root, dirs, files in os.walk(args.input_data):
    for file in files:
        if file.endswith(".shp"):
            print(os.path.join(root, file))
            with arcpy.da.SearchCursor((os.path.join(root, file)),["OID@", "SHAPE@WKT"]) as cursor:
                for row in cursor:
                    print("Feature {}:".format(row[0]))
                    #the_geom = row.getValue(row[0])
                    #wkt = the_geom.WKT
                    print(row[1])

#file_path = r'C:\Users\vitak\Downloads\Desktop\Bakalarka\Data\data_polygonz\BD3_Prah00_polygonZ\BD3_Prah00.shp'
#query = arcpy.SearchCursor(file_path)
#for row in query:
#    the_geom = row.getValue('Shape')  # Get Geometry field
#    wkt = the_geom.WKT
#    print(wkt)
print ('Message: Script successfully done!')