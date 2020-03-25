import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
<<<<<<< HEAD
<<<<<<< HEAD
    ENV = 'production'
    DEBUG = False
    TESTING = False

    # flask-dev/instance/config.py
    # 生产环境下以下变量请放在./instance目录下的config.py文件中
    SECRET_KEY = "write by java"
    OSS_AK_ID = 'uuid'
    OSS_AK_SECRET = 'uuid'
    OSS_ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    OSS_SERVER_BUCKET = {
    'production': 'ecs-photo',
    'develop': 'ecs-dev',
    'testing': 'ecs-test'
    }
=======
    DEBUG = False
    TESTING = False
    SECRET_KEY = "write by java"
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
    DEBUG = False
    TESTING = False
    SECRET_KEY = "write by java"
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
    
    # OSS环境变量配置
    OSS_AK_ID = os.environ.get('OSS_AK_ID', '<你的access_key_id')
    OSS_AK_SECRET = os.environ.get('OSS_AK_SECRET', '<你的access_key_secret>')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', '<你的服务器访问域名>')


class DevelopmentConfig(Config):
<<<<<<< HEAD
<<<<<<< HEAD
    ENV = 'develop'
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
    DEBUG = True


class TestingConfig(Config):
<<<<<<< HEAD
<<<<<<< HEAD
    ENV = 'testing'
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
    TESTING = True
    DEBUG = True
    SERVER_NAME = os.environ.get('SERVER_NAME', "localhost.localdomain")


config = {
    "develop": DevelopmentConfig,
    "testing": TestingConfig,
<<<<<<< HEAD
<<<<<<< HEAD
    "default": Config,
=======
    "default": DevelopmentConfig,
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
    "default": DevelopmentConfig,
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
}


