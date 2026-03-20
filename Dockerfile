FROM myflask-base:v1.0 AS myflask

# 添加标签说明
LABEL author="luowei" email="luowei@wodedata.com"  purpose="uwsgi+Python3 基础镜像"

# 环境变量（可通过 docker run -e 覆盖）
ENV APP_DIR=/myoss
ENV OSS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
ENV OSS_ACCESS_KEY_SECRET=YOUR_ACCESS_KEY_SECRET
ENV OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ENV OSS_BUCKET_NAME=lwmedia

# 创建工作目录
RUN mkdir -p ${APP_DIR}

VOLUME [${APP_DIR},/tmp/uwsgi.sock]
WORKDIR ${APP_DIR}

# 将本地的内容拷贝到容器
COPY . ${APP_DIR}

# 安装依赖
RUN chmod 777 /tmp/ -R \
    && pip3 install -r ${APP_DIR}/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir

EXPOSE 5000

# 启动 uwsgi
ENTRYPOINT uwsgi --ini ${APP_DIR}/uwsgi.ini

# 构建镜像
# docker build -t myoss:v1.0 .

# 运行容器（使用环境变量）
# docker run -d \
#   --name my-oss \
#   -e OSS_ACCESS_KEY_ID=your_key_id \
#   -e OSS_ACCESS_KEY_SECRET=your_key_secret \
#   -e OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com \
#   -e OSS_BUCKET_NAME=your_bucket \
#   -p 5000:5000 \
#   myoss:v1.0

# 创建工作路径
RUN mkdir /myoss

ENV APP_DIR /myoss
VOLUME [${APP_DIR},/tmp/uwsgi.sock]
WORKDIR ${APP_DIR}

# 将本地的内容拷贝到容器
COPY . /myoss

# 安装依赖
RUN chmod 777 /tmp/ -R \
    && pip3 install -r /myoss/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
    # --no-cache-dir

EXPOSE 9000

# 启动uwsgi
# ENTRYPOINT ["/entrypoint.sh"]
ENTRYPOINT uwsgi --ini /myoss/uwsgi.ini

# 构建镜像
# docker build -t myoss:v1.0 .  


