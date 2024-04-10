# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

import mysql.connector
import sqlite3
import unicodedata
import os

from .exceptions import DatabaseFetchError

class DBconnector:
    """
    Provides methods to access and manipulate the SoilPulse database storage of MetadataMappings and possibly the data storage as well
    """
    # server to connect to
    server = "localhost"
    # database name to use
    db_name = "soilpulse"
    # username for the db access
    username = "soilpulse"
    # password of the user
    pwd = "NFDI4earth"

    def __init__(self):
        try:
            self.db_connection = mysql.connector.connect(
                host = DBconnector.server,
                user = DBconnector.username,
                password = DBconnector.pwd,
                database = DBconnector.db_name
            )
        except mysql.connector.errors.InterfaceError as e:
            print("The SoilPulse database server is not accessible:")
            print(e)
        except mysql.connector.errors.ProgrammingError as e:
            print("Provided user credentials or database name seem to be invalid:")
            print(e)
        else:
            # print ("successfully connected to SoilPulse database")
            pass


    def loadSearchPatterns(self, entity):
        """
        Loads search patterns stored in the DB for given entityID (string ID from metadata scheme definition).
        Returns dictionary

        :param entity: MetadataEntity subclass

        :return: dictionary of regular expression patterns with group names {unique group name: search pattern, ...}
        """
        # get the cursor for current connection
        thecursor = self.db_connection.cursor()
        # execute the query and fetch the results
        thecursor.execute("SELECT `group_name`, `search_pattern` FROM `search_patterns` WHERE `entity_id` = '{}'".format(entity.ID))
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            patterns = {}
            for ss in results:
                patterns.update({entity.key+"_"+ss[0]: str(ss[1])})
            return patterns
        else:
            raise DatabaseFetchError("No search strings found for entity_id = '{}'".format(entity.ID))
        return None

class EntitySearchPatternsDB:
    """
    Provides methods to access and manipulate the SoilPulse metadata entity types and their properties stored in the DB "entities"
    """
    dbpath = "soilpulse\databases\entity_search_patterns"

    def __init__(self):
        pass

    @classmethod
    def connect(self):
        try:
            connection = sqlite3.connect(EntitySearchPatternsDB.dbpath)
        except sqlite3.CantOpenError as e:
            print("The SoilPulse 'entity_search_patterns' database file is not accessible:")
            print(e)
            return None
        else:
            # print ("successfully connected to SoilPulse database")
            return connection

    @classmethod
    def loadSearchPatterns(cls, entityClass):
        """
        Loads search patterns stored in the DB for given entityID (string ID from metadata scheme definition).
        Returns dictionary

        :param entityClass: MetadataEntity subclass

        :return: dictionary of regular expression patterns with group names {unique group name: search pattern, ...}
        """
        # get the cursor for current connection
        with cls.connect() as conn:
            thecursor = conn.cursor()
            # execute the query and fetch the results
            query = "select group_name, search_pattern from search_patterns where entity_id = '{}'".format(entityClass.ID)
            thecursor.execute(query)
            results = thecursor.fetchall()
            if len(results) > 0:
                patterns = {}
                for pat in results:
                    patterns.update({entityClass.key+"_"+pat[0]: str(pat[1])})
                return patterns
            else:
                # raise DatabaseFetchError("No search strings found for entity_id = '{}' ({})".format(entity.ID, entity.name))
                return None
        return None

class EntityKeywordsDB:
    """
    Provides methods to access and manipulate the SoilPulse metadata entity keywords.

    """
    dbDir = "soilpulse\databases"
    # dictionary of keywords databases by type {type: full path to DB}
    DBs = {}

    def __init__(self):
        print("\nEntityKeywords instance created.")
        print(f"DB directory: {EntityKeywordsDB.dbDir}")
        print(f"currently registered DBs: {EntityKeywordsDB.DBs}\n")
        pass

    @classmethod
    def connect(cls, dbpath):
        try:
            connection = sqlite3.connect(dbpath)
        except sqlite3.CantOpenError as e:
            print("The SoilPulse '{}' database file is not accessible:".format(dbpath))
            print(e)
            return None
        else:
            # print ("successfully connected to SoilPulse database")
            return connection

    @classmethod
    def registerKeywordsDB(cls, dbType, dbFilename):
        cls.DBs.update({dbType: os.path.join(cls.dbDir, dbFilename)})
        print("Keywords database {} registered as '{}'".format(os.path.join(cls.dbDir, dbFilename), dbType))
        print(EntityKeywordsDB.DBs)
        return

    @classmethod
    def loadKeywords(cls, entityClass):
        """
        Loads entity's keywords from DB and translates them into RE search patterns.
        Here the translation of the keywords by some thesaurus is possible ...

        :param entity: MetadataEntity subclass

        :return: dictionary of regular expression patterns with group names {unique group name: search pattern, ...}
        """
        keywords = {}

        for type, dbpath in cls.DBs.items():
            print("loading keywords from file: {}".format(dbpath))
            # get the cursor for current connection
            with cls.connect(dbpath) as conn:
                thecursor = conn.cursor()
                # execute the query and fetch the results
                query = "select keywords from keywords where entity_id = '{}'".format(entityClass.ID)
                thecursor.execute(query)
                results = thecursor.fetchall()
                if len(results) > 0:
                    typeKeywords = {}
                    for kw in results:
                        for w in kw[0].split(";"):
                            # convert any keyword into ascii for search pattern group name
                            w_ascii =str(unicodedata.normalize('NFD', w.strip()).encode('ascii', 'ignore'), "ascii")
                            typeKeywords.update({entityClass.key+"_kw_"+w_ascii: w.strip()})
                else:
                    # raise DatabaseFetchError("No keywords found for entity_id = '{}' ({})".format(entity.ID, entity.name))
                    typeKeywords = None
            keywords.update({type: typeKeywords})
        return  keywords