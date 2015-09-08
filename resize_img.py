# -*- coding: utf-8 -*-
"""图片批量调整

@author wocanmei
@date 2014-07-09 10:40:48
"""
import Image
import os


def resize(fname):  
    img = Image.open(fname)
    if img.size[0] > 2048:
        width = int(img.size[0] * 0.6) 
        height = int(img.size[1] * 0.6)
    else:
        width = img.size[0]
        height = img.size[1]
    resized_img = img.resize((width, height))  
    basename, extension = os.path.splitext(fname)
    resized_img.save(basename+'_resized.jpg')
    print  basename+'_resized.jpg ('+ str(width), str(height) + ') is saved!'

    
if __name__ == '__main__':  
    path = os.path.abspath(os.curdir)  
    dirList = os.listdir(path);
    count = 0
    for fname in dirList:  
        basename, extension = os.path.splitext(fname)  
        if extension.lower() == '.jpg':  
            resize(fname)
            count += 1       
    print 'The work has done, ' + str(count) + ' images have been resized!'
