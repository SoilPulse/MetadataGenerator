from soilpulse import db_access
import time


def test_initDB():

    def get_tables_of_DB():
        # get list of tables in DB
        db = db_access.DBconnector()
        cnx = db.db_connection
        cursor = cnx.cursor()
        cursor.execute("SHOW TABLES")
        result = cursor.fetchall()
        results = [r[0] for r in result]
        print(results)
        return results

    results = get_tables_of_DB()

    if 'containers' not in results:
#    if True:
        with open("./database/soilpulse.sql", "r") as file:
            sql = file.read()

        print(sql[0:100])

        # init DB
        db = db_access.DBconnector()
        cnx = db.db_connection
        cursor = cnx.cursor()
        cursor.execute(sql)
        cursor.fetchall()
        cursor.close()

        # wait for DB to be set up
        time.sleep(5)

        results = get_tables_of_DB()

    assert 'containers' in results


def test_getUser():
    db = db_access.DBconnector()
    user = db.getUserNameByID(1)
    assert (user[0][0] == 'D' and user[1][0] == 'U')
