import requests
from lxml import etree
import traceback
import mysql.connector as mc
import time
import random
from concurrent.futures import ThreadPoolExecutor

session = requests.session()

root = "https://www.4088877ca3e1ea03.com"


def getId():
    try:
        id = random.randint(1000,1000000)
        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='hm')
        ch = db.cursor()
        sql = "select * from list where id = {}".format(id)
        ch.execute(sql)
        result = ch.fetchall()
        db.close()
        if result != []:
            return getId()
        return id
    except:
        print("getid错误")
        traceback.print_exc()
    

def storeMh(id, cover, name):
    try:
        db = mc.connect(host='localhost',
                user='root',
                passwd='wodemima',
                database='hm')
        ch = db.cursor()
        sql = "select * from list where id = {} or name = '{}'".format(id,name)
        ch.execute(sql)
        if ch.fetchall() == []:
            sql = "insert into list (id,name,cover) values (%s,%s,%s)"
            ch.execute(sql,(id,name,cover,))
            db.commit()
        db.close()
    except:
        print("存储漫画失败！")
        traceback.print_exc()


def storePic(id,list):
    try:
        db = mc.connect(host='localhost',
                user='root',
                passwd='wodemima',
                database='hm')
        ch = db.cursor()
        sql = "select * from url where id = {}".format(id)
        ch.execute(sql)
        if ch.fetchall() == []:
            for i in range(len(list)):
                sql = "insert into url (id,num,url) values (%s,%s,%s)"
                ch.execute(sql,(id,i,list[i],))
                db.commit()
        db.close()
    except:
        print("存储图片失败！")
        traceback.print_exc()


def getPic(id,url):
    try:
        result = []
        req = requests.get(url)
        dom = etree.HTML(req.text)
        arr = dom.xpath("//div[@class='content']//img")
        cover = ""
        for i in range(len(arr)):
            url = arr[i].get("data-original")
            if i == 0:
                cover = url
            result.append(url)

        # print(result)
        storePic(id,result)
        return cover
    except:
        print("获取图片失败！")
        traceback.print_exc()
        
def getPage(num,name):
    try:
        # print(">>>>>>>>>>>>>>>>>>>>>正在获取第{}页内容".format(num))
        result = []
        url = root + "/tupian/list-{}-{}.html".format(name,num)
        req = session.get(url)
        req.encoding = "utf-8"
        dom = etree.HTML(req.text)
        arr = dom.xpath("//div[@class='box list channel max-border list-text-my']//ul//a")
        for i in arr:
            url = root + str(i.get("href"))
            title = i.get("title")
            result.append([title,url])
        
        for i in result:
            id = getId()
            url = i[1]
            title = i[0]
            print("{} - {}".format(title,url))
            cover = getPic(id,url)
            storeMh(id,cover,title)
            # t.submit(storeMh,id,cover,title)
    except:
        print("列表读取失败！")
        traceback.print_exc()
if __name__ == "__main__":
    with ThreadPoolExecutor(20) as t:
        for name in ["亚洲图片","欧美图片","偷拍自拍","乱伦熟女","精品套图","同性美图","美腿丝袜"]:
            for i in range(228):
                t.submit(getPage,i + 1,name)
    while True:
        time.sleep(1000)
    # getPic(1,"https://www.cdj7.com/tupian/96614.html")
    # print(getId())
