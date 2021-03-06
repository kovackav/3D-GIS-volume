import psycopg2
import argparse
import json
import datetime

parser = argparse.ArgumentParser(description = "This script calculates volume from footprints of buildings and raster with relative heights of the buildings. Should be used as extension of the ReconfigurableUrbanModeler (https://github.com/simberaj/rum). All inputs should share the same SRID as the grid of the RUM.")
parser.add_argument('-s', '--database_schema', type = str, metavar = '', required = True, help = 'Database schema.')
parser.add_argument('-d', '--input_footprints', type = str, metavar = '', required = True, help = 'Name of the table with bulding footprints.')
parser.add_argument('-c', '--area_column', type = str, metavar = '', required = True, help = 'Name of the column with area in the input footprint table.')
parser.add_argument('-r', '--input_raster', type = str, metavar = '', required = True, help = 'Name of the table with raster with relative heights of the buildings.')
parser.add_argument('-o', '--output_table', type = str, metavar = '', required = True, help = 'Name of the output table')
args = parser.parse_args()
schema = str(args.database_schema)

with open('dbconn.JSON') as config_file:
    login = json.load(config_file)

now = datetime.datetime.today()
print(str(now) + " Starting the script, connecting to database.")

class DatabaseTask:
    schemaSQL = str(args.database_schema)
    foot = str(args.input_footprints)
    rastr = str(args.input_raster)
    output = str(args.output_table)
    area_building = str(args.area_column)
    def __init__(self):
        try:
            self.connection = psycopg2.connect(**login)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            now = datetime.datetime.today()
            print(str(now) + " Connected to database.")
        except:
            now = datetime.datetime.today()
            print(str(now) + " Cannot connect to the database.")

    def add_id(self):
        schema = self.schemaSQL
        buildings = self.foot
        self.cursor.execute(f'ALTER TABLE {schema}.{buildings} ADD COLUMN uniqueid int GENERATED BY DEFAULT AS IDENTITY')

    def calc_points(self):
        schema = self.schemaSQL
        rastr = self.rastr
        buildings = self.foot
        self.cursor.execute(f'CREATE TABLE {schema}.bodyras (id integer, height float,geom geometry)')
        self.cursor.execute(f'INSERT INTO {schema}.bodyras(height, geom) SELECT band_1, ST_GeneratePoints(geometry, 1) FROM {schema}.{rastr}')
        self.cursor.execute(f'UPDATE {schema}.bodyras SET id = "uniqueid" FROM {schema}.{buildings} WHERE ST_Contains({buildings}.geometry, bodyras.geom)')
        now = datetime.datetime.today()
        print(str(now) + " Points calculated.")

    def calc_volume(self):
        schema = self.schemaSQL
        output = self.output
        buildings = self.foot
        area = self.area_building
        self.cursor.execute(f'CREATE TABLE {schema}.{output} AS (SELECT id, AVG(bodyras.height) FROM {schema}.bodyras WHERE id IS NOT NULL GROUP BY id)')
        self.cursor.execute(f'DROP TABLE {schema}.bodyras')
        self.cursor.execute(f'ALTER TABLE {schema}.{output} ADD COLUMN volumev float')
        self.cursor.execute(f'ALTER TABLE {schema}.{output} ADD COLUMN geom geometry')
        self.cursor.execute(f'ALTER TABLE {schema}.{output} ADD COLUMN areafoot float')
        self.cursor.execute(f'UPDATE {schema}.{output} SET geom = {buildings}.geometry FROM {schema}.{buildings} WHERE id = "uniqueid"')
        self.cursor.execute(f'UPDATE {schema}.{output} SET areafoot = {area} FROM {schema}.{buildings} WHERE id = "uniqueid"')
        self.cursor.execute(f'UPDATE {schema}.{output} SET volumev = ("avg"*areafoot)')
        now = datetime.datetime.today()
        print(str(now) + " Volume calculated.")

    def centroid_prepare(self):
        schema = self.schemaSQL
        output = self.output
        self.cursor.execute(f'CREATE TABLE {schema}.table1 AS ((SELECT geohash FROM {schema}.grid))')
        self.cursor.execute(f'ALTER TABLE {schema}.table1 ADD COLUMN volume float')
        self.cursor.execute(f'ALTER TABLE {schema}.table1 ADD COLUMN geom geometry')
        self.cursor.execute(f'UPDATE {schema}.table1 SET geom = grid.geometry FROM {schema}.grid WHERE grid.geohash = table1.geohash')
        self.cursor.execute(f'UPDATE {schema}.table1 SET volume = volumev FROM {schema}.{output} WHERE ST_Contains(table1.geom, (ST_Centroid({output}.geom)))')
        now = datetime.datetime.today()
        print(str(now) + " Centroids prepared.")


    def centroid_feat(self):
        schema = self.schemaSQL
        output = self.output
        self.cursor.execute(f'CREATE TABLE {schema}.table2 AS (SELECT id, volumev, ST_Centroid({output}.geom) FROM {schema}.{output})')
        self.cursor.execute(f'ALTER TABLE {schema}.table2 ADD COLUMN geohash text;')
        self.cursor.execute(f'UPDATE {schema}.table2 SET geohash = grid.geohash FROM {schema}.grid WHERE ST_contains(grid.geometry, table2.st_centroid)')
        self.cursor.execute(f'CREATE TABLE {schema}.feat_building_3 AS (SELECT geohash, SUM(volumev) AS volume_PostGIS FROM {schema}.table2 GROUP BY geohash)')
        self.cursor.execute(f'DROP TABLE {schema}.table1;')
        self.cursor.execute(f'DROP TABLE {schema}.table2;')
        now = datetime.datetime.today()
        print(str(now) + " Feat table prepared.")


if __name__ == '__main__':
    database_operation = DatabaseTask()
    database_operation.add_id()
    database_operation.calc_points()
    database_operation.calc_volume()
    database_operation.centroid_prepare()
    database_operation.centroid_feat()
    now = datetime.datetime.today()
    print(str(now) + " Script completed, volume calculated.")
