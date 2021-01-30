from django.db import models


class Store(models.Model):
    """店铺模型类"""
    STATUS_CHOICES = (
        (0, '关闭弃号'),
        (1, '正常可售'),
        (2, '注册中'),
        (3, '暂时关闭'),
        (4, '注册失败'),
        (5, '假期模式'),
    )
    # 可选择的店铺状态
    usable_status = (1, 3, 5)

    id = models.AutoField(primary_key=True, verbose_name='店铺ID')
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name='店铺名')
    manager_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='店铺负责人')
    manager_id = models.IntegerField(blank=True, null=True, verbose_name='店铺负责人ID')
    center = models.CharField(max_length=100, blank=True, null=True, verbose_name='渠道中心')
    center_id = models.IntegerField(blank=True, null=True, verbose_name='渠道中心ID')
    platform = models.CharField(max_length=45, blank=True, null=True, verbose_name='平台')
    market = models.CharField(max_length=200, blank=True, null=True, verbose_name='站点')
    market_id = models.IntegerField(blank=True, null=True, verbose_name='站点ID')
    status = models.SmallIntegerField(choices=STATUS_CHOICES, blank=True, null=True, verbose_name='状态')
    last_download_time = models.DateTimeField(blank=True, null=True, verbose_name='上次抓单时间')

    class Meta:
        # 告诉 Django 不要管理这个模型类的创建, 修改和删除
        # 想要允许 Django 管理这个模型类的生命周期, 直接删掉它(因为 True 是默认值)
        managed = False
        # 指明该模型类属于 store 这个子应用
        app_label = 'store'
        db_table = 'oms_store'
        verbose_name = verbose_name_plural = '店铺表'

    def __str__(self):
        return self.name
