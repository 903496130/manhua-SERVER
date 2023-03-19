import hxe
from lxml import etree
import requests
import mysql.connector as mc
from concurrent.futures import ThreadPoolExecutor
import time

thread_num = 10
root = 'http://99.hhxxee.com'

def check(url):
    db = mc.connect(host = 'localhost',user = 'root',passwd = 'wodemima',database = 'manhua')
    ch = db.cursor()
    sql = 'select mhid from list where source="{}";'.format(url)
    ch.execute(sql)
    result = ch.fetchone()
    if result == None:#说明不存在重复
        return True
    else:

        #说明存在重复
        return False

if __name__ == "__main__":
    while True:
        url = 'http://99.hhxxee.com/lists/'
        dom = hxe.getHtml(url)
        print("正在获取最大页数")
        #maxpage = dom.xpath('/html/body/div/div/div[5]/div/div/div[2]/div[3]/div/div[1]/span/b[3]/text()')[0]
        maxpage = 20
        print("最大页数为{}".format(maxpage))
        #print(maxpage)
        for i in range(int(maxpage)):
            with ThreadPoolExecutor(thread_num) as t:
                i += 1
                print("正在获取第{}页漫画列表".format(i))
                url = 'http://99.hhxxee.com/lists/{}/'.format(i)
                dom = hxe.getHtml(url)
                arr = dom.xpath("//ul[@class='hd-txt TopList_11']/li/a")
                for m in arr:
                    title = m.get('title')
                    url = root + m.get('href')
                    if check(url):
                        t.submit(hxe.jump,url,title,i)
                        #hxe.getInfo(url)
        print("开始休眠")
        time.sleep(60*60*12)




