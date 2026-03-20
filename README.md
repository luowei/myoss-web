# myoss - 阿里云 OSS 文件管理工具

> 基于 Flask 和阿里云 OSS SDK 开发的 Web 文件管理系统

## 📖 项目简介

myoss 是一个轻量级的阿里云对象存储 (OSS) Web 管理工具，提供文件浏览、预览、下载等功能。

### 核心功能

- 📁 文件浏览：支持目录层级浏览
- 🔄 多 Bucket 切换：支持配置多个 OSS Bucket
- 🖼️ 媒体预览：支持图片、音频、视频在线预览
- 🔗 签名 URL：生成带过期时间的临时访问链接
- 🐳 Docker 部署：支持容器化部署
- 🔐 权限控制：支持用户认证和 RBAC 权限管理
- 📦 批量操作：支持批量删除、移动文件
- 🔍 文件搜索：支持关键词搜索文件
- 💾 Redis 缓存：支持文件列表缓存
- 📊 监控告警：集成 Prometheus + Grafana

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

#### 1. 配置环境变量

创建 `.env` 文件：
```bash
cat > .env << 'EOF'
# 阿里云 OSS 配置
OSS_ACCESS_KEY_ID=你的 AccessKeyID
OSS_ACCESS_KEY_SECRET=你的 AccessKeySecret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=你的 Bucket 名称

# Bucket 列表配置（可选）
# 格式：bucket1:endpoint1,bucket2:endpoint2
OSS_BUCKET_LIST=demo:oss-cn-hangzhou.aliyuncs.com,test:oss-cn-hangzhou.aliyuncs.com

# Flask 密钥（用于会话加密）
SECRET_KEY=你的随机密钥
EOF
```

#### 2. 启动服务

```bash
# 基础部署（应用 + Redis）
docker-compose up -d

# 完整部署（包含监控）
docker-compose --profile monitoring up -d
```

#### 3. 访问应用

- **MyOSS**: http://localhost:5000
- **Grafana**: http://localhost:3000 (密码：admin)
- **Prometheus**: http://localhost:9090

### 方式二：本地部署

#### 1. 环境要求

- Python 3.10+
- Redis（可选，用于缓存）

#### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置环境变量

编辑 `~/.zshrc` 或 `.bash_profile`：
```bash
# 阿里云 OSS 配置
export OSS_ACCESS_KEY_ID=你的 AccessKeyID
export OSS_ACCESS_KEY_SECRET=你的 AccessKeySecret
export OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
export OSS_BUCKET_NAME=你的 Bucket 名称

# Bucket 列表配置（可选）
export OSS_BUCKET_LIST="demo:oss-cn-hangzhou.aliyuncs.com,test:oss-cn-beijing.aliyuncs.com"

# Flask 密钥
export SECRET_KEY=你的随机密钥

# 使配置生效
source ~/.zshrc
```

#### 4. 启动应用

```bash
# 创建数据目录
mkdir -p data logs

# 启动应用
python3 app/__init__.py

# 或使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

#### 5. 访问应用

打开浏览器访问：http://localhost:5001

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `OSS_ACCESS_KEY_ID` | 阿里云 AccessKey ID | - | ✅ |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret | - | ✅ |
| `OSS_ENDPOINT` | OSS 区域端点 | oss-cn-hangzhou.aliyuncs.com | ✅ |
| `OSS_BUCKET_NAME` | 默认 Bucket 名称 | lwmedia | ❌ |
| `OSS_BUCKET_LIST` | Bucket 列表配置 | demo,test | ❌ |
| `SECRET_KEY` | Flask 会话加密密钥 | 随机生成 | ❌ |
| `REDIS_HOST` | Redis 主机地址 | localhost | ❌ |
| `REDIS_PORT` | Redis 端口 | 6379 | ❌ |

### Bucket 列表配置

**格式**：`bucket1:endpoint1,bucket2:endpoint2`

**示例**：
```bash
# 单区域多 Bucket
OSS_BUCKET_LIST=demo,test,files

# 多区域 Bucket
OSS_BUCKET_LIST=beijing:oss-cn-beijing.aliyuncs.com,shanghai:oss-cn-shanghai.aliyuncs.com

# 混合格式
OSS_BUCKET_LIST=demo:oss-cn-hangzhou.aliyuncs.com,test,files:oss-cn-shanghai.aliyuncs.com
```

**默认配置**：
```python
[
    {'name': 'demo', 'endpoint': 'oss-cn-hangzhou.aliyuncs.com'},
    {'name': 'test', 'endpoint': 'oss-cn-hangzhou.aliyuncs.com'}
]
```

### 常用 OSS Endpoint

| 区域 | Endpoint |
|------|----------|
| 华东 1（杭州） | oss-cn-hangzhou.aliyuncs.com |
| 华东 2（上海） | oss-cn-shanghai.aliyuncs.com |
| 华北 2（北京） | oss-cn-beijing.aliyuncs.com |
| 华南 1（深圳） | oss-cn-shenzhen.aliyuncs.com |
| 香港 | oss-cn-hongkong.aliyuncs.com |

完整列表：https://help.aliyun.com/document_detail/31837.html

---

## 🔧 使用指南

### 1. 首次使用

1. **获取阿里云 AccessKey**
   - 访问 [阿里云 RAM 控制台](https://ram.console.aliyun.com/manage/ak)
   - 创建 AccessKey（建议使用 RAM 用户）

2. **配置环境变量**
   ```bash
   export OSS_ACCESS_KEY_ID=你的 AccessKeyID
   export OSS_ACCESS_KEY_SECRET=你的 AccessKeySecret
   ```

3. **创建管理员账号**
   - 访问 http://localhost:5001/register
   - 注册第一个用户（默认为管理员）

### 2. 文件管理

- **浏览文件**：点击目录进入，点击 `..` 返回上级
- **预览文件**：点击文件自动识别类型并预览
  - 图片：显示缩略图，点击打开原图
  - 音频/视频：显示播放器
  - 其他文件：直接下载
- **上传文件**：点击"选择文件"按钮
- **删除文件**：点击文件右侧删除按钮
- **重命名**：点击文件右侧编辑按钮
- **批量操作**：勾选文件后使用批量删除

### 3. 搜索文件

在搜索框输入关键词，按回车或点击搜索按钮。

---

## 📊 监控与日志

### Prometheus 指标

访问 `http://localhost:5001/metrics` 查看指标：
- `http_requests_total` - HTTP 请求总数
- `http_request_duration_seconds` - 请求耗时
- `oss_operations_total` - OSS 操作次数

### Grafana 仪表板

1. 登录 Grafana：http://localhost:3000
2. 添加 Prometheus 数据源：http://prometheus:9090
3. 导入仪表板配置：`monitoring/grafana-dashboard.json`

### 应用日志

```bash
# Docker 部署
docker-compose logs -f myoss

# 本地部署
tail -f logs/app.log
```

---

## 🏗️ 架构说明

### 系统架构

```
Nginx (反向代理)
    ↓
uWSGI (应用服务器)
    ↓
Flask 应用
    ├── Redis (缓存)
    ├── Prometheus (监控)
    └── 阿里云 OSS (存储)
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Bootstrap 5.3, Bootstrap Icons |
| 后端 | Flask 3.0, Python 3.10+ |
| 认证 | Flask-Login, bcrypt |
| 缓存 | Redis, Flask-Caching |
| 监控 | Prometheus, Grafana |
| 部署 | Docker, Docker Compose |
| 存储 | 阿里云 OSS |

---

## 🔐 权限管理

### 用户角色

| 角色 | 权限 | 说明 |
|------|------|------|
| **admin** | read, write, delete, upload, manage_users | 管理员，可管理用户 |
| **editor** | read, write, upload | 编辑者，可上传修改 |
| **viewer** | read | 查看者，只能浏览下载 |

### 权限配置

在 `app/auth.py` 中配置角色权限：
```python
ROLE_PERMISSIONS = {
    'admin': ['read', 'write', 'delete', 'upload', 'manage_users'],
    'editor': ['read', 'write', 'upload'],
    'viewer': ['read']
}
```

---

## 📦 部署选项

### Docker Compose 服务

| 服务 | 端口 | 说明 |
|------|------|------|
| myoss | 5000 | 应用服务 |
| redis | 6379 | 缓存服务 |
| prometheus | 9090 | 监控指标 |
| grafana | 3000 | 可视化仪表板 |
| node-exporter | 9100 | 系统指标 |

### 生产环境建议

1. **使用 HTTPS**
   - 配置 Nginx 反向代理
   - 使用 Let's Encrypt 证书

2. **配置 Redis 缓存**
   ```bash
   export REDIS_HOST=redis-server
   export REDIS_PORT=6379
   ```

3. **启用日志轮转**
   ```ini
   # uwsgi.ini
   log-maxsize = 10485760
   log-backupname = /var/log/myoss/app.log.bak
   ```

4. **配置监控告警**
   - Prometheus 告警规则
   - Grafana 告警通知

---

## ❓ 常见问题

### 1. 无法连接 OSS

**原因**：AccessKey 无效或已禁用

**解决**：
1. 登录阿里云 RAM 控制台
2. 检查 AccessKey 状态
3. 重新创建 AccessKey
4. 更新环境变量配置

### 2. 用户无法登录

**解决**：
```bash
# 重置管理员密码
python3 -c "
from app.auth import load_users, save_users
from werkzeug.security import generate_password_hash
users = load_users()
for user in users.values():
    if user.username == 'admin':
        user.password_hash = generate_password_hash('新密码')
        save_users(users)
        print('密码已重置')
"
```

### 3. 缓存不生效

**检查**：
```bash
# 测试 Redis 连接
docker-compose exec redis redis-cli ping

# 清除缓存
docker-compose exec redis redis-cli FLUSHALL
```

### 4. Bucket 列表不显示

**检查**：
```bash
# 查看环境变量
echo $OSS_BUCKET_LIST

# 验证配置
python3 -c "from app import app; print(app.config['OSS_BUCKET_LIST'])"
```

---

## 📝 更新日志

### v3.0 (2026-03-20)

**新增功能**：
- ✅ 用户认证系统（登录/注册）
- ✅ RBAC 权限管理
- ✅ 批量文件操作
- ✅ 文件搜索功能
- ✅ Redis 缓存支持
- ✅ Prometheus 监控集成
- ✅ Grafana 可视化仪表板

**优化改进**：
- ✅ 前端升级 Bootstrap 5.3
- ✅ 添加文件类型图标
- ✅ 面包屑导航
- ✅ 错误提示优化
- ✅ 依赖版本升级

### v2.0 (2026-03-20)

- ✅ 文件上传功能
- ✅ 文件删除/重命名
- ✅ 操作日志记录
- ✅ Docker 多阶段构建
- ✅ 健康检查配置

---

## 📄 许可证

本项目仅供内部使用

## 📧 联系方式

- **作者**: luowei
- **邮箱**: luowei@wodedata.com
- **项目**: https://github.com/luowei/myoss-web

---

**最后更新**: 2026-03-20  
**版本**: v3.0
