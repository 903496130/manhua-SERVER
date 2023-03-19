import os
import time
import mysql.connector as mc
import shutil

db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
ch = db.cursor()

run_dir = os.path.abspath(os.path.dirname(__file__))
dir = run_dir + "/source/download/"

def deleteSql(mhid):
    sql = "delete from url where mhid={};".format(mhid)
    ch.execute(sql)
    db.commit()
    sql = "delete from chapter where mhid={};".format(mhid)
    ch.execute(sql)
    db.commit()
    sql = "delete from list where mhid={};".format(mhid)
    ch.execute(sql)
    db.commit()

def check(mhid):
    sql = 'select mhid from list where mhid={};'.format(mhid)
    ch.execute(sql)
    if ch.fetchone() == None:
        return 1
    else:
        return 0

def deleteDir(mhid):
    shutil.rmtree(dir + str(mhid))

def checkFileSize(mhid):
    path = dir + str(mhid) + "/0.jpg"
    if os.path.exists(path) == False:
        print("文件不存在:" + path)
        return 1
    fsize = os.path.getsize(path)
    fsize = fsize / float(1024)
    if fsize < 10:
        return 1
    else:
        return 0

if __name__ == "__main__":
    dirs = os.listdir(dir)
    for i in dirs:
        if check(i):
            print("查找到不存在于数据库中的文件目录 - " + str(i))
            print("删除文件夹" + dir + str(i))
            deleteDir(i)
            print("删除数据库" + dir + str(i))
            deleteSql(i)
            print("==================================")
            
        if checkFileSize(i):
            print("查找到异常的文件目录 - " + str(i))
            print("删除文件夹" + dir + str(i))
            deleteDir(i)
            print("删除数据库" + dir + str(i))
            deleteSql(i)
            print("==================================")


    time.sleep(1000)
