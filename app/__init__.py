#!/usr/bin/env python

#####
# Helper script to read selected information from SQLLite DB to move to postgresDB.
# Executed at creation of the DB Docker build
####




import os
import time

import src.dbutils as dbu
from sqlalchemy.dialects import postgresql



SQLITE_FILE =os.environ['SQLITE_DB_FILE']

TBL_NAME = 'Fires'
TABLE_WF = 't_uswildfires'

STMT_WF = f'''select fod_id, fpa_id, fire_year, discovery_date,
                stat_cause_code, stat_cause_descr,
                fire_size, fire_size_class,
                latitude, longitude,state, county,fips_code, fips_name
                from {TBL_NAME}
                '''

TBL_COLS = {
    'fod_id': postgresql.INTEGER,
    'fpa_id': postgresql.TEXT,
    'fire_year': postgresql.INTEGER,
    'discovery_date': postgresql.FLOAT,
    'stat_cause_code': postgresql.INTEGER,
    'stat_cause_descr': postgresql.TEXT,
    'fire_size': postgresql.FLOAT, 
    'fire_size_class': postgresql.TEXT,
    'latitude' : postgresql.FLOAT,
    'longitude' : postgresql.FLOAT,
    'state': postgresql.TEXT, 
    'county': postgresql.TEXT,
    'fips_code': postgresql.TEXT, 
    'fips_name': postgresql.TEXT
}

TBL_COLS_COMMENTS = {
    'table':'spatial database of wildfires that occurred in the United States from 1992 to 2015.',
    'fod_id': 'Global unique identifier.',
    'fpa_id': 'Unique identifier that contains information necessary to track back to the original record in the source dataset.',
    'fire_year': 'Calendar year in which the fire was discovered or confirmed to exist.',
    'discovery_date': 'Date on which the fire was discovered or confirmed to exist.',
    'stat_cause_code': 'Code for the (statistical) cause of the fire.',
    'stat_cause_descr': 'Description of the (statistical) cause of the fire.',
    'fire_size': 'Estimate of acres within the final perimeter of the fire.', 
    'fire_size_class': 'Code for fire size based on the number of acres within the final fire perimeter expenditures (A=greater than 0 but less than or equal to 0.25 acres, B=0.26-9.9 acres, C=10.0-99.9 acres, D=100-299 acres, E=300 to 999 acres, F=1000 to 4999 acres, and G=5000+ acres).',
    'latitude' : 'Latitude (NAD83) for point location of the fire (decimal degrees).',
    'longitude' : 'Longitude (NAD83) for point location of the fire (decimal degrees).',
    'state': 'Two-letter alphabetic code for the state in which the fire burned (or originated), based on the nominal designation in the fire report.', 
    'county': 'County, or equivalent, in which the fire burned (or originated), based on nominal designation in the fire report',
    'fips_code': 'Three-digit code from the Federal Information Process Standards (FIPS) publication 6-4 for representation of counties and equivalent entities.', 
    'fips_name': 'County name from the FIPS publication 6-4 for representation of counties and equivalent entities.'
}


conn = dbu.get_db_connection()

if not dbu.table_exists(TABLE_WF,db_conn=conn):
    # read data from SQLite file
    df = dbu.read_sqlite_data(STMT_WF, SQLITE_FILE)

    df.columns = df.columns.str.lower()
    df = df.convert_dtypes()

    # add data into postgres DB
    start = time.perf_counter()
    dbu.init_pgdb(df,TABLE_WF, TBL_COLS,TBL_COLS_COMMENTS, fast=True)

    dur = time.perf_counter() - start

    print(f'time taken: {dur}')

