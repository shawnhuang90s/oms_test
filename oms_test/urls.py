from django.views.static import serve
from oms_test.settings import API_DOC_ROOT
from django.http import HttpResponseRedirect
from django.urls import path, include, re_path


def clock_show(request):
    """首页重定向到一个展示个性时钟的网址"""
    return HttpResponseRedirect('http://chabudai.sakura.ne.jp/blogparts/honehoneclock/honehone_clock_tr.swf')


urlpatterns = [
    path('', clock_show),
    path('store/', include(('store.urls', 'store'), namespace='store')),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('basic/', include(('basic.urls', 'basic'), namespace='basic')),
    re_path('api_doc/(?P<path>.*)', serve, {'document_root': API_DOC_ROOT}),
]
