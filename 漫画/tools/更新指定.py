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

def update(mhid):
    try:
        hxe.update(mhid)
    except:
        print(traceback.format_exc())


if __name__ == "__main__":
    id = eval(input("请输入指定漫画id:"))
    update(id)


