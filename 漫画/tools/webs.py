import json
import os
import random
import threading
import time

import mysql.connector as mc
import web

import hxe
import jh

default_encoding = 'utf-8'
debug = 0

urls = (
    #页面区
    '/','index',#导航页
    '/main','main',#主页
    '/search','search',#搜索接口
    '/(\d+)','table', #漫画章节列表展示
    '/(\d+)/(\d+)','show',#章节图片展示
    '/error','error',#404
    '/introduce','introduce',#介绍
    '/type','type1',#分类
    '/demo','demo',#分类


    #接口区
    '/update','update',#漫画更新
    '/tips','getTips',#获取搜索提示

    #资源接口
    '/static','source'

)

app = web.application(urls, globals())
a = {'mc': mc}
path = os.path.abspath(os.path.dirname(__file__))
render = web.template.render(path + '/html/',globals = a)

def notfound():
    return web.notfound(render.error())
    # You can use template result like below, either is ok:
    #return web.notfound(render.notfound())
    #return web.notfound(str(render.notfound()))

app.notfound = notfound
app.error = notfound

#==================================公共函数区==================================
def runSql(sql):
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    ch.execute(sql)
    result = ch.fetchall()
    db.close()
    return result

def getId():
    id = random.randint(10000,999999)
    sql = "select name from list where mhid={};".format(id)
    commander = runSql(sql)
    if commander.fetchone() == None:
        return id
    else:
        return getId()

#=====================================结束=====================================


#==================================页面区==================================

#错误页面
class error:
    def GET(self):
        return render.error()


class demo:
    def GET(self):
        return render.demo()


#导航页
class index:
    def GET(self):
        return render.index()

#99漫画页
class main:
    def GET(self):
        page = web.input().get("page")
        if page == None:
            page = '1'
        #return render.main(int(page),position_0)
        return render.main()

#类别显示页
class type1:
    def GET(self):
        type = web.input().get("type") or '剧情'
        page = web.input().get('page') or 1
        type = type.replace(" ",'').replace("-","")
        page = int(page)
        return render.type(page,type)

#章节显示页
class table:
    def GET(self,id):
        return render.table(id)

#图片显示页
class show:
    def GET(self,id1,id2):
        return render.show(id1,id2)


#漫画随机推荐页
class introduce:
    def GET(self):
        where = web.input().get("where") or 0
        return render.introduce(where)

#搜索页
class search:
    def GET(self):
        name = web.input().get("name")
        page = web.input().get("page") or '1'
        where = web.input().get("where") or '0'
        if name == None:
            return render.search_index(where)
        if page.isdigit():
            page = int(page)
        if int(page) <= 0:
            return render.error()

        if where not in ['0','1'] :
            return render.error()

        #value处理
        arr = name.split(' ')
        string = ''
        for i in arr:
            if i != '':
                string += '+{} '.format(i)

        return render.search(string,page,where)


#=================================页面区结束=================================

#WITH PARSER ngram

#==================================接口区==================================

#资源获取接口
class source:
    def GET(self,url):
        #web.header('content-type','image/jpeg')
        try:
            ps = path + '/source/' + url
            if os.path.exists(ps):
                with open(ps,'rb') as f:
                    return f.read()
        except:
            return ''

#获取漫画名提示接口
class getTips():
    def GET(self):
        value = web.input().get("value").replace("  "," ").replace("'","")
        where = web.input().get("where") or 1
        arr = value.split(' ')
        string = ''
        for i in arr:
            if i != '':
                string += '+{} '.format(i)
        db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
        ch = db.cursor()
        sql = "select SQL_CALC_FOUND_ROWS name,mhid from list where match(name) against('{}' IN BOOLEAN MODE) and position={} limit 10;".format(string,where)
        ch.execute(sql)
        result = ch.fetchall()
        sql = 'SELECT FOUND_ROWS();'
        ch.execute(sql)
        count = ch.fetchone()[0]
        db.close()
        return json.dumps({'result':result,'count':count})

#漫画更新
class update:
    def GET(self):
        id = web.input().get("id")
        try:
            id = int(id)
            return update1(id)
        except:
            return "更新出错或参数错误"

#更新漫画
def update1(id):
    try:
        t = threading.Thread(target=hxe.update,args=(id,))
        t.start()
        return "进入更新队列"
    except:
        return "更新出错"

#==================================接口区结束==================================

if __name__ == "__main__":

    app.run()
