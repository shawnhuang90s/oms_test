from django.urls import path
from basic.views.permission_config import PermissionConfigView, PermissionRecordListView, PermissionChangeView


urlpatterns = [
    path('permission_config/', PermissionConfigView.as_view()),  # 权限配置接口
    path('permission_record/', PermissionRecordListView.as_view()),  # 权限配置记录接口
    path('permission_change/', PermissionChangeView.as_view()),  # 权限配置更新接口
]
