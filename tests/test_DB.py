from soilpulse.db_access import MySQLConnector, NullConnector
import time
from pathlib import Path
import os

def test_mysql_storage():
    """
    Tests loading the MySQL code from a dump and then using the loaded code to establish the DB structure on a server.
    Checks for existence of the 4 core tables that (probably) won't change in the future.
    """
    def get_tables_of_DB(db_connection):
        # get list of tables in DB
        cursor = db_connection.cursor()
        cursor.execute("SHOW TABLES")
        result = cursor.fetchall()
        cursor.close()
        results = [r[0] for r in result]
        print(results)
        return results

    # load the SQL code from file
    with open("database/soilpulse.sql", "r") as file:
        sql = file.read()

    # establish the database on the server from the loaded code
    db = MySQLConnector()
    cursor = db.db_connection.cursor()
    cursor.execute(sql, multi=True)
    cursor.close()

    # wait for DB to be set up
    time.sleep(25)

    # get list of tables in established database
    results = get_tables_of_DB(db.db_connection)

    assert 'projects' in results
    assert 'containers' in results
    assert 'datasets' in results
#    assert 'users' in results


def test_mysql_user():
    """
    The freshly initialized MySQL database has one default user for testing purposes named "Demo User".
    Check if the user was correctly created in `users` table.
    """
    db = MySQLConnector()
    query = f"SELECT COUNT(*) FROM {db.userTableName}"
    thecursor = db.db_connection.cursor()
    thecursor.execute(query)
    user_count = thecursor.fetchone()[0]
    user = db.getUserNameByID(1)
    thecursor.close()

    assert (user_count == 1)
    assert (user[0][0] == 'D' and user[1][0] == 'U')
    # and return userID for valid userID otherwise None
    assert db.checkoutUser(1) == 1
    assert db.checkoutUser(2) is None
    assert db.checkoutUser(3) is None

def test_filesystem_storage():
    # get the instance of the NullConnector
    db = NullConnector()
    # it should create the project root directory
    assert os.path.isdir(db.project_files_root)
    # and return 0 for any provided user ID
    assert db.checkoutUser(1) == 0
    assert db.checkoutUser(2) == 0
    assert db.checkoutUser(3) == 0
