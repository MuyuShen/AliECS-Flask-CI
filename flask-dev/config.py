import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = "write by java"
    
    # OSS环境变量配置
    OSS_AK_ID = os.environ.get('OSS_AK_ID', '<你的access_key_id')
    OSS_AK_SECRET = os.environ.get('OSS_AK_SECRET', '<你的access_key_secret>')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', '<你的服务器访问域名>')


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost.localdomain"


config = {
    "develop": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


