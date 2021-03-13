from django.urls import path
from .views import DealExcelInfoView

urlpatterns = [
    path('test_celery/', DealExcelInfoView.as_view()),  # 测试 Celery 处理 excel 接口
]
