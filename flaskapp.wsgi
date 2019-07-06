#!/usr/bin/python
# coding=utf-8

__author__ = 'luowei'

import sys
import logging

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/myoss.wodedata.com/")  #你app的目录
from app import app as application
application.secret_key = 'Add your secret key' #随机秘钥