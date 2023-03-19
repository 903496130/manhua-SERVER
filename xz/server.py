import json
import os
import random
import threading
import time
import uuid

import mysql.connector as mc
import qrcode
import requests
import web

import 教务处 as jwc

default_encoding = 'utf-8'
web.config.debug = False
out_code = '1234'
in_code = '456'
fresh = 8

urls = (
    #页面区
    '/','index',  #主页
    '/choose','choose',  #主页
    '/login','login',  #主页
    '/out','goPage',  #主页
    '/in','backPage',  #主页
    '/getout','getOutPic',  #主页
    '/getin','getInPic',  #主页
    '/getout1/(.*)','getOutPic1',  #主页
    '/getin1/(.*)','getInPic1',  #主页
    '/regout','regout',
    '/regin','regin',
    '/checkNew','checkOpenId',
    '/reg','reg',
    '/history','getHistory',
    '/book','book',
    '/move','move',
    '/logout','logout'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count':'0'})
a = {'mc': mc}
path = os.path.abspath(os.path.dirname(__file__))
pc = web.template.render(path + '/html/', globals=a)

count_list = {
    "1234":"123",
    "456":"456"
    }


def getDate():
    arr = str(time.strftime("%Y-%m-%d"))
    return arr

def getHours():
    arr = str(time.strftime("%H:%M:%S"))
    return arr

def getOutCode():
    global out_code
    while True:
        code = str(uuid.uuid1())[0:5]
        qr = qrcode.QRCode(     
            version=1,     
            error_correction=qrcode.constants.ERROR_CORRECT_H,     
            box_size=10,     
            border=4, 
        ) 
        qr.add_data(code) 
        qr.make(fit=True)  
        img = qr.make_image()
        img.save('out.png')
        out_code = code
        time.sleep(fresh)

def getInCode():
    global in_code
    while True:
        code = str(uuid.uuid1())[0:5]
        qr = qrcode.QRCode(     
            version=1,     
            error_correction=qrcode.constants.ERROR_CORRECT_H,     
            box_size=10,     
            border=4, 
        ) 
        qr.add_data(code) 
        qr.make(fit=True)  
        img = qr.make_image()
        img.save('in.png')
        in_code = code
        time.sleep(fresh)

def getOpenId(code):
    appid = "wxf84e1756895c9507"
    secret = '0b304684179c5d7442fa6d68506c48e9'
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(appid,secret,code)
    req = requests.get(url)
    data = json.loads(req.text)
    return code

def getName(openid):
    db = mc.connect(host='localhost',
                    user='root',
                    passwd='wodemima',
                    database='xz')
    ch = db.cursor()
    sql = 'select xh,name from reg where openid="{}";'.format(openid)
    ch.execute(sql)
    result = ch.fetchone()
    db.close()
    return result

class index:
    def GET(self):
        return pc.index()

class login:
    def GET(self):
        username = web.input().get("username")
        password = web.input().get("password")
        if username == None or password == None:
            return 'fail'
        elif count_list.get(username) == password:
            session.count = username
        if session.get('count') not in ['0',None]:
            return 'success'
        else:
            return 'fail'

class choose:
    def GET(self):
        if session.get('count') not in ['0',None]:
            return pc.choose()
        else:
            return pc.login()

class getOutPic:
    def GET(self):
        if session.get('count') not in ['0',None]:
            with open("out.png",'rb') as f:
                return f.read()
        else:
             return pc.login()


class getInPic:
    def GET(self):
        if session.get('count') not in ['0',None]:
            with open("in.png",'rb') as f:
                return f.read()
        else:
            return pc.login()

class getOutPic1:
    def GET(self,random):
        openid = getOpenId(web.input().get('login_code')) or "1"
        if openid == '1':
            return ""
        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()
        sql = 'select admin from reg where openid = "{}";'.format(openid)
        ch.execute(sql)
        result = ch.fetchone()
        if result == None:
            return ""
        if result[0] in [1,'1']:
            with open("out.png",'rb') as f:
                return f.read()
        return ""
        

class getInPic1:
    def GET(self,random):
        openid = getOpenId(web.input().get('login_code')) or "1"
        if openid == '1':
            return ""
        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()
        sql = 'select admin from reg where openid = "{}";'.format(openid)
        ch.execute(sql)
        result = ch.fetchone()
        if result == None:
            return ""
        if result[0] in [1,'1']:
            with open("in.png",'rb') as f:
                return f.read()
        return ""


class goPage:
    def GET(self):
        if session.get('count') not in ['0',None]:
            return pc.goout()
        else:
            return pc.login()

class backPage:
    def GET(self):
        if session.get('count') not in ['0',None]:
            return pc.goin()
        else:
             return ''

class book:
    def GET(self):
        openid = getOpenId(web.input().get('login_code')) or "1"
        if openid == '1':
            return json.dumps({'info':"用户验证失败","code":"10"},ensure_ascii=False)

        xh,name = getName(openid)

        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()
        
        sql = 'select * from reg where openid="{}" and xh = "{}";'.format(openid,xh)
        ch.execute(sql)
        
        if ch.fetchone() != None:
            sql = 'select * from book where xh="{}" and date="{}";'.format(xh,getDate())
            ch.execute(sql)
            if ch.fetchone() != None:
                #说明已经预约过了
                db.close()
                return json.dumps({'info':"今天已经预约过了","code":"7"},ensure_ascii=False)
            else:
                sql = "insert into book (xh,date,name) values ('{}','{}','{}');".format(xh,getDate(),name);
                ch.execute(sql)
                db.commit()
                db.close()
                return json.dumps({'info':"预约成功。","code":"6"},ensure_ascii=False)
        else:
            db.close()
            return json.dumps({'info':"用户认证失败或过期，请重新登录。","code":"4"},ensure_ascii=False)

class move:
    def GET(self):
        openid = getOpenId(web.input().get('login_code')) or "1"
        code = web.input().get('code') or ""
        if openid == '1':
            return json.dumps({'info':"用户验证失败","code":"10"},ensure_ascii=False)
        xh,name = getName(openid)
        
        head = "姓名:{}\n学号:{}\n当前时间:{}\n".format(name,xh,getHours())

        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()
        sql = 'select * from reg where openid="{}" and xh = "{}";'.format(openid,xh)
        ch.execute(sql)
        
        if ch.fetchone() != None:#检测登陆是否有效
            #检查是否预约
            sql = 'select out_time,in_time from book where date="{}" and xh="{}";'.format(getDate(),xh)
            ch.execute(sql)
            result = ch.fetchone()
            if result == None:
                db.close()
                return json.dumps({'info':"请先预约。","code":"5"},ensure_ascii=False)
            if code == out_code and result[0] == None and result[1] == None:
                sql = 'update book set out_time = "{}" where xh="{}" and date="{}";'.format(getHours(),xh,getDate())
                ch.execute(sql)
                db.commit()
                db.close()
                return json.dumps({"code":"1","xh":xh,'name':name,"time":getHours()},ensure_ascii=False)
            elif code == in_code and result[0] != None and result[1] == None:
                sql = 'update book set in_time = "{}" where xh="{}" and date="{}";'.format(getHours(),xh,getDate())
                ch.execute(sql)
                db.commit()
                db.close()
                return json.dumps({"code":"2","xh":xh,'name':name,"time":getHours()},ensure_ascii=False)
            else:
                db.close()
                return json.dumps({'info':"数据无效.\n1.二维码过期，请重新扫描\n2.无法重复进出校。\n3.应先扫描出校码，再扫描入校码。","code":"3"},ensure_ascii=False)
        else:
            db.close()
            return json.dumps({'info':"用户认证失败或过期，请重新登录。","code":"4"},ensure_ascii=False)

class checkOpenId():
    def GET(self):
        openid = getOpenId(web.input().get('login_code')) or "1"
        if openid == '1':
            return json.dumps({'status':"fail"})
        db = mc.connect(host='localhost',
                        user='root',
                        passwd='wodemima',
                        database='xz')
        ch = db.cursor()
        sql = 'select xh,admin from reg where openid = "{}";'.format(openid)
        ch.execute(sql)
        result = ch.fetchone()
        if result == None:
            db.close()
            return json.dumps({"isNew":"true"})
        else:
            xh = result[0]
            admin = result[1]
            if count_list.get(str(xh)) == None and admin in [1,"1"]:
                print(count_list,xh,admin)
                sql = 'delete from reg where openid="{}";'.format(openid)
                ch.execute(sql)
                db.commit()
                db.close()
                return json.dumps({"isNew":"true"})
            else:
                db.close()
                return json.dumps({"isNew":"false","admin":admin})

class reg():
    def GET(self):
        admin = web.input().get('admin') or '0'
        openid = getOpenId(web.input().get('login_code')) or "1"
        username = web.input().get('username') or ""
        password = web.input().get('password') or ""
       
        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()

        if openid == '1':
            return json.dumps({'status':"fail"})

        if admin in [0,"0"]:
            name = jwc.getName(username,password)
            print(name)
            if name != 'fail':
                sql = 'delete from reg where xh = {};'.format(username)
                ch.execute(sql)
                db.commit()
                ch = db.cursor()
                sql = 'delete from reg where openid = "{}";'.format(openid)
                ch.execute(sql)
                db.commit()
                sql = 'insert into reg (xh,openid,name) values ({},"{}","{}");'.format(username,openid,name)
                ch.execute(sql)
                db.commit()
                db.close()
                return json.dumps({'status':"success",'name':name,'xh':username,'admin':str(admin)})
            return {'status':"fail"}
        elif admin in [1,'1']:
            name = '管理员'
            if count_list.get(username) == password:
                sql = 'delete from reg where openid = "{}";'.format(openid)
                ch.execute(sql)
                db.commit()
                sql = 'insert into reg (xh,openid,name,admin) values ({},"{}","{}",1);'.format(username,openid,name)
                ch.execute(sql)
                db.commit()
                db.close()
                return json.dumps({'status':"success",'name':name,'xh':username,'admin':str(admin)})
            else:
                return {'status':"fail"}
        return {'status':"fail"}


class getHistory():
    def GET(self):
        openid = getOpenId(web.input().get('login_code')) or "1"
        if openid == '1':
            return json.dumps({'status':"fail"})
        
        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()
        xh,name = getName(openid)
        if name != None:
            sql = 'select date,out_time,in_time from book where xh="{}" order by date;'.format(xh)
            ch.execute(sql)
            result = ch.fetchall()
            db.close()
            return json.dumps({"status":'success',"data":result,"xh":xh,"name":name})
        else:
            db.close()
            return json.dumps({"status":'fail'})

class logout:
    def GET(self):
        openid = getOpenId(web.input().get('login_code')) or "1"
        db = mc.connect(host='localhost',
            user='root',
            passwd='wodemima',
            database='xz')
        ch = db.cursor()
        sql = 'delete from reg where openid="{}";'.format(openid)
        ch.execute(sql)
        db.commit()
        db.close()

if __name__ == "__main__":
    t1 = threading.Thread(target=getInCode)
    t1.start()
    t2 = threading.Thread(target=getOutCode)
    t2.start()
    app.run()
    t1.join()
    t2.join()
