import mysql.connector as mc

def getId():
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    commander = db.cursor()
    for i in range(10000):
        sql = "select name from list where mhid={};".format(i + 10000)
        commander.execute(sql)
        if commander.fetchone() == None:
            db.close()
            return i + 10000

def jh(name):
    print("开始运行，参数=" + name)
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    print("检查重复聚合")
    ch.execute('select * from list where name="{}";'.format(name))
    a = ch.fetchone()
    if a != None:
        print("检查未通过，聚合已经存在")
        return
    print("检查通过,开始查找关键字")
    sql = 'select mhid,name,source from list where name like "%{}%";'.format(name)
    ch.execute(sql)
    all = ch.fetchall()
    if len(all) == 0:
        print("聚合结果为空，聚合取消")
        return
    print("查找到{}个结果,删除旧数据".format(len(all)))
    ch.execute('delete from list where name like "%{}%";'.format(name))
    db.commit()
    id = getId()
    print("获取到新的id：{}".format(id))
    sql = "insert into list (mhid,author,status,members,source,name,jianjie,visible,position) values ({},'群星','完结','{}','{}','{}','无',1,1)".format(id,len(all),name,name)
    print('插入新数据' + sql)
    ch.execute(sql)
    db.commit()
    for i in range(len(all)):
        mhid = all[i][0]
        name = all[i][1]
        source = all[i][2]
        print("处理章节:" + name + "," + str(mhid))
        sql = "update chapter set mhid={},zjid={},name='{}',url='{}' where mhid={};".format(id,i,name,source,mhid)
        print("更新章节数据" + sql)
        ch.execute(sql)
        sql = 'update url set mhid={},zjid={} where mhid={};'.format(id,i,mhid)
        print("更新图片数据" + sql)
        ch.execute(sql)
        db.commit()
    print('=====================聚合成功=====================')
    db.close()

if __name__ == "__main__":
    jh('都市记事录')