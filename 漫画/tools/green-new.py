import os
import time
import random
from concurrent.futures import ThreadPoolExecutor
import traceback
import mysql.connector as mc
import requests
import datetime
from bs4 import BeautifulSoup as bs
import threading

root = 'http://www.greenhangbao.com/'
local = True
run_dir = os.path.abspath(os.path.dirname(__file__))
thread_num = 20

page_now = 0
doing_list = []
done_list = []

def getId():
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    commander = db.cursor()
    id = random.randint(10000,999999)
    sql = "select name from list where mhid={};".format(id)
    commander.execute(sql)
    if commander.fetchone() == None:
        db.close()
        return id
    else:
        db.close()
        return getId()
    
def checkSource(url):
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    sql = 'select * from list where source="{}";'.format(url)
    ch.execute(sql)
    if ch.fetchone() != None:
        return 0
    sql = 'select * from chapter where url="{}";'.format(url)
    ch.execute(sql)
    if ch.fetchone() != None:
        db.close()
        return 0
    db.close()
    return 1

def checkName(name):
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    sql = 'select * from list where name="{}";'.format(name.replace("\"",""))
    ch.execute(sql)
    if ch.fetchone() != None:
        db.close()
        return 0
    sql = 'select * from chapter where name="{}";'.format(name.replace("\"",""))
    ch.execute(sql)
    if ch.fetchone() != None:
        db.close()
        return 0
    db.close()
    return 1

def saveErrorPage(page):#保存列表获取失败的页数
    with open("jao4-page-error.txt",'a',encoding='utf-8') as f:
        f.write(str(page) + "\n")

def saveErrorPicList(title,url,mhid,zjid):#保存获取图片列表失败的信息
    with open("jao4-chapter-error.txt",'a',encoding='utf-8') as f:
        f.write("{}-{}-{}-{}\n".format(title,url,mhid,zjid))

def saveErrorPic(url,mhid,zjid,tpid):#保存下载到本地失败的图片的信息
    with open("jao4-pic-error.txt",'a',encoding='utf-8') as f:
        f.write("{}-{}-{}-{}\n".format(url,mhid,zjid,tpid))

def errorlog(error):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("error_log.txt","a",encoding='utf-8') as f:
        f.write("【{}】{}\n".format(time,error))

def runSql(sql):
    try:
        db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
        ch = db.cursor()
        ch.execute(sql)
        db.commit()
        db.close()
    except:
        errorlog("数据库指令执行出错。\n执行语句：\n{}\n错误详细信息：\n{}".format(sql,traceback.format_exc()))

def saveList(mhid,title,url):
    sql = 'insert into list (mhid,name,source,author,status,jianjie,members,position) values ({},"{}","{}","群星","完结","无",1,1);'.format(mhid,title.replace("\"",""),url)
    runSql(sql)

def saveChapter(mhid,title):
    sql = 'insert into chapter (mhid,zjid,name) values ({},0,"{}");'.format(mhid,title)
    runSql(sql)

def saveUrl(mhid,zjid,tpid,picurl):
    sql = 'insert into url (mhid,zjid,tpid,url) values ({},{},{},"{}");'.format(mhid,zjid,tpid,picurl)
    runSql(sql)
   
def http(url,type=0):
    #type = 1说明下载图片，type = 0说明下载页面
    retry = 10 #重新连接次数
    result = ''
    for i in range(retry):
        try:
            result = requests.get(url,timeout = 10)
            result.encoding = 'utf-8'
            break
        except:
            if i >= retry - 1:
                if type == 0:
                    errorlog("http请求出错，url=" + url + "\n错误详细信息:\n" + traceback.format_exc())
                else:
                    errorlog("图片下载出错，url=" + url + "\n错误详细信息:\n" + traceback.format_exc())
                return ""
            else:
                print("加载链接超时，重新加载中（{}/{}）……".format(i + 1,retry))

    if type == 0:
        return result.text
    else:
        return result.content

def clear():
    global page_now,doing_list,done_list
    page_now = 0
    doing_list = []
    done_list = []

def getchapterlist(page):
    try:
        #===============自定义部位 获取章节列表==================
        url = 'http://www.greenhangbao.com/index.php/art/type/id/26/page/{}.html'.format(page)
        print("=================开始下载第{}页=================".format(page))
        html = http(url)
        if html == "":
            raise TypeError
        
        div = bs(html,'html.parser').find_all('div',class_="box list channel")
        li = bs(str(div[0]),'html.parser').find_all('ul')
        a = bs(str(li),'html.parser').find_all('a')
        #=========================end===========================
        with ThreadPoolExecutor(thread_num) as t:
            for each in a:
                title = each.text
                chapterurl = each.get('href')
                if checkName(title) and checkSource(chapterurl):#检查是否存在重名的章节或作品
                    mhid = getId()
                    saveList(mhid,title,chapterurl)
                    doing_list.append(title)
                    t.submit(getpiclist,chapterurl,title,mhid)
                else:
                    #存在同名
                    #print("{} - {}")
                    pass
    except:
        errorlog("作品列表获取失败，页数={}\n详细错误信息:\n{}".format(page,traceback.format_exc()))
        saveErrorPage(page)

def getpiclist(url,title,mhid):
    global doing_list,done_list
    #图片全部下载之前，保存章节信息
    saveChapter(mhid,title)
    try:
        html = http(root + url)
        if html == "":
            raise TypeError
        #===============自定义部位 获取图片信息==================
        div = bs(html,'html.parser').find_all('div',class_="content")
        img = bs(str(div),'html.parser').find_all('img')
        #=========================end===========================
        with ThreadPoolExecutor(thread_num) as t:
            for i in range(len(img)):

                #==================还有这里===================
                imgurl = img[i].get('src')
                #==================还有这里===================
                if local:
                    #本地保存
                    #savelocal(mhid,0,i,imgurl)
                    a = run_dir + "/source/download/" + str(mhid)
                    if not os.path.exists(a):
                        os.mkdir(a)
                    t.submit(savelocal,mhid,0,i,imgurl)
                else:
                    #盗链
                    saveUrl(mhid,0,i,imgurl)
            doing_list.remove(title)
            done_list.append(title)
    except:
        errorlog("图片列表获取失败，图片标题={}，url={}\n详细错误信息:\n{}".format(title,url,traceback.format_exc()))
        saveErrorPicList(title,url,mhid,0)
        
        
def savelocal(mhid,zjid,tpid,url):
    #将图片下载下来，储存内链
    try:
        dir = "/source/download/" + str(mhid)
        a = run_dir + dir
        pic = http(url,1)
        if pic == "":
            saveErrorPic(url,mhid,zjid,tpid)
        localpath = "/{}.jpg".format(tpid)
        with open(a + localpath,"wb") as f:
            f.write(pic)
        saveUrl(mhid,zjid,tpid,dir + localpath)
    except:
        errorlog("图片写入发生错误，mhid={},tpid={},url={}\n详细错误信息:\n{}".format(mhid,tpid,url,traceback.format_exc()))
        saveErrorPic(url,mhid,zjid,dir + tpid)
        
def show():
    while True:
        os.system('clear')
        string = "[{}]当前页数:{}\n".format(root,page_now)
        string += "下载完成的任务:\n" + '\n'.join(done_list)
        string += "\n\n=============================================\n\n当前页面正在进行的任务:\n" + '\n'.join(doing_list) + "\n"
        print(string)
        time.sleep(1)
       
if __name__ == "__main__":
    print("当前运行目录{}".format(run_dir))
    max_page = 83
    t = threading.Thread(target=show)
    t.setDaemon(True)
    t.start()
    for i in range(1,max_page + 1):
        clear()
        page_now = i
        getchapterlist(i)
    
    