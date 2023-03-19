import mysql.connector as mc


if __name__ == "__main__":
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    ch2 = db.cursor()

    sql = 'select mhid from list where name like "%喜欢%";'
    ch.execute(sql)
    ch2.execute(sql)

    print(1)

