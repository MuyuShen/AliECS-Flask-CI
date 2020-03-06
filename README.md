# AliECS-Flask-CI
pre-project for flask-ci-demo project

# 用途说明
本项目是用于理解和使用ECS部署的项目。
我之前一直使用本地环境进行web开发，但由于celery和其他组件对于windows系统的有限支持，只能使用本地虚拟化环境。
本地虚拟化环境在新机器上部署的时候特别缓慢，尤其是受限于网络速度。因而考虑使用云服务器来部署开发环境。
为了保证开发环境的拓展和快速部署，项目所有内容都运行在docker中。在使用组件化的构建之前，打算先从容器构建和通信开始。



# 环境准备

1. 选择一台阿里云ECS

   我使用的镜像是：centos_7_04_64_20G_alibase_201701015.vhd

2. 在服务器上安装DOCKER

   详细说明请参考https://docs.docker.com/install/linux/docker-ce/centos/

   安装docker之前，首先安装docker存储库： 

   ```
   $ sudo yum install -y yum-utils \
     device-mapper-persistent-data \
     lvm2
   $ sudo yum-config-manager \
       --add-repo \
       https://download.docker.com/linux/centos/docker-ce.repo
   ```

   然后安装docker并启动

   ```
   $ sudo yum install docker-ce docker-ce-cli containerd.io
   $ sudo systemctl start docker
   ```

   下载python+nginx+redis基础镜像，我在这里选用了python3.8，因为写这份文档时，这是pyenv里面当前最新的python版本，请谨慎选择安装的python镜像，这个镜像942M.

   ```
   $ docker pull python:3.8.1
   $ docker pull redis
   $ docker pull nginx
   ```
# 测试搭建flask
1. 在系统中创建flask项目工作目录
   ```
   $ cd /home
   $ mkdir /flask-dev
   $ cd /flask-dev
   ```
   
2. 创建一个最小的flask-web服务
   ```
   from flask import Flask
   app = Flask(__name__)

   @app.route('/')
   def hello_world():
       return 'Hello, World!'
   ```
   将以上代码在flask-dev目录下保存为app.py
   
3. 回到home目录下面编写Dockerfile构建
   ```
   FROM python:3.8.1
   COPY ./flask-dev ./flask-dev
   workdir ./flask-dev
   ENV FLASK_APP app.py
   ENV FLASK_RUN_HOST 0.0.0.0
   RUN pip install -r requirements.txt
   CMD ["flask", "run"]
   ```
   保存为Dockerfile
   运行命令
   ```
   $ docker build -t flask:dev .
   ```
   运行flask
   ```
   $ docker run --name=app flask:dev
   ```
   
4. 构建nginx
   创建nginx目录
   ```
   $ mkdir /nginx-dev
   ```
   将default.conf文件（nginx配置）放在工作目录下
   注意设置location的值,其中proxy_pass里面的域名要和flask容器的名称一致。
   这样才能映射到对应的容器上。
   ```
   server {
        listen          80;
        server_name     _;

        access_log      /dev/fd/1 main;
        error_log       /dev/fd/2 notice;

        location / {
            proxy_pass         http://app:5000/;
            proxy_redirect     off;

            proxy_set_header   Host                 $http_host;
            proxy_set_header   X-Real-IP            $remote_addr;
            proxy_set_header   X-Forwarded-For     			$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto    $scheme;
        }
    }
   ```
   启动nginx容器,将宿主机的80端口映射到nginx容器的80端口，再通过--link指令链接nginx和flask容器
   ```
   $ docker run -p 80:80 --link app
   ```
   至此，已经可以通过网络进行服务器访问了。
   
5. 访问web网站
   单独拿出来说一下，在ECS环境中，访问控制需要在服务商提供的管理控制台里面配置。对于阿里云内网环境，则是进入到控制台，选择对应的实例，然后对实例进行安全组配置。只有在同一个安全组内的内网IP的机器才能成功访问。如果是公网环境访问，需要额外购买公网地址。
   
# 组件化部署
1. 项目目录结构
   ```
   │  .gitignore
   │  LICENSE
   │  list.txt
   │  README.md
   │  
   ├─flask-dev
   │      app.py
   │      Dockerfile
   │      requirements.txt
   │      
   └─nginx-dev
          Dockerfile
          nginx.conf
   ```
2. /flask-dev/Dockerfile
   ```
   FROM python:3.8.1
   COPY ./flask-dev ./flask-dev
   workdir ./flask-dev
   ENV FLASK_APP app.py
   ENV FLASK_RUN_HOST 0.0.0.0
   RUN pip install -r requirements.txt
   CMD ["flask", "run"]
   ```
3. /nginx-dev/Dockerfile
   ```
   FROM nginx
   COPY ./nginx-test/conf.d/default.conf /etc/nginx/nginx.conf
   ```
