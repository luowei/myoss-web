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

from flask import Flask, request,render_template, redirect, url_for,make_response,jsonify
from markupsafe import Markup
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from logging.handlers import RotatingFileHandler
import time
import os
import secrets

# 从环境变量读取 OSS 配置（推荐）
# 或使用默认值（仅限开发环境）
OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', 'YOUR_ACCESS_KEY_SECRET')
OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')
OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME', 'lwmedia')

# Bucket 列表配置（从环境变量读取，逗号分隔）
# 格式：BUCKET_NAME1:ENDPOINT1,BUCKET_NAME2:ENDPOINT2
# 示例：OSS_BUCKET_LIST="demo:oss-cn-hangzhou.aliyuncs.com,test:oss-cn-beijing.aliyuncs.com"
OSS_BUCKET_LIST_RAW = os.environ.get('OSS_BUCKET_LIST', '')
if OSS_BUCKET_LIST_RAW:
    # 解析环境变量配置的 Bucket 列表
    OSS_BUCKET_LIST = []
    for item in OSS_BUCKET_LIST_RAW.split(','):
        if ':' in item:
            name, endpoint = item.split(':', 1)
            OSS_BUCKET_LIST.append({'name': name.strip(), 'endpoint': endpoint.strip()})
        else:
            # 只有 bucket 名，使用默认 endpoint
            OSS_BUCKET_LIST.append({'name': item.strip(), 'endpoint': OSS_ENDPOINT})
else:
    # 默认 Bucket 列表
    OSS_BUCKET_LIST = [
        {'name': 'demo', 'endpoint': 'oss-cn-hangzhou.aliyuncs.com'},
        {'name': 'test', 'endpoint': 'oss-cn-hangzhou.aliyuncs.com'}
    ]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['OSS_BUCKET_LIST'] = OSS_BUCKET_LIST
app.config['OSS_ENDPOINT'] = OSS_ENDPOINT

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

# 导入认证模块
try:
    from app.auth import load_users, permission_required, bucket_access_required, create_user, User
except ImportError:
    from auth import load_users, permission_required, bucket_access_required, create_user, User

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

    def bucket(self, endPoint=None, bucketName=None):
        if endPoint is None:
            endPoint = self.endPoint
        if bucketName is None:
            bucketName = self.bucketName
            
        if self._bucket is None:
            self._bucket = oss2.Bucket(auth, endPoint, bucketName)
        elif endPoint != self._bucket.endpoint or bucketName != self._bucket.bucket_name:
            self._bucket = oss2.Bucket(auth, endPoint, bucketName)
        return self._bucket


myoss = MyOSS()

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    return users.get(user_id)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_operation(action, key, status='success', message=''):
    user = current_user.username if current_user.is_authenticated else 'anonymous'
    logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {user} - {action} - {key} - {status} - {message}")

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
    try:
        bucket = currentBucket()

        path = request.args.get('path', '')
        if path and not path.endswith('/'):
            path += '/'
        
        items = []
        try:
            for item in oss2.ObjectIterator(bucket, prefix=path, delimiter='/'):
                if item.key not in (path, 'oss-accesslog/'):
                    items.append(item)
        except Exception as e:
            logger.error(f"列出文件失败：{e}")
            error_message = f"无法连接 OSS: {str(e)}"
            return render_template('home.html', error=error_message, items=[], parent='', bucket=None)

        # 父级目录
        pItems = path.rsplit('/')
        res = path.rsplit('/', 1)
        parent = res[0]+'/'
        if len(res) <= 1 or (len(pItems) == 2 and pItems[-1] == ''):
            parent = ''
        elif len(pItems) > 2:
            parent = path.rsplit('/', 2)[0] + '/'

        resp = make_response(render_template('home.html', bucket=bucket, items=items, parent=parent))

        # 设置 cookie
        resp.set_cookie('endPoint', myoss.endPoint)
        resp.set_cookie('bucketName', myoss.bucketName)
        return resp
    except Exception as e:
        logger.error(f"首页访问错误：{e}")
        return render_template('home.html', error=f"服务器错误：{str(e)}", items=[], parent='')

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
@permission_required('write')
@bucket_access_required()
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember', False)
    
    users = load_users()
    user = None
    for u in users.values():
        if u.username == username:
            user = u
            break
    
    if user and user.check_password(password):
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        log_operation('LOGIN', username)
        return redirect(next_page or url_for('home'))
    else:
        log_operation('LOGIN', username, 'failed', 'Invalid credentials')
        return render_template('login.html', error='用户名或密码错误')

@app.route('/logout')
@login_required
def logout():
    log_operation('LOGOUT', current_user.username)
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not username or not password:
        return render_template('register.html', error='用户名和密码不能为空')
    
    if password != confirm_password:
        return render_template('register.html', error='两次密码输入不一致')
    
    user, message = create_user(username, password)
    if user:
        return redirect(url_for('login'))
    else:
        return render_template('register.html', error=message)

@app.route('/users', methods=['GET', 'POST'])
@login_required
@permission_required('manage_users')
def manage_users():
    if request.method == 'GET':
        users = load_users()
        return render_template('users.html', users=users)
    
    action = request.form.get('action')
    if action == 'create':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'viewer')
        buckets = request.form.get('buckets', '').split(',')
        
        user, message = create_user(username, password, role, buckets)
        if user:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': message})
    
    return jsonify({'success': False, 'message': '未知操作'})

@app.route('/search')
@login_required
@bucket_access_required()
def search_files():
    try:
        bucket = currentBucket()
        keyword = request.args.get('q', '')
        path = request.args.get('path', '')
        
        if not keyword:
            return jsonify({'success': False, 'message': '请输入搜索关键词'})
        
        items = []
        for item in oss2.ObjectIterator(bucket, prefix=path):
            if keyword.lower() in item.key.lower():
                items.append({
                    'key': item.key,
                    'size': item.size,
                    'last_modified': item.last_modified
                })
        
        return jsonify({'success': True, 'items': items[:100]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/batch_delete', methods=['POST'])
@login_required
@permission_required('delete')
@bucket_access_required()
def batch_delete():
    try:
        bucket = currentBucket()
        keys = request.json.get('keys', [])
        
        if not keys:
            return jsonify({'success': False, 'message': '未选择文件'})
        
        deleted = []
        for key in keys:
            try:
                bucket.delete_object(key)
                deleted.append(key)
                log_operation('BATCH_DELETE', key)
            except Exception as e:
                logger.error(f"删除失败 {key}: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'成功删除 {len(deleted)} 个文件',
            'deleted': deleted
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/batch_move', methods=['POST'])
@login_required
@permission_required('write')
@bucket_access_required()
def batch_move():
    try:
        bucket = currentBucket()
        items = request.json.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'message': '未选择文件'})
        
        moved = []
        for item in items:
            old_key = item.get('old_key')
            new_key = item.get('new_key')
            if old_key and new_key:
                try:
                    bucket.copy_object(bucket.bucket_name, old_key, new_key)
                    bucket.delete_object(old_key)
                    moved.append({'old': old_key, 'new': new_key})
                    log_operation('BATCH_MOVE', f'{old_key} -> {new_key}')
                except Exception as e:
                    logger.error(f"移动失败 {old_key}: {e}")
        
        return jsonify({
            'success': True,
            'message': f'成功移动 {len(moved)} 个文件',
            'moved': moved
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    #port 为端口，host 值为 0.0.0.0 即不单单只能在 127.0.0.1 访问，外网也能访问
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)