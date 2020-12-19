from django.views.static import serve
from oms_test.settings import API_DOC_ROOT
from django.urls import path, include, re_path

urlpatterns = [
    path('store/', include(('store.urls', 'store'), namespace='store')),
    re_path('api_doc/(?P<path>.*)', serve, {'document_root': API_DOC_ROOT}),
]
