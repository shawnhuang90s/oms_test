import os
from pathlib import Path
from oms_conf import oms_db, oms_redis, oms_kafka, oms_log


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'xqd19(a7n=3#+c#1w-$^v*v*d-ity4s(x+6afhjnk7q1_)wd_y'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',

    # 自建应用
    'store.apps.StoreConfig',
    'user.apps.UserConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oms_test.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oms_test.wsgi.application'

DATABASES = oms_db.DATABASES
# 配置读写分离
DATABASE_ROUTERS = ['oms_conf.oms_db.MasterSlaveDBRouter']

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
API_DOC_ROOT = os.path.join(BASE_DIR, 'api_doc/')

# Redis 配置
REDIS_CONF = oms_redis.REDIS_CONF

# Kafka 配置
KAFKA_HOST = oms_kafka.KAFKA_HOST
KAFKA_PORT = oms_kafka.KAFKA_PORT

REST_FRAMEWORK = {
    # 全局设置, 默认所有接口都需要被验证
    'DEFAULT_PERMISSION_CLASSES': (
        'utils.permissions.APIPermission',
        # 'utils.permissions.IsIdempotent',
    ),
}

########## 日志配置 ##########
KAFKA_LOG = oms_log.kafka_log