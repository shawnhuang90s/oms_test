from django.db import models
from user.models import User
from utils.base_model import BaseModel


class PermissionList(BaseModel):
    """权限接口详情表"""

    id = models.AutoField(primary_key=True)
    api_url_address = models.CharField(max_length=256, verbose_name="接口地址")
    request_method = models.CharField(max_length=10, verbose_name="请求方式")
    permission_name = models.CharField(max_length=128, verbose_name="权限名称")

    class Meta:
        db_table = 'oms_permission_list'
        app_label = 'basic'
        verbose_name = verbose_name_plural = '权限接口详情表'
        unique_together = ["api_url_address", "request_method"]


class Permission(BaseModel):
    """查看/操作权限表"""

    PERMISSION_TYPE = (
        (0, "查看"),
        (1, "操作"),
    )
    STATE_TYPE = (
        (0, "禁用"),
        (1, "启用"),
    )
    CATEGORY_TYPE = (
        (0, '模块1'),
        (1, '模块2'),
        (2, '模块3'),
    )
    id = models.AutoField(primary_key=True)
    api_name = models.CharField(max_length=64, null=True, blank=True, verbose_name="界面模块")
    permission_list = models.CharField(max_length=64, null=True, blank=True, verbose_name="权限ID组合")
    # 注意：之前有提供用户名接口, 没有传用户ID给前端, 因此这里保存时也只能存用户名. 当然, 也可以在那个接口把 ID 和用户名都传给前端, 这样的话这里保存前端返回的 ID 即可
    executor = models.CharField(max_length=64, verbose_name="执行人")
    operator = models.CharField(max_length=64, verbose_name="操作人")
    permission_type = models.SmallIntegerField(choices=PERMISSION_TYPE, default=0, verbose_name="权限类型")
    is_active = models.SmallIntegerField(choices=STATE_TYPE, default=0, verbose_name="是否启用(默认启用)")
    category = models.SmallIntegerField(choices=CATEGORY_TYPE, default=0, verbose_name='模块类别')

    class Meta:
        db_table = 'oms_permission'
        app_label = 'basic'
        verbose_name = verbose_name_plural = '查看/操作权限表'


class PermissionRecord(BaseModel):
    """查看/操作权限分配记录表"""

    STATE_TYPE = (
        (0, "未分配权限"),
        (1, "禁用"),
        (2, "启用"),
    )
    id = models.AutoField(primary_key=True)
    permission = models.ForeignKey(Permission, related_name="permission_id", verbose_name="权限ID", on_delete=models.CASCADE)
    before_change = models.SmallIntegerField(choices=STATE_TYPE, verbose_name="被修改之前的状态")
    after_change = models.SmallIntegerField(choices=STATE_TYPE, verbose_name="被修改之后的状态")

    class Meta:
        db_table = 'oms_permission_record'
        app_label = 'basic'
        verbose_name = verbose_name_plural = '查看/操作权限记录表'
