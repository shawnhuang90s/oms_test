[TOC]

### 项目中生成 API 文档

#### 1. 安装 apidoc

```bash
npm install apidoc -g
# 升级版本
npm install -g npm
# 运行以下命令
apidoc -i myapp/ -o apidoc/ -t mytemplate/
# 运行结果如下, 提示要创建一个 apidoc.json 之类的文件
{"message":"Please create an apidoc.json or apidoc.config.js configuration file or add an 'apidoc' key to your package.json.","level":"warn"}
{"Path":"/home/yanfa","level":"error","message":"No files found."}
```

#### 2. 项目根目录下新建 apidoc.json 文件

```json
{
  "name": "OMS API DOCUMENTS",
  "version": "1.0.0",
  "description": "订单管理系统前后端联调的接口文档",
  "title": "API接口文档",
  "url" : "https://127.0.0.1:8080",
  "template": {
    "withCompare": true,
    "withGenerator": true,
    "aloneDisplay": false
  }
}
```

#### 3. apidoc 在项目中的配置

```python
# 项目根目录下新建 api_doc 目录

# oms_test/oms_test/settings.py
# 文件开头导入 os 模块
import os
......
INSTALLED_APPS = [
    ......
    # 这里注释掉
    # 'django.contrib.staticfiles',

    # 自建应用
    'store.apps.StoreConfig',
]
......
STATIC_URL = '/static/'
# 添加路径
API_DOC_ROOT = os.path.join(BASE_DIR, 'api_doc/')
```

#### 4. 添加路径

```python
# oms_test/oms_test/settings.py
from django.views.static import serve
from oms_test.settings import API_DOC_ROOT
from django.urls import path, include, re_path

urlpatterns = [
    path('store/', include(('store.urls', 'store'), namespace='store')),
    re_path('api_doc/(?P<path>.*)', serve, {'document_root': API_DOC_ROOT}),
]
```

#### 5. 项目子应用下添加文档文件

```python
# oms_test/store/documents.py
"""
@api {GET} /store/store_account/ 查询Redis中店铺账户信息
@apiVersion 1.0.0
@apiName redis_query
@apiGroup Store
@apiDescription 查询Redis中店铺账户信息

@apiParam {String} key 店铺ID

@apiParamExample {String} 请求参数示例
http://127.0.0.1:8080/store/store_account/?key=54

@apiSuccessExample {Json} 查询成功示例
HTTP 1.1/ 200K
{
    "url": "url_54",
    "app_key": "app_key_54",
    "app_secret": "app_secret_54",
    "access_token": "access_token_54"
}
@apiErrorExample 查询失败示例
HTTP 1.1/ 200K
"Redis中没有店铺ID:aa 对应的账户信息"
"""
```

#### 8. 执行文档生成命令

```bash
# api_doc 目录下新建 docs 目录
# 打开 Pycharm 终端，执行命令
# 命令语法格式：
# apidoc -i 包含注释信息的 .py 文件 -o 自动生成文档的目录
# 这里的 ./ 表示在当前项目根目录下的所有包含注释信息的 .py 文件
# api_doc/ 表示将生成的文件放在 api_doc 目录下
# 如果文档更新了，或者项目中其他地方也有接口文档，再次执行该命令即可
apidoc -i ./ -o api_doc/
```

#### 9. 验证是否生成文档

重启项目，浏览器访问以下 URL 查看效果

>http://127.0.0.1:8080/api_doc/index.html

#### 10. 忽略文件新增忽略内容

>api_doc/ 目录下的内容显然没有必要上传到远程仓库，因此要忽略它

```bash
# oms_test/.gitignore
.idea/
*.pyc
__pycache__/
oms_conf/
*/migrations/*
api_doc/
```

由于 git 已经有本地缓存，因此必须删除缓存，再把代码重新上传到远程仓库，否则忽略文件不生效

```bash
# 打开 Pycharm 终端
git rm -r -f --cached .
git add .
git commit -m '添加忽略文件并重新上传代码到远程仓库'
git push origin master
```

### 



### 权限验证