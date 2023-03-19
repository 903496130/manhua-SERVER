import web
import os
import mysql.connector as mc
import math
import sys

default_encoding = 'utf-8'

urls = (
    '/', 'index',
    "/random", "random",
    "/show/(\d+)", "show",
)

app = web.application(urls, globals())
a = {'mc': mc}
path = os.path.abspath(os.path.dirname(__file__))
render = web.template.render(path + '/html/', globals=a)


class index:
    def GET(self):
        page = web.input().get("page") or "1"
        num = web.input().get("num") or "30"
        num = int(num)
        page = int(page)
        db = mc.connect(host='localhost', user='root',passwd='wodemima', database='hm')
        ch = db.cursor()
        sql = "select id,name,cover from list limit {},{}".format(num * (page - 1),num)
        ch.execute(sql)
        result = ch.fetchall()
        sql = "select count(*) from list where id != 0"
        ch.execute(sql)
        total = ch.fetchone()[0]
        total_page = math.ceil(total / num)
        db.close()

        return render.index(page,total_page,result)


class random:
    def GET(self):
        result = []
        db = mc.connect(host='localhost', user='root',passwd='wodemima', database='hm')
        ch = db.cursor()
        if web.input().get("type") == "pic":
            sql = "select url from url order by rand() limit 20 "
            ch.execute(sql)
            result = ch.fetchall()
            db.close()
            return render.random_pic(result)
        else:
            sql = "select id,name,cover from list order by rand() limit 20"
            ch.execute(sql)
            result = ch.fetchall()
            db.close()
            return render.random(result)

class show:
    def GET(self, id):
        db = mc.connect(host='localhost', user='root',passwd='wodemima', database='hm')
        ch = db.cursor()
        sql = "select name from list where id = {}".format(id)
        ch.execute(sql)
        name = ch.fetchone()[0]
        sql = "select url from url where id = {}".format(id)
        ch.execute(sql)
        result = ch.fetchall()
        db.close()
        return render.show(name,result)


if __name__ == "__main__":
    sys.argv.append("80")
    app.run()
