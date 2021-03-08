from django.urls import path
from basic.views.permission_config import PermissionConfigView


urlpatterns = [
    path('permission_config/', PermissionConfigView.as_view()),  # 权限配置接口
]
