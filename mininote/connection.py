# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
import os



dbtype = 'sqlite'
dbname = 'piconote'

if dbtype == 'sqlite':
    path = os.path.dirname(__file__)
    sqliteFile = os.path.join(path,dbname + '.db') 
    connection_string = 'sqlite:///'+sqliteFile.replace("\\","/") 
elif dbtype == 'mysql': 
    connection_string = 'mysql+mysqlconnector://user:password@127.0.0.1:3306/piconote'

    



def CreateEngine(url, echo = False):
    """
    Creates a database engine
    """
    return create_engine(url, echo = echo)


def DropDatabase(url, echo = False):
    """
    engine is required if dbtype is not sqlite
    """

    if url.lower().startswith('sqlite'): 
        sqliteFile = url.partition(':///')[-1]
        if os.path.exists(sqliteFile):
            print('Deleting sqlite piconote db - path = {0}'.format(sqliteFile))
            os.remove(sqliteFile)

    else:
        print('Dropping mysql piconote db')
        try:
            server_string = url.rpartition('/')[0] #pulls the database name off the end of the string
            engine = CreateEngine(server_string, echo = False)
            conn = engine.connect()
            conn.execute("drop database if exists piconote")
            conn.execute("commit")
            conn.close()
        except: 
            #data base does not exist
            pass


def CreateDatabase(url, echo = False):
    """
    engine is required if dbtype is not sqlite
    """
    print('Creating database')
    if not url.lower().startswith('sqlite'): 
        server_string = url.rpartition('/')[0]
        engine = CreateEngine(server_string, echo=echo)
        conn = engine.connect()
        conn.execute("create database if not exists piconote")
        conn.execute("use piconote")
        conn.execute("commit")
        conn.close()

    engine = CreateEngine(url, echo=echo)
    return engine
    
if __name__ == "__main__":

    DropDatabase(connection_string, echo_sql)
    engine = CreateDatabase(connection_string, echo_sql)

