import mysql.connector as mc


def rmAll():
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    sql = "delete from list;"
    ch.execute(sql)
    sql = "delete from chapter;"
    ch.execute(sql)
    sql = "delete from url;"
    ch.execute(sql)
    db.commit()
    db.close()

if __name__ == "__main__":
    #if input("即将清空数据库，确定请输入确定:") == "确定":
    rmAll()
    
