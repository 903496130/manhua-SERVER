from concurrent.futures import ThreadPoolExecutor
import mysql.connector as mc
import traceback
import hxe
import os
import time

total = 0

def save(string):
    with open('error.txt','a',encoding='utf-8') as f:
        f.write(string)

def update(mhid, num):
    try:
        print("进度{:.2f}% ({}/{})...".format(num / int(total) * 100, num,total),end='\r')
        hxe.update(mhid)
    except:
        print(traceback.format_exc())


if __name__ == "__main__":
    while True:
        try:
            db = mc.connect(host='localhost',
                            user='root',
                            passwd='wodemima',
                            database='manhua')
            ch = db.cursor()
            sql = 'select count(*) from list where position=0 and status like "%连载%";'
            #sql = 'select count(*) from list where position=0;'
            ch.execute(sql)
            total = ch.fetchone()[0]

            sql = 'select mhid from list where position=0 and status like "%连载%";'
            #sql = 'select mhid from list where position=0 order by mhid desc;'
            ch.execute(sql)
            result = ch.fetchall()
            db.close()
            step = 40
            for i in range(0, len(result), step):
                with ThreadPoolExecutor(10) as t:
                    for m in range(step):
                        num = m + i
                        if num < total:
                            #update(result[m + i][0], num)
                            t.submit(update,result[num][0], num)
            print("开始休眠")
        except:
            save(traceback.format_exc())
        time.sleep(60*60*24)
