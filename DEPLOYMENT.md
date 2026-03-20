# MyOSS 部署指南

## 快速部署

### 方式一：Docker Compose（推荐）

#### 1. 基础部署（仅应用 + Redis）

```bash
# 设置环境变量
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export OSS_BUCKET_NAME="your_bucket"
export SECRET_KEY="your_secret_key_change_this"

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问：http://localhost:5000

#### 2. 完整部署（包含监控）

```bash
# 设置 Grafana 密码
export GRAFANA_PASSWORD="admin_password"

# 启动所有服务（包括监控）
docker-compose --profile monitoring up -d

# 查看服务状态
docker-compose ps
```

访问服务：
- **MyOSS**: http://localhost:5000
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (密码：admin_password)
- **Node Exporter**: http://localhost:9100

### 方式二：手动部署

#### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
# Linux/Mac
export OSS_ACCESS_KEY_ID="your_key"
export OSS_ACCESS_KEY_SECRET="your_secret"
export OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export OSS_BUCKET_NAME="your_bucket"
export SECRET_KEY="change_this_secret"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"

# Windows (PowerShell)
$env:OSS_ACCESS_KEY_ID="your_key"
$env:OSS_ACCESS_KEY_SECRET="your_secret"
```

#### 3. 启动应用

```bash
# 开发模式
python app/__init__.py

# 生产模式（uWSGI）
uwsgi --ini uwsgi.ini

# 或使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 初始化管理员账号

首次部署需要创建管理员账号：

```bash
# 创建 data 目录
mkdir -p data

# 使用 Python 脚本创建
python -c "
from app.auth import create_user
user, msg = create_user('admin', 'admin123', role='admin', buckets=['*'])
print(f'创建结果：{msg}')
"
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `OSS_ACCESS_KEY_ID` | 阿里云 AccessKey ID | - | ✅ |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret | - | ✅ |
| `OSS_ENDPOINT` | OSS 区域端点 | oss-cn-hangzhou.aliyuncs.com | ✅ |
| `OSS_BUCKET_NAME` | 默认 Bucket 名称 | lwmedia | ❌ |
| `SECRET_KEY` | Flask 密钥（用于会话加密） | 随机生成 | ❌ |
| `REDIS_HOST` | Redis 主机地址 | localhost | ❌ |
| `REDIS_PORT` | Redis 端口 | 6379 | ❌ |
| `GRAFANA_PASSWORD` | Grafana 管理员密码 | admin | ❌ |

### 用户角色权限

| 角色 | 权限 | 说明 |
|------|------|------|
| **admin** | read, write, delete, upload, manage_users | 管理员，可管理用户和所有 Bucket |
| **editor** | read, write, upload | 编辑者，可上传和修改文件 |
| **viewer** | read | 查看者，只能浏览和下载 |

### 目录结构

```
myoss/
├── app/                      # 应用代码
│   ├── __init__.py          # 主应用
│   ├── auth.py              # 认证模块
│   ├── cache.py             # 缓存模块
│   └── templates/           # HTML 模板
├── data/                     # 用户数据（.gitignore）
├── logs/                     # 日志文件（.gitignore）
├── monitoring/               # 监控配置
│   ├── prometheus.yml
│   └── grafana-dashboard.json
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 监控配置

### Prometheus 指标

访问 `http://localhost:5000/metrics` 查看指标：

- `http_requests_total` - HTTP 请求总数
- `http_request_duration_seconds` - 请求耗时
- `oss_operations_total` - OSS 操作次数
- `cache_hits_total` - 缓存命中数
- `cache_misses_total` - 缓存未命中数

### Grafana 仪表板

1. 登录 Grafana：http://localhost:3000
2. 添加 Prometheus 数据源：
   - URL: http://prometheus:9090
3. 导入仪表板：
   - 使用 `monitoring/grafana-dashboard.json`

## 常见问题

### 1. 无法连接 Redis

```bash
# 检查 Redis 是否运行
docker-compose ps redis

# 查看 Redis 日志
docker-compose logs redis

# 重启 Redis
docker-compose restart redis
```

### 2. 用户无法登录

```bash
# 检查用户数据文件
ls -la data/users.json

# 重置管理员密码
python -c "
from app.auth import load_users, save_users, generate_password_hash
users = load_users()
for user in users.values():
    if user.username == 'admin':
        user.password_hash = generate_password_hash('new_password')
        save_users(users)
        print('密码已重置')
"
```

### 3. 缓存不生效

```bash
# 检查 Redis 连接
docker-compose exec redis redis-cli ping

# 清除所有缓存
docker-compose exec redis redis-cli FLUSHALL

# 查看缓存统计
curl http://localhost:5000/cache/stats
```

### 4. Prometheus 无法抓取指标

```bash
# 检查 Prometheus 配置
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# 重新加载配置
docker-compose exec prometheus kill -HUP 1

# 查看抓取目标
curl http://localhost:9090/api/v1/targets
```

## 性能优化建议

### 1. Redis 缓存优化

```yaml
# docker-compose.yml
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 2. 应用性能

```bash
# 增加工作进程数（根据 CPU 核心数）
uwsgi --ini uwsgi.ini --processes 8 --threads 4
```

### 3. 数据库优化

```bash
# 定期清理日志
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 备份与恢复

### 备份用户数据

```bash
# 备份用户数据
cp data/users.json data/users.json.backup.$(date +%Y%m%d)

# 备份 Redis 数据
docker-compose exec redis redis-cli BGSAVE
cp redis-data/dump.rdb redis-data/dump.rdb.backup.$(date +%Y%m%d)
```

### 恢复数据

```bash
# 恢复用户数据
cp data/users.json.backup.20260320 data/users.json

# 恢复 Redis 数据
docker-compose stop redis
cp redis-data/dump.rdb.backup.20260320 redis-data/dump.rdb
docker-compose start redis
```

## 安全建议

1. **修改默认密码**：首次部署后立即修改 admin 密码
2. **使用 HTTPS**：生产环境配置 SSL 证书
3. **定期轮换密钥**：每 90 天更换一次 AccessKey
4. **限制访问 IP**：配置防火墙规则
5. **启用日志审计**：定期检查操作日志

---

**更新时间**: 2026-03-20  
**版本**: v3.0
