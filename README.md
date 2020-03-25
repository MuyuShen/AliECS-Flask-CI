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
      
   4. 构建及测试执行
   
      对于web应用而言，验证其工作的有效性有很多种途径。对于开发者而言，倾向于选用更直接的验证方法，对于测试人员，倾向于更贴近使用场景的测试方法。
   
      对于场景的测试，在CI前篇中的flask启动后，已经可以使用浏览器访问欢迎页了。说明我们的web服务具备真实访问的能力。但开发过程中的粒度更小，排查时不应该跨界面运行。
   
      之前部署中提到了pytest配置中的conftest.py文件的入口作用。在Flask实践中，会引入flask的test_client方法来进行上下文环境的管理。通过入口处加载此方法，我们可以直接使用Flask内建的url_for的路由规则，直接捕获http请求的数据，在可靠性和效率上都是最佳的选择。
   
      Flask文档中也有关于整合pytest的示例。在写法上有区别，因为官方文档应用pytest比项目中这段引用晚了一年。这段引用是基于unittest的方法构建改造的，项目中还保留原有的unittest方法，也许以后还会用到？
   
      有一个需要提到的地方，在实际部署时，pytest构建测试类时，不会像运行flask run一样对端口进行绑定。而是需要在环境变量中配置'SERVER_NAME'的值。本地测试，按理说该值绑定的对象在/etc/hosts中。所以此处采用的绑定是localhost。采用不存在的SERVER_NAME是否能启动测试我没有验证，有兴趣的可以自己尝试。
   
      在配置完成以后，构建的第一个测试方法是这样的：
   
      ```
      import pytest
      from flask import current_app, url_for
      
      def test_visit_index(app_content):
          current_app.logger.debug(app_content.app.config['SERVER_NAME'])
          current_app.logger.debug(url_for('main.index'))
          response = app_content.client.get(url_for("main.index"))
          current_app.logger.info(response.data)
          assert response.status_code == 200
      ```
   
      除去打印日志的内容，函数的功能只有获取response和assert两行。
   
      上面只保留了状态码验证，如果要对页面内容验证的话，则是：
   
      ```
      	assert b"welcome to CI/CD world" in response.data
      ```
   
      在完成这个测试以后，对于接口的测试用例编写已经可以开展了。
   
      但这里想对url_for方法的调用做一个简单介绍。url_for函数的调用路径，取决于flask create_app方法中注册的蓝图路径。在项目中是：
   
      ```
      def _register_blueprints(app):
          from .blueprints.main.views import bp as main_bp
      
          app.register_blueprint(main_bp, url_prefix="/main")
      ```
   
      对应路由处的方法是：
   
      ```
      @bp.route("/")
      def index():
          return "welcome to CI/CD world 🌏"
      ```
   
      因此此处的路径为"main.index"，即路径+方法名称。
   
   5. 文件处理
   
      上面说完了基础测试用例的执行，回归正题。文件上传/图片服务。使用OSS对象时，我们的开发只是对SDK中的方法进行了二次封装。因此从过程来看，在CI运行的服务器端不会保留文件的信息。为了保证每个文件在OSS存储时的独立性，使用uuid来锁定文件的唯一性。
   
      此外，后续根据实际业务需求，还要考虑对文件大小的限制，或者有可能需要留存和管理上传文件，这也是文件处理的考虑内容。
   
      根据唯一性要求，选用uuid.uuid1()或者uuid.uuid4()方法都是不错的。这里呢，就先用uuid1好了。
   
      写好方法以后，原函数的上传就改成这样了：
   
      ```
      		from app.wheel import create_unique_name
              name = create_unique_name()
              bucket.put_object(name, f)
              return "upload success, filename is {0}".format(name)
      ```
   
      运行$ make test-one结果：
   
      ```
      =========================== short test summary info ===========================
      FAILED flask-dev/tests/oss_test/test_main_api.py::test_upload_file - AssertionError: assert b'upload succ...-00163e0405b1' == b'upload success'
      ================== 1 failed, 1 passed, 1 warning in 0.28s======================
      ```
   
      然后简单修改测试用例：
   
      ```
      	response = app_content.client.post(url_for("main.upload_file"), data=payload, headers=headers)
          assert b"upload success" in response.data
          assert response.status_code == 200
      ```
   
      当然修改的不够严谨，项目中没有对这里进行展开，比较严谨的设计是：a.通过测试方法传递uuid，这修改了原函数的功能；b.使用mock对象进行mock。
   
      mock有很多方法，我常用的有两种，mock.patch方法用于mock调用方法，没有返回值或者需要mock返回值时，以及mock对象时使用的mock.patch.object方法：
   
      ```
      @mock.patch('main.index')
      @mock.patch('main.index', mock.Mock(return_value='uuid'))
      @mock.patch.object(Wechat)
      ```
   
       贴一下改造后的方法和测试函数：
   
      ```
      #testcase
      
      @mock.patch("app.wheel.create_unique_name", mock.Mock(return_value="c764d110-69bf-11ea-8cf0-00163e0405b1"))
      def test_upload_file(app_content):
          headers = {'content-type': 'multipart/form-data'}
          payload = {'data': 'aaa'}
          fileobj = b'test_file_upload_success'
          payload.update({'file': fileobj})
          response = app_content.client.post(url_for("main.upload_file"), data=payload, headers=headers)
          assert b"upload success, filename is c764d110-69bf-11ea-8cf0-00163e0405b1" == response.data
          assert response.status_code == 200
      ```
   
      ```
      #upload func
      @bp.route("/upload", methods=['GET', 'POST'])
      def upload_file():
          if request.method == 'POST':
              f = request.form['file']
              current_app.logger.info(f)
              import oss2
              access_key_id = current_app.config['OSS_AK_ID']
              access_key_secret = current_app.config['OSS_AK_SECRET']
              endpoint = current_app.config['OSS_ENDPOINT']
              bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, 'lxq-photo')
              from app.wheel import create_unique_name
              name = create_unique_name()
              bucket.put_object(name, f)
              return "upload success, filename is {0}".format(name)
      ```
   
      download的测试也已经完成，相关代码也已经整合，但目前没有对流数据的下载做实际验证，手头没有很好的工具。等之后再做补充吧。
   
# 题外话-额外的测试保障
​        在完成了上传和下载功能的测试以后，有几个待解决的问题：如何保障接口的可用性？系统面临的实际用户场景是怎样的？怎样了解当前服务的能力，能支持多大的用户数量？

​        只有这几个问题得到了有效的答案，才是考虑如何在项目上做加法和有序开发的时候。这也是项目到现在为止都没有引入消息队列，数据库或其他工具的原因。我们只有一个web服务和一个nginx服务，是时候对它们进行暴力验证的时候了。



1. 简单聊聊Jmeter

   ​		在这个项目之前，我对jmeter的认识停留在理论上。之前的项目可能什么都有了，但并不需要性能测试，因为瓶颈往往没有出现，或者是已有的监控手段下，系统设计欠缺导致的问题比性能问题更多，或者在问题来临前我们就把场景的规模给限制了。这些也许都不是重要的原因，因为万事的根源只有一个：人力。

   ​		我很清楚现在要做什么：测试我的上传下载服务接口，真正了解我部署的nginx和flask的性能极限，了解我的图片服务能否支持我当前的业务预期。

   ​		所以还是用jmeter来做测试吧

2. 开发准备

   ​		为了方便调试和脚本编写，jmeter推荐用GUI工具来做开发。所以为此还得先本地安装一个Java。

   ​		在安装完成java以后，Jmeter就可以正常使用了。这里推荐使用java8环境及3.x版本的jmeter(新版本可能会有插件不兼容的问题)

   ​		关于Jmeter的使用有很多介绍的教程。这里只展开当前需要用到的部分。

   ​		Jmeter软件打开后，选择新建-测试计划。创建一个Jmeter.jmx文件。这个文件相当于打包好的一整套测试用例集合。用例新建完成后，会有几个默认的组件被构建，分别是：

   ```
   User Defined Variables  # 用户定义的变量，我们可以把session类的数据放在这个集合里面
   HTTP Cookie Manager  # cookie管理，用于保存执行过程中产生和使用的数据
Thread Group  # 线程组，所有请求都建立在线程组之下，通过线程调度运行
   View Result Tree  # 请求结果树，用于查看每个http请求的详细报告
   ```
   
   ​		除了以上组件以外，还需要添加“聚合报告”组件，用以查看性能评估的结果。报告中提供执行样本的统计报表。
   
   ​		有了这几个基本组件后，我们就可以开始构建jmeter的测试了。
   
   ​		但直接进行跨网络的测试，步子仍然迈的大了。不仅是因为省略了nginx代理所产生的中间过程。更重要的是，在之前的测试中，我们使用的是基于flask上下文的接口测试。或者说的更清楚一点，我们只是进行了上传服务api的调用测试。但我们没有分离请求和服务，请求发起时，和服务是一体的。或者它们本身是隔离的，但是由于调用的基础构件都是flask，我们仍不能保证这个服务是可用的。因为flask是第三方的框架。
   
   ​		因此下一步的测试应该是启用两个服务，一个是flask服务，一个是调用服务，通过进程隔离来保障调用可以在通用的环境下正确运行。我本想用request包进行验证。但在这一层上更有效的方法是使用接口测试工具——postman/jmeter。
   
   ————————————
   
   ​		有趣的是，项目实际运行的结果产生了预料中的测试失败，并导致了我不能跳过这一部分的测试，而使用本地化构建最简Flask模型来验证flask提供的http服务。
   
3. 本地FLASK+Jmeter测试

   ​		本地化构建Flask服务时，至少目前，我们不能直接使用flask run来加载debug模式对服务进行验证。即使我在本地（win10）设置了FLASK_ENV, FLASK_APP, 甚至DEBUG=True。也不能正确加载配置服务。原因应该是和flask集成的脚本设置有关。因此我选择使用python直接运行的方式来启动，并修改了manage.py文件，加上了启动入口。

   ```
   $ python manage.py
   
   # manage.py
   
   ...
   
   if __name__ == "__main__":
       app.run(debug=True)
   ```

   ​		在之前的pytest中，已经测试过的multiple/form-data类型可以正确传递数据，传递的数据格式为ImmutableDict（['data':'aaa', 'file': b'test_file_upload']），在这个类型的基础上，可以通过request.form['file']来获取文件内容。

   ​	----2020.3.24更新----
   ​	昨天碰到了使用软件进行测试，返回http_code 400 error的问题。经过今天的定位调试。发现问题出在postman工具进行文件上传时，丢失了文件中的filename字段（例：Content-Disposition: form-data; name="file"; filename="list.txt"）。在更新过文件上传字段以后。顺便也将flask接口的request.form获取文件的方式改为了通过文件流request.files来获取的方式。对应的测试用例已经更新。另外，由于之前.gitignore文件注释掉了app/wheels文件，现将wheels文件夹更名为wheel文件夹。
    ​	---------------------
   ​	至此，本地化测试完成，可以进行网络测试并编写对应的压力测试计划了。

4. 压力测试

   ​	目前项目中完成的接口有两个： 1./upload; 2./download

   ​	假设待测场景的用户操作为：

   	1. 上传图片
    	2. 查看保存的图片

   ​	那么实际过程中，应该分别对两个接口各产生了一次调用。以这个操作为一个模拟，测试服务器的性能。先不引入性能测试中的指标的概念。

   ​	因而对于线程组的设置为： 请求间隔：1s 循环次数： 永远 线程设置 100-max

   ​	梯度测试结果如下：

   ```
   测试编号	名称	样本数	平均响应	中位响应	90%	95%	99%	最小响应	最大响应	错误比
   1	HTTP请求	4834	923	39	1470	3142	25089	10	44407	0.020686802
   2	HTTP请求	5107	1105	40	1472	3262	26377	13	46948	0.023497161
   3	HTTP请求	6115	1385	41	1509	6374	30144	12	56275	0.024529845
   4	HTTP请求	8383	2957	40	3140	12983	82001	12	84521	0.035667422
   5	HTTP请求	8818	6008	50	12953	52226	90930	13	92426	0.06804264
   6	HTTP请求	9702	7921	57	22750	86757	99315	13	100858	0.082457225
   吞吐量/秒	流量（接收）	流量（发送）	线程数（并发数）	请求间隔（秒）
   106.9895091	125.7914388	145.6000177	100	1
   107.3643492	126.283962	146.0709573	120	1
   107.2807018	126.320244	145.905993	150	1
   99.0804652	120.3158172	130.5566923	300	1
   95.37097123	120.1929593	121.3186572	600	1
   96.12793278	122.9146547	120.4185317	800	1
   
   ```

   ​	从测试结果看，按照90%的标准，响应时间3s，并发300左右。
   
   

# CI下篇：持续交付的环境改造



​		项目进行过程中，碰到了很多小疏漏，简单的文件上传/下载功能，用了很长的篇幅还发生了不少问题。好在目前已经是一个可用的，较为稳定服务了。

​		但到目前为止，项目仍然是在开发状态运行。由于手头资源所限，开发和生产环境打算都在一台机器上做，因此要对项目的配置进行一定的改造：对于开发和生产环境启动项的配置，账号的设置，nginx的代理分流，快速构建的指令及精简的环境包，一切看起来好像有了。但是没有实际测试之前，一切都谈不上就绪。



1. 多容器的构建

   nginx本身具有代理转发的功能。因此我们只需要把nginx中location设置为不同路径，在请求时就能根据路由跳转到不同服务上了。

   在设置完nginx后，docker-compose.yml也进行了对应的更新，分成了pro/dev/test三个不同的容器。与此同时，我们还需要对OSS服务进行隔离。创建新的bucket供测试和开发使用。

   为了测试不同环境下能正确加载GRAPH_SERVER_BUCKET的设置，先进行本地测试：

   对于flask shell命令，在启动之前要先设置环境变量，在不同的系统中设置环境变量的方式是不同的：

   ```
   # Linux
   $ export FLASK_APP=manage.py
   # windows
   C:\path\to\app>set FLASK_APP=manage.py
   # windows powershell
   PS C:\path\to\app> $env:FLASK_APP = "manage.py"
   ```

   设置完启动命令后，可以开始测试config的加载顺序了。

   我们在/flask-dev/app/__init__.py中有以下函数

   ```
   def create_app(config_name):
       app = Flask(__name__, instance_relative_config=True)
       app.config.from_object(config[config_name])
       app.config.from_pyfile("config.py", silent=True)
   
       _init_errors(app)
       _register_blueprints(app)
   
       return app
   ```

   其中from_object和from_pyfile两个方法分别对应读取flask-dev/config.py及读取.instance/config.py。

   第一个方法会执行Config类的加载，把config类的内容导入上下文环境中。第二个方法会重载已经导入的环境内容。这里的修改主要是为了额外支持重载OSS_SERVER_BUCKET属性。把OSS上生产环境的数据和开发环境隔离。