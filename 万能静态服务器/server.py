import web
import os
import sys

urls = (
    '(.*)', 'index'
)

path = os.path.abspath(os.path.dirname(__file__))

class index:
    def GET(self,a):
        try:
            if a == '/':
                file = path + "/index.html"
                print(file)
                with open(file,"rb") as f:
                    return f.read()
            file = path + a
            print(file)
            with open(path + a,"rb") as f:
                return f.read()
        except:
            return "404"




if __name__ == "__main__":
    sys.argv.append("80")
    app = web.application(urls, globals())
    app.run()
