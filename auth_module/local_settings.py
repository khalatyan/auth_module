import pymysql
pymysql.install_as_MySQLdb()
# import os
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'auth_module',
        'USER': 'mysql',
        'PASSWORD': 'mysql',
        'HOST': '127.0.0.1',
    }
}
