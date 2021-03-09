from django.db import models


class User(models.Model):
    """用户信息表"""
    id = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')
    is_superuser = models.BooleanField(default=False, verbose_name='是否是超级用户')
    email = models.CharField(max_length=50, blank=True, verbose_name='邮箱')
    is_active = models.BooleanField(default=True, verbose_name='在职/离职状态')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')

    class Meta:
        db_table = 'oms_user'
        app_label = 'user'
        verbose_name = verbose_name_plural = '用户表'

    def __str__(self):
        # 优先显示用户名, 其次是ID
        return str(self.username) or str(self.id)

