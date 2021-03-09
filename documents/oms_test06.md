[TOC]

### 定时任务

#### 1. 日志配置

```python
# oms_test/oms_conf/oms_log.py
......
# 定时任务路径配置
crontab_log = f'{log_base_path}/crontab/'
```

#### 2. 下载并添加 django-crontab

```bash
pip install django-crontab

# oms_test/oms_test/settings.py
INSTALLED_APPS = [
    ......
    
    # 第三方应用
    'django_crontab',

    # 自建应用
    'store.apps.StoreConfig',
    'user.apps.UserConfig',
    'basic.apps.BasicConfig',
]

......
# 
```

#### 3. 编写一个测试函数

```python
# oms_test/basic/tests.py
import loguru
from oms_test.settings import CRONTAB_LOG
logger = loguru.logger
logger.add(f'{CRONTAB_LOG}basic_tests.log', format='{time} {level} {message}', level='INFO')


def crontab_test():
    """测试定时任务"""
    logger.info(1111111111111111111)
    logger.info('这是定时任务测试...')
    logger.info(2222222222222222222)


if __name__ == '__main__':
    crontab_test()
```

#### 4. 配置定时任务

```python
# oms_test/oms_test/settings.py
......
# 定时任务配置
CRONJOBS = [
    # 每一分钟执行一次测试函数, 后面的参数从项目根目录开始
    # 比如这里相当于执行 oms_test/basic/tests 下的 crontab_test() 
    ('*/1 * * * *', 'basic.tests.crontab_test'),
]
```

#### 5. 执行定时任务

```bash
python manage.py crontab add
# 一分钟后，查看对应日志文件，发现有内容了，说明定时任务生效

# 查看有哪些定时任务
python manage.py crontab show
# 删除所有的定时任务(上面测试的定时任务生效后记得移除)
python manage.py crontab remove
```

