from soilpulse import db_access

with open("./database/soilpulse.sql", "r") as file:
    sql = file.read()

def test_initDB():
    #init DB
    db = db_access.DBconnector()
    cnx = db.db_connection
    cursor = cnx.cursor()

    cursor.execute(sql)
    cursor.fetchall()
    cursor.close()

    # get list of tables in DB
    db = db_access.DBconnector()
    cnx = db.db_connection
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()
    results = [r[0] for r in result]

    assert 'containers' in results

def test_getUser():
    db = db_access.DBconnector()
    user = db.getUserNameByID(1)
    assert user == ('Jan', 'DevÃ¡tÃ½')
