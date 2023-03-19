import requests
from lxml import etree

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getName(username,password):
    session = requests.Session()
    header = {'Host': 'jxgl.bistu.edu.cn:8443', 'Connection': 'keep-alive', "Content-Length": "66",'Cache-Control': 'max-age=0', 'Upgrade-Insecure-Requests': '1', 'Origin': 'http://jxgl.bistu.edu.cn', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Sec-Fetch-Dest': 'document', 'Referer': 'http://jxgl.bistu.edu.cn/index.html', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
    session.get('http://jxgl.bistu.edu.cn')
    session.get('http://jxgl.bistu.edu.cn/index')
    data = {
        "username":"2017011295",
        "password":"asdfg456123..",
        "issubmit":"true",
        "isyh":"true"
    }
    url = "https://jxgl.bistu.edu.cn:8443/zfca/remoteLogin?service=http://jxgl.bistu.edu.cn/portal.do"
    req = session.post(url,data=data,headers=header,verify = False)
    html = etree.HTML(req.text)
    url = html.xpath("/html/body/form/div/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[1]/a/@href")[0]
    req = session.get(url)
    html = etree.HTML(req.text)
    name = html.xpath("//span[@id='xhxm']/text()")
    return name.pop()


if __name__ == "__main__":
    print(getName("2017011295",'asdfg456123..'))
