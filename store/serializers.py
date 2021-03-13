from .models import Store
from rest_framework import serializers


class StoreInfoSerializer(serializers.ModelSerializer):
    """权限记录序列化器"""

    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ['last_download_time']
