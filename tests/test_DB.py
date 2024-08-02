from soilpulse import db_access
import time


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
time.sleep(2)

db = db_access.DBconnector()
cnx = db.db_connection
cursor = cnx.cursor()
cursor.execute("SHOW DATABASES")
result = cursor.fetchall()
for r in result:
    print(r)
cursor.close()


def test_initDB():
    # get list of tables in DB
    db = db_access.DBconnector()
    cnx = db.db_connection
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    results = [r[0] for r in result]
    print(results)

    assert 'containers' in results


def test_getUser():
    db = db_access.DBconnector()
    user = db.getUserNameByID(1)
    assert (user[0][0] == 'J' and user[1][0] == 'D')
