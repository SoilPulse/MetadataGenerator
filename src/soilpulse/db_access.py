# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

import mysql.connector
from .exceptions import DatabaseFetchError

class DBconnector:
    """
    Provides methods to access and manipulate the SoilPulse database storage
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
            return
        return None

    def loadKeywords(self, entityID):
        """
        Loads search strings stored in the DB for given entityID (string ID from metadata scheme definition)
        """
        # get the cursor for current connection
        thecursor = self.db_connection.cursor()
        # execute the query and fetch the results
        thecursor.execute("SELECT `string_name`, `search_string` FROM `entity_keywords` WHERE `entity_id` = '{}'".format(entityID))
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            keywords = {}
            for ss in results:
                keywords.update({ss[0]: ss[1]})
            return keywords
        else:
            raise DatabaseFetchError("No search strings found for entity_id = '{}'".format(entityID))
        return None
