from soilpulse import db_access
import time
from pathlib import Path
import os

project_files_dir_name = "project_files"
project_files_root = Path(os.path.join(Path.home(), project_files_dir_name))
print(project_files_root)
project_files_root.mkdir(parents=True, exist_ok=True)

def test_initDB():

    def get_tables_of_DB():
        # get list of tables in DB
        db = db_access.DBconnector.get_connector(project_files_root=project_files_root)
        cnx = db.db_connection
        cursor = cnx.cursor()
        cursor.execute("SHOW TABLES")
        result = cursor.fetchall()
        cursor.close()
        results = [r[0] for r in result]
        print(results)
        return results

    with open("./database/soilpulse.sql", "r") as file:
        sql = file.read()

    print(sql[0:100])

    # init DB
    db = db_access.DBconnector.get_connector(project_files_root=project_files_root)
    cnx = db.db_connection
    cursor = cnx.cursor()
    cursor.execute(sql)
    cursor.close()

    # wait for DB to be set up
    time.sleep(5)

    results = get_tables_of_DB()

    assert 'containers' in results


def test_getUser():
    db = db_access.DBconnector.get_connector(project_files_root=project_files_root)
    user = db.getUserNameByID(1)
    assert (user[0][0] == 'D' and user[1][0] == 'U')
