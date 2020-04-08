# -*- coding: latin-1 -*-

'''******************************************************************
Name: merge_files
Description: This script merges multiple shapefiles.
******************************************************************'''

import arcpy
import os
import argparse

parser = argparse.ArgumentParser(description = "This script merges multiple shapefiles.")
parser.add_argument('-d', '--input_data', type = str, metavar = '', required = True, help = 'Folder, where the footprints are stored. It can be stored in sub-folders.')
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

allfoots = args.output_folder + '/merged.shp'
arcpy.Merge_management(foots, allfoots)

print ('Message: Script successfully done!')
