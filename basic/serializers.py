from rest_framework import serializers
from .models import PermissionRecord, Permission


class PermissionRecordSerializer(serializers.ModelSerializer):
    """权限记录序列化器"""

    class Meta:
        model = PermissionRecord
        fields = "__all__"
        read_only_fields = ['create_time', 'update_time']


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    class Meta:
        model = Permission
        fields = "__all__"
        read_only_fields = ['create_time', 'update_time']

