from django.db import models


class BaseModel(models.Model):
    """公共模型类"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 定义为抽象基类, 表示迁移数据库的时候忽略这个公共模型类
        # 换句话说, 数据库不会创建这个模型类对应的表
        abstract = True
