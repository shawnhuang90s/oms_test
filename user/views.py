from user.models import User
from rest_framework.views import APIView
from utils.decorator_func import login_auth
from rest_framework.response import Response
from django.utils.decorators import method_decorator


class UserListView(APIView):
    """用户信息展示接口"""

    # @method_decorator(login_auth)
    def get(self, request):
        try:
            user_list = [i.username for i in User.objects.all()]
        except Exception as e:
            print(e)
            user_list = []
        ret = {'code': 1, 'data': user_list}

        return Response(data=ret)
