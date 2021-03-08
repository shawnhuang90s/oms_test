from django.urls import path
from .views import UserListView

urlpatterns = [
    path('user_list/', UserListView.as_view()),  # 提供用户名接口
]
