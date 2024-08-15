# -*- coding: utf-8 -*-
"""
@author: Jan Devátý, Jonas Lenz
"""

import json
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

    dirname_prefix = None

    @classmethod
    def get_connector(cls, project_files_root):
        try:
            return MySQLConnector(project_files_root)
        except Exception:
            print("\nSoilPulse MySQL database instance couldn't be reached.\nFalling back to local filesystem.")
            return NullConnector(project_files_root)

    def __init__(self, project_files_root):
        self.project_files_root = project_files_root

    def getNewProjectID(self):
        """
        Finds a correct ID that should be assigned to next new project.
        """
        pass
    def getUserNameByID(self, id):
        pass
    def getProjectsOfUser(self, user_id):
        pass

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
        return

    def establishProjectRecord(self, user_id, project, unique_names=True):
        pass

    def updateProjectRecord(self, project):
        pass

    def loadProject(self, project):
        pass

    def deleteProjectRecord(self, project, delete_dir):
        pass

    def _create_project_directory(self, project_id, prefix=""):
        dir_name = f"{prefix}{project_id}"
        project_dir = os.path.join(self.project_files_root, dir_name)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    def getDatasetsOfProject(self, project_id):
        pass

class MySQLConnector(DBconnector):
    """
    Provides methods to access and manipulate the SoilPulse database storage of MetadataMappings and possibly the data storage as well
    """
    dirname_prefix = ""

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


    def __init__(self, project_files_root):
        super().__init__(project_files_root)
        print("\nconnecting to MySQL ...")

        try:
            self.db_connection = mysql.connector.connect(
                host = self.server,
                user = self.username,
                password = self.pwd,
                database = self.db_name
            )
        except mysql.connector.errors.InterfaceError as e:
            print("The SoilPulse database server is not accessible:")
            print(e)
            raise
        except mysql.connector.errors.ProgrammingError as e:
            print("Provided user credentials or database name seem to be invalid:")
            print(e)
            raise
        else:
            print ("successfully connected to SoilPulse MySQL database\n")
            pass

    def __del__(self):
        pass

    def getUserNameByID(self, id):
        thecursor = self.db_connection.cursor()
        query = f"SELECT `first_name`, `last_name` FROM {self.userTableName} WHERE `id` = {id}"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            return results[0]
        else:
            return None

    def checkoutUser(self, user_id):
        thecursor = self.db_connection.cursor()
        query = f"SELECT `id` FROM {self.userTableName}"
        thecursor.execute(query)
        results = thecursor.fetchall()
        all_user_ids = []
        if thecursor.rowcount > 0:
            for res in results:
                all_user_ids.append(res[0])
            if user_id in all_user_ids:
                return user_id
            return None
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
        query = f"SELECT {self.userProjectsTableName}.`project_id`, {self.projectsTableName}.`name` FROM {self.userProjectsTableName} "\
              f"JOIN {self.projectsTableName} ON {self.projectsTableName}.`id` = {self.userProjectsTableName}.`project_id` "\
              f"WHERE {self.userProjectsTableName}.`user_id` = {user_id}"
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
        query = f"SELECT `name` FROM {self.datasetsTableName} "\
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

    def getNewProjectID(self):
        thecursor = self.db_connection.cursor()
        thecursor.execute(f"SELECT AUTO_INCREMENT FROM information_schema.tables "
                          f"WHERE table_name = '{self.projectsTableName}'")
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            for nextID in results:
                return nextID[0]

    def establishProjectRecord(self, user_id, project, unique_names=True):
        thecursor = self.db_connection.cursor()

        newID = self.getNewProjectID()
        # if no name was provided create one
        if project.name is None or project.name == "":
            print(f"next project id will be: {newID}")
            project.name = f"Unnamed project {newID}"

        usersProjects = self.getProjectsOfUser(user_id)
        if usersProjects is not None:
            if project.name in usersProjects.values() and unique_names:
                print(f"Project with name \"{project.name}\" already exists.")
                project.name = generate_project_unique_name(usersProjects.values(), project.name)
                print(f"The name was modified to \"{project.name}\" and can be changed later.")

        # insert line to `projects` table
        # execute the query
        query = f"INSERT INTO {self.projectsTableName} (`name`, `doi`) VALUES (%s, %s)"
        values = [project.name, project.doi]
        thecursor.execute(query, values)
        # insert queries must be committed
        self.db_connection.commit()
        # get and return the ID of newly created ProjectManager record
        thecursor.execute("SELECT LAST_INSERT_ID()")
        results = thecursor.fetchall()
        # assign the DB ID to Project instance
        for nid in results:
            project.id = nid[0]
        # assign the project files directory path
        project.temp_dir = os.path.join(self.project_files_root, str(project.id))
        # insert line to `user_projects` table
        query = f"INSERT INTO {self.userProjectsTableName} (`user_id`, `project_id`) VALUES (%s, %s)"
        values = [user_id, project.id]
        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return project.id

    def updateProjectRecord(self, project):
        """
        Updates database record of a Project and all of its contents

        :param prj: the Project instance reference to be saved
        """
        # default is that the name is updated as well
        update_name = True
        # but will be not updated if empty
        if project.name is None or project.name == "":
            print(f"Project name can't be empty.")
            update_name = False

        # or when duplicit with another project name of the same user
        thecursor = self.db_connection.cursor()
        # check for name duplicity
        query = f"SELECT COUNT(*) FROM {self.projectsTableName} " \
                f"JOIN {self.userProjectsTableName} ON {self.projectsTableName}.`id` = {self.userProjectsTableName}.`project_id` " \
                f"WHERE {self.userProjectsTableName}.`user_id`  = {project.ownerID} " \
                f"AND {self.projectsTableName}.`id` <> %s " \
                f"AND {self.projectsTableName}.`name` = %s"
        thecursor.execute(query, [project.id, project.name])

        count = thecursor.fetchone()[0]
        if count > 0:
            update_name = False

        newValues = {"doi": project.getDOI(), "temp_dir": project.temp_dir, "keep_files": (1 if project.keepFiles else 0)}
        if update_name:
            newValues.update({"name": project.name})

        thecursor.reset()
        query = f"UPDATE {self.projectsTableName} SET "
        query += ", ".join([f"`{key}` = %s" for key in newValues.keys()])
        query += " WHERE `id` = %s"

        values = list(newValues.values())
        values.append(project.id)

        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()
        return

    def loadProject(self, project, cascade=True):
        """
        Loads database record of Project and all of its contents if cascade == True

        :param project: the Project instance to be loaded from DB
        :param cascade: whether to load all contents
        :return: input Project instance with filled attributes
        """

        thecursor = self.db_connection.cursor(dictionary=True)

        query = f"SELECT * FROM {self.projectsTableName} WHERE `id` = {project.id}"
        thecursor.execute(query)
        result = thecursor.fetchone()
        thecursor.close()
        if result is None:
            raise DatabaseFetchError(f"Project ID {project.id} does not exist within MySQL database.")
        else:
            project.name = result["name"]
            project.doi = result["doi"]
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

        query = f"SELECT * FROM {self.containersTableName} " \
                f"WHERE `project_id` = {project.id}"
        query += f" AND `parent_id_local` IS NULL" if parent_container is None else f" AND `parent_id_local` = {parent_container.id}"

        thecursor.execute(query)
        results = thecursor.fetchall()
        thecursor.close()

        if len(results) > 0:
            for cont_args in results:
                ## general properties common for all container types
                # replace the global id from DB by project scope 'id_local'
                del(cont_args["id"])
                cont_args.update({"id": cont_args.pop("id_local")})
                # delete properties that are being handled different ways
                del (cont_args["parent_id_local"])
                del (cont_args["project_id"])

                ## type-specific attributes handling
                # replace relative path stored in DB by absolute path needed for proper container creation in factory
                rel_path = cont_args.pop("relative_path")
                # the "NULL" value from DB is returned as string "None" ...
                rel_path = None if rel_path == "None" else rel_path

                if rel_path is None:
                    abs_path = None
                else:
                    abs_path = os.path.join(project.temp_dir, rel_path)

                cont_args.update({"path": abs_path})
                cont_type = cont_args.get("type")

                newCont = project.containerFactory.createHandler(cont_type, project, parent_container, cascade=False, **cont_args)

                out_container_list.append(newCont)
                newCont.containers = self.loadChildContainers(project, newCont)

            thecursor.close()

        return out_container_list


    def deleteProject(self, project, delete_dir=True):
        cursor = self.db_connection.cursor()
        query = "DELETE FROM projects WHERE id = %s"
        cursor.execute(query, project.id)
        self.db_connection.commit()
        cursor.close()

        # Optionally delete the project directory
        if delete_dir:
            if os.path.exists(project.temp_dir):
                os.rmdir(project.temp_dir)
        return

    def containerRecordExists(self, cont_id, project_id):
        """
        Checks if container with provided local ID (Project scope) and Project ID already has database entry

        :param cont_id: local container ID
        :param project_id: ID of project the container belongs to
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT COUNT(*) FROM {self.containersTableName} " \
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
        query = f"SELECT COUNT(*) FROM {self.datasetsTableName} " \
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
            query = f"UPDATE {self.containersTableName} SET "
            query += ", ".join([f"`{key}` = %s" for key in arglist.keys()])
            query += " WHERE `id_local` = %s AND project_id = %s"

            values = list(arglist.values())
            values.extend([container.id, container.project.id])

        # insert new record if not yet in DB
        else:
            arglist.update({"id_local": container.id, "project_id": container.project.id})

            query = f"INSERT INTO {self.containersTableName} ("
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
            query = f"UPDATE {self.datasetsTableName} SET "
            query += ", ".join([f"`{key}` = %s" for key in arglist.keys()])
            query += " WHERE `id_local` = %s AND project_id = %s"

            values = list(arglist.values())
            values.extend([dataset.id, dataset.project.id])

        # insert new record if not yet in DB
        else:
            arglist.update({"name": dataset.name, "project_id": dataset.project.id})

            query = f"INSERT INTO {self.datasetsTableName} ("
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

class NullConnector(DBconnector):
    dirname_prefix = "temp_"
    project_attr_filename = "_project.json"
    containers_attr_filename = "_containers.json"
    datasets_attr_filename = "_datasets.json"

    def __init__(self, project_files_root):
        super().__init__(project_files_root)

    def getUserNameByID(self, user_id):
        return ["Local", "User"]
    def checkoutUser(self, user_id):
        return 0

    def getProjectsOfUser(self, user_id):

        local_project_dirs = [name for name in os.listdir(self.project_files_root) if name.startswith(self.dirname_prefix)]
        if len(local_project_dirs) > 0:
            projects = {}
            for dirname in local_project_dirs:
                project_id = int(dirname.split('_')[1])
                project_dir = os.path.join(self.project_files_root, dirname)
                # check if the json with essential project properties exists
                if os.path.isfile(os.path.join(project_dir, self.project_attr_filename)):
                    # Load the JSON file to get the project name
                    with open(os.path.join(project_dir, self.project_attr_filename), "r") as f:
                        project_attributes = json.load(f)
                        project_name = project_attributes.get("name",
                                                              "Unnamed Project")  # Default to "Unnamed Project" if name is not found
                    projects[project_id] = project_name
            return projects
        return None

    def printUserInfo(self, user_id):
        if user_id != 0:
            print("Only one local user with ID = 0 is allowed - all local projects belong to him/her/them/it")
            user_id = 0
        print("\n" + 70 * "-")
        userinfo = self.getUserNameByID(user_id)
        usersProjects = self.getProjectsOfUser(user_id=user_id)
        if usersProjects is not None:
            print(f"Saved project of user id = {user_id} ({userinfo[1]}, {userinfo[0]}):")
            for rid, rname in usersProjects.items():
                print(f"\t{rid}: {rname}")
        else:
            print(f"User id = {user_id} ({userinfo[1]}, {userinfo[0]}) has no saved project.")
        print(70 * "-" + "\n")

    def establishProjectRecord(self, user_id, project, unique_names=True):
        # assign correct ID to Project instance
        project.id = self.getNewProjectID()
        project.user_id = 0
        # assign the project files directory path
        project.temp_dir = self._create_project_directory(project.id, prefix="temp_")
        project.keepFiles = True
        # save attributes to a JSON file
        with open(os.path.join(project.temp_dir, self.project_attr_filename), "w") as f:
            project_attr = {"name": project.name, "doi": project.getDOI(), "temp_dir": project.temp_dir,
                         "keep_files": (1 if project.keepFiles else 0)}
            json.dump(project_attr, f)

        return project.id

    def updateProjectRecord(self, project, cascade=False):
        with open(os.path.join(project.temp_dir, self.project_attr_filename), "w") as f:
            project_attr = {"name": project.name, "doi": project.getDOI(), "temp_dir": project.temp_dir,
                         "keep_files": (1 if project.keepFiles else 0)}
            json.dump(project_attr, f)

        if cascade:
            print(f"\tsaving containers ...")
            with open(os.path.join(project.temp_dir, self.containers_attr_filename), "w") as f:
                json.dump(project.getContainersSerialization(), f)

        return

    def loadProject(self, project):
        if project.id in self.getAllTempProjectIDs():
            project_json = os.path.join(self.project_files_root, self.dirname_prefix+str(project.id), self.project_attr_filename)
            with open(project_json, "r") as f:
                attributes = json.load(f)
                project.name = attributes["name"]
                project.doi = attributes["doi"]
                project.temp_dir = attributes["temp_dir"]

                if attributes["keep_files"] == 0:
                    project.keepFiles = False
                else:
                    project.keepFiles = True
            return project
        else:
            raise DatabaseFetchError(f"Project ID {project.id} does not exist within local temporary projects."
                 f"\nAvailable project IDs are: {', '.join([str(pid) for pid in self.getAllTempProjectIDs()])}")

    def deleteProject(self, project, delete_dir):
        if os.path.exists(project.temp_dir):
            os.rmdir(project.temp_dir)

    def updateContainerRecord(self, container):
        pass
    def updateDatasetRecord(self, dataset):
        pass

    def getAllTempProjectIDs(self):
        return [int(name.split('_')[1]) for name in os.listdir(self.project_files_root) if name.startswith(self.dirname_prefix)]

    def getNewProjectID(self):
        existing_ids = self.getAllTempProjectIDs()
        return max(existing_ids, default=0) + 1

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
#        with cls.connect() as conn:
#            thecursor = conn.cursor()
#            # execute the query and fetch the results
#            query = f"select group_name, search_pattern from search_patterns where entity_id = '{entityClass.ID}'"
#            thecursor.execute(query)
#            results = thecursor.fetchall()
#            if len(results) > 0:
#                patterns = {}
#                for pat in results:
#                    patterns.update({entityClass.key+"_"+pat[0]: str(pat[1])})
#                return patterns
#            else:
#                # raise DatabaseFetchError("No search strings found for entity_id = '{}' ({})".format(entity.ID, entity.name))
#                return None
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


