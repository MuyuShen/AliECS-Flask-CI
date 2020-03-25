import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
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
    
    # OSS环境变量配置
    OSS_AK_ID = os.environ.get('OSS_AK_ID', '<你的access_key_id')
    OSS_AK_SECRET = os.environ.get('OSS_AK_SECRET', '<你的access_key_secret>')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', '<你的服务器访问域名>')


class DevelopmentConfig(Config):
    ENV = 'develop'
    DEBUG = True


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    DEBUG = True
    SERVER_NAME = os.environ.get('SERVER_NAME', "localhost.localdomain")


config = {
    "develop": DevelopmentConfig,
    "testing": TestingConfig,
    "default": Config,
}


