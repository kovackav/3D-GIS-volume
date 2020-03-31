import psycopg2
import argparse
import json
import datetime

parser = argparse.ArgumentParser(description = "This script calculates volume from footprints of buildings and raster with relative heights of the buildings. Should be used as extension of the ReconfigurableUrbanModeler (https://github.com/simberaj/rum). All inputs should share the same SRID as the grid of the RUM.")
parser.add_argument('-s', '--database_schema', type = str, metavar = '', required = True, help = 'Database schema.')
parser.add_argument('-d', '--input_footprints', type = str, metavar = '', required = True, help = 'Name of the table with bulding footprints.')
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
    def __init__(self):
        try:
            self.connection = psycopg2.connect(**login)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            print(str(now) + " Connected to database.")
        except:
            print(str(now) + " Cannot connect to the database.")

    def add_id(self):
        add_id_command = 'ALTER TABLE {schema}.{buildings} ADD COLUMN uniqueid int GENERATED BY DEFAULT AS IDENTITY;'.format(
        schema=self.schemaSQL,
        buildings=self.foot
        )
        self.cursor.execute(add_id_command)

    def calc_points(self):
        create_table_command = "CREATE TABLE {schema}.bodyras (id integer, height float,geom geometry);".format(schema=self.schemaSQL)
        self.cursor.execute(create_table_command)
        insert_into_command = "INSERT INTO {schema}.bodyras(height, geom) SELECT band_1, ST_GeneratePoints(geometry, 1) FROM {schema}.{rastr};".format(
            schema = self.schemaSQL,
            rastr = self.rastr)
        self.cursor.execute(insert_into_command)
        update_command = 'UPDATE {schema}.bodyras SET id = "uniqueid" FROM {schema}.{buildings} WHERE ST_Contains({buildings}.geometry, bodyras.geom)'.format(
        schema=self.schemaSQL,
        buildings=self.foot)
        self.cursor.execute(update_command)

    def calc_volume(self):
        create_table_command = 'CREATE TABLE {schema}.{output} AS (SELECT id, AVG(bodyras.height) FROM {schema}.bodyras WHERE id IS NOT NULL GROUP BY id);'.format(
        schema=self.schemaSQL,
        output=self.output
        )
        self.cursor.execute(create_table_command)
        drop_table_command = 'DROP TABLE {schema}.bodyras'.format(schema=self.schemaSQL)
        self.cursor.execute(drop_table_command)
        alter_table_command1 = 'ALTER TABLE {schema}.{output} ADD COLUMN volume float;'.format(
        schema=self.schemaSQL,
        output=self.output
        )
        self.cursor.execute(alter_table_command1)
        alter_table_command2 = 'ALTER TABLE {schema}.{output} ADD COLUMN geom geometry;'.format(
        schema=self.schemaSQL,
        output=self.output
        )
        self.cursor.execute(alter_table_command2)
        alter_table_command3 = 'ALTER TABLE {schema}.{output} ADD COLUMN area float;'.format(
        schema=self.schemaSQL,
        output=self.output
        )
        self.cursor.execute(alter_table_command3)
        update_command1 = 'UPDATE {schema}.{output} SET geom = {buildings}.geometry FROM {schema}.budovy WHERE id = "uniqueid"'.format(
        schema=self.schemaSQL,
        buildings=self.foot,
        output=self.output
        )
        self.cursor.execute(update_command1)
        update_command2 = 'UPDATE {schema}.{output} SET area = "Shape_Area" FROM {schema}.{buildings} WHERE id = "uniqueid"'.format(
        schema=self.schemaSQL,
        buildings=self.foot,
        output=self.output
        )
        self.cursor.execute(update_command2)
        update_command3 = 'UPDATE {schema}.{output} SET volume = ("avg"*area)'.format(
        schema=self.schemaSQL,
        output=self.output
        )
        self.cursor.execute(update_command3)


if __name__ == '__main__':
    database_operation = DatabaseTask()
    database_operation.add_id()
    database_operation.calc_points()
    database_operation.calc_volume()
    print(str(now) + " Script completed, volume calculated.")