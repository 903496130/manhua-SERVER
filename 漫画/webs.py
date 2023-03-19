import json
import os
import random
import threading
import time
import sys
import mysql.connector as mc
import web

default_encoding = 'utf-8'
debug = 0

urls = (
    #页面区
    '/','index',  #主页
    '/search','search',  #搜索接口
    '/(\d+)','table',  #漫画章节列表展示
    '/(\d+)/(\d+)','show',  #章节图片展示
    '/error','error',  #404
    '/introduce','introduce',  #介绍
    '/type','type1',  #分类
    '/demo','demo',  #分类

    #接口区
    '/tips','getTips'  #获取搜索提示
)

app = web.application(urls, globals())
a = {'mc': mc}
path = os.path.abspath(os.path.dirname(__file__))

pc = web.template.render(path + '/html/pc', base='mb', globals=a)
mobile = web.template.render(path + '/html/mobile', globals=a)


def notfound():
    return web.notfound(render.error())
    # You can use template result like below, either is ok:
    #return web.notfound(render.notfound())
    #return web.notfound(str(render.notfound()))


#app.notfound = notfound
#app.error = notfound


#==================================公共函数区==================================
def checkValue(*data):
    arr = ["'", "-", '"', "\n", "\r"]
    for i in data:
        for char in arr:
            if char in i:
                return True
    return False


#=====================================结束=====================================

#==================================页面区==================================


#错误页面
class error:
    def GET(self):
        agent = web.ctx.env.get("HTTP_USER_AGENT") or ''
        if 'Mobile' in agent:
            return mobile.error()
        else:
            return pc.error()

#首页
class index:
    def GET(self):
        agent = web.ctx.env.get("HTTP_USER_AGENT") or ''
        if 'Mobile' in agent:
            return mobile.index()
        else:
            return pc.index()


#章节显示页
class table:
    def GET(self, mhid):
        agent = web.ctx.env.get("HTTP_USER_AGENT") or ''
        if 'Mobile' in agent:
            return mobile.table(mhid)
        else:
            return pc.table(mhid)


#图片显示页
class show:
    def GET(self, mhid, zjid):
        agent = web.ctx.env.get("HTTP_USER_AGENT") or ''
        if 'Mobile' in agent:
            return mobile.show(mhid, zjid)
        else:
            return mobile.show(mhid, zjid)


#类别显示页
class type1:
    def GET(self):
        type = web.input().get("type") or '全部'
        order = web.input().get("order") or 'members'
        how = web.input().get("how") or 'desc'
        page = web.input().get("page") or '1'
        typeString = '亲情,全部,伪娘,侦探,冒险,剧情,厨艺,图片,小说,惊栗,成人,搞笑,日文,校园,格斗,欧美,港漫,神鬼,科幻,竞技,经典,耽美,萌系,魔法'
        orderString = 'hot,members,update_date'
        howString = 'descasc'
        if checkValue(type, order, how, page) or not page.isdigit(
        ) or type not in typeString or order not in orderString or how not in howString:
            return ''
        else:
            agent = web.ctx.env.get("HTTP_USER_AGENT") or ''
            if 'Mobile' in agent:

                return mobile.type(type, order, how, int(page))

            else:
                return pc.type(type, order, how, int(page))

#漫画随机推荐页
class introduce:
    def GET(self):
        where = web.input().get("where") or 0
        return mobile.introduce(where)

#搜索页
class search:
    def GET(self):
        name = web.input().get("name")
        page = web.input().get("page") or '1'
        if name == None:
            return mobile.search_index()

        if checkValue(page,name) or not page.isdigit():
            return web.error(mobile.error)


        #value处理
        arr = name.split(' ')
        string = ''
        for i in arr:
            if i != '':
                string += '+{} '.format(i)

        return mobile.search(string, int(page))


#=================================页面区结束=================================

#WITH PARSER ngram

#==================================接口区==================================


#资源获取接口
class source:
    def GET(self, url):
        #web.header('content-type','image/jpeg')
        try:
            ps = path + '/source/' + url
            if os.path.exists(ps):
                with open(ps, 'rb') as f:
                    return f.read()
        except:
            return ''


#获取漫画名提示接口
class getTips():
    def GET(self):
        value = web.input().get("value").replace("  ", " ").replace("'", "")
        arr = value.split(' ')
        string = ''
        for i in arr:
            if i != '':
                string += '+{} '.format(i)
        db = mc.connect(host='localhost',
                        user='root',
                        passwd='wodemima',
                        database='manhua')
        ch = db.cursor()
        sql = "select SQL_CALC_FOUND_ROWS name,mhid from list where match(name) against('{}' IN BOOLEAN MODE) limit 10;".format(
            string)
        ch.execute(sql)
        result = ch.fetchall()
        sql = 'SELECT FOUND_ROWS();'
        ch.execute(sql)
        count = ch.fetchone()[0]
        db.close()
        return json.dumps({'result': result, 'count': count})


#==================================接口区结束==================================

if __name__ == "__main__":
    sys.argv.append("80")
    app.run()
