import requests
from bs4 import BeautifulSoup as bs
import os
from langconv import *
import mysql.connector as mc
import random
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import re

thread_num = 10
#path = os.path.abspath(os.path.dirname(__file__))
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
root = 'http://99.hhxxee.com'


# 随机生成一个漫画id
def getId():
    db = mc.connect(host='localhost',
                    user='root',
                    passwd='wodemima',
                    database='manhua')
    commander = db.cursor()
    id = random.randint(10000, 999999)
    sql = "select name from list where mhid={};".format(id)
    commander.execute(sql)
    if commander.fetchone() == None:
        db.close()
        return id
    else:
        db.close()
        return getId()


# 获取members数


def getMembers(mhid):
    db = mc.connect(host='localhost',
                    user='root',
                    passwd='wodemima',
                    database='manhua')
    ch = db.cursor()
    sql = "select count(*) from chapter where mhid={};".format(mhid)
    ch.execute(sql)
    num = ch.fetchone()[0]
    db.close()
    return num


# 获取网页文本
def getHtml(url, times=[]):
    if times == []:
        times = 1
    if times > 10:
        return None
    try:
        req = requests.get(url)
        req.encoding = 'utf-8'
        html = etree.HTML(req.text)
        return html
    except:
        return getHtml(url, times + 1)


# 运行sql语句


def runSql(sql):
    sql = turn(sql)
    db = mc.connect(host='localhost',
                    user='root',
                    passwd='wodemima',
                    database='manhua')
    ch = db.cursor()
    ch.execute(sql)
    db.commit()
    db.close()


# 将繁体转换成简体


def turn(line):
    line = Converter('zh-hans').convert(line)
    return line


# 下载封面


def getCover(mhid, url):
    pic_path = path + '/static/cover/{}.jpg'.format(mhid)
    if not os.path.exists(pic_path):
        req = requests.get(url)
        with open(pic_path, 'wb') as f:
            f.write(req.content)
        print("{}封面缓存成功".format(mhid))

def jump(url, title, page):
    print("开始加载第{}页的{}从{}".format(page, title, url))
    getInfo(url)


# 获取漫画信息


def getInfo(url, update=[]):
    dom = getHtml(url)
    cover = dom.xpath(
        "/html/body/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/ul/li[1]/div[1]/img/@src"
    )[0]
    author = dom.xpath(
        "/html/body/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/ul/li[2]/ul/li[1]/a/text()"
    )[0]
    type = dom.xpath(
        "/html/body/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/ul/li[2]/ul/li[2]/a/text()"
    )[0]
    status = dom.xpath(
        "/html/body/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/ul/li[2]/ul/li[4]/b[2]/text()"
    )[0]
    create_date = dom.xpath(
        "/html/body/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/ul/li[2]/ul/li[6]/text()"
    )[0]
    update_date = dom.xpath(
        "/html/body/div[2]/div/div[5]/div/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/ul/li[2]/ul/li[8]/text()"
    )[0]
    jianjie = dom.xpath("//div[@class='cCon']/text()")[0].replace(
        " ",
        '').replace("\r",
                    "").replace("\n",
                                "").replace("\t",
                                            "").replace("\t",
                                                        "").replace("'", "")
    members = len(dom.xpath("//div[@class='cVolList']/div/a"))
    name = dom.xpath('//*[@id="titleDiv"]/h1/a/@title')[0]

    if update:
        mhid = update
        sql = "update list set author='{}',status='{}',members='{}',source='{}',name='{}',jianjie='{}',type='{}',create_date='{}',update_date='{}',cover='{}' where mhid='{}';".format(
            author, status, members, url, name, jianjie, type, create_date,
            update_date, cover, mhid)

        #getCover(mhid, cover)
        runSql(sql)
        getChapters(dom, mhid, update)
    else:
        mhid = getId()
        sql = "insert into list (mhid,author,status,members,source,name,jianjie,position,visible,type,create_date,update_date,cover) values ({},'{}','{}',{},'{}','{}','{}',0,1,'{}','{}','{}','{}');".format(
            mhid, author, status, members, url, name, jianjie, type,
            create_date, update_date, cover)
        getCover(mhid, cover)
        runSql(sql)
        getChapters(dom, mhid)


# 获取章节列表
def getChapters(dom, mhid, update=[]):
    link = dom.xpath("//div[@class='cVolList']//a")[::-1]
    if update:
        members = getMembers(mhid)
        if len(link) == members:
            #print("{}无需更新".format(mhid))
            return
        else:
            print("检测到漫画更新，id={},新增章节数量={}".format(mhid, members))

    with ThreadPoolExecutor(thread_num) as t:
        for i in range(len(link)):
            try:
                name = link[i].text
                url = root + link[i].get('href')
                sql = "insert into chapter (mhid,zjid,name,url) values ({},{},'{}','{}');".format(
                    mhid, i, name, url)
                runSql(sql)
                # getPic(mhid,i,url)
                t.submit(getPic, mhid, i, url)
            except:
                pass


# 保存图片信息
def getPic(mhid, zjid, url):
    dom = getHtml(url)
    try:
        sc = dom.xpath('//script')[0].text
        match = re.match('var sFiles="(.*)";var sPath="(\d*)";', sc)
        num = int(match.groups()[1])
        if num < 10:
            num = "0" + str(num)
        else:
            num = str(num)
        link = match.groups()[0].split("|")
        for i in range(len(link)):
            pic = 'http://99.94201314.net/dm{}/{}'.format(num, link[i])
            sql = 'insert into url (mhid,zjid,tpid,url) values ({},{},{},"{}");'.format(
                mhid, zjid, i, pic)
            # print(sql)
            runSql(sql)
    except:
        pass


# 更新漫画


def update(mhid):
    db = mc.connect(host='localhost',
                    user='root',
                    passwd='wodemima',
                    database='manhua')
    ch = db.cursor()
    sql = 'select source from list where mhid={};'.format(mhid)
    ch.execute(sql)
    url = ch.fetchone()[0]
    getInfo(url, mhid)


if __name__ == "__main__":
    url = "http://99.hhxxee.com/comic/9929411/"
    # getPic(123,2,'http://99.hhxxee.com/comics/2779o286340/')
    # getInfo(url)
    update(10050)
