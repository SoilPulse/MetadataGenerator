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

    def __init__(self):
        # file with the DB
        # self.dbfile = "soilpulse\databases\entity_types"
        self.dbfile = "soilpulse\databases\entity_search_patterns"
    def connect(self):
        try:
            connection = sqlite3.connect(self.dbfile)
        except sqlite3.CantOpenError as e:
            print("The SoilPulse 'entity_search_patterns' database file is not accessible:")
            print(e)
            return None
        else:
            # print ("successfully connected to SoilPulse database")
            return connection

    def loadSearchPatterns(self, entity):
        """
        Loads search patterns stored in the DB for given entityID (string ID from metadata scheme definition).
        Returns dictionary

        :param entity: MetadataEntity subclass

        :return: dictionary of regular expression patterns with group names {unique group name: search pattern, ...}
        """
        # get the cursor for current connection
        with self.connect() as conn:
            thecursor = conn.cursor()
            # execute the query and fetch the results
            query = "select group_name, search_pattern from search_patterns where entity_id = '{}'".format(entity.ID)
            thecursor.execute(query)
            results = thecursor.fetchall()
            if len(results) > 0:
                patterns = {}
                for pat in results:
                    patterns.update({entity.key+"_"+pat[0]: str(pat[1])})
                return patterns
            else:
                # raise DatabaseFetchError("No search strings found for entity_id = '{}' ({})".format(entity.ID, entity.name))
                return None
        return None
class EntityKeywordsDB:
    """
    Provides methods to access and manipulate the SoilPulse metadata entity types and their properties stored in the DB "entities"
    """

    def __init__(self, db_filename):
        # file with the DB
        # self.dbfile = "soilpulse\databases\entity_types"
        self.dbDir = "soilpulse\databases"
        self.dbpath = os.path.join(self.dbDir, db_filename)
    def connect(self):
        try:
            connection = sqlite3.connect(self.dbpath)
        except sqlite3.CantOpenError as e:
            print("The SoilPulse '{}' database file is not accessible:".format(self.dbpath))
            print(e)
            return None
        else:
            # print ("successfully connected to SoilPulse database")
            return connection

    def loadKeywords(self, entity):
        """
        Loads entity's keywords from DB and translates them into RE search patterns.
        Here the translation of the keywords by some thesaurus is possible ...

        :param entity: MetadataEntity subclass

        :return: dictionary of regular expression patterns with group names {unique group name: search pattern, ...}
        """
        # get the cursor for current connection
        with self.connect() as conn:
            thecursor = conn.cursor()
            # execute the query and fetch the results
            query = "select keywords from keywords where entity_id = '{}'".format(entity.ID)
            thecursor.execute(query)
            results = thecursor.fetchall()
            if len(results) > 0:
                keywords = {}
                for kw in results:
                    for w in kw[0].split(";"):
                        # convert any keyword into ascii for search pattern group name
                        w_ascii =str(unicodedata.normalize('NFD', w.strip()).encode('ascii', 'ignore'), "ascii")
                        keywords.update({entity.key+"_kw_"+w_ascii: w.strip()})
                return keywords
            else:
                # raise DatabaseFetchError("No keywords found for entity_id = '{}' ({})".format(entity.ID, entity.name))
                return None