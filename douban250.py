# -*- codeing = utf-8 -*-
# @Time :2023/3/14 16:10
# @Author:Jayq
# @File : douban250.py
# @Software: PyCharm
import os
import sys
import re # 正则
import urllib.request

from bs4 import BeautifulSoup #解析网页
import xlwt #表格处理
import sqlite3 # 数据库
from urllib import request,parse # http

def main():
    print("开始爬取...")
    baseurl = "https://movie.douban.com/top250?start="
    savepath = "豆瓣电影Top250.xls"
    # 1.爬取网页
    datalist = getData(baseurl)
    # 3.保存数据
    # 保存到EXCEL
    # saveDataAsExcel(datalist,savepath)

    # 保存到sqllite
    dbpath = "douban.db"
    saveDataAsDatabase(datalist,dbpath)

    # test
    # getSingleUrl("https://movie.douban.com/top250?start=")


# 正则表达式
findlink = re.compile(r'<a href="(.*?)">')
findtitles = re.compile(r'<span class="title">(.*?)</span>')
findimgsrc = re.compile(r'<img.*src="(.*?)"',re.S) # re.S:忽略换行符
findscore = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
findrated = re.compile(r'<span>(\d*)人评价</span>')
findintro = re.compile(r'<span class="inq">(.*?)</span>')
findinfo = re.compile(r'<p class="">(.*?)</p>',re.S)



def getData(baseurl):
    datalist = []
    for i in range(0,10):
        html = getSingleUrl(baseurl + str(i * 25))

        # 2.逐一解析
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all("div", class_ = "item"):
            # 保存一部电影的所有信息
            data = []
            item = str(item)
            link = re.findall(findlink, item)
            # link 类型是list，注意转换成str
            data.append(link[0])
            imgsrc = re.findall(findimgsrc, item)
            data.append(imgsrc[0])
            titles = re.findall(findtitles, item)
            if len(titles) == 2:
                ctitle = titles[0]
                ftitle = titles[1].replace("/", "") # 去掉无关符号
                data.append(ctitle)
                data.append(ftitle)
            else:
                data.append(titles[0])
                data.append("")

            score = re.findall(findscore, item)
            data.append(score[0])
            rated = re.findall(findrated, item)
            data.append(rated[0])
            intro = re.findall(findintro, item)
            if len(intro) != 0:
                intro = intro[0].replace("。","")
                data.append(intro)
            else:
                data.append("")
            info = re.findall(findinfo, item)[0]
            info = re.sub('<br(\s+)?/>(\s+)?'," ",info) # 去掉<br/>
            info = re.sub("/"," ",info) # 去掉/
            data.append(info.strip())
            datalist.append(data)
            # test
            # print(datalist)
    return datalist

# 得到指定url的内容
def getSingleUrl(url):
    # 伪装用户
    header = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    request = urllib.request.Request(url=url,headers=header)
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


def saveDataAsExcel(datalist,savepath):
    print("开始保存...")
    workbook = xlwt.Workbook(encoding='utf-8',style_compression=0)  # 创建workbook 对象
    worksheet = workbook.add_sheet('豆瓣Top250',cell_overwrite_ok=True)  # 创建工作表sheet
    col = ("电影详情链接","图片链接","影片中文名","影片外文名","评分","评价数","概况","相关信息")
    for i in range(0,8):
        worksheet.write(0,i,col[i]) # 写入列名

    movienum = len(datalist)
    for i in range(0,movienum):
        data = datalist[i]
        for j in range(0,8):
            if j == 0:
                worksheet.write(i + 1, j, data[0])
            elif j == 1:
                worksheet.write(i + 1, j, data[1])
            elif j == 2:
                worksheet.write(i + 1, j, data[2])
            elif j == 3:
                worksheet.write(i + 1, j, data[3])
            elif j == 4:
                worksheet.write(i + 1, j, data[4])
            elif j == 5:
                worksheet.write(i + 1, j, data[5])
            elif j == 6:
                worksheet.write(i + 1, j, data[6])
            elif j == 7:
                worksheet.write(i + 1, j, data[7])

    if os.path.exists(savepath):
        os.remove(savepath)
    workbook.save(savepath)
    print("保存成功！")

def init_db(dpbath):
    sql = '''
         
            create table movie250 
            (
                id integer primary key autoincrement,
                film_link text,
                pic_link text,
                cname varchar,
                fname varchar,
                score numeric,
                rated numeric,
                intro text,
                info text
            )
    '''
    # 创建数据表
    conn = sqlite3.connect(dpbath)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
    except:
        print("movie250已经存在")
    finally:
        conn.commit()
        conn.close()


def saveDataAsDatabase(datalist,dbpath):
    print("开始保存...")
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    for data in datalist:
        for index in range(len(data)):  # index是每行数据的下标
            data[index] = '"'+data[index]+'"'  # 对每个数据添加前后的双引号，\是转义字符
        # 拼接建表语句，连接data列表中的每一项，使用逗号分隔
        sql = '''
                INSERT INTO movie250
                (film_link, pic_link, cname, fname, score, rated, intro, info) 
                values(%s)'''%",".join(data)
        # print(sql)
        cursor.execute(sql)  # 执行SQL语句：创建数据表
        conn.commit()  # 事务提交：让操作生效
    cursor.close()  # 关闭游标
    conn.close()  # 关闭连接

    print("保存成功！")

if __name__ == '__main__':
    # init_db("movietst.db")
    main()


