FROM alpine:3.8

# 添加标签说明
LABEL author="luowei" email="luowei@wodedata.com"  purpose="flask基础镜像"

# 安装依赖
RUN echo "https://mirror.tuna.tsinghua.edu.cn/alpine/v3.8/main/" > /etc/apk/repositories \
    && apk add --update --upgrade \
    && apk add --no-cache bash vim python3 uwsgi uwsgi-python3 \
    && apk add --no-cache --virtual .build-deps gcc musl-dev curl \
	&& pip3 install --no-cache-dir --upgrade pip \
    && ln -s /usr/bin/python3 /usr/bin/python \
    # && ln -s /usr/bin/pip3 /usr/bin/pip \
	&& pip3 install flask 

# 构建Flask基础镜像
# docker build -t myflask-base:v1.0 . -f Flask-base.dockerfile  


