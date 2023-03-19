import mysql.connector as mc
db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
ch = db.cursor()
sql = "delete from list where mhid not in (select mhid from url);"
ch.execute(sql)
db.commit()
sql = "delete from chapter where mhid not in (select mhid from url);"
ch.execute(sql)
db.commit()

sql = "delete from url where mhid not in (select mhid from list);"
ch.execute(sql)
db.commit()
sql = "delete from chapter where mhid not in (select mhid from list);"
ch.execute(sql)
db.commit()

db.close()
