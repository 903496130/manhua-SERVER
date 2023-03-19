import datetime
import json
import os
import re
import time
import urllib
import threading
import sys
import requests
import web
from bs4 import BeautifulSoup as bs

import table
from mysql import connector as mc

default_encoding = 'utf-8' 
version = ''
info = ''

urls = (
    '/','login',
    '/course','course',
    '/feedback','feedback',
    '/download','download',
    '/update','update',
    "/login","login",
    "/show","show",
    "/fb","fb",
)
app = web.application(urls, globals())
path = os.path.abspath(os.path.dirname(__file__))
render = web.template.render(path + '/html/')


def count():
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'kb')
    ch = db.cursor()
    ch.execute("select COUNT(id) from feedback;")
    result = ch.fetchone()[0]
    db.close()
    return result

def count2():
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'kb')
    ch = db.cursor()
    ch.execute("select COUNT(id) from user;")
    result = ch.fetchone()[0]
    db.close()
    return result

def getTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def read():
    global version,info
    path = os.path.dirname(__file__) + "/file/update.txt"
    with open(path,'r',encoding='UTF-8-sig') as f:
        arr = f.read().split("\n")

        version = arr[0].replace("\n","")
        info = "\n".join(arr[1:])


class fb:
    def GET(self):
        return render.feedback()
        

class show:
    def GET(self):
        return render.show()

class login:
    def GET(self):
        return render.login()
     
class feedback:
    def GET(self):
        string = "服务器收到了你的反馈（＾_＾）"
        title = web.input().get('title')
        content = web.input().get('content')
        contact = web.input().get('contact')
        # db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'kb')
        # ch = db.cursor()
        # sql = 'insert into feedback (id,title,content,contact,time) values ({},"{}","{}","{}","{}");'.format(count(),title,content,contact,getTime())
        # ch.execute(sql)
        # db.commit()
        # db.close()
        return json.dumps({'status':'success','info':string})

class update:
    def GET(self):
        num = web.input()['version']
        read()
        if int(num) < int(version):
            return json.dumps({
                'status':'no',
                'info':info
            })
        return json.dumps({'status':'yes'})

class download:
    def GET(self):
        web.header('Content-Disposition','attachment;filename=' + urllib.parse.quote("update.wgt"))
        path = os.path.dirname(__file__) + "/file/update.wgt"
        size = os.path.getsize(path)
        web.header('content-length',str(size))
        f = open(path,"rb")
        return f.read()
       
class course:
    def GET(self):
        username = web.input().get('username')
        password = web.input().get('password')
        if username == "123":
            username = "2017011295"
            password = "asdfg456123.."
        # db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'kb')
        # ch = db.cursor()
        # sql = 'select * from user where account={}'.format(username)
        # ch.execute(sql)
        # tag = 1
        # for i in ch:
        #     tag = 0
        #     break
        # if tag:
        #     sql = 'insert into user (id,account) values ({},{});'.format(count2(),username)
        #     ch.execute(sql)
        # db.commit()
        # db.close()
        return table.get(username,password)

if __name__ == "__main__":
    #read()
    sys.argv.append("8848")
    app.run()
    #print(table.get('2017011295','asdfg456123..',3))



'''
create table feedback(
    id int  primary key not null,
     title varchar(60) not null,
     content varchar(600) not null,
     contact varchar(60),
     time  varchar(20) not null
);

create table user(
    id int primary key,
    account int not null;
);


'''
