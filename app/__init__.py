#!/usr/bin/python
# coding=utf-8

__author__ = 'luowei'

import os
import oss2
import json
import re
import sys


from base64 import b64encode,b64decode
from itertools import islice
# from urllib.parse import urlencode
from urllib.parse import urlencode,quote,unquote

from flask import Flask, request,render_template, redirect, url_for,make_response,jsonify,Markup
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os

# 从环境变量读取 OSS 配置（推荐）
# 或使用默认值（仅限开发环境）
OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', 'YOUR_ACCESS_KEY_SECRET')
OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME', 'lwmedia')

auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
# bucket = oss2.Bucket(auth, 'oss-cn-beijing.aliyuncs.com', 'lwdemo')
# bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'luoweitest')
# bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'lwmedia')
# bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'wodedata')


endPoints = {'杭州':OSS_ENDPOINT}
# endPoints = {'杭州':'oss-cn-hangzhou.aliyuncs.com','北京':'oss-cn-beijing.aliyuncs.com'}

class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance


class MyOSS(Singleton):
    def __init__(self,endPoint=endPoints['杭州'],bucketName=OSS_BUCKET_NAME):
        self.auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        self.endPoint = endPoint
        self.bucketName = bucketName
        self._bucket = None

    def bucket(self,endPoint=endPoints['杭州'],bucketName='lwmedia'):
        if self._bucket == None:
            self._bucket = oss2.Bucket(auth, self.endPoint, self.bucketName)
        elif (endPoint not in self._bucket.endpoint) or (bucketName not in self._bucket.bucket_name):
            self.endPoint = endPoint
            self.bucketName = bucketName
            self._bucket = oss2.Bucket(auth, self.endPoint, self.bucketName)
        return self._bucket


myoss = MyOSS()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_operation(action, key, status='success', message=''):
    logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {action} - {key} - {status} - {message}")

def currentBucket():
    endPoint = request.args.get('endPoint', '')
    if endPoint == '' or endPoint == None:
        endPoint = request.cookies.get('endPoint')

    bucketName = request.args.get('bucketName', '')
    if bucketName=='' or bucketName == None:
        bucketName = request.cookies.get('bucketName')

    bucket = myoss.bucket(endPoint, bucketName)
    return bucket


# service = oss2.Service(auth, 'oss-cn-hangzhou.aliyuncs.com')
# service = oss2.Service(auth, 'oss-cn-beijing.aliyuncs.com')
# print([b.name for b in oss2.BucketIterator(service)])


# ------ Routing URL -------

@app.route('/',methods=['GET', 'POST'])
def home():

    # 获取bucket列表
    # service = oss2.Service(auth, endPoint)
    # bucketList = [b.name for b in oss2.BucketIterator(service)]

    bucket = currentBucket()

    path = request.args.get('path', '')
    if path.endswith('/') is False  and path != '':
        path += '/'
    # items = list(item for item in oss2.ObjectIterator(bucket, prefix=path, delimiter='/'))
    items = []
    for item in oss2.ObjectIterator(bucket, prefix=path, delimiter='/'):
        # print('====key:'+item.key)
        if item.key not in (path,'oss-accesslog/'):
            items.append(item)

    # 父级目录
    pItems = path.rsplit('/')
    res = path.rsplit('/', 1)
    parent = res[0]+'/'
    if len(res) <= 1 or (len(pItems) == 2 and pItems[-1] == ''):
        parent = ''
    elif len(pItems) > 2:
        parent = path.rsplit('/', 2)[0] + '/'

    resp = make_response(render_template('home.html',bucket=bucket,items=items,parent=parent))

    # 设置cookie
    resp.set_cookie('endPoint', myoss.endPoint)
    resp.set_cookie('bucketName', myoss.bucketName)
    return resp
    # return render_template('home.html', name=name)

@app.route('/itemInfo',methods=['POST'])
def itemInfo():
    key = request.form['key']
    expire = request.form['expire']

    bucket = currentBucket()

    url = bucket.sign_url('GET', key, int(expire))
    contentType = bucket.get_object(key).content_type

    return jsonify({'url':url,'contentType':contentType})

@app.route('/audio',methods=['POST'])
def openAudio():
    title = request.form['title']
    url = request.form['url']
    return redirect(url_for('player', type='audio', title=title, url=url))

@app.route('/video',methods=['POST'])
def openVideo():
    title = request.form['title']
    url = request.form['url']
    return redirect(url_for('player', type='video',title=title,url=url))

@app.route('/player',methods=['GET'])
def player():
    type = request.args.get('type','')
    title = request.args.get('title','')
    url = request.args.get('url','')
    return "<!DOCTYPE html><html lang='en'><head><meta name='applicable-device' content='mobile'><meta name='viewport' content='width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=0,viewport-fit=cover'><meta charset='UTF-8'>" \
           "<title>" + title + "</title></head><body><"+type+" controls preload='metadata'><source src='" + url + "'/></"+type+"></body></html>"

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        bucket = currentBucket()
        files = request.files.getlist('file')
        path = request.form.get('path', '')
        
        if not files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        uploaded = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                key = path + filename if path else filename
                
                bucket.put_object(key, file.read())
                uploaded.append(filename)
                log_operation('UPLOAD', key)
        
        return jsonify({'success': True, 'message': f'成功上传 {len(uploaded)} 个文件'})
    except Exception as e:
        log_operation('UPLOAD', 'unknown', 'error', str(e))
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete', methods=['POST'])
def delete_file():
    try:
        bucket = currentBucket()
        key = request.form.get('key', '')
        
        if not key:
            return jsonify({'success': False, 'message': '文件名为空'})
        
        bucket.delete_object(key)
        log_operation('DELETE', key)
        
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        log_operation('DELETE', key, 'error', str(e))
        return jsonify({'success': False, 'message': str(e)})

@app.route('/rename', methods=['POST'])
def rename_file():
    try:
        bucket = currentBucket()
        old_key = request.form.get('old_key', '')
        new_key = request.form.get('new_key', '')
        
        if not old_key or not new_key:
            return jsonify({'success': False, 'message': '文件名不能为空'})
        
        bucket.copy_object(bucket.bucket_name, old_key, new_key)
        bucket.delete_object(old_key)
        log_operation('RENAME', f'{old_key} -> {new_key}')
        
        return jsonify({'success': True, 'message': '重命名成功'})
    except Exception as e:
        log_operation('RENAME', f'{old_key} -> {new_key}', 'error', str(e))
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    #port为端口，host值为0.0.0.0即不单单只能在127.0.0.1访问，外网也能访问
    app.run(host='0.0.0.0',port='5000')
    # app.run()