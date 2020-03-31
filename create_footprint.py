# -*- coding: utf-8 -*-

'''******************************************************************
Name: data_calc
Description: This script takes multipatch files from a folder and
creates footprint of them with column "volume" with default value 0.
******************************************************************'''

import arcpy
import os
import argparse

parser = argparse.ArgumentParser(description = "This script takes multipatch files from a folder and creates footprint of them with column volume with default value 0.")
parser.add_argument('-d', '--input_data', type = str, metavar = '', required = True, help = 'Folder, where the inputs are stored. It can be stored in sub-folders.')
args = parser.parse_args()

print ('Message: Parameters valid, starting the script.')

arcpy.env.overwriteOutput = 1
data = args.input_data

class LicenseError(Exception):
    pass

try:
    if arcpy.CheckExtension("3D") == "Available":
        arcpy.CheckOutExtension("3D")
    else:
        raise LicenseError

    for root, dirs, files in os.walk(data):
        for file in files:
            if file.endswith(".shp"):
                inFeature = (os.path.join(root, file))
                footprint = str(os.path.join(root, file)).replace(".shp","") + "_foot.shp"
                print (inFeature)
                arcpy.MultiPatchFootprint_3d(inFeature, footprint)
                arcpy.AddField_management(footprint, "volume", "DOUBLE")

except LicenseError:
    print("3D Analyst license is unavailable")
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))

print ('Message: Script successfully done!')
