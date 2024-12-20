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
import shutil
from pathlib import Path
import importlib.resources

from .exceptions import DatabaseFetchError, DatabaseEntryError, NameNotUniqueError, DeserializationError, ContainerStructureError

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
    soilpulse_root_dir_name = "SoilPulse"
    project_files_dir_name = "project_files"
    project_files_root = Path(Path.home(), soilpulse_root_dir_name, project_files_dir_name)
    project_files_root.mkdir(parents=True, exist_ok=True)

    # prefix for directory project directory name - to distinguish between JSON saved projects and MySQL saved projects
    dirname_prefix = None
    # subdirectory name for the datasets files
    datasets_directory_name = "datasets"

    vocabularies_dir_name = "vocabularies"

    # global concepts vocabularies
    concepts_vocabulary_filenames = {"AGROVOC": "agrovoc_excerpt.json"}
    # global methods vocabularies
    methods_vocabulary_filenames = {}
    # global units vocabularies
    units_vocabulary_filenames = {}

    # project dictionaries filenames
    concepts_translations_filename = "_concepts_translations.json"
    methods_translations_filename = "_methods_translations.json"
    units_translations_filename = "_units_translations.json"

    @classmethod
    def get_connector(cls):
        """
        Returns DBconnector subclass instance that links to storage where project structural information will be stored.
        If running MySQL server with soilpulse DB is found MySQLconnector is return otherwise NullConnector
        """
        try:
            return MySQLConnector()
        except Exception:
            print("\nSoilPulse MySQL database instance couldn't be reached.\nFalling back to local filesystem.")
            return NullConnector()

    def __init__(self):
        # load the vocabularies to memory
        self.concepts_vocabularies = self.loadConceptsVocabularies()
        self.methods_vocabularies = self.loadMethodsVocabularies()
        self.units_vocabularies = self.loadUnitsVocabularies()


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

    def updateProjectRecord(self, project, cascade=False):
        pass
    def updateTranslationDictionaries(self, project):
        # update the projects vocabulary by concepts of containers
        # project.updateConceptsVocabularyFromContents()
        project.exportTranslationsDictionaryToFile(project.conceptsTranslations, os.path.join(project.temp_dir, self.concepts_translations_filename))
        # with open(os.path.join(project.temp_dir, self.concepts_translations_filename), "w") as f:
        #     json.dump(project.conceptsTranslations, f, ensure_ascii=False, indent=4)
        print(f"\tconcepts vocabulary saved")

        # update the projects vocabulary by methods of containers
        # project.updateMethodsVocabularyFromContents()
        project.exportTranslationsDictionaryToFile(project.methodsTranslations, os.path.join(project.temp_dir, self.methods_translations_filename))

        # with open(os.path.join(project.temp_dir, self.concepts_translations_filename), "w") as f:
        #     json.dump(project.methodsTranslations, f, ensure_ascii=False, indent=4)
        print(f"\tmethods vocabulary saved")

        # update the projects vocabulary by units of containers
        # project.updateUnitsVocabularyFromContents()
        project.exportTranslationsDictionaryToFile(project.unitsTranslations, os.path.join(project.temp_dir, self.units_translations_filename))

        # with open(os.path.join(project.temp_dir, project.units_translations_filename), "w") as f:
        #     json.dump(project.unitsTranslations, f, ensure_ascii=False, indent=4)
        print(f"\tunits vocabulary saved")
        return

    def loadProject(self, project):
        pass

    def loadTranslationsOfProject(self, project):
        # load concepts vocabulary
        concepts_dictionary_path = os.path.join(project.temp_dir, self.concepts_translations_filename)
        if os.path.isfile(concepts_dictionary_path) and os.path.getsize(concepts_dictionary_path) > 0:
            with open(concepts_dictionary_path, "r") as f:
                project.conceptsTranslations = json.load(f)
        else:
            print(f"string-concept translations dictionary '{concepts_dictionary_path}' does not exist or is empty.")

        # load methods vocabulary
        methods_dictionary_path = os.path.join(project.temp_dir, self.methods_translations_filename)
        if os.path.isfile(methods_dictionary_path) and os.path.getsize(methods_dictionary_path) > 0:
            with open(methods_dictionary_path, "r") as f:
                project.methodsTranslations = json.load(f)
        else:
            print(f"string-method translations dictionary '{methods_dictionary_path}' does not exist or is empty.")

        # load units vocabulary
        units_dictionary_path = os.path.join(project.temp_dir, self.units_translations_filename)
        if os.path.isfile(units_dictionary_path) and os.path.getsize(units_dictionary_path) > 0:
            with open(units_dictionary_path, "r") as f:
                project.unitsTranslations = json.load(f)
        else:
            print(f"string-unit translations dictionary '{units_dictionary_path}' does not exist or is empty.")


    def deleteProject(self, project, delete_dir=True):
        pass

    def updateContainerRecord(self, container, cascade=False):
        pass

    def deleteDatasetRecord(self, dataset):
        pass

    def create_project_directory(self, project_id):
        dir_name = f"{self.dirname_prefix}{project_id}"
        project_dir = os.path.join(self.project_files_root, dir_name)

        if os.path.isdir(project_dir):
            print(f"Directory for newly established project '{project_dir}' already exists - all of it's current contents will be deleted.")
            shutil.rmtree(project_dir)
        os.mkdir(project_dir)

        # create directory for the datasets
        datasets_dir = os.path.join(project_dir, self.datasets_directory_name)
        if not os.path.isdir(datasets_dir):
            os.mkdir(datasets_dir)

        return project_dir, datasets_dir

    def getDatasetsOfProject(self, project_id):
        pass

    def loadVocabularyFromResource(self, filename):
        """
        Loads string-* translations JSON file

        :param filename: name of vocabulary file inside the package 'vocabularies' folder
        """
        out_dict = []
        with importlib.resources.open_text(f"{__package__}.{self.vocabularies_dir_name}", filename) as f:
            for item in json.load(f):
                out_dict.append(item)
        return out_dict

    def loadVocabularyFromFile(self, input_file):
        vocab = []
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                vocab = json.load(f)
        except:
            print(f"Loading vocabulary from file '{input_file}' failed.")
        else:
            print(f"Vocabulary from file '{input_file}' successfully loaded.")
        return vocab


    def loadConceptsVocabularies(self):
        """
        Loads string-concepts translations JSON file
        """
        vocabs = {}
        loaded = []
        for vocab, filename in self.concepts_vocabulary_filenames.items():
            try:
                vocabs.update({vocab: self.loadVocabularyFromResource(filename)})
            except:
                print(f"failed to load concept vocabulary '{vocab}' from '{os.path.join(self.vocabularies_dir_name, filename)}'")
            else:
                loaded.append(vocab)
        if len(loaded) > 0:
            print(f"loaded concepts vocabularies: {', '.join([str(v) for v in loaded])}")
        return vocabs

    def loadMethodsVocabularies(self):
        """
        Loads string-method translations JSON file
        """
        vocabs = {}
        loaded = []
        for vocab, filename in self.methods_vocabulary_filenames.items():
            try:
                vocabs.update({vocab: self.loadVocabularyFromResource(filename)})
            except:
                print(
                    f"failed to load method vocabulary '{vocab}' from '{os.path.join(self.vocabularies_dir_name, filename)}'")
            else:
                loaded.append(vocab)
        if len(loaded) > 0:
            print(f"loaded methods vocabularies: {', '.join([str(v) for v in loaded])}")
        return vocabs

    def loadUnitsVocabularies(self):
        """
        Loads string-unit translations JSON file
        """
        vocabs = {}
        loaded = []
        for vocab, filename in self.units_vocabulary_filenames.items():
            try:
                vocabs.update({vocab: self.loadVocabularyFromResource(filename)})
            except:
                print(
                    f"failed to load units vocabulary '{vocab}' from '{os.path.join(self.vocabularies_dir_name, filename)}'")
            else:
                loaded.append(vocab)
        if len(loaded) > 0:
            print(f"loaded units vocabularies: {', '.join([str(v) for v in loaded])}")
        return vocabs

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
    datasetsContainersTableName = "`datasets_containers`"
    conceptsContainersTableName = "`container_concepts`"
    unitsContainersTableName = "`container_units`"
    methodsContainersTableName = "`container_methods`"
    conceptDictionaryTableName = "`concepts_dictionary`"
    methodsDictionaryTableName = "`methods_dictionary`"
    unitsDictionaryTableName = "`units_dictionary`"


    def __init__(self):
        print("\nconnecting to MySQL ...")

        try:
            self.db_connection = mysql.connector.connect(
                host=self.server,
                user=self.username,
                password=self.pwd,
                database=self.db_name
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

        super().__init__()

    def __del__(self):
        pass

    def checkContainersTableStructure(self, needed_fields):
        thecursor = self.db_connection.cursor()
        query = f"SHOW COLUMNS FROM {self.containersTableName} FROM {self.db_name};"
        thecursor.execute(query)
        results = thecursor.fetchall()
        thecursor.close()

        existing_fields = [res[0] for res in results] if len(results) > 0 else []

        print(f"fields in SoilPulse DB:\n{', '.join([str(f) for f in existing_fields])}")

        missing_fields = [field for field in needed_fields if field not in existing_fields]

        if len(missing_fields) > 0:
            print(f"missing fields in SoilPulse DB:\n{', '.join([str(f) for f in missing_fields])}")
            return False
        else:
            return True

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
        query = f"SELECT AUTO_INCREMENT FROM information_schema.tables "\
                          f"WHERE table_name = '{self.projectsTableName.strip('`')}'"
        thecursor.execute(query)
        results = thecursor.fetchall()

        if thecursor.rowcount > 0:
            for nextID in results:
                if nextID[0] is None:
                    return 1
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

        project_id = newID
        project_temp_dir, datasets_dir = self.create_project_directory(project_id)

        # insert line to `projects` table
        query = f"INSERT INTO {self.projectsTableName} (`name`, `doi`, `temp_dir`) VALUES (%s, %s, %s)"
        values = [project.name, project.doi, project_temp_dir]
        thecursor.execute(query, values)
        # insert queries must be committed
        self.db_connection.commit()

        # insert line to `user_projects` table
        query = f"INSERT INTO {self.userProjectsTableName} (`user_id`, `project_id`) VALUES (%s, %s)"
        values = [user_id, project_id]
        thecursor.execute(query, values)
        self.db_connection.commit()
        thecursor.close()

        # create empty project translation dictionaries
        with open(os.path.join(project_temp_dir, self.concepts_translations_filename), "w") as f:
            f.close()
        with open(os.path.join(project_temp_dir, self.methods_translations_filename), "w") as f:
            f.close()
        with open(os.path.join(project_temp_dir, self.units_translations_filename), "w") as f:
            f.close()
        return project_id, project_temp_dir, datasets_dir

    def updateProjectRecord(self, project, cascade=False):
        """
        Updates database record of a Project and all of its contents

        :param project: the Project instance reference to be saved
        :param cascade: whether to update the containers too
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
        # don't update name if another project exists with the same name
        count = thecursor.fetchone()[0]
        if count > 0:
            update_name = False

        newValues = {"doi": project.doi, "temp_dir": project.temp_dir, "keep_files": (1 if project.keepFiles else 0)}
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

        if cascade:
            # save containers and their strings translations
            if len(project.containerTree) > 0:
                # list of container ids that are part of the in memory instance of ProjectManager
                happy_containers = []
                for cont in project.containerTree:
                    happy_containers.extend(self.updateContainerRecord(cont, cascade, []))
                print(f"\tcontainers saved")
                print(f"\tvocabularies saved")

                # deleting orphaned container entries (containers that were deleted in memory)
                # TODO first get all files that are related to the orphaned containers and delete them

                thecursor = self.db_connection.cursor()
                query = f"DELETE FROM {self.containersTableName} " \
                        f"WHERE `id_local` NOT IN ({', '.join([str(o) for o in happy_containers])}) " \
                        f"AND `project_id` = {project.id}"
                thecursor.execute(query)
                self.db_connection.commit()
                # print the number of deleted rows if any
                deleted_rows = thecursor.rowcount
                if deleted_rows > 0:
                    print(f"\t{deleted_rows} orphaned containers deleted")

                thecursor.close()


            else:
                print(f"\t(no containers to save)")

            # delete DB records of containers that are no longer existing
            self.deleteRemovedContainers()

            # save datasest
            if len(project.datasets) > 0:
                for dats in project.datasets:
                    self.updateDatasetRecord(dats)
                print(f"\tdatasets saved")
            else:
                print(f"\t(no datasets to save)")

        # save project concept/methods/units translation dictionaries
        self.updateTranslationDictionaries(project)

        # delete string-concept translations that are no longer in use
        self.deleteOrphannedConceptTranslations(project.id, project.collectContainerConcepts())
        # delete string-method translations that are no longer in use
        self.deleteOrphannedMethodTranslations(project.id, project.collectContainerMethods())
        # delete string-unit translations that are no longer in use
        self.deleteOrphannedUnitTranslations(project.id, project.collectContainerUnits())


        thecursor.close()
        return

    def deleteRemovedContainers(self):
        pass

    def deleteOrphannedConceptTranslations(self, project_id, current_vocab):
        """
        Deletes translations from the database that are no longer in use for given project.

        :param project_id: The ID of the project for which to clean up translations.
        :param current_vocab: A dictionary of currently used translations (structured as {string: [{vocabulary, uri}, ...]}).
        """
        # transform currently used translations into set of tuples
        current_translations_set = set(
            (string, translation['vocabulary'], translation['uri'])
            for string, translations in current_vocab.items()
            for translation in translations
        )
        # fetch all translations from the database for the project
        thecursor = self.db_connection.cursor()
        select_query = f"SELECT `id`, `string`, `vocabulary`, `uri`  FROM {self.conceptDictionaryTableName} " \
                       f"WHERE `project_id` = {project_id}"
        thecursor.execute(select_query)
        rows = thecursor.fetchall()

        # collect IDs of unused translations
        ids_to_delete = []
        for row in rows:
            db_id, db_string, db_vocabulary, db_uri = row
            # Check if the translation is not in the current translations set
            if (db_string, db_vocabulary, db_uri) not in current_translations_set:
                ids_to_delete.append(db_id)

        # if there are IDs to delete, execute the deletion
        if ids_to_delete:
            delete_query = f"DELETE FROM {self.conceptDictionaryTableName} WHERE id IN " \
                           f" ({', '.join([str(id) for id in ids_to_delete])})"
            thecursor.execute(delete_query)
            self.db_connection.commit()
        thecursor.close()
        return

    def deleteOrphannedMethodTranslations(self, project_id, current_vocab):
        """
        Deletes string-method translations from the database that are no longer in use for given project.

        :param project_id: The ID of the project for which to clean up translations.
        :param current_vocab: A dictionary of currently used translations (structured as {string: [{vocabulary, uri}, ...]}).
        """
        # transform currently used translations into set of tuples
        current_translations_set = set(
            (string, translation['vocabulary'], translation['uri'])
            for string, translations in current_vocab.items()
            for translation in translations
        )
        # fetch all translations from the database for the project
        thecursor = self.db_connection.cursor()
        select_query = f"SELECT `id`, `string`, `vocabulary`, `uri`  FROM {self.methodsDictionaryTableName} " \
                       f"WHERE `project_id` = {project_id}"
        thecursor.execute(select_query)
        rows = thecursor.fetchall()

        # collect IDs of unused translations
        ids_to_delete = []
        for row in rows:
            db_id, db_string, db_vocabulary, db_uri = row
            # Check if the translation is not in the current translations set
            if (db_string, db_vocabulary, db_uri) not in current_translations_set:
                ids_to_delete.append(db_id)

        # if there are IDs to delete, execute the deletion
        if ids_to_delete:
            delete_query = f"DELETE FROM {self.methodsDictionaryTableName} WHERE id IN " \
                           f" ({', '.join([str(id) for id in ids_to_delete])})"
            thecursor.execute(delete_query)
            self.db_connection.commit()
        thecursor.close()
        return

    def deleteOrphannedUnitTranslations(self, project_id, current_vocab):
        """
        Deletes string-unit translations from the database that are no longer in use for given project.

        :param project_id: The ID of the project for which to clean up translations.
        :param current_vocab: A dictionary of currently used translations (structured as {string: [{vocabulary, uri}, ...]}).
        """
        # transform currently used translations into set of tuples
        current_translations_set = set(
            (string, translation['vocabulary'], translation['uri'])
            for string, translations in current_vocab.items()
            for translation in translations
        )
        # fetch all translations from the database for the project
        thecursor = self.db_connection.cursor()
        select_query = f"SELECT `id`, `string`, `vocabulary`, `uri`  FROM {self.unitsDictionaryTableName} " \
                       f"WHERE `project_id` = {project_id}"
        thecursor.execute(select_query)
        rows = thecursor.fetchall()

        # collect IDs of unused translations
        ids_to_delete = []
        for row in rows:
            db_id, db_string, db_vocabulary, db_uri = row
            # Check if the translation is not in the current translations set
            if (db_string, db_vocabulary, db_uri) not in current_translations_set:
                ids_to_delete.append(db_id)

        # if there are IDs to delete, execute the deletion
        if ids_to_delete:
            delete_query = f"DELETE FROM {self.unitsDictionaryTableName} WHERE id IN " \
                           f" ({', '.join([str(id) for id in ids_to_delete])})"
            thecursor.execute(delete_query)
            self.db_connection.commit()
        thecursor.close()
        return


    def updateContainerRecord(self, container, cascade=False, cont_updated=[]):
        """
        Updates DB entry of the container and its related entities (concepts, unit, methods)
        On cascade=True recursively invokes update on all sub-containers
        Records list of updated container ids in cont_updated

        :param container: the container instance to be updated
        :param cascade: whether or not to update the sub-containers' records too
        :param cont_updated: list of IDs of updated containers
        """

        thecursor = self.db_connection.cursor()

        # set the general core of properties to be stored
        arglist = {"type": container.containerType,
                   "name": container.name,
                   "parent_id_local": container.parentContainer.id if container.parentContainer is not None else None,
                   "crawler_type": container.crawler.crawlerType if container.crawler is not None else None}

        # add container subclass specific properties to be stored
        for db_key, attr_key in container.serializationDict.items():
            arglist.update({db_key: str(getattr(container, attr_key))})

        # update properties if the container already exists
        if self.getContainerGlobalID(container) is not None:
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
        # add this container to updated list
        cont_updated.append(container.id)

        # update concepts records of container
        self.updateConceptsOfContainer(container)
        # update methods records of container
        self.updateMethodsOfContainer(container)
        # update units records of container
        self.updateUnitsOfContainer(container)

        # update sub-containers records if desired
        if cascade:
            for cont in container.containers:
                self.updateContainerRecord(cont, cascade, cont_updated)
        return cont_updated

    def updateConceptsOfContainer(self, container):
        """
        Updates DB record of all string-concept translations of a container
        """
        if len(container.concepts) > 0:
            # get container's global ID for foreign key
            cont_glob_id = self.getContainerGlobalID(container)
            for string, concepts in container.concepts.items():
                for concept in concepts:
                    # get string-concept translation id from DB if exists
                    trans_id = self.getConceptTranslationID(string, concept['vocabulary'], concept['uri'], container.project.id)
                    # if the translation doesn't exist create it
                    if trans_id is None:
                        trans_id = self.insertStringConceptTranslation(string, concept['term'], concept['vocabulary'], concept['uri'], container.project.id)

                    thecursor = self.db_connection.cursor()
                    thecursor.execute(f"SELECT COUNT(*) FROM {self.conceptsContainersTableName}"
                                      f"WHERE `container_id` = {cont_glob_id} AND `translation_id` = {trans_id}")
                    count = thecursor.fetchone()[0]
                    if count == 0:
                        query = f"INSERT INTO {self.conceptsContainersTableName} (`container_id`, `translation_id`) " \
                                  f"VALUES {cont_glob_id, trans_id}"
                        thecursor.execute(query)
                        self.db_connection.commit()
                    thecursor.close()
        return

    def updateMethodsOfContainer(self, container):
        """
        Updates DB record of all string-method translations of a container
        """
        if len(container.methods) > 0:
            # get container's global ID for foreign key
            cont_glob_id = self.getContainerGlobalID(container)
            for string, methods in container.methods.items():
                for method in methods:
                    # get string-method translation id from DB if exists
                    trans_id = self.getMethodTranslationID(string, method['vocabulary'], method['uri'], container.project.id)
                    # if the translation doesn't exist create it
                    if trans_id is None:
                        trans_id = self.insertStringMethodTranslation(string, method['term'], method['vocabulary'], method['uri'], container.project.id)

                    thecursor = self.db_connection.cursor()
                    thecursor.execute(f"SELECT COUNT(*) FROM {self.methodsContainersTableName}"
                                      f"WHERE `container_id` = {cont_glob_id} AND `translation_id` = {trans_id}")
                    count = thecursor.fetchone()[0]
                    if count == 0:
                        query = f"INSERT INTO {self.methodsContainersTableName} (`container_id`, `translation_id`) " \
                                  f"VALUES {cont_glob_id, trans_id}"
                        thecursor.execute(query)
                        self.db_connection.commit()
                    thecursor.close()
        return

    def updateUnitsOfContainer(self, container):
        """
        Updates DB record of all string-units translations of a container
        """
        if len(container.units) > 0:
            # get container's global ID for foreign key
            cont_glob_id = self.getContainerGlobalID(container)
            for string, units in container.units.items():
                for unit in units:
                    # get string-units translation id from DB if exists
                    trans_id = self.getUnitTranslationID(string, unit['vocabulary'], unit['uri'], container.project.id)
                    # if the translation doesn't exist create it
                    if trans_id is None:
                        trans_id = self.insertStringUnitTranslation(string, unit['term'], unit['vocabulary'], unit['uri'], container.project.id)

                    thecursor = self.db_connection.cursor()
                    thecursor.execute(f"SELECT COUNT(*) FROM {self.unitsContainersTableName}"
                                      f"WHERE `container_id` = {cont_glob_id} AND `translation_id` = {trans_id}")
                    count = thecursor.fetchone()[0]
                    if count == 0:
                        query = f"INSERT INTO {self.unitsContainersTableName} (`container_id`, `translation_id`) " \
                                  f"VALUES {cont_glob_id, trans_id}"
                        thecursor.execute(query)
                        self.db_connection.commit()
                    thecursor.close()
        return

    def getConceptTranslationID(self, string, vocabulary, uri, project_id):
        """
        Returns id of string-concept translation in DB or None if no such translation exists.
        The return ID is used in container-translation relation
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"SELECT `id` FROM {self.conceptDictionaryTableName} " \
              f"WHERE `string` = '{string}' AND `vocabulary` = '{vocabulary}' AND `uri` = '{uri}' "
        query += f"AND `project_id` = {project_id}" if project_id is not None else None
        thecursor.execute(query)
        results = thecursor.fetchall()
        thecursor.close()

        if len(results) == 0:
            return None
        elif len(results) > 1:
            raise DatabaseEntryError(f"Duplicit string-concept translation '{string}'-'{vocabulary}'-'{uri}' in project {project_id}")
        else:
            return results[0]['id']


    def getMethodTranslationID(self, string, vocabulary, uri, project_id):
        """
        Returns id of string-method translation in DB or None if no such translation exists.
        The return ID is used in container-translation relation
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"SELECT `id` FROM {self.methodsDictionaryTableName} " \
              f"WHERE `string` = '{string}' AND `vocabulary` = '{vocabulary}' AND `uri` = '{uri}' "
        query += f"AND `project_id` = {project_id}" if project_id is not None else None
        thecursor.execute(query)
        results = thecursor.fetchall()
        thecursor.close()

        if len(results) == 0:
            return None
        elif len(results) > 1:
            raise DatabaseEntryError(f"Duplicit string-method translation '{string}'-'{vocabulary}'-'{uri}' in project {project_id}")
        else:
            return results[0]['id']

    def getUnitTranslationID(self, string, vocabulary, uri, project_id):
        """
        Returns id of string-unit translation in DB or None if no such translation exists.
        The return ID is used in container-translation relation
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"SELECT `id` FROM {self.unitsDictionaryTableName} " \
                f"WHERE `string` = '{string}' AND `vocabulary` = '{vocabulary}' AND `uri` = '{uri}' "
        query += f"AND `project_id` = {project_id}" if project_id is not None else None
        thecursor.execute(query)
        results = thecursor.fetchall()
        thecursor.close()

        if len(results) == 0:
            return None
        elif len(results) > 1:
            raise DatabaseEntryError(
                f"Duplicit string-unit translation '{string}'-'{vocabulary}'-'{uri}' in project {project_id}")
        else:
            return results[0]['id']


    def insertStringConceptTranslation(self, string, term, vocabulary, uri, project_id):
        """
        Inserts DB entry of a string-concept definition into database table and returns ID of the translation

        :param string: the string which translation it is
        :param term: the term of the uri
        :param vocabulary: vocabulary of the unit definition
        :param uri: unique identifier of the term within specified vocabulary
        :param project_id: ID of project to which the translation belongs
        :returns: ID of the newly created translation DB entry
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"INSERT INTO {self.conceptDictionaryTableName} (`string`, `term`, `vocabulary`, `uri`, `project_id`) " \
              f"VALUES ('{string}', '{term}', '{vocabulary}', '{uri}', {project_id});"
        thecursor.execute(query)
        self.db_connection.commit()
        # get the last inserted ID
        thecursor.execute("SELECT LAST_INSERT_ID()")
        new_id = thecursor.fetchone()['LAST_INSERT_ID()']
        thecursor.close()

        return new_id

    def insertStringMethodTranslation(self, string, term, vocabulary, uri, project_id):
        """
        Inserts DB entry of a string-method definition into database table and returns ID of the translation

        :param string: the string which translation it is
        :param term: the term of the uri
        :param vocabulary: vocabulary of the unit definition
        :param uri: unique identifier of the term within specified vocabulary
        :param project_id: ID of project to which the translation belongs
        :returns: ID of the newly created translation DB entry
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"INSERT INTO {self.methodsDictionaryTableName} (`string`, `term`, `vocabulary`, `uri`, `project_id`) " \
              f"VALUES ('{string}', '{term}', '{vocabulary}', '{uri}', {project_id});"
        thecursor.execute(query)
        self.db_connection.commit()
        # get the last inserted ID
        thecursor.execute("SELECT LAST_INSERT_ID()")
        new_id = thecursor.fetchone()['LAST_INSERT_ID()']
        thecursor.close()

        return new_id

    def insertStringUnitTranslation(self, string, term, vocabulary, uri, project_id):
        """
        Inserts DB entry of a string-unit definition into database table and returns ID of the translation

        :param string: the string being translated
        :param term: the term of the uri
        :param vocabulary: vocabulary of the unit definition
        :param uri: unique identifier of the term within specified vocabulary
        :param project_id: ID of project to which the translation belongs
        :returns: ID of the newly created translation DB entry
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"INSERT INTO {self.unitsDictionaryTableName} (`string`, `term`, `vocabulary`, `uri`, `project_id`) " \
              f"VALUES ('{string}', '{term}', '{vocabulary}', '{uri}', {project_id});"
        thecursor.execute(query)
        self.db_connection.commit()
        # get the last inserted ID
        thecursor.execute("SELECT LAST_INSERT_ID()")
        new_id = thecursor.fetchone()['LAST_INSERT_ID()']
        thecursor.close()

        return new_id

    def updateDatasetRecord(self, dataset):
        """
        Saves dataset state into DB
        """
        thecursor = self.db_connection.cursor()

        # update properties if the dataset record already exists
        dataset_glob_id = self.getDatasetGlobalID(dataset)
        if dataset_glob_id is not None:
            query = f"UPDATE {self.datasetsTableName} SET `name` = '{dataset.name}' "
            query += f"WHERE `id` = {dataset_glob_id}"
            thecursor.execute(query)
            self.db_connection.commit()
        # insert new dataset record if not yet in DB
        else:
            query = f"INSERT INTO {self.datasetsTableName} (`dataset_id`, `project_id`, `name`) "
            query += f"VALUES ({dataset.id}, {dataset.project.id}, '{dataset.name}')"
            thecursor.execute(query)
            self.db_connection.commit()
            thecursor.execute("SELECT LAST_INSERT_ID()")
            results = thecursor.fetchone()
            dataset_glob_id = results[0]

        # update container links
        for container in dataset.containers:
            # check if the link already exists
            if not self.datasetContainerRecordExists(dataset, container):
                query = f"INSERT INTO {self.datasetsContainersTableName} (`dataset_id`, `container_id`) "
                query += f"VALUES ({dataset_glob_id}, {self.getContainerGlobalID(container)})"
                thecursor.execute(query)
                self.db_connection.commit()

        thecursor.close()
        return

    def deleteDatasetRecord(self, dataset):
        dataset_glob_id = self.getDatasetGlobalID(dataset)
        if dataset_glob_id is not None:
            thecursor = self.db_connection.cursor()
            query = f"DELETE FROM {self.datasetsTableName} WHERE `id` = {dataset_glob_id}"
            thecursor.execute(query)
            self.db_connection.commit()
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
            project.datasets_dir = os.path.join(project.temp_dir, self.datasets_directory_name)

            if result["keep_files"] == 0:
                project.keepFiles = False
            else:
                project.keepFiles = True

            # load translation dictionaries
            self.loadTranslationsOfProject(project)

            if cascade:
                # load the container tree
                project.containerTree = self.loadChildContainers(project, parent_container=None)
                # load the datasets
                self.loadDatasetsOfProject(project)

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
            for container_data in results:
                # print(container_data)
                # missing type attribute is critical ... or doesn't have to be if handled properly some other way
                if container_data.get("type") is None:
                    raise DeserializationError(f"Container type is not specified for container ID {container_data.get('id_local')}.\n"
                                               f"This container and its sub-containers will not be included in the project/dataset tree")
                elif container_data.get("type") not in project.containerFactory.containerTypes.keys():
                    raise DeserializationError(
                        f"Container type '{container_data.get('type')}' is not recognized by container factory.\n"
                        f"Container ID {container_data.get('id_local')} and its sub-containers will not be included in the project/dataset tree")

                else:
                    ## general properties common for all container types
                    container_type = container_data.get("type")
                    container_id = container_data.pop("id_local")

                    # replace the global id from DB by project scope 'id_local'
                    del(container_data["id"])
                    container_data.update({"id": container_id})
                    # delete properties that are being handled different ways
                    del (container_data["parent_id_local"])
                    del (container_data["project_id"])

                    ## relative/absolute file path handling ... this could be done in more elegant and general way I'm sure
                    # replace relative path stored in files by absolute path needed for proper container creation in factory
                    rel_path = container_data.get("relative_path")
                    # the "NULL" value from DB is returned as string "None" ...
                    rel_path = None if rel_path == "None" else rel_path

                    if rel_path is None:
                        abs_path = None
                    else:
                        abs_path = os.path.join(project.temp_dir, rel_path)
                    container_data.update({"path": abs_path})

                    ## type-specific attributes handling
                    # get the attributes for particular container subclass from the factory
                    attr_dict = project.containerFactory.containerTypes.get(container_type).serializationDict

                    missing_keys = []
                    for key, attr_name in attr_dict.items():
                        # print(f"{key} - {attr_name}: {container_data.get(key)}")
                        if key not in container_data.keys():
                            missing_keys.append(key)
                        else:
                            container_data.update({attr_name: container_data.get(key)})
                    if len(missing_keys) > 0:
                        raise DeserializationError(
                            f"Needed attribute{'s' if len(missing_keys) > 1 else ''} {', '.join([k for k in missing_keys])} "
                            f"{'was' if len(missing_keys) == 1 else 'were'} not found on deserialization of Container ID {container_id}.\n"
                            f"This container and its sub-containers will not be included in the project/dataset tree")

                    newCont = project.containerFactory.createHandler(container_type, project, parent_container, cascade=False, **container_data)
                    out_container_list.append(newCont)

                    ## crawler assignment
                    newCont.crawler = None if container_data.get("crawler_type") is None \
                        else project.crawlerFactory.createCrawler(container_data.get("crawler_type"), newCont)

                    # load concepts
                    newCont.concepts = self.loadConceptsOfContainer(newCont)
                    # load methods
                    if hasattr(newCont, "methods"):
                        newCont.methods = self.loadMethodsOfContainer(newCont)
                    # load units
                    if hasattr(newCont, "units"):
                        newCont.units = self.loadUnitsOfContainer(newCont)

                    # load subcontainers
                    newCont.containers = self.loadChildContainers(project, newCont)

            thecursor.close()
        return out_container_list

    def loadDatasetsOfProject(self, project):
        thecursor = self.db_connection.cursor(dictionary=True)
        # load datasets of project
        query = f"SELECT `id`, `dataset_id`, `name` FROM {self.datasetsTableName} WHERE `project_id` = {project.id}"
        thecursor.execute(query)
        results = thecursor.fetchall()
        if len(results) > 0:
            # and for each of them load its containers
            for res in results:
                new_dataset = project.createDataset(res['name'], res['dataset_id'])
                # find and get reference of the containers of the dataset
                # need to join the containers table to get local ids
                query = f"SELECT {self.containersTableName}.`id_local` as id FROM {self.containersTableName} " \
                        f"INNER JOIN {self.datasetsContainersTableName} " \
                        f"ON {self.datasetsContainersTableName}.`container_id` = {self.containersTableName}.`id` " \
                        f"WHERE {self.datasetsContainersTableName}.`dataset_id` = {res['id']} "
                thecursor.execute(query)
                cont_res = thecursor.fetchall()
                if len(cont_res) > 0:
                    container_ids = []
                    for cont in cont_res:
                        container_ids.append(cont['id'])
                    new_dataset.containers = project.getContainerByID(container_ids)
                new_dataset.directory_path = os.path.join(project.temp_dir, self.datasets_directory_name, str(new_dataset.id))
        thecursor.close()
        return

    def deleteProject(self, project, delete_dir=True):
        cursor = self.db_connection.cursor()
        query = f"DELETE FROM {self.projectsTableName} WHERE `id` = {project.id}"
        cursor.execute(query)
        self.db_connection.commit()
        cursor.close()

        # Optionally delete the project directory
        if delete_dir:
            if os.path.exists(project.temp_dir):
                shutil.rmtree(project.temp_dir)
        return

    def datasetContainerRecordExists(self, dataset, container):
        """
        Checks if datset-container link already has database entry

        :param dataset: local container ID
        :param container: ID of project the container belongs to
        """
        thecursor = self.db_connection.cursor()
        dataset_global_id = self.getDatasetGlobalID(dataset)
        container_global_id = self.getContainerGlobalID(container)
        query = f"SELECT COUNT(*) FROM {self.datasetsContainersTableName} " \
                f"WHERE `dataset_id` = %s " \
                f"AND `container_id` = %s"
        values = [dataset_global_id, container_global_id]
        thecursor.execute(query, values)

        count = thecursor.fetchone()[0]
        if count == 0:
            return False
        elif count == 1:
            return True
        else:
            raise DatabaseEntryError(f"More then one ({count}) entry of link between dataset ID {dataset_global_id} and container ID {container_global_id}.")

    def loadConceptsOfContainer(self, container):
        """
        Collects all concept records from DB belonging to a given container

        :param container: the container instance
        :return:
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"SELECT `string`, `vocabulary`, `uri`, `term` FROM {self.conceptDictionaryTableName} " \
                f"INNER JOIN {self.conceptsContainersTableName} ON {self.conceptsContainersTableName}.`translation_id` = {self.conceptDictionaryTableName}.`id` " \
                f"INNER JOIN {self.containersTableName} ON {self.containersTableName}.`id` = {self.conceptsContainersTableName}.`container_id` " \
                f"WHERE {self.containersTableName}.`id_local` = {container.id} " \
                f"AND {self.containersTableName}.`project_id` = {container.project.id}"
        thecursor.execute(query)

        concepts_dict = {}
        results = thecursor.fetchall()
        for res in results:
            if res["string"] not in concepts_dict.keys():
                # concepts_list.append("string": res["string"] "concept": {res["vocabulary"], "uri": res["uri"])
                concepts_dict.update({res["string"]: [{"term": res["term"], "vocabulary": res["vocabulary"], "uri": res["uri"]}]})
            else:
                concepts_dict.get(res["string"]).append({"term": res["term"], "vocabulary": res["vocabulary"], "uri": res["uri"]})

        return concepts_dict


    def loadMethodsOfContainer(self, container):
        """
        Collects all method records from DB belonging to a given container

        :param container: the container instance
        :return:
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"SELECT `string`, `vocabulary`, `uri`, `term` FROM {self.methodsDictionaryTableName} " \
                f"INNER JOIN {self.methodsContainersTableName} ON {self.methodsContainersTableName}.`translation_id` = {self.methodsDictionaryTableName}.`id` " \
                f"INNER JOIN {self.containersTableName} ON {self.containersTableName}.`id` = {self.methodsContainersTableName}.`container_id` " \
                f"WHERE {self.containersTableName}.`id_local` = {container.id} " \
                f"AND {self.containersTableName}.`project_id` = {container.project.id}"
        thecursor.execute(query)

        methods_dict = {}
        results = thecursor.fetchall()
        for res in results:
            if res["string"] not in methods_dict.keys():
                methods_dict.update({res["string"]: [{"term": res["term"], "vocabulary": res["vocabulary"], "uri": res["uri"]}]})
            else:
                methods_dict.get(res["string"]).append({"term": res["term"], "vocabulary": res["vocabulary"], "uri": res["uri"]})

        return methods_dict

    def loadUnitsOfContainer(self, container):
        """
        Collects all unit records from DB belonging to a given container

        :param container: the container instance
        :return:
        """
        thecursor = self.db_connection.cursor(dictionary=True)
        query = f"SELECT `string`, `vocabulary`, `uri`, `term` FROM {self.unitsDictionaryTableName} " \
                f"INNER JOIN {self.unitsContainersTableName} ON {self.unitsContainersTableName}.`translation_id` = {self.unitsDictionaryTableName}.`id` " \
                f"INNER JOIN {self.containersTableName} ON {self.containersTableName}.`id` = {self.unitsContainersTableName}.`container_id` " \
                f"WHERE {self.containersTableName}.`id_local` = {container.id} " \
                f"AND {self.containersTableName}.`project_id` = {container.project.id}"
        thecursor.execute(query)

        units_dict = {}
        results = thecursor.fetchall()
        for res in results:
            if res["string"] not in units_dict.keys():
                units_dict.update({res["string"]: [{"term": res["term"], "vocabulary": res["vocabulary"], "uri": res["uri"]}]})
            else:
                units_dict.get(res["string"]).append({"term": res["term"], "vocabulary": res["vocabulary"], "uri": res["uri"]})

        return units_dict

    def getContainerGlobalID(self, container):
        """
        Get a global ID (SoilPulse DB scope) of a container

        :param container: the container
        :return: global ID of the container in SoilPulse DB
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT `id` FROM {self.containersTableName} " \
                f"WHERE `project_id` = %s AND `id_local` = %s"
        values = [container.project.id, container.id]
        thecursor.execute(query, values)

        results = thecursor.fetchall()
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0][0]
        else:
            raise DatabaseEntryError(
                f"More then one ({len(results)}) database entry of a container with local ID {container.id}"
                f" and project ID {container.project.id}.")

    def getDatasetGlobalID(self, dataset):
        """
        Checks if dataset with provided name and Project ID already has database entry

        :param dataset: dataset object instance
        """
        thecursor = self.db_connection.cursor()
        query = f"SELECT `id` FROM {self.datasetsTableName} " \
                f"WHERE `name` = %s  AND `project_id` = %s"
        values = [dataset.name, dataset.project.id]
        thecursor.execute(query, values)

        results = thecursor.fetchall()
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0][0]
        else:
            raise DatabaseEntryError(
                f"More then one ({len(results)}) database entry of dataset with local ID {dataset.id}"
                f" and project ID {dataset.project_id}.")

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
    # project files dedicated direcotry
    dirname_prefix = "temp_"
    # filename with saved project definition
    project_attr_filename = "_project.json"
    # filename with saved containers definition
    containers_attr_filename = "_containers.json"
    # filename with saved datasets definition
    datasets_attr_filename = "_datasets.json"

    def __init__(self):
        super().__init__()
        pass

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
                        try:
                            project_attributes = json.load(f)
                        except json.decoder.JSONDecodeError as e:
                            print("The project definition file doesn't have proper JSON structure.")
                        else:
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
        project_id = self.getNewProjectID()
        project.user_id = 0
        # assign the project files directory path
        project_temp_dir, datasets_dir = self.create_project_directory(project_id)

        project.keepFiles = True
        # save attributes to a JSON file
        with open(os.path.join(project_temp_dir, self.project_attr_filename), "w") as f:
            project_attr = {"name": project.name, "doi": project.doi, "temp_dir": project_temp_dir,
                         "keep_files": (1 if project.keepFiles else 0)}
            json.dump(project_attr, f)

        # create empty datasets file if don't exist to prevent future problems ...
        if not os.path.isfile(os.path.join(project_temp_dir, self.datasets_attr_filename)):
            with open(os.path.join(project_temp_dir, self.datasets_attr_filename), 'a') as f:
                f.write("[]")
                f.close()

        # create empty project translation dictionaries
        with open(os.path.join(project_temp_dir, self.concepts_translations_filename), "w") as f:
            f.close()
        with open(os.path.join(project_temp_dir, self.methods_translations_filename), "w") as f:
            f.close()
        with open(os.path.join(project_temp_dir, self.units_translations_filename), "w") as f:
            f.close()

        return project_id, project_temp_dir, datasets_dir

    def updateProjectRecord(self, project, cascade=False):
        # write project dump
        with open(os.path.join(project.temp_dir, self.project_attr_filename), "w") as f:
            project_attr = {"name": project.name, "doi": project.doi, "temp_dir": project.temp_dir,
                         "keep_files": (1 if project.keepFiles else 0)}
            json.dump(project_attr, f, ensure_ascii=False, indent=4)

        if cascade:
            # write containers dump
            if len(project.containerTree) > 0:
                with open(os.path.join(project.temp_dir, self.containers_attr_filename), "w") as f:
                    json.dump(project.getContainersSerialization(), f, ensure_ascii=False, indent=4)
                print(f"\tcontainers saved")
            else:
                print(f"\t(no containers to save)")

            # write datasets dump
            if len(project.datasets) > 0:
                with open(os.path.join(project.temp_dir, self.datasets_attr_filename), "w") as f:
                    json.dump(project.getDatasetsSerialization(), f, ensure_ascii=False, indent=4)
                print(f"\tdatasets saved")
            else:
                print(f"\t(no datasets to save)")

        # update project translation dictionaries
        self.updateTranslationDictionaries(project)

        return

    def loadProject(self, project, cascade=True):
        # load the project itself
        if project.id in self.getAllTempProjectIDs():
            project_json = os.path.join(self.project_files_root, self.dirname_prefix+str(project.id), self.project_attr_filename)
            with open(project_json, "r") as f:
                attributes = json.load(f)
                project.name = attributes["name"]
                project.doi = attributes["doi"]
                project.temp_dir = attributes["temp_dir"]
                project.datasets_dir = os.path.join(project.temp_dir, self.datasets_directory_name)

                if attributes["keep_files"] == 0:
                    project.keepFiles = False
                else:
                    project.keepFiles = True
        else:
            raise DatabaseFetchError(f"Project ID {project.id} does not exist within local temporary projects."
                 f"\nAvailable project IDs are: {', '.join([str(pid) for pid in self.getAllTempProjectIDs()])}")

        # load translation dictionaries
        self.loadTranslationsOfProject(project)

        # load containers structure
        if cascade:
            # load containers
            containers_attr_filepath = os.path.join(project.temp_dir, self.containers_attr_filename)
            if os.path.isfile(containers_attr_filepath):
                with open(containers_attr_filepath, "r") as f:
                    containers_serialized = json.load(f)

                    project.containerTree = self.loadChildContainers(project, containers_serialized, parent_container=None)
            else:
                raise DatabaseFetchError(f"JSON file with stored containers info '{self.containers_attr_filename}'"
                                         f" was not found in project's directory '{project.temp_dir}'")

            # load datasets
            datasets_attr_filepath = os.path.join(project.temp_dir, self.datasets_attr_filename)
            if os.path.isfile(datasets_attr_filepath):
                with open(datasets_attr_filepath, "r") as f:
                    datasets_serialized = json.load(f)
                    project.datasets = self.loadDatasets(project, datasets_serialized)
            else:
                raise DatabaseFetchError(f"JSON file with stored dataset info '{self.datasets_attr_filename}'"
                                         f" was not found in project's directory '{project.temp_dir}'")
        return project

    def loadChildContainers(self, project, containers_serialized, parent_container=None):
        out_container_list = []

        for container_id, container_data in containers_serialized.items():
            # missing type attribute is critical ... or doesn't have to be if handled properly some other way
            if container_data.get("type") is None:
                raise DeserializationError(f"Container type is not specified for container ID {container_id}.\n"
                           f"This container and its sub-containers will not be included in the project/dataset tree")
            elif container_data.get("type") not in project.containerFactory.containerTypes.keys():
                raise DeserializationError(f"Container type '{container_data.get('type')}' is not recognized by container factory.\n"
                           f"Container ID {container_id} and its sub-containers will not be included in the project/dataset tree")

            else:
                ## general properties common for all container types
                container_type = container_data.get("type")
                try:
                    id = int(container_id)
                except ValueError as e:
                    raise DeserializationError(f"Container ID is not a valid integer: {container_id}.\n"
                           f"This container and its sub-containers will not be included in the project/dataset tree")
                cont_args = {"id": id, "type": container_data.get("type"), "name": container_data.get("name")}
                cont_args.update({"parentContainer": parent_container})

                ## relative/absolute file path handling ... this could be done in more elegant and general way I'm sure
                # replace relative path stored in files by absolute path needed for proper container creation in factory
                rel_path = container_data.get("relative_path")
                if rel_path is None:
                    abs_path = None
                else:
                    abs_path = os.path.join(project.temp_dir, rel_path)
                cont_args.update({"path": abs_path})

                ## type-specific attributes handling
                # get the attributes for particular container subclass from the factory
                attr_dict = project.containerFactory.containerTypes.get(container_type).serializationDict

                # check for missing attribute keys in the input
                missing_keys = []
                for key, attr_name in attr_dict.items():
                    if key not in container_data.keys():
                        missing_keys.append(key)
                    else:
                        cont_args.update({attr_name: container_data.get(key)})
                if len(missing_keys) > 0:
                    raise DeserializationError(
                        f"Needed attribute{'s' if len(missing_keys)>1 else ''} {', '.join([k for k in missing_keys])} "
                        f"{'was' if len(missing_keys)==1 else 'were'} not found on deserialization of Container ID {container_id}.\n"
                        f"This container and its sub-containers will not be included in the project/dataset tree")

                try:
                    newCont = project.containerFactory.createHandler(container_type, project, parent_container, cascade=False, **cont_args)
                except ContainerStructureError as e:
                    print(f"Container ID {container_data.get('id')} with name {container_data.get('name')} was not created!")
                    print(e.message)
                else:
                    out_container_list.append(newCont)

                    ## crawler assignment
                    newCont.crawler = None if container_data.get("crawler_type") is None \
                        else project.crawlerFactory.createCrawler(container_data.get("crawler_type"), newCont)

                    # load concepts
                    if container_data.get("concepts"):
                        newCont.concepts = container_data.get("concepts")
                    # load methods
                    if container_data.get("methods"):
                        newCont.methods = container_data.get("methods")
                    # load units
                    if container_data.get("units"):
                        newCont.units = container_data.get("units")


                    # print(str(newCont))

                    # load subcontainers
                    if container_data.get("containers"):
                        if len(container_data.get("containers")) > 0:
                            newCont.containers = self.loadChildContainers(project, container_data.get("containers"), newCont)

        return out_container_list

    def loadDatasets(self, project, datasets_serialized):
        datasets = []
        for dataset_record in datasets_serialized:
            new_dataset = project.createDataset(dataset_record['name'], dataset_record['id'])
            new_dataset.containers = project.getContainerByID(dataset_record['container IDs'])
            new_dataset.directory_path = os.path.join(project.temp_dir, self.datasets_directory_name, str(new_dataset.id))
            datasets.append(new_dataset)
        return datasets

    def deleteProject(self, project, delete_dir=True):
        if os.path.exists(project.temp_dir):
            shutil.rmtree(project.temp_dir)

    def updateContainerRecord(self, container, cascade=False):
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
        print("* Keywords database {} registered as '{}'".format(os.path.join(cls.dbDir, dbFilename), dbType))
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
        return keywords


