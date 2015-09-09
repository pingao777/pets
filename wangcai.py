# -*- coding: utf-8 -*-
"""一条旺财狗

其实这是一个公司OA报销单状态流转监控程序。
Created on Tue Jan 13 21:49:36 2015

@author: valar
"""
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import re
import sys
import datetime


EMAILLIST_DIR = './wangcai_email.log'
LOG_DIR = './wangcai.log'
FINANCIAL_MANAGER = u''
FINANCIAL_STAFF = u''

#指定系统默认编码
reload(sys)
sys.setdefaultencoding('utf8')


def login_emoss(username, password, session):
    hds = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; \
    Trident/6.0)'}

    postdata = {'userName': username,
                's_Pwd': password,
                'target': ''
    }
    
    session.get('http://fmx38a1.commany.cn/fm/login.jsp')
    session.post('http://fmx38a1.commany.cn/fm/login.jsp?actionName=doLogin', 
           data=postdata, headers=hds)
    
    
def check(begin_date, end_date, session):
    """查询报销单信息
    
    begin_date和end_date的格式都为yyyy-mm    
    """
    
    hds = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; \
    Trident/6.0)'}
    
    #获得一年的报销单
    querydata = {'pageCount': 1,
                 'rowCount': 0,
                 'cur_pageIndex': 1,
                 'beginDate': begin_date,
                 'endDate': end_date
    }
    
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    main_url = 'http://fmx38a1.commany.cn/fm/newflow/usersqlist.jsp?\
    jdf_check_login_session=100008803:A211000:' + str(year) + ':' + str(month)
    html = session.post(main_url, data=querydata, 
    headers=hds).text
    soup = BeautifulSoup(html) 
    table = soup.find('table', class_='main_table')
    
    #保存报销单信息
    datas = []
    #保存未发送邮件报销单的索引号
    ns = []     
    
    #这个for循环的功能为获得html标签中的文本
    for tr in table.children:
        #检查是否是Tag，否则没有children属性，因为里面有一些非打印字符
        if isinstance(tr, Tag):
            for td in tr.children:
                if isinstance(td, Tag):
                    #去掉字符串中的非打印字符
                    datas.append(''.join(td.get_text().split()))
    
    #三种类型报销单计数器
    cm = 0
    cs = 0
    cd = 0
    #这个for循环获得ns的值并添加相应log信息             
    for n in xrange(len(datas)/14 - 1):
        #有三种情况需要发送邮件：1.流程到财务部经理 2流程到财务部分管员工 3.状态为结束
        if datas[10 + 14*n] == u'结束':
                if not is_emailed(datas[12 + 14*n], None, isover=True):
                    add_email_list(datas[12 + 14*n], None, isover=True)
                    ns.append(n)
                    cd += 1
        else:
            if datas[6 + 14*n] == FINANCIAL_MANAGER:   #财务经理名字
                if not is_emailed(datas[12 + 14*n], 'financial_manager'):
                    add_email_list(datas[12 + 14*n], 'financial_manager')
                    ns.append(n)
                    cm += 1
            if datas[6 + 14*n] == FINANCIAL_STAFF:    #财务员工
                if not is_emailed(datas[12 + 14*n], 'financial_staff'):
                    add_email_list(datas[12 + 14*n], 'financial_staff')
                    ns.append(n)
                    cs += 1
    
    if not ns:
        add_log('太冷清了，没有单子！(╯﹏╰）')
    else:
        sub = '主人，'
        if cd > 0:
            sub += str(cd) + '个单子已完成，'
        if cm > 0:
            sub += str(cm) + '个单子已到财务经理，'
        if cs > 0:
            sub += str(cs) + '个单子已到最后一步，别忘了贴流程单哦，'
        sub += '汪汪！！'
        t = to_text(datas, ns) 
        send_email(sub, t)
        add_log(sub + '发送邮件了！！')
                
  
def is_emailed(sn, role, isover=False):
    """检查相应流水号的报销单是否已发送过邮件
    
    与add_email_list配合使用。    
    """
    el = open(EMAILLIST_DIR, 'a+')
    if isover:
        for line in el:
            if ''.join(line.split()) == sn + '-done':
                el.close()
                return True
    else:
        if role == 'financial_manager':
            for line in el:
                if ''.join(line.split()) == sn + '-financial_manager':
                    el.close()
                    return True
        elif role == 'financial_staff':
            for line in el:
                if ''.join(line.split()) == sn + '-financial_staff':
                    el.close()
                    return True
    
    el.close()
    return False
  
  
def add_email_list(sn, role, isover=False):
    """添加流水号信息到邮件清单文件中
    
    当报销单状态为结束，添加sn-end，否则添加sn-huangyang    
    """
    el = open(EMAILLIST_DIR, 'a+')
    if isover:
        el.write(sn + '-done\n')
    else:
        if role == 'financial_manager':
            el.write(sn + '-financial_manager\n')
        elif role == 'financial_staff':
            el.write(sn + '-financial_staff\n')
        
    el.close()


def add_log(msg):
    log = open(LOG_DIR, 'a+')
    now = datetime.datetime.now()
    log.write(now.ctime() + ' ' + msg + '\n')
    log.close()  
    
             
def to_text(datas, ns):
    """将data中的报销单字段转换成字符串
    
    """
    text = ''
    text += "报销单：\n"
    text += "<html><body><table border='1px' cellspacing='0' \
    style='border-collapse:collapse'><tr><th>流程号</th><th>申请名称</th>\
    <th>项目名称</th><th>待办人</th><th>金额</th><th>申请时间</th>\
    <th>凭证描述</th></tr>"

    pattern = re.compile(r'\d+')
    for n in ns:
    
            m = pattern.search(datas[7 + 14*n])
            text += "<tr>"
            text += "<td>" + datas[12 + 14*n] + "</td>"
            text += "<td>" + datas[0 + 14*n] + "</td>"
            text += "<td>" + datas[2 + 14*n] + "</td>"
            text += "<td>" + datas[6 + 14*n] + "</td>"
            text += "<td>" + m.group() + '元' + "</td>"
            text += ("<td>" + datas[9 + 14*n][0:10] + ' ' + 
            datas[9 + 14*n][10:18] + "</td>")
            text += "<td>" + datas[11 + 14*n] + "</td>"
            text += "</tr>"
    text += "</table></body></html>"
    
    return text
        

def send_email(subject, contents):
    mail_to = ['email@163.com']
    mail_from = '旺财<from@commany.cn>'

    smtp_server = 'smtp.company.net'
    username = 'username@commany.cn'
    password = 'password'
    
    msg = MIMEText(contents, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8') 
    msg['From'] = mail_from
    msg['To'] = ';'.join(mail_to)
    
    smtp = smtplib.SMTP()
    smtp.connect(smtp_server)
    smtp.login(username, password)
    smtp.sendmail(mail_from, mail_to, msg.as_string())
    smtp.quit()

    
if __name__ == '__main__':
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    begin_date = str(year - 1) + '-' + str(month)
    end_date = str(year) + '-' + str(month)
    try:
        s = requests.session()
        login_emoss('userid', 'password', s)
        check(begin_date, end_date, s)
    except requests.exceptions.ConnectionError:
        add_log('主人，连不上网，%>_<%')
    except Exception as e:
        add_log('主人，出错了，错误信息：' + str(e))
    finally:
        s.close()
        
    
        
        
