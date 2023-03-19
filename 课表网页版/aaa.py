import requests
from bs4 import BeautifulSoup as bs
import re
import json
import os
from datetime import datetime
import table

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

turn = {"一":0,"二":1,"三":2,"四":3,"五":4,"六":5,"日":6}


def write(name,string):
    with open(name + ".txt",'w',encoding='utf-8') as f:
        f.write(str(string))

def writeHtml(name,string):
    with open(name + ".html",'w',encoding='utf-8') as f:
        f.write(str(string))

def checkTime(string):
    arr = re.findall(r'\d+', string)
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

#制作table表单~

def makeForm(table):
    course = {}
    all = bs(str(table),'html.parser').find_all('tr')[2:]
    for i in range(len(all)):
        #处理标签头
        if i in [0,5,9]:
            row = bs(str(all[i]),'html.parser').find_all('td')[2:]
        else:
            row = bs(str(all[i]),'html.parser').find_all('td')[1:]
        
        #便利课程信息
        for m in range(len(row)):
            if len(row[m].contents) < 4:
                continue
            #存在课程信息，整合课程介绍本文
            string = ""
            for n in row[m].contents:
                string += str(n)
            #分割多次显示
            for y in string.split("<br/><br/>"):
                x = y.split("<br/>")
                #整合课程信息
                name = x[0]
                type = x[1]
                day = m

                teacher = x[3]
                classroom = x[4]

                #获取课程的周和节的信息，添加到course字典中
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
    total = 21
    result = {'status':'success','course':{}}
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
        '''
        for i in range(len(title)):
            title[i] = '<tr>' + title[i] + '</tr>'

        table = ''.join(title)
        result['course'][week] = table
        '''
        for i in range(len(title)):
            title[i] = '<tr>' + title[i] + '</tr>'
        
        table = ''.join(title)
        result['course'][week] = table
    return str(json.dumps(result,indent=2,ensure_ascii=False))
    

class Light():
    #初始化
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.right = self.checkAccount()

    #检查账号密码正确性 
    def checkAccount(self):
        header1 = {'Host': 'jxgl.bistu.edu.cn:8443', 'Connection': 'keep-alive', 'Content-Length': '66', 'Cache-Control': 'max-age=0', 'Origin': 'http://jxgl.bistu.edu.cn', 'Upgrade-Insecure-Requests': '1', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36', 'Sec-Fetch-Dest': 'document', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Referer': 'http://jxgl.bistu.edu.cn/index.html', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6'}
        header2 = {'Host': 'jxgl.bistu.edu.cn', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Referer': 'http://jxgl.bistu.edu.cn/index.html', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6'}
        url = 'https://jxgl.bistu.edu.cn:8443/zfca/remoteLogin?service=http://jxgl.bistu.edu.cn/portal.do'
        data = {"issubmit":"true","isyh":"true","username":self.username,"password":self.password}
        #构建登录信息进行登录
        req = requests.post(url,data=data,headers=header1,allow_redirects=False,verify=False,timeout=5)
        url = req.headers.get('Location')
        #判断登陆是否成功
        if url == None:
            return False
        else:
            #账号正确性验证成功，获取cookie，字符串key，个人信息
            cookie = requests.utils.dict_from_cookiejar(req.cookies)
            req = requests.get(url,headers=header2,cookies=cookie)
            html = bs(req.text,'html.parser')
            href = html.find_all("a",id='125481701964098680')[0].get('href')
            for i in range(4):
                req = requests.get(href,cookies=cookie,allow_redirects=False,verify=False)
                href = req.headers["Location"]
            
            cookie = requests.utils.dict_from_cookiejar(req.cookies)
            url = 'http://jwgl.bistu.edu.cn/xskbcx.aspx?xh={}&gnmkdm=N121603'.format(self.username)
            req = requests.post(url,cookies=cookie,verify=False,data=data)
            html = bs(req.text,'html.parser')
            #开始分离数据
            self.cookie = cookie
            self.url = url
            self.key = html.find("input",id='__VIEWSTATE').get("value")
            self.html = html
            return True

    '''
        获取学生的简略信息
        json格式:
            学号：2017011295| 姓名：姜兆光| 学院：计算机学院| 专业：网络工程(卓越)| 行政班：网工1701 
            {
                xh:学号,xm:名字,xy:xxx学院,zy:xx专业,bj:xxxx
            }
    '''
    def getStudentInfo(self):
        span = bs(
            str(self.html.find("div",class_="search_con")),
            'html.parser'
        ).find_all("span")[0:5]
        xh = span[0].text.split("：")[1]
        xm = span[1].text.split("：")[1]
        xy = span[2].text.split("：")[1]
        zy = span[3].text.split("：")[1]
        bj = span[4].text.split("：")[1]
        return {
            'xh':xh,'xm':xm,'xy':xy,'zy':zy,'bj':bj
        }
        

    #获取课表的table文本
    def getCourseTable(self,xn,xq):
        data = {'__EVENTTARGET':'xqd',
        '__VIEWSTATE':self.key, 
        'xnd':xn,
        'xqd':xq
        }
        req = requests.post(self.url,cookies=self.cookie,verify=False,data=data)
        html = bs(req.text,'html.parser')
        table = html.find_all("table")[0]
        return table

    '''
        获取学期的年份
        数据格式：
            ['20xx-20xx','20xx-20xx','20xx-20xx']
    '''
    def getTermList(self):
        option = bs(
            str(self.html.find("select",class_="form-control")),
            'html.parser'
        )
        return option.text.split("\n")[1:-1]

    
if __name__ == "__main__":
    
    sd = Light("2017011295",'asdfg456123..')
    if(sd.right):
        table1 = sd.getCourseTable("2017-2018",'1')
        writeHtml("table",str(table1))
        table1 = table.manageTable(table1)
        write('dic',str(table1))
        write("result",str(
            table.get(table1)
        ))
    '''
    with open("1.txt",'r',encoding='utf-8') as f:
            table1 = f.read()
    write("12",str(
        json.dumps(
            json.dump(eval(table.get(table1)))
            ,indent=2,ensure_ascii=False
        )
    ))
    '''
        