#!/usr/bin/env python
# coding=utf-8
"""
用户认证和权限管理模块
"""

import os
import hashlib
import secrets
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging

logger = logging.getLogger(__name__)

# 用户数据文件路径
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
ROLE_PERMISSIONS = {
    'admin': ['read', 'write', 'delete', 'upload', 'manage_users'],
    'editor': ['read', 'write', 'upload'],
    'viewer': ['read']
}

class User(UserMixin):
    def __init__(self, user_id, username, password_hash, role='viewer', buckets=None):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.buckets = buckets or []
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def can_access_bucket(self, bucket_name):
        if self.role == 'admin':
            return True
        return bucket_name in self.buckets

def load_users():
    """加载用户数据"""
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = {}
            for user_id, user_data in data.items():
                users[user_id] = User(
                    user_id=user_id,
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    role=user_data.get('role', 'viewer'),
                    buckets=user_data.get('buckets', [])
                )
            return users
    except Exception as e:
        logger.error(f"加载用户数据失败：{e}")
        return {}

def save_users(users):
    """保存用户数据"""
    try:
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        data = {}
        for user_id, user in users.items():
            data[user_id] = {
                'username': user.username,
                'password_hash': user.password_hash,
                'role': user.role,
                'buckets': user.buckets
            }
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败：{e}")
        return False

def create_user(username, password, role='viewer', buckets=None):
    """创建新用户"""
    users = load_users()
    
    for user in users.values():
        if user.username == username:
            return None, "用户名已存在"
    
    user_id = secrets.token_hex(8)
    password_hash = generate_password_hash(password)
    
    user = User(
        user_id=user_id,
        username=username,
        password_hash=password_hash,
        role=role,
        buckets=buckets or []
    )
    
    users[user_id] = user
    if save_users(users):
        return user, "创建成功"
    else:
        return None, "保存失败"

def permission_required(permission):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            
            if not current_user.has_permission(permission):
                return jsonify({'success': False, 'message': '权限不足'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def bucket_access_required():
    """Bucket 访问检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            
            bucket_name = request.args.get('bucketName') or request.cookies.get('bucketName')
            if bucket_name and not current_user.can_access_bucket(bucket_name):
                return jsonify({'success': False, 'message': '无权访问此 Bucket'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
