from django.urls import path
from store.views.redis_query import StoreAccountView


urlpatterns = [
    path('store_account/',StoreAccountView.as_view()),
]