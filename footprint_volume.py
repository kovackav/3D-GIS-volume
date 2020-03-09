# -*- coding: utf-8 -*-

'''******************************************************************
Name: footprint_volume
Description: This script calculates volume from footprints of
multipatches, which were not enclosed and their volume was 0.
******************************************************************'''

import arcpy
import os
import argparse

parser = argparse.ArgumentParser(description = "This script calculates volume from footprints of multipatches, which were not enclosed and their volume was 0.")
parser.add_argument('-d', '--input_data', type = str, metavar = '', required = True, help = 'Folder, where the inputs are stored. It can be stored in sub-folders.')
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
z_foots = []
cnt = 0
cnt_z = 0

with arcpy.da.UpdateCursor(allfoots,["FID", "Volume"]) as cursor:
    for row in cursor:
        cnt = cnt+1
        if row[1] == 0:
            cnt_z = cnt_z + 1
            sql = """{0} = {1}""".format(arcpy.AddFieldDelimiters(allfoots, arcpy.Describe(
                allfoots).OIDFieldName), row[0])
            arcpy.Select_analysis(in_features=allfoots,
                                  out_feature_class=os.path.join(outfolder, 'Shapefile_{0}.shp'.format(row[0])),
                                  where_clause=sql)
            cursor.deleteRow()
            z_foots.append(os.path.join(outfolder, 'Shapefile_{0}.shp'.format(row[0])))
all_z_foots = args.output_folder + 'all_z_foots.shp'
relative_heights_raster = args.input_raster
print('Message: ' + str(cnt) + ' buildings were checked, ' + str(cnt_z) + ' buildings were calculated.')
class LicenseError(Exception):
    pass

try:
    if arcpy.CheckExtension("3D") == "Available":
        arcpy.CheckOutExtension("3D")
    else:
        raise LicenseError

    arcpy.Merge_management(z_foots, all_z_foots)
    arcpy.CreateRandomPoints_management(outfolder, "points", constraining_feature_class = all_z_foots,
                                        minimum_allowed_distance = "0,9")
    arcpy.AddSurfaceInformation_3d(outfolder + "\points.shp", relative_heights_raster, "Z")
    arcpy.Statistics_analysis(outfolder + "\points.shp", outfolder + "\points_cal.shp", [["Z", "MEAN"]], case_field = "CID")
    arcpy.AddField_management(all_z_foots, "height", "DOUBLE")
    arcpy.CalculateField_management(all_z_foots, "height", "[Z_Max] - [Z_Min]")
    arcpy.AddGeometryAttributes_management(all_z_foots, "AREA")
    arcpy.CalculateField_management(all_z_foots, "volume", "[height] * [POLY_AREA]")

except LicenseError:
    print('3D Analyst license is unavailable')
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))

all_calc = args.output_folder + 'all_calc.shp'
arcpy.Merge_management([allfoots, all_z_foots], all_calc)
arcpy.DeleteField_management(all_calc, ["height", "POLY_AREA", "Z_MIN", "Z_MAX"])

del(cursor)
print ('Message: Script successfully done!')
