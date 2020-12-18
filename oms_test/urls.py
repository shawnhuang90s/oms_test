from django.urls import path, include

urlpatterns = [
    path('store/', include(('store.urls', 'store'), namespace='store')),
]
