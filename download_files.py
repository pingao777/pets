# -*- coding: utf-8 -*-
"""根据条件批量下载文件
Created on Wed Jul 24 12:22:28 2013

@author: T430
"""
import sys
import os
import re
import urllib


def progress_bar(percent, download_size, total_size, flag='#'):
    for i in range(percent / 2):
       flag += '#'
    print '\r' + flag + ' ' +str(percent) + '% ' + \
    str(total_size / 1024) + 'KB',


def reporthook(blocks_read,block_size,total_size): 
    download_size = blocks_read * block_size
    percent = 100 * download_size / total_size
    progress_bar(percent, download_size, total_size)    
    

def download(url, re_, local_path=os.path.abspath(os.curdir)):
    html = urllib.urlopen(url).read()
    pattern = re.compile(re_)
    urls = pattern.findall(html)
    n = 0
    for u in urls:
        print str(n + 1) + '.Downloading ' + u
        urllib.urlretrieve(u, local_path + u.split('/')[-1], reporthook)
        n += 1
    print '\nYou have downloaded ' + str(n) + ' files.'
    

if __name__ == '__main__':
    download(sys.argv[1], sys.argv[2])


