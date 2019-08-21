# myoss
========

### 运行

`python __init__.py`

### 参考：

[Flask Quickstart](http://flask.pocoo.org/docs/1.0/quickstart/#routing)

[Jinja Template Designer Documentation](http://jinja.pocoo.org/docs/2.10/templates/#synopsis)

[How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

[Ubuntu Apache Server 部署 Flask 程序](https://eliyar.biz/deploy-a-flask-application-on-an-ubuntu-apache-server/)

## uWSGI启动

构建镜像
docker build -t myoss:v1.0 .

运行flask app
docker run --rm -it\
  --name my-oss \
  --network network_mynginx \
  -p 5000:5000 \
  myoss:v1.0

运行nginx
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