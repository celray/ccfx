'''
a module that helps ease the management of MSSQL databases

Author  : Celray James CHAWANDA
Email   : celray.chawanda@outlook.com
Licence : MIT 2023
Repo    : https://github.com/celray

Date    : 2023-07-20
'''
# imports

import sys
import urllib
import sys
import pandas
import pyodbc
from sqlalchemy import MetaData, Table, create_engine, func, select
from shapely import wkt
import geopandas


# classes
class mssql_connection:
    def __init__(self, server, username, password, driver, trust_server_ssl = True) -> None:
        self.server     = server
        self.username   = username
        self.password   = password
        self.driver     = driver

        self.trust_server_ssl     = trust_server_ssl
        
        self.connection = None
        self.cursor     = None
        self.db_name    = "TMP_CJames"
        
        self.databases  = []

    def connect(self):
        # Connect to the SQL Server instance
        connection_string   = f'DRIVER={self.driver};SERVER={self.server};UID={self.username};PWD={self.password};TrustServerCertificate={"yes" if self.trust_server_ssl else "no"}'
        try:
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            print(f"> connection to {self.server} established...")
        except pyodbc.Error as e:
            print("! error occurred while connecting to the SQL Server instance:")
            print(e)


    def listDatabases(self) -> list:
        query = "SELECT name FROM sys.databases"
        
        if self.connection is None:
            print("! there is no connection to the MSSQL server instance")
            sys.exit(1)
            
        # Execute the query and fetch the results
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(query)
            self.databases = [row[0] for row in self.cursor.fetchall()]
            print("\n> List of available databases:")
            for db in self.databases:
                print(f"\t- {db}")
        except pyodbc.Error as e:
            print("! error occurred while fetching the list of databases:")
            print(e)
        
        return self.databases
    
    
    def listTables(self, db_name = None) -> list:
        
        if not db_name is None:
            self.connect_db(db_name)
            
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        """

        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(query)
            tables = [row[0] for row in self.cursor.fetchall()]
            print("> list of tables in the active database:")
            for table in tables:
                print(f"\t- {table}")
        except pyodbc.Error as e:
            print("Error occurred while fetching the list of tables:")
            print(e)
        
        return tables
    
        
    def readTable(self, table_name:str, db_name:str = None, columns:list = None, geom_col:str = None, v = True):
        if db_name is not None:
            self.connect_db(db_name)

        if columns is not None and geom_col is not None:
            columns.append(f"{geom_col}.STAsText() as {geom_col}_wkt")
            query = f"SELECT {','.join(columns)} FROM {table_name}"
        elif columns is not None:
            query = f"SELECT {','.join(columns)} FROM {table_name}"
        elif geom_col is not None:
            query = f"SELECT *, {geom_col}.STAsText() as {geom_col}_wkt FROM {table_name}"
        else:
            query = f"SELECT * FROM {table_name}"

        # Load as a regular DataFrame
        if v: print(f"> reading table: {table_name} from {self.db_name}")
        df = pandas.read_sql(query, self.connection)

        # Convert WKT column to a GeoPandas geometry column if needed
        if geom_col is not None:
            df[geom_col] = df[geom_col+"_wkt"].apply(wkt.loads)
            df = geopandas.GeoDataFrame(df, geometry=geom_col)
            
        return df
        
    # Function to change the active database
    def connectDB(self, db_name = None, v = True):
        if not self.connection:
            self.connect()
        try:
            self.cursor     = self.connection.cursor()
            self.cursor.execute(f"USE {db_name if not db_name is None else self.db_name}")
            self.db_name    = db_name if not db_name is None else self.db_name
            self.cursor.commit()

            if v: print(f"> changed active database to: {db_name if not db_name is None else self.db_name}")
        except pyodbc.Error as e:
            print("! error occurred while changing the active database:")
            print(e)

    def dataframeToSql(self, df, table_name, if_exists='fail', geom_col='geometry', v = True):
        """
        Write records stored in a DataFrame to a SQL database.
        """
        print(f"> saving data to table: {table_name}...")

        # Create SQLAlchemy engine
        params = urllib.parse.quote_plus(f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.db_name};UID={self.username};PWD={self.password};TrustServerCertificate=yes')
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

        # Check if dataframe is a GeoDataFrame and has a geometry column
        if isinstance(df, geopandas.GeoDataFrame) and geom_col in df.columns:
            # Create a new column for WKT format
            df[geom_col+'_wkt'] = df[geom_col].apply(lambda x: x.wkt)
            
            # Drop the original geometry column
            df = df.drop(columns=[geom_col])
            
            # Write DataFrame to SQL table
            df.to_sql(table_name, engine, if_exists=if_exists, index=False)

            # Create a new connection and cursor
            conn = engine.raw_connection()
            cursor = conn.cursor()

            # Convert the WKT column back to a geometry column in SQL Server
            cursor.execute(f"ALTER TABLE [{table_name}] ADD [{geom_col}] geometry")
            cursor.execute(f"UPDATE [{table_name}] SET [{geom_col}] = geometry::STGeomFromText([{geom_col}_wkt], 4326)")
            
            # Drop the WKT column
            cursor.execute(f"ALTER TABLE [{table_name}] DROP COLUMN [{geom_col}_wkt]")
            
            conn.commit()

            # Close the connection and cursor
            cursor.close()
            conn.close()

        else:
            # If dataframe is not a GeoDataFrame or doesn't have a geometry column, write it to SQL as usual
            df.to_sql(table_name, engine, if_exists=if_exists, index=False)

        if v:
            print(f"> saved data to table: {table_name}...")



    def modifySqlTable(self, df, table_name):
        """
        Replace an existing SQL table with a new one based on a DataFrame.

        Parameters:
        df : DataFrame
        table_name : string
            Name of SQL table
        """
        self.dataframe_to_sql(df, table_name, if_exists='replace')
    
    def dropTable(self, table_name, v = True):
        """
        Drops a table from the database.

        Parameters:
        table_name : string
            Name of SQL table
        """
        
        if not self.connection:
            self.connect()

        # Drop the table
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Commit the transaction
        self.connection.commit()

        if v: print(f"> deleted table {table_name}")

    def deleteTable(self, table_name, v = True):
        self.dropTable(table_name, v = v)

    def close(self, v = True):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
        if v: print("> connection closed...")

    def disconnect(self, v = True):
        self.close(v = v)

