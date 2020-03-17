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
   COPY . /flask-dev
   workdir /flask-dev
   ENV FLASK_APP app.py
   ENV FLASK_RUN_HOST 0.0.0.0
   RUN pip install -r requirements.txt
   CMD ["flask", "run"]
   ```
   
3. /nginx-dev/Dockerfile
   ```
   FROM nginx
   COPY ./nginx.conf /etc/nginx/nginx.conf
   ```

4. docker-compose安装

   https://docs.docker.com/compose/install/#install-compose-on-linux-systems

   官方安装说明如上，内容太长，简单来说就是系统安装pip，然后再用pip安装docker-compose。

   在安装时注意，python-dev在centos中的名称是python-devel，必须先安装python-devel，否则pip不能顺利安装docker-compose。

   ```
   $ sudo yum install pip
   $ sudo yum install python-devel
   $ pip install docker-compose
   ```

5. 定义组件服务

   ```
   version: '3'
   services:
     web:
       build: ./flask-dev
       ports:
         - "5000:5000"
     nginx:
       build: ./nginx-dev
       ports:
         - "80:80"
   ```

6. 启动docker-compose

   ```
   $ docker-compose up
   ```

   启动成功后效果如下：

   ```
   CONTAINER ID        IMAGE                   COMMAND                  CREATED              STATUS              PORTS                    NAMES
   7e30591e4aa6        aliecs-flask-ci_web     "flask run"              About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp   aliecs-flask-ci_web_1
   148399e8ae63        aliecs-flask-ci_nginx   "nginx -g 'daemon ..."   About a minute ago   Up 5 seconds        0.0.0.0:80->80/tcp       aliecs-flask-ci_nginx_1
   ```

   

   # CI前篇 - 配置准备

   1. 改造flask

      说是改造，不如说是区分不同环境下使用的配置信息。以下配置的主要目的是为了满足快速测试，需要使用不同的组件测试，典型的例子为，线上使用mysql，开发使用sqlite。

      ```
      # config.py
      class Config:
          DEBUG = False
          TESTING = False
          SECRET_KEY = "write by java"
      
      
      class DevelopmentConfig(Config):
          DEBUG = True
      
      
      class TestingConfig(Config):
          TESTING = True
          DEBUG = True
      
      
      config = {
          "develop": DevelopmentConfig,
          "testing": TestingConfig,
          "default": DevelopmentConfig,
      }  
      ```

      ```
      # app.py
      import os
      from . import create_app
      
      app = create_app(os.getenv("FLASK_CONFIG", "default"))
      
      
      @app.shell_context_processor
      def make_shell_context():
          context = dict(app=app)
          return context
      ```

      ```
      # /blueprints/main/views
      from flask import Blueprint
      
      bp = Blueprint("main", __name__)
      
      
      @bp.route("/")
      def index():
          return "welcome to CI/CD world 🌏"
      
      from flask import Blueprint
      
      bp = Blueprint("main", __name__)
      
      
      @bp.route("/")
      def index():
          return "welcome to CI/CD world 🌏"
      ```

      ```
      # __init__.py
      from flask import Flask
      from .config import config
      
      
      def _init_errors(app):
          @app.errorhandler(403)
          def page_permission_deny(e):
              return "403", 403
      
          @app.errorhandler(404)
          def page_not_found(e):
              return "404", 404
      
          @app.errorhandler(500)
          def internal_server_error(e):
              return "500", 500
      
      
      def _register_blueprints(app):
          from .blueprints.main.views import bp as main_bp
      
          app.register_blueprint(main_bp, url_prefix="/main")
      
      
      def create_app(config_name):
          app = Flask(__name__, instance_relative_config=True)
          app.config.from_object(config[config_name])
          app.config.from_pyfile("config.py", silent=True)
      
          _init_errors(app)
          _register_blueprints(app)
      
          return app
      ```

      首先改动的是上述四个文件。改动后的项目目录结构如下：

      ```
      │  .gitignore
      │  docker-compose.yml
      │  LICENSE
      │  list.txt
      │  README.md
      │  
      ├─flask-dev
      │  │  app.py
      │  │  config.py
      │  │  Dockerfile
      │  │  requirements.txt
      │  │  __init__.py
      │  │  
      │  ├─blueprints
      │  │  │  __init__.py
      │  │  │  
      │  │  └─main
      │  │  │  │  views.py
      │  │  │  │  __init__.py
      │          
      └─nginx-dev
              Dockerfile
              nginx.conf
      ```

      改动后项目结构变成标准的flask开发结构：

      根路径下保存入口文件app.py，配置文件config.py，项目包管理方法__init__.py

      内部增加blueprint文件夹，提供基本的接口路由方法，

      手动验证运行：

      1.设置FLASK_APP=app.py

      2.运行 $ flask

      在本地浏览器中访问http://localhost:5000/main/，显示

      ```
      welcome to CI/CD world 🌏
      ```

   2. 改造本地测试

      在上面的测试中，需要手工设置环境变量后运行，为了减少操作次数，使用make指令来进行本地化测试管理。

      首先在项目根路径（flask-dev的上级目录）创建Makefile

      ```
      .PHONY: app shell
      
      FLASK_APP_NAME='flask-dev/app.py'
      
      all: app
      
      app:
      	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='default' flask run --host=0.0.0.0
      ```

      保存后，直接在当前目录下运行

      ```
      make all
      ```

      启动成功：

      ```
      [root@devtest0213 AliECS-Flask-CI]# make all
      FLASK_APP='flask-dev/app.py' FLASK_ENV='default' flask run --host=0.0.0.0
       * Serving Flask app "flask-dev/app.py"
       * Environment: default
       * Debug mode: off
       * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
      ```

   # CI中篇 - 实践：对接OSS的图片功能

     1. 开始

        因为是在云服务器上开发，从快速上手和功能拆分的角度考虑，一般会利用厂商提供的对象存储服务来进行文件的管理。

        阿里云对接OSS的模块为oss2，只需要通过pip下载即可。

        ```
        $ pip install -i https://mirrors.aliyun.com/pypi/simple/ oss2
        ```

        OSS的付费方式选择按量计费，会按照使用的存储大小和流量来计价。

        开通步骤如下：

        ```
        登录阿里云官网。
        将鼠标移至产品，单击对象存储 OSS，打开 OSS 产品详情页面。
        在 OSS 产品详情页，单击立即开通。
        开通服务后，在 OSS 产品详情页单击管理控制台直接进入 OSS 管理控制台界面。
        您也可以单击位于官网首页右上方菜单栏的控制台，进入阿里云管理控制台首页，然后单击左侧的对象存储 OSS 菜单进入 OSS 管理控制台界面。
        ```

        在开通OSS服务后，需要到RAM访问控制台（https://ram.console.aliyun.com/overview）

        添加子账户访问key。使用子账户Key的原因是因为账户本身的key相当于操作系统root级别，因此不适合应用程序的开发。

        添加子账户key并设置用户组权限，并添加bucket，即可开始使用OSS。

   ​		

   2. 在项目中支持pytest

      在写下说明的此刻，pytest最新的版本是5.4.0
   
      以当前的pytest构建工程项目，首先要对项目目录结构做设计。pytest的包引入机制，决定了pytest无法引用根目录下的环境配置。这应该是出于包管理的需要。由于我们当前配置上下文的__init__.py文件写在了根目录下，在tests下的pytest配置将无法引入。
   
      所以最佳的办法就是在root目录下使用一个启动入口。对应的开发环境下写配置入口。
   
      改造后的结构如下：
   
      ```
      flask-dev目录:.
      │  app.py
      │  config.py
      │  Dockerfile
      │  list.txt
      │  pytestdebug.log
      │  requirements.txt
      │  
      ├─tests
      │  │  conftest.py
      │  │  unittest.py
      │  │  __init__.py
      │  │  
      │  └─oss_test
      │          test_api_access.py
      │          __init__.py
      │          
      └─web
          │  __init__.py
          │  
          └─blueprints
              │  __init__.py
              │  
              └─main
                      views.py
                      __init__.py
      ```
   
      测试成功：
   
      ```
      =================================================================================== test session starts ====================================================================================
      platform win32 -- Python 3.7.4, pytest-5.4.0, py-1.8.1, pluggy-0.13.1 -- d:\python\python.exe
      cachedir: .pytest_cache
      rootdir: D:\AliECS-Flask-CI\flask-dev
      collected 1 item
      
      tests/oss_test/test_api_access.py::test_get_bucket_lists PASSED                                                                                                                       [100%]
      
      ==================================================================================== 1 passed in 0.07s =====================================================================================
      ```
   
   3. pytest in CI
   
      上一节中配置了项目相关的pytest配置。但显然存在一个问题，例如在测试获取OSS-Bucket的列表时，需要配置相关的账户及私钥。因此，对于不同的测试，需要考虑加载环境变量的方式，是否灵活，快速，安全。
   
      由于项目是基于Docker的，所有环境变量都可以使用docker的配置文件进行配置。因此接下来就是对docker配置的管理。
   
      做到这里的时候，又涉及到项目结构的调整。因为之前的设计中，docker只管理了web和nginx两个服务，两者是平行的，现在需要增加一个test的服务，因而test和web也是保持平行的关系。因此整个项目目录结构就需要调整了。
   
      调整后的目录结构如下：
   
      ```
      D:.
      │  .gitignore
      │  docker-compose.yml
      │  LICENSE
      │  list.txt
      │  Makefile
      │  projects.ini
      │  README.md
      │  
      ├─flask-dev
      │  │  config.py
      │  │  manage.py
      │  │  requirements.txt
      │  │  
      │  ├─app
      │  │  │  __init__.py
      │  │  │  
      │  │  ├─blueprints
      │  │  │  │  __init__.py
      │  │  │  │  
      │  │  │  └─main
      │  │  │          views.py
      │  │  │          __init__.py
      │  │  │          
      │  │  └─oss
      │  │          oss_api.py
      │  │          __init__.py
      │  │          
      │  ├─docker
      │  │  ├─app
      │  │  │      Dockerfile
      │  │  │      
      │  │  ├─product
      │  │  │      Dockerfile
      │  │  │      
      │  │  └─test
      │  │          Dockerfile
      │  │          
      │  ├─instance
      │  │      config.py
      │  │      
      │  └─tests
      │      │  conftest.py
      │      │  unittest.py
      │      │  __init__.py
      │      │  
      │      └─oss_test
      │              test_api_access.py
      │              __init__.py
      │              
      └─nginx-dev
              Dockerfile
              nginx.conf
      ```
      
      该结构中新增了instance/config.py
      
      用于生产服务器/本地服务器保存额外环境配置（比如oss_ak_id）。
      
      
      
      在根目录使用：
      
      ```
      $ make test
      ```
      
      即可本地运行测试。
      
      
      
      另外，还调整了docker-compose的配置项。变更为：
      
      ```
      version: '3'
      services:
        web:
          build:
            context: .
            dockerfile: ./flask-dev/docker/app
          ports:
            - "5000:5000"
        test:
          build:
            context: .
            dockerfile: ./flask-dev/docker/test
        nginx:
          build: ./nginx-dev
          ports:
            - "80:80"
      ```
      
      其中，context项指定compose文件所在目录为根目录，通过web和test的不同来指定测试和开发环境配置。
      
      
      
      
   
   