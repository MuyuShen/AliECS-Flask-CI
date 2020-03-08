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