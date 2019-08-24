FROM myflask-base:v1.0 AS myflask

# 添加标签说明
LABEL author="luowei" email="luowei@wodedata.com"  purpose="uwsgi+Python3基础镜像"

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


