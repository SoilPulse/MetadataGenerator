# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

import mysql.connector
import sqlite3
import unicodedata
import os
import re

from .exceptions import DatabaseFetchError, DatabaseEntryError, NameNotUniqueError


def generate_project_unique_name(existing_names, name):
    """
    Generates a unique name for a user's project by appending a number in parentheses if the name already exists.

    :param existing_names: list of currently existing names in database
    :param name: the original name to check and modify if necessary.
    :return: a unique name
    """
    if name not in existing_names:
        return name

    # Regular expression to match names ending with " (number)"
    pattern = re.compile(r'^(.*?)(?: \((\d+)\))?$')

    match = pattern.match(name)
    base_name = match.group(1)
    count = int(match.group(2)) if match.group(2) else 1

    # generate new names until a unique one is found
    new_name = f"{base_name} ({count})"
    while new_name in existing_names:
        count += 1
        new_name = f"{base_name} ({count})"

    return new_name

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

    projectsTableName = "`projects`"
    userProjectsTableName = "`user_projects`"
    userTableName = "`users`"
    containersTableName = "`containers`"
    datasetsTableName = "`datasets`"


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

    def __del__(self):
        self.db_connection.close()

    def getUserNameByID(self, id):
        thecursor = self.db_connection.cursor()
        query = f"SELECT `first_name`, `last_name` FROM {DBconnector.userTableName} WHERE `id` = {id}"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            return results[0]
        else:
            return None
    def getProjectsOfUser(self, user_id):
        """
        Loads Projects info of a given user from SoilPulse database.
        Call this function to obtain dictionary of Project names and IDs that are owned by user with given user_id

        :param user_id: ID of the user whose Projects should be loaded
        :return: dictionary of ProjectManagers info {Project id: Project name, ...}
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT {DBconnector.userProjectsTableName}.`project_id`, {DBconnector.projectsTableName}.`name` FROM {DBconnector.userProjectsTableName} "\
              f"JOIN {DBconnector.projectsTableName} ON {DBconnector.projectsTableName}.`id` = {DBconnector.userProjectsTableName}.`project_id` "\
              f"WHERE {DBconnector.userProjectsTableName}.`user_id` = {user_id}"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            projects = {}
            for res in results:
                projects.update({res[0]: res[1]})
            return projects
        else:
            return None

    def getDatasetsOfProject(self, project_id):
        """
        Loads Dataset info of a given project ID from SoilPulse database.
        Call this function to obtain list of dataset names within a project

        :param project_id: ID of the Project whose Datasets should be loaded
        :return: list of dataset names [ID, ... ]
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT `name` FROM {DBconnector.datasetsTableName} "\
              f"WHERE `project_id` = {project_id}"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            projects = {}
            for res in results:
                projects.update({res[0]: res[1]})
            return projects
        else:
            return None

    def printUserInfo(self, user_id):
        print("\n" + 70 * "-")
        userinfo = self.getUserNameByID(user_id)
        usersProjects = self.getProjectsOfUser(user_id=user_id)
        if usersProjects is not None:
            print(f"Saved project of user id = {user_id} ({userinfo[1]}, {userinfo[0]})")
            for rid, rname in usersProjects.items():
                print(f"\t{rid}: {rname}")
        else:
            print(f"User id = {user_id} ({userinfo[1]}, {userinfo[0]}) has no saved project.")
        print(70 * "-" + "\n")

    def establishProjectRecord(self, user_id, prj, unique_names=True):
        thecursor = self.db_connection.cursor()

        # if no name was provided create one
        if prj.name is None or prj.name == "":
            thecursor.execute(f"SELECT AUTO_INCREMENT FROM information_schema.tables "
                              f"WHERE table_name = '{DBconnector.projectsTableName}'")
            results = thecursor.fetchall()

            if thecursor.rowcount > 0:
                for nextID in results:
                    print(f"next project id will be: {nextID[0]}")
                    prj.name = f"Unnamed project {nextID[0]}"

        usersProjects = self.getProjectsOfUser(user_id)
        if usersProjects is not None:
            if prj.name in usersProjects.values() and unique_names:
                print(f"Project with name \"{prj.name}\" already exists.")
                prj.name = generate_project_unique_name(usersProjects.values(), prj.name)
                print(f"The name was modified to \"{prj.name}\" and can be changed later.")

        # insert line to `projects` table
        # execute the query
        query = f"INSERT INTO {DBconnector.projectsTableName} (`name`, `doi`) VALUES (%s, %s)"
        values = [prj.name, prj.doi]
        thecursor.execute(query, values)
        # insert queries must be committed
        self.db_connection.commit()
        # get and return the ID of newly created ProjectManager record
        thecursor.execute("SELECT LAST_INSERT_ID()")
        results = thecursor.fetchall()
        for nid in results:
            prj.id = nid[0]

        # insert line to `user_projects` table
        query = f"INSERT INTO {DBconnector.userProjectsTableName} (`user_id`, `project_id`) VALUES (%s, %s)"
        values = [user_id, prj.id]
        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return prj.id

    def updateProjectRecord(self, prj):
        """
        Updates database record of a Project and all of its contents

        :param prj: the Project instance reference to be saved
        """
        # default is that the name is updated as well
        update_name = True
        # but will be not updated if empty
        if prj.name is None or prj.name == "":
            print(f"Project name can't be empty.")
            update_name = False

        # or when duplicit with another project name of the same user
        thecursor = self.db_connection.cursor()
        # check for name duplicity
        query = f"SELECT COUNT(*) FROM {DBconnector.projectsTableName} " \
                f"JOIN {DBconnector.userProjectsTableName} ON {DBconnector.projectsTableName}.`id` = {DBconnector.userProjectsTableName}.`project_id` " \
                f"WHERE {DBconnector.userProjectsTableName}.`user_id`  = {prj.ownerID} " \
                f"AND {DBconnector.projectsTableName}.`id` <> %s " \
                f"AND {DBconnector.projectsTableName}.`name` = %s"
        thecursor.execute(query, [prj.id, prj.name])

        count = thecursor.fetchone()[0]
        if count > 0:
            update_name = False

        newValues = {"doi": prj.getDOI(), "temp_dir": prj.temp_dir, "keep_files": (1 if prj.keepFiles else 0)}
        if update_name:
            newValues.update({"name": prj.name})

        thecursor.reset()
        query = f"UPDATE {DBconnector.projectsTableName} SET "
        query += ", ".join([f"`{key}` = %s" for key in newValues.keys()])
        query += " WHERE `id` = %s"

        values = list(newValues.values())
        values.append(prj.id)

        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return

    def loadProject(self, project, cascade=True):
        """
        Loads database record of Project and all of its contents if cascade == True

        :param project: the Project instance to be loaded from DB
        :param cascade: whether to load all contents
        :return: instance of the input Project with filled attributes
        """

        thecursor = self.db_connection.cursor(dictionary=True)

        query = f"SELECT * FROM {DBconnector.projectsTableName} WHERE `id` = {project.id}"
        print(query)

        thecursor.execute(query)
        result = thecursor.fetchone()
        thecursor.close()
        if result is None:
            raise DatabaseFetchError(f"No record found in saved projects for given ID {project.id}")
        else:
            project.name = result["name"]
            project.temp_dir = result["temp_dir"]

            if result["keep_files"] == 0:
                project.keepFiles = False
            else:
                project.keepFiles = True

            if cascade:
                project.containerTree = self.loadChildContainers(project, parent_container=None)

        return

    def loadChildContainers(self, project, parent_container=None):
        out_container_list = []
        thecursor = self.db_connection.cursor(dictionary=True)

        query = f"SELECT * FROM {DBconnector.containersTableName} " \
                f"WHERE `project_id` = {project.id}"
        query += f" AND `parent_id_local` IS NULL" if parent_container is None else f" AND `parent_id_local` = {parent_container.id}"

        thecursor.execute(query)
        results = thecursor.fetchall()
        thecursor.close()

        if len(results) > 0:
            for cont in results:
                # replace the global id from DB by project scope 'id_local'
                del(cont["id"])
                cont.update({"id": cont.pop("id_local")})
                # delete properties that are being handled different ways
                del (cont["parent_id_local"])
                del (cont["project_id"])
                # replace relative path stored in DB by absolute path needed for proper container creation in factory
                rel_path = cont.pop("relative_path")
                print(rel_path)
                abs_path = os.path.join(project.temp_dir, rel_path) if rel_path is not None else None
                print(abs_path)
                cont.update({"path": abs_path})
                cont_type = cont.get("type")

                newCont = project.containerFactory.createHandler(cont_type, project, parent_container, cascade=False, **cont)

                out_container_list.append(newCont)
                newCont.containers = self.loadChildContainers(project, newCont)

            thecursor.close()

        return out_container_list



    def deleteProject(self, id):
        pass

    def containerRecordExists(self, cont_id, project_id):
        """
        Checks if container with provided local ID (Project scope) and Project ID already has database entry

        :param cont_id: local container ID
        :param project_id: ID of project the container belongs to
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT COUNT(*) FROM {DBconnector.containersTableName} " \
                f"WHERE `id_local` = %s " \
                f"AND `project_id` = %s"
        values = [cont_id, project_id]
        thecursor.execute(query, values)

        count = thecursor.fetchone()[0]
        if count == 0:
            return False
        elif count == 1:
            return True
        else:
            raise DatabaseEntryError(f"More then one ({count}) occurrence of a local container ID {cont_id} within a Project ID {project_id}.")

    def datasetRecordExists(self, name, project_id):
        """
        Checks if dataset with provided name and Project ID already has database entry

        :param name: dataset name
        :param project_id: ID of project the container belongs to
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT COUNT(*) FROM {DBconnector.datasetsTableName} " \
                f"WHERE `name` = %s " \
                f"AND `project_id` = %s"
        values = [name, project_id]
        thecursor.execute(query, values)

        count = thecursor.fetchone()[0]
        if count == 0:
            return False
        elif count == 1:
            return True
        else:
            raise DatabaseEntryError(
                f"More then one ({count}) occurrence of dataset '{name}' within a project ID {project_id}.")

    def updateContainerRecord(self, container):
        thecursor = self.db_connection.cursor()

        # set the general core of properties to be stored
        arglist = {"type": container.containerType, "name": container.name, "parent_id_local": container.parentContainer.id if container.parentContainer is not None else None}
        # add container subclass specific properties to be stored
        for db_key, attr_key in container.serializationDict.items():
            arglist.update({db_key: str(getattr(container, attr_key))})

        # update properties if the container already exists
        if self.containerRecordExists(container.id, container.project.id):
            query = f"UPDATE {DBconnector.containersTableName} SET "
            query += ", ".join([f"`{key}` = %s" for key in arglist.keys()])
            query += " WHERE `id_local` = %s AND project_id = %s"

            values = list(arglist.values())
            values.extend([container.id, container.project.id])

        # insert new record if not yet in DB
        else:
            arglist.update({"id_local": container.id, "project_id": container.project.id})

            query = f"INSERT INTO {DBconnector.containersTableName} ("
            query += ", ".join([f"`{key}`" for key in arglist])
            query += f") VALUES ("
            query += ", ".join(["%s" for key in arglist])+")"

            values = list(arglist.values())

        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return

    def updateDatasetRecord(self, dataset):

        thecursor = self.db_connection.cursor()
        idListString =  "|".join([str(cid) for cid in dataset.getContainerIDsList()])
        arglist = {"name": dataset.name, "project_id": dataset.project.id, "container_ids": idListString}

        # update properties if the container already exists
        if self.containerRecordExists(dataset.name, dataset.project.id):
            query = f"UPDATE {DBconnector.datasetsTableName} SET "
            query += ", ".join([f"`{key}` = %s" for key in arglist.keys()])
            query += " WHERE `id_local` = %s AND project_id = %s"

            values = list(arglist.values())
            values.extend([dataset.id, dataset.project.id])

        # insert new record if not yet in DB
        else:
            arglist.update({"name": dataset.name, "project_id": dataset.project.id})

            query = f"INSERT INTO {DBconnector.datasetsTableName} ("
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
            query = f"select group_name, search_pattern from search_patterns where entity_id = '{entityClass.ID}'"
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


