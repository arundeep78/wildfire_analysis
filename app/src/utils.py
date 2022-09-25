"""
General purpose utilities package to help simplify common operations
"""

import io

import sqlalchemy as sa
from sqlalchemy import engine
from typing import List

import pandas as pd
import numpy as np
import streamlit as st
import us

TABLE_WF = "t_uswildfires"

CSS_FILE = "./src/css/styles.css"


def get_state_name(state_code:str):
    """
    Get US state name

    Args:
        state_code (str): State code
    """

    return 'All US States' if state_code.lower() == 'all' else us.states.lookup(state_code).name

def get_states(conn:engine):
    """
    Get list of states from the DB

    Args:
        conn (engine): SQLAlchemy engine

    Return:
        Dataframe of US state codes as exists in US fire database 
    """

    stmt = f'select distinct(state) from {TABLE_WF}'

    list_states = ['all'] + pd.read_sql(stmt,con=conn).squeeze().to_list()
    return list_states

def get_state_years(conn:engine, state:str):
    """
    Get start and end years for given state

    Args:
        conn (engine): SQLAlchemy engine
        state (str): State code
    
    Return:
        list containg start year and end year for fires for given state
    """
    if state.lower() == 'all':
        stmt = f"select min(fire_year) as s_year, max(fire_year) as e_year from {TABLE_WF}"
    else:
        stmt = f"select min(fire_year) as s_year, max(fire_year) as e_year from {TABLE_WF} where state='{state}'"

    df= pd.read_sql(stmt, con=conn).squeeze()

    return df.values.tolist()


def get_state_fire_locs(conn:engine, state_name: str, year:int):
    """
    Get lat lon values for a given state for selected year

    Args:
        conn (engine): SQL Alchemy engine
        state_name (string): name of the state
        year (int): year for which fire locations to be selected

    Return:
        Dataframe of latitude and longitudes for fire location
    """

    stmt = f"""select latitude as lat, longitude as lon from {TABLE_WF} 
                    where 
                    fire_year='{year}'
                    """

    if state_name.lower() != 'all':
        stmt = f"{stmt} and state='{state_name}' "
         
    df_loc = pd.read_sql(stmt,con=conn)

    return df_loc

def get_us_wf_stats(conn:engine ):
    '''
    get overall wildfire count and area trend by frequency
    
    Inputs:
        conn: SqlAlchemy engine
    Output:
        Dict: Dictionary with stats
    '''

    stmt = f'select fire_year as year, count(fire_year) as count, sum(fire_size) as area from {TABLE_WF} group by fire_year'
    
    df = pd.read_sql(stmt, conn)
    df = df.set_index('year')

    tot_fire = df['count'].sum()
    tot_area = df['area'].sum()
    s_year = df.index.min()
    e_year = df.index.max()


    count_coef = np.polyfit(df.index, df['count'], deg=1)
    area_coef = np.polyfit(df.index, df['area'], deg=1)

    return {
            'start_year': s_year, 
            'end_year': e_year, 
            'total_fire': tot_fire, 
            'total_area': tot_area, 
            'count_coef': count_coef,
            'area_coef': area_coef
    }


def get_state_wf_trend(conn:engine, state_code:str = 'all' ):
    '''
    get overall wildfire count and area trend by frequency
    
    Inputs:
        conn: SqlAlchemy engine
        state_code: state for which wildfire trends to be fetched
    Output:
        Dict: Dictionary with stats
    '''
    if state_code == 'all':
        stmt = f'select fire_year as year, count(fire_year) as count, sum(fire_size) as area from {TABLE_WF} group by fire_year'
    else:
        stmt = f"""select fire_year as year, count(fire_year) as count, sum(fire_size) as area 
                    from {TABLE_WF} 
                    where state = '{state_code}'
                    group by fire_year"""

    df = pd.read_sql(stmt, conn)
    df = df.set_index('year')

    tot_fire = df['count'].sum()
    tot_area = df['area'].sum()
    s_year = df.index.min()
    e_year = df.index.max()


    count_coef = np.polyfit(df.index, df['count'], deg=1)
    area_coef = np.polyfit(df.index, df['area'], deg=1)

    return {
            'start_year': s_year, 
            'end_year': e_year, 
            'total_fire': tot_fire, 
            'total_area': tot_area, 
            'count_coef': count_coef,
            'area_coef': area_coef,
            'data_table': df
    }


def get_county_stats(conn:engine, n:int):
    '''
    Provide stats and data for US wildfires by counties

    Args:

        conn (engine) : SQLAlchemy engine
        n (int): count or top and bottom lists to retrieve

    Return:
        Dictionary with stats information
    '''

    stmt = f'''select fire_year as year, fips_name as county, 
                count(fire_year) as count, sum(fire_size) as area 
                from {TABLE_WF}
                    group by fire_year, fips_name
                '''

    df = pd.read_sql(stmt,conn)

    missing_county_pct = df.loc[df['county'].isna(),'count'].sum()/df['count'].sum()*100

    # filter out records where county information is not available
    df = df[~df['county'].isna()]

    # Get overall county data
    df_county = df.drop(columns='year'
                        ).groupby('county'
                            ).sum().sort_values(
                                by='count',
                                ascending = False
                                ).round(2)

    return {
        'missing_county_pct': missing_county_pct,
        'top_by_count': df_county.head(n),
        'bottom_by_count': df_county[df_county['count'] == df_county['count'].min()].sort_index().head(n),
        'top_by_area': df_county.sort_values(by='area',ascending=False).head(n),
        'bottom_by_area': df_county.sort_values(by='area').head(n)
    }


def slope_text(rate:float):
    return 'increased' if np.sign(rate)>0 else 'decreased'

def load_css():
    with open(CSS_FILE) as f:
        css_text = f.read()
        st.markdown('<style>{}</style>'.format(css_text), unsafe_allow_html=True)

# def init_connection():

#     # return psycopg2.connect(**st.secrets["postgres"])

#     return sa.create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}")

# # Initialize Db connection
# conn = init_connection()
