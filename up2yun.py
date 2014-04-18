#!/usr/bin/python
#-*- encoding:utf-8 -*-
'''
Created on Apr 18, 2014
@author: sunlt

将oopress/_site中内容上传到又拍云的bucket中。
请先安装upyun库：pip install upyun

本程序在Linux Mint 16下运行正常。
'''
import upyun
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def cleanBucket(bucket):
    ''' 清空bucket '''
    dirs = ['/']
    files = []
    current_dir_index = 0
    
    while current_dir_index < len(dirs):
        for item in bucket.getlist(dirs[current_dir_index]):
            if item['type'] == 'F':
                dirs.append(dirs[current_dir_index] + item['name'] + '/')
            else:
                files.append(dirs[current_dir_index] + item['name'])
        current_dir_index += 1
    dirs.sort(key=lambda x:-len(x)) #按照字符串长度从大到小到排序
    
    print 'start delete files'
    for fname in files:
        print 'delete ', fname
        try:
            bucket.delete(fname)
        except Exception, e:
            print e
    print 'start delete dirs'
    for dname in dirs:
        print 'delete ', dname
        try:
            bucket.delete(dname)
        except Exception, e:
            print e            

def upload2Bucket(local_upload_dir, bucket):
    ''' 将local_dir下的内容传到bucket下 '''
    def toBucketPath(local_upload_dir, local_path):
        ''' '''
        path = local_path.replace(local_upload_dir, '', 1)
        if len(path) == 0:
            path = '/'
        elif path[0] != '/': 
            path = '/' + path
        return path   
        
    dirs_list = []
    files_list = []
    
    for root, _, files in os.walk(local_upload_dir):
        dirs_list.append(root)
        if len(files) > 0:
            for fname in files:
                files_list.append(root + '/' + fname)
        dirs_list.sort(key=lambda x:len(x)) #按照字符串长度从小到大到排序
        
    print 'start make dir in bucket...'
    for d in dirs_list:
        print d, '->', toBucketPath(local_upload_dir, d)
        try:
            bucket.mkdir( toBucketPath(local_upload_dir, d) )
        except Exception, e:
            print e
    print 'start upload file to bucket...'
    for fname in files_list:
        print fname, '->', toBucketPath(local_upload_dir, fname)
        with open(fname, 'rb') as f:
            try:
                bucket.put(toBucketPath(local_upload_dir, fname), f, checksum=True, headers=None)
            except Exception, e:
                print e

def main(bucket_name, user_name, passwd, local_dir):
    ''' 主函数 '''
    def printHelp():
        print '''
        请指定操作：
        $ ./up2yun clean  #清空指定的bucket
        $ ./up2yun upload  #将指定目录的内容上传到指定的bucket中
        '''
        
    upyun_bucket = upyun.UpYun(bucket_name, user_name, passwd, timeout=30, endpoint=upyun.ED_AUTO)

    if len(sys.argv) < 2:
        printHelp()
        sys.exit(1)
    if sys.argv[1].lower() == 'clean':
        cleanBucket(upyun_bucket)
    elif sys.argv[1].lower() == 'upload':
        upload2Bucket(local_dir, upyun_bucket)
    else:
        printHelp()

if __name__ == '__main__':
    
    bucket_name = 'your-bucket-name' 
    user_name = 'your-name'
    passwd = 'your-password'
        
    local_dir = './_site'
    
    main(bucket_name, user_name, passwd, local_dir)