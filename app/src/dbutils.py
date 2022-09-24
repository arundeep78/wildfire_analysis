import sqlalchemy as sa
import os
from sqlalchemy import text
import pandas as pd
import io


def table_exists( tbl_name , db_conn = None):
    """
    Returns true or false if table exists in DB
    
    Inputs:
        tbl_name (String): name of the table to be searched.
        db_conn (SQLAlchemy engine): SQLAlchemy creat_engine object
    """
    if db_conn is None:
        db_conn = sa.create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}")

    return sa.inspect(db_conn).has_table(tbl_name)

def get_table_columns(tbl_name, db_conn):
    """
    Returns column names of the given table
    
    Inputs:
        tbl_name (String): name of the table to be searched.
        db_conn (SQLAlchemy engine): SQLAlchemy creat_engine object
    
    """
    
    res = db_conn.execute(f"select column_name from information_schema.columns where table_name='{tbl_name}'")
    cols = [ col[0] for col in res.fetchall()]
    return cols

def create_table_comments(tbl_name, db_conn, tbl_comments):
    """
    Creates table comments in the database for a given table. 
    
    Inputs:
        tbl_name[String] : table name for which comments needs to be updated
        db_conn[SQLAlchemy connection] : SQL Alchmey db connection object
        tbl_comments[dict] : dictionary with column names and column description. If exits special key "table", then its value is used to add table description 
        
    """
    if not isinstance(tbl_comments, dict):
        print("tbl_comments is must be a dictionary with column names and their description")
        return

    stmt = "COMMENT On COLUMN {}.{} is :com"

    for k,v in tbl_comments.items():
        if k =="table":
            stmt_tbl = text(f"COMMENT ON TABLE {tbl_name} IS :com").execution_options(autocommit=True)
            db_conn.execute(stmt_tbl, com=v)
        else:
            db_conn.execute(text(stmt.format(tbl_name,k)).execution_options(autocommit=True),com=v)

def get_db_connection():

    # return psycopg2.connect(**st.secrets["postgres"])

    return sa.create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}")


def read_sqlite_data(stmt , sqlite_file ):

    sqlite_conn = sa.create_engine(sqlite_file)
    df = pd.read_sql(stmt, sqlite_conn)
    return df

def init_pgdb(df, tbl_name, tbl_cols, tbl_comments, fast = True):
    
    #get pgsql connection
    db_conn = get_db_connection()

    #create blank DB table with structure
    pd.DataFrame(columns=tbl_cols
                ).to_sql(tbl_name, 
                            con= db_conn, 
                            index=False, 
                            if_exists='replace', 
                            dtype=tbl_cols)

    # add table and column description
    create_table_comments(tbl_name, db_conn, tbl_comments)
    
    #populate DB table with data
    if fast:
        df_toPG(df, tbl_name, db_conn, if_exists='append',index=False)
    else:
        df.to_sql(tbl_name, con = db_conn, if_exists='append', index=False)



def df_toPG(df, table_name, con,if_exists='replace', sep='\t', index= False,dtypes= None , encoding='utf-8'):
    """
    Faster way to pushing large pandas dataframe ( million+ rows) to database. This one is specifically tested for Postgres.
    In comparison to df.to_sql this function took only 16s, while to_sql took about 3min for 6 million rows with no indexes.
    Orig source : https://github.com/blaze/odo/issues/614
    Args:
        df (DatFrame): Single index and column Dataframe to be pushed to Database 
        table_name (String): name of the table in the Database
        con (SQlAlchemy.Engine.Connection): SQLAlchemy database connection
        if_exists (str, optional): if table already exists then to replace it on append to it. Defaults to 'replace'.
        sep (str, optional): CSV file separator. Defaults to '\t'.
        index(bool, optional) : to use index as values for Db table or not. Defaults to False. 
        encoding (str, optional): Encoding for Db connection. Defaults to 'utf-8'.
        dtypes (Dict, optional): Dictionary of column names and database to be set in Databasse. Defaults to None.
    """
    # Create Table
    if not dtypes is None:
        df[:0].to_sql(table_name, con, if_exists=if_exists, index=index,dtype=dtypes)
    elif if_exists == "replace":
        df[:0].to_sql(table_name, con, if_exists=if_exists, index=False)

    #Prepare data
    output = io.StringIO()
    df.to_csv(output, sep=sep, header=False, index=index,encoding=encoding)
    #output.getvalue()
    output.seek(0)
    
    #Insert data
    raw = con.engine.raw_connection()
    curs = raw.cursor()
    # null values become ''
    columns = df.columns
    curs.copy_from(output, table_name, null="")
    curs.connection.commit()
    curs.close()
    del output
