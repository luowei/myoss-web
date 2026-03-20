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

### ⚠️ 安全配置（重要）

**敏感信息已移除！** 本项目现已改为使用环境变量管理敏感配置。

#### 环境变量配置

1. **复制配置模板**
```bash
cp .env.example .env
```

2. **编辑 `.env` 文件**，填入你的真实配置：
```bash
OSS_ACCESS_KEY_ID=your_actual_access_key_id
OSS_ACCESS_KEY_SECRET=your_actual_access_key_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name
```

3. **获取 AccessKey**
   - 登录 [阿里云 RAM 控制台](https://ram.console.aliyun.com/manage/ak)
   - 创建或获取 AccessKey ID 和 AccessKey Secret
   - ⚠️ **重要**：不要将 `.env` 文件提交到 Git 仓库！

#### Docker 环境变量

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

## 有待优化改进

### 🔴 高优先级（安全&稳定性）

1. **AccessKey 硬编码问题** ⚠️
   - **现状**: OSS 访问密钥直接写在代码中 (`app/__init__.py:27,48`)
   - **风险**: 密钥泄露风险高，无法灵活轮换
   - **建议**: 
     - 使用环境变量或配置文件存储密钥
     - 集成阿里云 RAM 角色（ECS 环境）
     - 使用阿里云 KMS 服务管理密钥

2. **依赖版本过旧** ⚠️
   - **现状**: 
     - `Werkzeug==0.15.5` (2019 年版本，存在已知漏洞)
     - `urllib3==1.23` (存在 CVE-2019-11324 等漏洞)
     - `oss2==2.5.0` (2018 年版本)
     - `Bootstrap 3.3.6` (已停止维护)
     - `jQuery 2.2.1` (存在 XSS 漏洞)
   - **建议**: 升级到最新稳定版本

3. **Python 2 兼容代码** ⚠️
   - **现状**: 存在 `reload(sys)` 和 `sys.setdefaultencoding('utf-8')` (Python 2 代码)
   - **建议**: 移除 Python 2 兼容代码

4. **异常处理缺失**
   - **现状**: OSS 操作无 try-catch 保护
   - **风险**: 网络错误、权限错误会导致应用崩溃
   - **建议**: 添加完善的异常处理和错误提示

### 🟡 中优先级（功能&体验）

5. **文件上传功能缺失**
   - **建议**: 添加文件上传接口
   - 支持拖拽上传
   - 支持分片上传（大文件）
   - 上传进度显示

6. **文件管理功能不完善**
   - **建议添加**:
     - 文件重命名
     - 文件删除
     - 文件复制/移动
     - 批量操作
     - 文件搜索

7. **权限控制缺失**
   - **现状**: 任何人可访问所有文件
   - **建议**:
     - 添加用户认证系统
     - 基于角色的访问控制 (RBAC)
     - Bucket/目录级别的权限控制

8. **前端体验优化**
   - **建议**:
     - 升级到 Bootstrap 5 + 现代化 UI
     - 添加文件图标（根据扩展名）
     - 添加面包屑导航
     - 支持键盘快捷键
     - 响应式优化（移动端适配）
     - 添加加载动画和骨架屏

9. **日志系统缺失**
   - **建议**:
     - 添加访问日志
     - 添加操作日志（谁在什么时候做了什么）
     - 集成日志轮转
     - 错误日志告警

### 🟢 低优先级（扩展&优化）

10. **性能优化**
    - **建议**:
      - 添加文件列表缓存
      - 支持 CDN 加速
      - 图片缩略图预生成
      - 分页加载（大目录）
      - 异步加载（AJAX）

11. **多区域支持**
    - **现状**: 仅支持杭州区域（代码注释提到北京但未启用）
    - **建议**: 完善多区域切换功能

12. **Docker 优化**
    - **建议**:
      - 使用多阶段构建减小镜像体积
      - 添加健康检查
      - 使用 Docker Compose 编排
      - 添加日志收集
      - 配置资源限制

13. **监控告警**
    - **建议**:
      - 集成 Prometheus + Grafana
      - 添加应用性能监控 (APM)
      - 配置告警通知

14. **文档完善**
    - **建议**:
      - API 接口文档
      - Nginx 配置示例
      - 常见问题 FAQ
      - 故障排查指南

15. **测试覆盖**
    - **建议**:
      - 单元测试（pytest）
      - 集成测试
      - E2E 测试
      - CI/CD 流水线

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