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

# 构建参数
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# 镜像标签
LABEL org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.name="MyOSS" \
      org.label-schema.description="阿里云 OSS 文件管理工具" \
      org.label-schema.url="https://github.com/luowei/myoss-web" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.vcs-url="https://github.com/luowei/myoss-web" \
      org.label-schema.version="${VERSION}" \
      maintainer="luowei <luowei@wodedata.com>"

# 环境变量
ENV APP_DIR=/myoss
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OSS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
ENV OSS_ACCESS_KEY_SECRET=YOUR_ACCESS_KEY_SECRET
ENV OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ENV OSS_BUCKET_NAME=lwmedia
ENV OSS_BUCKET_LIST=demo:oss-cn-hangzhou.aliyuncs.com,test:oss-cn-hangzhou.aliyuncs.com
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV SECRET_KEY=change_this_secret_key
ENV PORT=5000

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
COPY --chown=myoss:myoss start.sh ./
COPY --chown=myoss:myoss stop.sh ./

# 创建日志和数据目录
RUN mkdir -p /var/log/myoss /myoss/data /myoss/logs && \
    chown -R myoss:myoss /var/log/myoss /myoss/data /myoss/logs && \
    chmod +x ./start.sh ./stop.sh

# 切换到非 root 用户
USER myoss

# 暴露端口
EXPOSE ${PORT}

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; r = requests.get('http://localhost:${PORT}/', timeout=5); exit(0 if r.status_code == 200 else 1)" || exit 1

# 入口点
ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]

# 使用说明
# 构建镜像:
#   docker build -t myoss:latest .
#
# 运行容器:
#   docker run -d \
#     --name myoss \
#     -p 5000:5000 \
#     -e OSS_ACCESS_KEY_ID=your_key \
#     -e OSS_ACCESS_KEY_SECRET=your_secret \
#     -e OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com \
#     -e OSS_BUCKET_NAME=your_bucket \
#     myoss:latest
#
# 使用 Docker Compose:
#   docker-compose up -d
#
# 查看日志:
#   docker logs -f myoss
#
# 进入容器:
#   docker exec -it myoss /bin/bash
