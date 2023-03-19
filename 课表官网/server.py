import os
import web
import urllib
import time

default_encoding = 'utf-8' 
version = '1'
info = '更新了课程显示异常的问题'

urls = (
    '/','index',
    '/download','download',
    '/source/(.*)','source'
)

app = web.application(urls, globals())
render = web.template.render(os.path.dirname(__file__) + '/html/')

def read():
    with open(os.path.dirname(__file__) + '/filename.txt','r',encoding='utf-8') as f:
        return f.read()

class index:
    def GET(self):
        agent = web.ctx.env.get("HTTP_USER_AGENT")
        if 'micromessenger' in str(agent).lower():
            return render.index(1)
        else:
            return render.index(0)

class download:
    def GET(self):
        web.header('Content-Disposition','attachment;filename=' + urllib.parse.quote(read()))
        path = os.path.dirname(__file__) + "/apk.apk"
        size = os.path.getsize(path)
        web.header('content-length',str(size))
        f = open(os.path.dirname(__file__) + "/apk.apk","rb")
        return f.read()


class source:
    def GET(self,url):
        #web.header('content-type','image/jpeg')
        fname = os.path.dirname(__file__) + '/source/' + url
        if os.path.isfile(fname):
            f = open(fname,'rb')
            return f.read()
        else:
            return ''

if __name__ == "__main__":
    app.run()
    thread
    #print(table.get('2017011295','asdfg456123..',3))
