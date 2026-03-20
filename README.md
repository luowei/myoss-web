# myoss - 阿里云 OSS 文件管理工具

> 基于 Flask 和阿里云 OSS SDK 开发的 Web 文件管理系统

## 项目简介

myoss 是一个轻量级的阿里云对象存储 (OSS) Web 管理工具，提供文件浏览、预览、下载等功能。支持多 Bucket 切换、文件分类预览（图片/音频/视频）、临时 URL 签名等特性。

### 核心功能

- 📁 **文件浏览**：支持目录层级浏览，类似文件管理器的交互体验
- 🔄 **多 Bucket 切换**：支持多个 OSS Bucket 快速切换
- 🖼️ **媒体预览**：支持图片、音频、视频在线预览
- 🔗 **签名 URL**：生成带过期时间的临时访问链接
- 🐳 **Docker 部署**：支持容器化部署，配合 Nginx 反向代理

---

## 模块架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                      Nginx (反向代理)                      │
│                   端口：80/443                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              uWSGI (应用服务器)                            │
│              端口：5000                                   │
│  配置：processes=CPU 核数*2, threads=CPU 核数*10           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask 应用 (app/__init__.py)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  路由层 (Routes)                                  │   │
│  │  - / (首页/文件列表)                               │   │
│  │  - /itemInfo (获取文件信息)                        │   │
│  │  - /audio (音频播放)                               │   │
│  │  - /video (视频播放)                               │   │
│  │  - /player (媒体播放器)                            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  业务逻辑层                                       │   │
│  │  - MyOSS (OSS 客户端单例)                           │   │
│  │  - currentBucket() (当前 Bucket 获取)               │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           阿里云 OSS (对象存储服务)                        │
│  支持 Bucket: lwdemo, luoweitest, lwmedia, wodedata      │
│  支持区域：杭州 (oss-cn-hangzhou.aliyuncs.com)            │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
myoss/
├── app/                          # 应用主目录
│   ├── __init__.py               # Flask 应用入口 & 核心逻辑
│   ├── static/                   # 静态资源 (CSS/JS/图片)
│   └── templates/                # Jinja2 模板
│       └── home.html             # 首页模板
├── .venv/                        # Python 虚拟环境
├── conf/                         # Nginx 配置 (外部)
│   ├── conf.d/                   # Nginx 站点配置
│   └── nginx.conf                # Nginx 主配置
├── Dockerfile                    # 应用容器构建文件
├── Flask-base.dockerfile         # 基础镜像构建文件
├── flaskapp.wsgi                 # WSGI 入口配置
├── uwsgi.ini                     # uWSGI 服务器配置
├── requirements.txt              # Python 依赖
└── README.md                     # 项目文档
```

### 核心模块说明

#### 1. Flask 应用模块 (`app/__init__.py`)

| 组件 | 说明 |
|------|------|
| `app` | Flask 应用实例 |
| `MyOSS` | OSS 客户端单例类，管理 Bucket 连接 |
| `currentBucket()` | 根据请求参数/cookie 获取当前 Bucket |

#### 2. 路由模块

| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET/POST | 首页，显示文件列表 |
| `/itemInfo` | POST | 获取文件签名 URL 和内容类型 |
| `/audio` | POST | 打开音频播放器 |
| `/video` | POST | 打开视频播放器 |
| `/player` | GET | 媒体播放器页面 |

#### 3. 前端模块 (`app/templates/home.html`)

- **UI 框架**: Bootstrap 3.3.6 + jQuery 2.2.1
- **核心功能**:
  - Bucket 切换按钮组
  - 文件列表展示（目录/文件区分）
  - 文件点击预览（根据内容类型自动识别）
  - Cookie 存储用户选择

---

## 技术方案栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.x | 编程语言 |
| Flask | - | Web 框架 |
| oss2 | 2.5.0 | 阿里云 OSS SDK |
| Werkzeug | 0.15.5 | WSGI 工具库 |
| uWSGI | - | 应用服务器 |
| Jinja2 | - | 模板引擎 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Bootstrap | 3.3.6 | CSS 框架 |
| jQuery | 2.2.1 | JavaScript 库 |
| HTML5 | - | 音频/视频标签 |

### 部署技术

| 技术 | 用途 |
|------|------|
| Docker | 容器化部署 |
| Nginx | 反向代理/静态资源服务 |
| Alpine Linux | 基础镜像 (3.8) |

---


## 部署指南

### 环境要求

- Python 3.6+
- Docker 18.0+
- Docker Compose (可选)
- 阿里云 OSS 访问密钥 (AccessKey)

### 部署方式

#### 方式一：Docker 部署（推荐）

##### 1. 构建基础镜像

```bash
# 构建 Flask 基础镜像
docker build -t myflask-base:v1.0 . -f Flask-base.dockerfile
```

##### 2. 构建应用镜像

```bash
# 构建 myoss 应用镜像
docker build -t myoss:v1.0 .
```

##### 3. 创建 Docker 网络

```bash
docker network create network_mynginx
```

##### 4. 启动 Flask 应用

```bash
# 开发模式（前台运行）
docker run --rm -it \
  --name my-oss \
  --network network_mynginx \
  -p 5000:5000 \
  myoss:v1.0

# 生产模式（后台运行，自动重启）
docker run -d -it \
  --name my-oss \
  --restart=always \
  --network network_mynginx \
  -p 5000:5000 \
  myoss:v1.0

# 自动映射端口
docker run -d -it \
  --name my-oss \
  --restart=always \
  --network network_mynginx \
  -P \
  myoss:v1.0
```

##### 5. 启动 Nginx

```bash
docker run --rm -p 80:80 \
    --name mynginx \
    --network network_mynginx \
    --hostname=wodedata.com \
    --add-host=app.wodedata.com:127.0.0.1 \
    --add-host=bbs.wodedata.com:127.0.0.1 \
    --add-host=myoss.wodedata.com:127.0.0.1 \
    -v $PWD/conf/conf.d:/etc/nginx/conf.d \
    -v $PWD/conf/nginx.conf:/etc/nginx/nginx.conf \
    -v $PWD/log:/var/log/nginx \
    -v $PWD/www:/usr/share/nginx \
    -v $PWD/../jekyll/_site:/usr/share/nginx/jekyll \
    -v $PWD/../php:/usr/share/nginx/php \
    -v $PWD/../myflask:/usr/share/nginx/flask \
    nginx
```

#### 方式二：本地开发部署

##### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

##### 2. 安装依赖

```bash
pip install -r requirements.txt
```

##### 3. 启动应用

```bash
# 方式 1: 直接运行
python app/__init__.py

# 方式 2: 使用 uWSGI
uwsgi --ini uwsgi.ini

# 方式 3: Flask 开发服务器
export FLASK_APP=app/__init__.py
flask run --host=0.0.0.0 --port=5000
```

---

## 配置说明

### 环境变量配置

本项目使用环境变量管理配置，支持多种配置方式。

#### 方式一：使用 .env 文件

1. **复制配置模板**
```bash
cp .env.example .env
```

2. **编辑 `.env` 文件**，填入你的配置：
```bash
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name
```

#### 方式二：系统环境变量

在 `~/.zshrc` 或 `~/.bash_profile` 中添加：
```bash
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export OSS_BUCKET_NAME="your_bucket_name"
```

#### 方式三：Docker 环境变量

使用 Docker 部署时，通过 `-e` 参数传递环境变量：

```bash
docker run -d \
  --name my-oss \
  -e OSS_ACCESS_KEY_ID=your_key_id \
  -e OSS_ACCESS_KEY_SECRET=your_key_secret \
  -e OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com \
  -e OSS_BUCKET_NAME=your_bucket \
  -p 5000:5000 \
  myoss:v1.0
```

#### 获取 OSS 配置

1. 登录 [阿里云 OSS 控制台](https://oss.console.aliyun.com/)
2. 获取 Bucket 的 Endpoint（区域端点）
3. 在 [RAM 访问控制](https://ram.console.aliyun.com/manage/ak) 获取 AccessKey

详细配置说明请参考 [配置更新说明](SECURITY_NOTICE.md)

### uWSGI 配置 (`uwsgi.ini`)

```ini
[uwsgi]
socket=:5000                    # 监听端口
chmod-socket=777                # Socket 权限
callable=app                    # Flask 应用实例名
plugin=python3                  # Python 插件
wsgi-file=app/__init__.py       # WSGI 入口文件
route-run=fixpathinfo:          # 支持 Nginx location 前缀
buffer-size=65535               # 请求缓冲区大小
processes=%(%k * 2)             # 进程数=CPU 核数*2
threads=%(%k * 10)              # 线程数=CPU 核数*10
disable-logging=true            # 禁用日志
```

### Dockerfile 配置

| 配置项 | 说明 |
|--------|------|
| 基础镜像 | `myflask-base:v1.0` (基于 Alpine 3.8) |
| 工作目录 | `/myoss` |
| 暴露端口 | 9000 (实际使用 5000) |
| 启动命令 | `uwsgi --ini /myoss/uwsgi.ini` |

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_DIR` | `/myoss` | 应用目录 |

---

## 使用说明

### 访问首页

浏览器访问：`http://localhost:5000/`

### Bucket 切换

页面顶部提供 Bucket 切换按钮：
- **lwdemo** (北京区域)
- **luoweitest** (杭州区域)
- **lwmedia** (杭州区域)
- **wodedata** (杭州区域)

### 文件操作

| 操作 | 说明 |
|------|------|
| 点击目录 | 进入子目录 |
| 点击 `..` | 返回上级目录 |
| 点击文件 | 根据类型自动预览或下载 |
| 图片文件 | 显示缩略图，点击打开原图 |
| 音频文件 | 显示播放器，可在线播放 |
| 视频文件 | 显示播放器，可在线播放 |
| 其他文件 | 直接下载 |

### URL 参数

| 参数 | 说明 |
|------|------|
| `path` | 当前浏览的目录路径 |
| `endPoint` | OSS 区域端点 |
| `bucketName` | Bucket 名称 |

---

## 更新日志

### v2.0 (2026-03-20) - 重大更新

#### ✅ 已完成功能

1. **前端全面升级**
   - ✨ 升级到 Bootstrap 5.3 + Bootstrap Icons
   - ✨ 添加文件类型图标（支持 20+ 种文件类型）
   - ✨ 添加面包屑导航，清晰显示目录层级
   - ✨ 现代化 UI 设计，响应式布局
   - ✨ 文件大小和修改时间显示
   - ✨ 操作按钮（打开、重命名、删除）

2. **文件管理功能**
   - ✨ 文件上传（支持多文件选择）
   - ✨ 上传进度条显示
   - ✨ 文件删除功能
   - ✨ 文件重命名功能
   - ✨ 操作日志记录

3. **后端优化**
   - ✨ 添加日志系统（访问日志 + 操作日志）
   - ✨ 完善的异常处理
   - ✨ 环境变量配置管理
   - ✨ 移除 Python 2 兼容代码

4. **Docker 优化**
   - ✨ 多阶段构建，减小镜像体积（~150MB → ~120MB）
   - ✨ 健康检查配置
   - ✨ Docker Compose 支持
   - ✨ 非 root 用户运行（安全性提升）
   - ✨ 日志卷挂载

5. **依赖升级**
   - ✨ Flask 1.x → 3.0.0
   - ✨ Werkzeug 0.15.5 → 3.0.1
   - ✨ oss2 2.5.0 → 2.19.1
   - ✨ urllib3 1.23 → 2.1.0
   - ✨ Python 3.6 → 3.11

#### 📋 待完成功能

1. **权限控制**（计划中）
   - 添加用户认证系统
   - 基于角色的访问控制 (RBAC)
   - Bucket/目录级别的权限控制

2. **高级文件管理**
   - 文件复制/移动
   - 批量操作
   - 文件搜索
   - 文件版本管理

3. **性能优化**
   - 文件列表缓存（Redis）
   - CDN 加速集成
   - 图片缩略图预生成
   - 分页加载（大目录）

4. **监控告警**
   - 集成 Prometheus + Grafana
   - 错误日志告警通知

5. **测试覆盖**
   - 单元测试（pytest）
   - 集成测试
   - CI/CD 流水线

---

## 技术栈总览

---

## 快速开始（5 分钟体验）

```bash
# 1. 克隆项目
git clone <repo-url>
cd myoss

# 2. 构建镜像
docker build -t myflask-base:v1.0 . -f Flask-base.dockerfile
docker build -t myoss:v1.0 .

# 3. 创建网络
docker network create network_mynginx

# 4. 启动应用
docker run -d \
  --name my-oss \
  --restart=always \
  --network network_mynginx \
  -p 5000:5000 \
  myoss:v1.0

# 5. 访问
open http://localhost:5000
```

---

## 参考资源

### 官方文档

- [Flask Quickstart](http://flask.pocoo.org/docs/1.0/quickstart/#routing)
- [Jinja Template Designer Documentation](http://jinja.pocoo.org/docs/2.10/templates/#synopsis)
- [阿里云 OSS SDK 文档](https://help.aliyun.com/document_detail/32026.html)
- [uWSGI 文档](https://uwsgi-docs.readthedocs.io/)

### 部署教程

- [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
- [Ubuntu Apache Server 部署 Flask 程序](https://eliyar.biz/deploy-a-flask-application-on-an-ubuntu-apache-server/)

---

## 技术栈总览

```
┌─────────────────────────────────────────────────────┐
│                    前端层                            │
│  Bootstrap 3.3.6 + jQuery 2.2.1 + HTML5             │
├─────────────────────────────────────────────────────┤
│                    应用层                            │
│  Flask + Jinja2 + Werkzeug                          │
├─────────────────────────────────────────────────────┤
│                   服务层                             │
│  uWSGI (多进程 + 多线程)                              │
├─────────────────────────────────────────────────────┤
│                   代理层                             │
│  Nginx (反向代理 + 负载均衡)                          │
├─────────────────────────────────────────────────────┤
│                   存储层                             │
│  阿里云 OSS (对象存储)                                │
└─────────────────────────────────────────────────────┘
```

---

## 变更日志

### v1.0 (当前版本)
- ✅ 基础文件浏览功能
- ✅ 多 Bucket 切换
- ✅ 图片/音频/视频预览
- ✅ Docker 容器化部署
- ⚠️ 待优化项见上方"有待优化改进"章节

---

## 许可证

本项目仅供内部使用

---

## 联系方式

- **作者**: luowei
- **邮箱**: luowei@wodedata.com
- **项目地址**: myoss.wodedata.com
docker build -t myoss:v1.0 .
```

运行flask app  
```
docker run --rm -it\
  --name my-oss \
  --network network_mynginx \
  -p 5000:5000 \
  myoss:v1.0

docker run -d -it\         
  --name my-oss \
  --restart=always \
  --network network_mynginx \
  -p 5000:5000 \
  myoss:v1.0

docker run -d -it\         
  --name my-oss \
  --restart=always \
  --network network_mynginx \
  -P \
  myoss:v1.0

```

运行nginx  
```
docker run --rm -p 80:80 \   
    --name mynginx \
    --network network_mynginx \
    --hostname=wodedata.com \
    --add-host=app.wodedata.com:127.0.0.1 \
    --add-host=bbs.wodedata.com:127.0.0.1 \
    --add-host=myoss.wodedata.com:127.0.0.1 \
    -v $PWD/conf/conf.d:/etc/nginx/conf.d \
    -v $PWD/conf/nginx.conf:/etc/nginx/nginx.conf \
   -v $PWD/log:/var/log/nginx \
   -v $PWD/www:/usr/share/nginx \
   -v $PWD/../jekyll/_site:/usr/share/nginx/jekyll \
   -v $PWD/../php:/usr/share/nginx/php \
   -v $PWD/../myflask:/usr/share/nginx/flask \
   nginx
```