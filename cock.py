# -*- coding: utf-8 -*-
"""一只打鸣鸡

其实这是一个自动打卡程序。
@author wocanmei
@date 2015-05-05 9:08:59
"""
import sys
import time
import datetime
import random
import logging
import logging.handlers
import requests


#指定系统默认编码
reload(sys)
sys.setdefaultencoding('utf8')

LOG_FILE = './cock.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, 
                                               maxBytes = 10 * 1024 * 1024,
                                               backupCount = 5)
fmt = '%(asctime)s - %(module)s - %(funcName)s:%(lineno)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter 

logger = logging.getLogger('cock')    # 获取名为cock的logger
logger.addHandler(handler)           # 为logger添加handler

logger.setLevel(logging.INFO) 


def login(username, password, session):
    hds = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    postdata = {'username': username,
                'password': password,
                'origUrl': '',
                'rememberme': 'yes',
                'atl_token': '' 
    }
    
    session.get('http://10.126.2.41:8060')
    html = session.post('http://10.126.2.41:8060/login', 
           data=postdata, headers=hds).text
    return html


def logout(session):
    session.get('http://10.126.2.41:8060/logout')


def sleep(minute):
    stime = random.randint(5,60 * minute)
    time.sleep(stime)
    return stime
    

if __name__ == '__main__':
    try:
        now = datetime.datetime.now()
        hour = now.hour
        s = requests.session()
        waittime = sleep(10) if hour <= 8 or hour >= 18 else sleep(0.2)
        login('username', 'password', s)
        staytime = sleep(0.2)
        logout(s)
        greeting = 'Good morning!' if hour <= 12 else 'Good evening!'
        logger.info(greeting + ' I have wait for ' + str(waittime) +
                   ' seconds and stayed here for ' + str(staytime) + 
                   ' seconds')
    except Exception, e:
    	print e
        logger.error(e)
    finally:
    	s.close()
