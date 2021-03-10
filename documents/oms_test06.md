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

### 获取项目所在服务器的 IP 地址

```python
# oms_test/utils/get_host_ip.py
import socket


def get_ip():
    """查询项目所在服务器的 IP 地址"""
    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_obj.connect(('8.8.8.8', 80))
        ip = socket_obj.getsockname()[0]
    finally:
        socket_obj.close()

    return ip


if __name__ == '__main__':
    r = get_ip()
    print(f"项目所在服务器的 IP 地址：{r}")
```

### excel 文件上传下载 + Celery

#### 1. Celery 基本概念

- 倘若一个用户在执行某些操作需要等待很久才返回，这大大降低了网站的吞吐量，而 Celery 可以解决这个问题
- Celery 是一个基于 python 开发的分布式任务队列
- Django 的请求处理过程都是同步的无法实现异步任务，Celery 可以实现异步任务处理
- Django 请求过程简单说明：浏览器发起请求-->请求处理-->请求经过中间件-->路由映射-->视图处理业务逻辑-->响应请求

#### 1. 定义 excel 文件表头样式

```python
# oms_test/utils/excel_config.py
import xlwt


def set_excel_style(color='white', colour_index=0, height=180, bold=False, name=u'宋体',
                        horz=xlwt.Alignment.HORZ_CENTER, vert=xlwt.Alignment.VERT_CENTER):
    """定义 excel 文件内容样式"""
    style = xlwt.XFStyle()
    # 设置字体
    font_one = xlwt.Font()
    font_one.name = name
    font_one.bold = bold
    font_one.colour_index = colour_index
    font_one.height = height
    style.font = font_one

    # 设置文字位置
    alignment = xlwt.Alignment()
    alignment.horz = horz  # 水平方向设置：左对齐/居中/右对齐
    alignment.vert = vert  # 垂直方向设置
    style.alignment = alignment

    # 设置单元格背景颜色
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map[color]
    style.pattern = pattern

    # 设置单元格边框线条
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style.borders = borders

    return style
```



