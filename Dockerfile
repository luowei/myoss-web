# 构建阶段
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim

# 添加标签说明
LABEL author="luowei" 
LABEL email="luowei@wodedata.com"
LABEL purpose="MyOSS - 阿里云 OSS 文件管理工具"
LABEL version="2.0"

# 环境变量
ENV APP_DIR=/myoss
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OSS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
ENV OSS_ACCESS_KEY_SECRET=YOUR_ACCESS_KEY_SECRET
ENV OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ENV OSS_BUCKET_NAME=lwmedia

# 创建非 root 用户
RUN groupadd -r myoss && useradd -r -g myoss myoss

# 创建工作目录
RUN mkdir -p ${APP_DIR} && chown -R myoss:myoss ${APP_DIR}
WORKDIR ${APP_DIR}

# 从构建阶段复制依赖
COPY --from=builder /root/.local /home/myoss/.local
ENV PATH=/home/myoss/.local/bin:$PATH

# 复制应用代码
COPY --chown=myoss:myoss app/ ./app/
COPY --chown=myoss:myoss uwsgi.ini ./
COPY --chown=myoss:myoss requirements.txt ./

# 创建日志目录
RUN mkdir -p /var/log/myoss && chown -R myoss:myoss /var/log/myoss

# 切换到非 root 用户
USER myoss

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# 启动 uwsgi
ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]

# 构建镜像
# docker build -t myoss:v2.0 .

# 运行容器
# docker run -d \
#   --name my-oss \
#   --restart=always \
#   -e OSS_ACCESS_KEY_ID=your_key_id \
#   -e OSS_ACCESS_KEY_SECRET=your_key_secret \
#   -e OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com \
#   -e OSS_BUCKET_NAME=your_bucket \
#   -p 5000:5000 \
#   myoss:v2.0
