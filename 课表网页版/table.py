import requests
from bs4 import BeautifulSoup as bs
import re
import json
import os
from datetime import datetime
from lxml import etree

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

root = '2020-02-24'

session = requests.session()

color={
    1:'#FFC125',#浅黄
    2:'#FF7256',#橙红
    3:'#8B2500',#黑红
    4:'#8470FF',#蓝紫
    5:'#765500',#淡绿
    6:'#000080',#深蓝
    7:'#66CDAA',#墨绿
    8:'#00BFFF',#天蓝
    0:'#5e3f44',#瞎编
}


dic = {"一":0,"二":1,"三":2,"四":3,"五":4,"六":5,"日":6}

def write(name,string):
    with open(name + ".txt",'w',encoding='utf-8') as f:
        f.write(str(string))
   

def read():
    with open("result.txt",'r',encoding='utf-8') as f:
        return f.read()

def getNumber(string):
    return re.findall(r'\d+', string)

def checkTime(string):
    arr = getNumber(string)
    endweek = arr.pop()
    startweek = arr.pop()
    endjie = arr[-1]#
    startjie = arr[0]
    jie = list(range(int(startjie),int(endjie) + 1))
    arr = list(range(int(startweek),int(endweek) + 1))
    result = [arr,{}]
    for i in arr:
        result[1][i] = jie
    return result

#获取课表在html中的table文本
def getTable(username,password):
    # try:
    header1 = {'Host': 'jxgl.bistu.edu.cn:8443', 'Connection': 'keep-alive', 'Content-Length': '66', 'Cache-Control': 'max-age=0', 'Origin': 'http://jxgl.bistu.edu.cn', 'Upgrade-Insecure-Requests': '1', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36', 'Sec-Fetch-Dest': 'document', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Referer': 'http://jxgl.bistu.edu.cn/index.html', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6'}
    header2 = {'Host': 'jwgl.bistu.edu.cn', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.58', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Referer': 'http://jwgl.bistu.edu.cn/xs_main.aspx?xh=2017011295', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9'}

    url = 'https://jxgl.bistu.edu.cn:8443/zfca/remoteLogin?service=http://jxgl.bistu.edu.cn/portal.do'
    data = {"issubmit":"true","isyh":"true","username":username,"password":password}

    #构建登录信息进行登录
    req = session.post(url,data=data,headers = header1,verify=False,timeout=5)
    dom = etree.HTML(req.text)
    #判断登陆是否成功
    try:
        url = dom.xpath("/html/body/form/div/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[1]/a/@href")[0]
        req = session.get(url)
    except:
        return 'fail','fail'

    url = "http://jwgl.bistu.edu.cn/xskbcx.aspx?xh={}&xm=姜兆光&gnmkdm=N121603".format(username)
    #url = "http://jwgl.bistu.edu.cn/xskbcx.aspx?xh=2017011295&xm=%E5%A7%9C%E5%85%86%E5%85%89&gnmkdm=N121603"
    req = session.get(url,headers = header2,data=data)
    dom = etree.HTML(req.text)
    viewstate = dom.xpath("//input[@id='__VIEWSTATE']/@value")[0]
    generator = dom.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value")[0]

    data = {
        "xnd":"2019-2020",
        "xqd":2,
        "__EVENTTARGET":"xqd",
        "__EVENTARGUMENT":"",
        "__LASTFOCUS":"",
        "__VIEWSTATE":viewstate,
        "__VIEWSTATEGENERATOR":generator,
    }

    req = session.post(url,headers = header2,data=data)
    dom = etree.HTML(req.text)

    name = dom.xpath("/html/body/form/div[3]/div/div/span[2]/text()")[0].replace("姓名：","")
    table = dom.xpath("//table[@id='Table1']")[0]

    return name,etree.tostring(table,encoding=str)
        

    # except:
    #     return 'error','error'

'''
    #将获取到的table html文本转换成字典数据
    字典格式:
    {
        课程名:{
                'name':课程名
                'type':选修/必修等
                'day':0-6的数字，表示星期几
                'teacher':老师名字
                'classroom':上课地点
                'week':
                    [
                        [1,2,3,4 ……] 哪些周上这门课
                        {1:[1,2,3],2:[2,3] ……} 相应周哪些节上课
                    ]
            }
        }

    }
'''
def manageTable(username,password):
    xm = username
    xm,string = getTable(username,password)
    if string == 'error':
        return 'error','error'
    if string == 'fail':
        return 'fail','fail'
    course = {}
    all = bs(str(string),'html.parser').find_all('tr')[2:]
    for i in range(len(all)):

        #处理标签头
        if i in [0,5,9]:
            row = bs(str(all[i]),'html.parser').find_all('td')[2:]
        else:
            row = bs(str(all[i]),'html.parser').find_all('td')[1:]
        
        #便利课程信息
        for m in row:
            if len(m.contents) < 4:
                continue
            #存在课程信息，整合课程介绍本文
            string = ""
            for n in m.contents:
                string += str(n)
            #分割多次显示
            for y in string.split("<br/><br/>"):
                x = y.split("<br/>")
                #整合课程信息
                name = x[0]
                type = x[1]
                day = dic[x[2][1]]
                teacher = x[3]
                classroom = x[4]
                #获取课程的周和节的信息
                week = checkTime(x[2])
                if course.get(name) == None:
                    course[name] = {
                    'name':name,
                    'type':type,
                    'day':day,
                    'teacher':teacher,
                    "classroom":classroom,
                    'week':week,
                    }
                else:
                    
                    for key in week[0]:
                        if key not in course[name]['week'][0]:
                            course[name]['week'][1][key] = week[1][key]
                        else:
                            course[name]['week'][1][key] =  course[name]['week'][1][key] + week[1][key]
                    course[name]['week'][0] = course[name]['week'][0] + week[0]
                    course[name]['week'][0].sort()
                    course[name]['week'][0] = list(set(course[name]['week'][0]))
                    for i in course[name]['week'][1]:
                        course[name]['week'][1][i] = list(set(course[name]['week'][1][i]))

                #week = [{1:[3,4],2:[3,4]},[1,2,3,4,5]]
    return xm,course


def get(username,password):
    name,course = manageTable(username,password)
    if course == 'fail':
        return json.dumps({'status':'fail'})
    if course == 'error':
        return json.dumps({'status':'error'})

    now = datetime.now()
    total = 21
    result = {'status':'success','root':root,"name":name,'course':{}}
    for week in range(1,total):
        arr = []#一个13*7的矩阵。表示每节课的占用情况。
        #矩阵初始化
        for i in range(13):
            arr.append([0,0,0,0,0,0,0])

        courseid = 1

        dic = {}#用来保存课程id对应的课程信息。结构: {课程id:[课程文本介绍，课程节数]}

        title = [
            '<td class="num">1 <br><span class="time">08:00</span> </td>', 
            '<td class="num">2 <br><span class="time">08:50</span> </td>', 
            '<td class="num">3 <br><span class="time">09:50</span> </td>', 
            '<td class="num">4 <br><span class="time">10:40</span> </td>', 
            '<td class="num">5 <br><span class="time">11:30</span> </td>', 
            '<td class="num">5.5 <br><span class="time"></span> </td><td class="wuxiu" colspan="7">午休~</td>',
            '<td class="num">6 <br><span class="time">13:30</span> </td>', 
            '<td class="num">7 <br><span class="time">14:20</span> </td>', 
            '<td class="num">8 <br><span class="time">15:20</span> </td>', 
            '<td class="num">9 <br><span class="time">16:10</span> </td>', 
            '<td class="num">10 <br><span class="time">--</span> </td>', 
            '<td class="num">11 <br><span class="time">--</span> </td>',
            '<td class="num">12 <br><span class="time">--</span> </td>',
            '<td class="num">13 <br><span class="time">--</span> </td>',
            ]

        #检索所有课程，检查课程在当前设定的周数是否上课。
        for i in course:
            if week in course[i]['week'][0]:
                day = course[i]['day']
                classroom = course[i]['classroom']
                teacher = course[i]['teacher']
                jie = course[i]['week'][1][week]
                for m in jie:
                    arr[m - 1][day] = courseid
                    dic[courseid] = ['{}<br>{}'.format(i,classroom),len(jie),teacher,str(course[i]['week'][0]).replace("[","").replace("]",""),course[i]['type']]
                courseid += 1

        #处理title数组的文本，按列处理
        jump = 0
        for i in range(7):
            string = ""
            py = 0
            for m in range(13):
                if jump != 0 :
                    jump -= 1
                    continue
                if m >= 5:
                    py = 1

                #竖条的颜色
                if i % 2 == 0:
                    style = 'dd'
                else:
                    style = 'bb'

                if arr[m][i] == 0:#没课，使用空td填充
                    title[m + py] += '<td class="{}"></td>'.format(style)
                else:
                    title[m + py] += '<td class="{} course" kind="{}" week="{}" teacher="{}" rowspan="{}" style="background:{};">{}</td>'.format(style,dic[arr[m][i]][4],dic[arr[m][i]][3],dic[arr[m][i]][2],dic[arr[m][i]][1],color[arr[m][i] % 9],dic[arr[m][i]][0])
                    jump = dic[arr[m][i]][1] - 1
        head = '<table border="0" cellpadding="0" cellspacing="0">\n<th class="month num" style="height: 10px;">$month月</th><th class="day dd">周一</br><font size="1" color="">$1日</font></th><th class="day bb">周二</br><font size="1" color="">$2日</font></th><th class="day dd">周三</br><font size="1" color="">$3日</font></th><th class="day bb">周四</br><font size="1" color="">$4日</font></th><th class="day dd">周五</br><font size="1" color="">$5日</font></th><th class="day bb">周六</br><font size="1" color="">$6日</font></th><th class="day dd">周日</br><font size="1" color="">$7日</font></th></tr></table>\n'
        for i in range(len(title)):
            title[i] = '<tr>' + title[i] + '</tr>'
        table = ''.join(title)
        result['course'][week] = table
    return str(json.dumps(result,indent=2,ensure_ascii=False))

if __name__ == "__main__":
    print(get("2017011295","asdfg456123.."))