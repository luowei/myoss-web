#!/usr/bin/env python
# coding=utf-8
"""
Redis 缓存模块
用于缓存文件列表和常用数据
"""

import os
import json
import logging
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    import redis
    from flask_caching import Cache
    
    cache = Cache(config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'CACHE_REDIS_PORT': int(os.environ.get('REDIS_PORT', 6379)),
        'CACHE_REDIS_DB': int(os.environ.get('REDIS_DB', 0)),
        'CACHE_REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD', None),
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    
    REDIS_AVAILABLE = True
    logger.info("Redis 缓存已启用")
    
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis 未安装，缓存功能已禁用")
    
    class MockCache:
        def get(self, key):
            return None
        
        def set(self, key, value, timeout=None):
            pass
        
        def delete(self, key):
            pass
        
        def clear(self):
            pass
    
    cache = MockCache()

def cached_file_list(timeout=300):
    """文件列表缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return f(*args, **kwargs)
            
            bucket_name = kwargs.get('bucket_name', 'default')
            path = kwargs.get('path', '')
            cache_key = f'file_list:{bucket_name}:{path}'
            
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"缓存命中：{cache_key}")
                return json.loads(cached_data)
            
            result = f(*args, **kwargs)
            
            if result:
                cache.set(cache_key, json.dumps(result), timeout=timeout)
                logger.debug(f"缓存已设置：{cache_key}")
            
            return result
        return decorated_function
    return decorator

def invalidate_file_list_cache(bucket_name, path=None):
    """清除文件列表缓存"""
    if not REDIS_AVAILABLE:
        return
    
    if path:
        cache_key = f'file_list:{bucket_name}:{path}'
        cache.delete(cache_key)
    else:
        pattern = f'file_list:{bucket_name}:*'
        keys = cache.cache.get_keys(pattern)
        for key in keys:
            cache.delete(key)
    
    logger.info(f"已清除 Bucket {bucket_name} 的缓存")

def get_cache_stats():
    """获取缓存统计信息"""
    if not REDIS_AVAILABLE:
        return {'enabled': False}
    
    try:
        redis_client = cache.cache.get_client()
        info = redis_client.info('stats')
        return {
            'enabled': True,
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'keys': redis_client.dbsize()
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败：{e}")
        return {'enabled': False, 'error': str(e)}
