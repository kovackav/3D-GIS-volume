# -*- coding: latin-1 -*-

'''******************************************************************
Name: volume_f_rbh_raster
Description: This script calculates volume from building footprints
and raster of relative building heights.
******************************************************************'''

import arcpy
import os
import argparse

parser = argparse.ArgumentParser(description = "This script calculates volume from footprints of multipatches, which were not enclosed and their volume was 0.")
parser.add_argument('-d', '--input_data', type = str, metavar = '', required = True, help = 'Folder, where the footprints are stored. It can be stored in sub-folders.')
parser.add_argument('-r', '--input_raster', type = str, metavar = '', required = True, help = 'Raster with relative heights of the buildings.')
parser.add_argument('-o', '--output_folder', type = str, metavar = '', required = True, help = 'Folder, where the output should be saved.')
parser.add_argument('-c', '--condition', type = str, metavar = '', help = 'Optional condition, which determines string with which the input ends.')
args = parser.parse_args()

print ('Message: Parameters valid, starting the script.')

arcpy.env.overwriteOutput = 1

foots = []

for root, dirs, files in os.walk(args.input_data):
    for file in files:
        if file.endswith(args.condition):
            print(file)
            foot = (os.path.join(root, file))
            foots.append(foot)

allfoots = args.output_folder + '/all_foots.shp'
arcpy.Merge_management(foots, allfoots)
outfolder = args.output_folder
arcpy.AddField_management(allfoots, "volume", "DOUBLE")

all_z_foots = args.output_folder + 'all_z_foots.shp'
relative_heights_raster = args.input_raster
class LicenseError(Exception):
    pass

try:
    if arcpy.CheckExtension("3D") == "Available":
        arcpy.CheckOutExtension("3D")
    else:
        raise LicenseError

    arcpy.CreateRandomPoints_management(outfolder, "points", constraining_feature_class = allfoots,
                                        minimum_allowed_distance = "0,9")
    arcpy.AddSurfaceInformation_3d(outfolder + "\points.shp", relative_heights_raster, "Z")
    arcpy.Statistics_analysis(outfolder + "\points.shp", outfolder + "\points_cal.shp", [["Z", "MEAN"]], case_field = "CID")
    arcpy.AddField_management(allfoots, "height", "DOUBLE")
    arcpy.CalculateField_management(allfoots, "height", "[Z_Max] - [Z_Min]")
    arcpy.AddGeometryAttributes_management(allfoots, "AREA")
    arcpy.AddField_management(allfoots, "volume", "DOUBLE")
    arcpy.CalculateField_management(allfoots, "volume", "[height] * [POLY_AREA]")

except LicenseError:
    print('3D Analyst license is unavailable')
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))

arcpy.DeleteField_management(allfoots, ["height", "POLY_AREA", "Z_MIN", "Z_MAX"])

print ('Message: Script successfully done!')
