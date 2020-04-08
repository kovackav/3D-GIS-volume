import psycopg2
import argparse
import json
import datetime

parser = argparse.ArgumentParser(description = "This script creates feat table with geohash using table with already calculated volume. Should be used as extension of the ReconfigurableUrbanModeler (https://github.com/simberaj/rum). All inputs should share the same SRID as the grid of the RUM.")
parser.add_argument('-s', '--database_schema', type = str, metavar = '', required = True, help = 'Database schema.')
parser.add_argument('-i', '--input_table', type = str, metavar = '', required = True, help = 'Name of the input table with footprints and calculated volume.')
parser.add_argument('-c', '--geom_column', type = str, metavar = '', required = True, help = 'Name of the column with geometry in the input table.')
parser.add_argument('-v', '--volume_column', type = str, metavar = '', required = True, help = 'Name of the column with volume in the input table.')
parser.add_argument('-o', '--output_table', type = str, metavar = '', required = True, help = 'Name of the output table. Should be like "feat_')
args = parser.parse_args()
schema = str(args.database_schema)

with open('dbconn.JSON') as config_file:
    login = json.load(config_file)

now = datetime.datetime.today()
print(str(now) + " Starting the script, connecting to database.")

class DatabaseTask:
    schemaSQL = str(args.database_schema)
    input = str(args.input_table)
    volume = str(args.volume_column)
    geom = str(args.geom_column)
    output_table = str(args.output_table)
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


    def create_feat(self):
        schema = self.schemaSQL
        input = self.input
        volume = self.volume
        geom = self.geom
        output_table = self.output_table
        self.cursor.execute(f'CREATE TABLE {schema}.table3 AS (SELECT {volume}, {geom} FROM {schema}.{input});')
        self.cursor.execute(f'ALTER TABLE {schema}.table3 ADD COLUMN geohash text;')
        self.cursor.execute(f'UPDATE {schema}.table3 SET geohash = grid.geohash FROM {schema}.grid WHERE ST_contains(grid.geometry, table3.{geom});')
        self.cursor.execute(f'CREATE TABLE {schema}.{output_table} AS (SELECT geohash, SUM({volume}) AS volume FROM {schema}.table3 GROUP BY geohash);')
        self.cursor.execute(f'DROP TABLE {schema}.table3;')


if __name__ == '__main__':
    database_operation = DatabaseTask()
    database_operation.create_feat()
    now = datetime.datetime.today()
    print(str(now) + " Script completed, feat created.")
