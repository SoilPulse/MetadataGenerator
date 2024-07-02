# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

import mysql.connector
import sqlite3
import unicodedata
import os

from .exceptions import DatabaseFetchError, DatabaseEntryError, NameNotUniqueError

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

    resourcesTableName = "resources"
    userResourcesTableName = "user_resource"
    userTableName = "users"
    containersTableName = "containers"
    datasetsTableName = "datasets"


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

    def getUserNameByID(self, id):
        thecursor = self.db_connection.cursor()
        query = f"SELECT `first_name`, `last_name` FROM `{DBconnector.userTableName}` WHERE `id` = {id}"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            return results[0]
        else:
            return None
    def getResourcesOfUser(self, user_id):
        """
        Loads ResourceManagers' info of a given user from SoilPulse database.
        Call this function to obtain dictionary of ResourceManagers' names and IDs that are owned by user with given user_id

        :param user_id: ID of the user whose ResourceManagers should be loaded
        :return: dictionary of ResourceManagers info {ResourceManager id: ResourceManager name, ...}
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT `{DBconnector.userResourcesTableName}`.`resource_id`, `{DBconnector.resourcesTableName}`.`name` FROM `{DBconnector.userResourcesTableName}` "\
                          f"JOIN `{DBconnector.resourcesTableName}` ON `{DBconnector.resourcesTableName}`.`id` = `{DBconnector.userResourcesTableName}`.`resource_id` "\
                          f"WHERE `{DBconnector.userResourcesTableName}`.`user_id` = {user_id}"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            resources = {}
            for res in results:
                resources.update({res[0]: res[1]})
            return resources
        else:
            return None

    def printUserInfo(self, user_id):
        print("\n" + 70 * "-")
        userinfo = self.getUserNameByID(user_id)
        usersResources = self.getResourcesOfUser(user_id=user_id)
        if usersResources is not None:
            print(f"Saved ResourceManagers of user id = {user_id} ({userinfo[1]}, {userinfo[0]})")
            for rid, rname in usersResources.items():
                print(f"\t{rid}: {rname}")
        else:
            print(f"User id = {user_id} ({userinfo[1]}, {userinfo[0]}) has no saved Resource project.")
        print(70 * "-" + "\n")

    def saveResourceManager(self, user_id, name=None, doi=None, unique_names=True):
        thecursor = self.db_connection.cursor()

        # if no name was provided create one
        if name is None:
            thecursor.execute(f"SELECT AUTO_INCREMENT FROM information_schema.tables"
                              f"WHERE table_name = '{DBconnector.resourcesTableName}'")
            results = thecursor.fetchall()

            if thecursor.rowcount > 0:
                for nextID in results:
                    print(f"next resource id will be: {nextID}")
                    name = f"Unnamed resource {nextID}"

        usersResources = self.getResourcesOfUser(user_id)
        if usersResources is not None:
            if name in self.getResourcesOfUser(user_id).values():
                if unique_names:
                    raise NameNotUniqueError(name)
                print(f"ResourceManager with name \"{name}\" will be overwritten.")

        # insert line to `resource` table
        # execute the query
        query = f"INSERT INTO `{DBconnector.resourcesTableName}` (`name`, `doi`) VALUES (%s, %s)"
        values = [name, doi]
        thecursor.execute(query, values)
        # insert queries must be committed
        self.db_connection.commit()
        # get and return the ID of newly created ResourceManager record
        thecursor.execute("SELECT LAST_INSERT_ID()")
        results = thecursor.fetchall()
        for nid in results:
            resource_id = nid[0]

        # insert line to `user_resource` table
        query = f"INSERT INTO `{DBconnector.userResourcesTableName}` (`user_id`, `resource_id`) VALUES (%s, %s)"
        values = [user_id, resource_id]
        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return resource_id

    def updateResourceManager(self, rm):
        """
        Updates database record of ResourceManager and all of its contents

        :param rm: the ResourceManager instance reference to be saved
        """

        thecursor = self.db_connection.cursor()
        # check for name duplicity
        query = f"SELECT COUNT(*) FROM `{DBconnector.resourcesTableName}` " \
                f"JOIN `{DBconnector.userResourcesTableName}` ON `{DBconnector.resourcesTableName}`.`id` = `{DBconnector.userResourcesTableName}`.`resource_id` " \
                f"WHERE `{DBconnector.userResourcesTableName}`.`user_id`  = {rm.ownerID} " \
                f"AND `{DBconnector.resourcesTableName}`.`id` <> %s " \
                f"AND `{DBconnector.resourcesTableName}`.`name` = %s"
        thecursor.execute(query, [rm.id, rm.name])

        count = thecursor.fetchone()[0]
        if count > 0:
            raise NameNotUniqueError(rm.name)

        newValues = {"name": rm.name, "doi": rm.getDOI(), "files_stored": rm.keepFiles}

        thecursor.reset()
        query = f"UPDATE `{DBconnector.resourcesTableName}` SET "
        query += ", ".join([f"`{key}` = %s" for key in newValues.keys()])
        query += " WHERE `id` = %s"

        values = list(newValues.values())
        values.append(rm.id)

        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return

    def loadResourceManager(self, id):
        pass

    def deleteResourceManager(self, id):
        pass

    def containerRecordExists(self, cont_id, res_id):
        """
        Checksk if container with provided local ID (Resourcemanager scope) and ResourceManager ID already has database entry

        :param cont_id: local container ID
        :param res_id: ID of resource manager the container belongs to
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT COUNT(*) FROM `{DBconnector.containersTableName}` " \
                f"WHERE `{DBconnector.containersTableName}`.`id_local` = %s " \
                f"AND `{DBconnector.containersTableName}`.`resource_id` = %s"
        values = [cont_id, res_id]
        thecursor.execute(query, values)

        count = thecursor.fetchone()[0]
        if count == 0:
            return False
        elif count == 1:
            return True
        else:
            raise DatabaseEntryError(f"More then one ({count}) occurrence of a local container ID {cont_id} within a ResourceManager ID {res_id}.")

    def updateContainer(self, container):
        thecursor = self.db_connection.cursor()

        if hasattr(container, "path"):
            path = container.path
        else:
            path = None
        pContID = container.parentContainer.id if container.parentContainer is not None else None
        arglist = {"name": container.name, "parent_id_local": pContID, "path": path}

        # update properties if the container already exists
        if self.containerRecordExists(container.id, container.resourceManager.id):
            query = f"UPDATE `{DBconnector.containersTableName}` SET "
            query += ", ".join([f"`{key}` = %s" for key in arglist.keys()])
            query += " WHERE `id_local` = %s AND resource_id = %s"

            values = list(arglist.values())
            values.append(container.id, container.resourceManager.id)

        # insert new record if not yet in DB
        else:
            arglist.update({"id_local": container.id, "resource_id": container.resourceManager.id})

            query = f"INSERT INTO `{DBconnector.containersTableName}` ("
            query += ", ".join([f"`{key}`" for key in arglist])
            query += f") VALUES ("
            query += ", ".join(["%s" for key in arglist])+")"

            values = list(arglist.values())

        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return

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
        except sqlite3.OperationalError as e:
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
        except sqlite3.OperationalError as e:
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


