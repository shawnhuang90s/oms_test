from datetime import datetime
from django.db import transaction
from rest_framework.views import APIView
from utils.get_username import get_username
from rest_framework.response import Response
from utils.page_settings import MyPageNumber
from django.utils.decorators import method_decorator
from basic.models import Permission, PermissionRecord
from utils.decorator_func import login_auth, admin_auth
from utils.permission_combination import get_permission_combination
from basic.serializers import PermissionRecordSerializer, PermissionSerializer


class PermissionConfigView(APIView):
    """权限配置"""

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def post(self, request):
        """新增权限配置"""

        operator = get_username(request)
        category = request.data.get('category', '')
        executor = request.data.get('executor', None)
        api_name_list = request.data.get('api_name_list', [])
        permission_type = request.data.get('permission_type', None)
        update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if not api_name_list:
            return Response({"code": 0, "desc": "界面模块名未知"})
        if not permission_type:
            return Response({"code": 0, "desc": "操作权限未知"})
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                for api_name in api_name_list:
                    permission_obj = Permission.objects.filter(api_name=api_name, operator=operator,
                                                               permission_type=permission_type).first()
                    # 如果已经创建了权限配置记录, 则更新权限记录表
                    if permission_obj:
                        if permission_obj.is_active == 1:
                            continue
                        permission_obj.is_active = 1
                        permission_obj.update_time = update_time
                        permission_obj.save(update_fields=['is_active', 'update_time'])

                        record_dict = {"permission": permission_obj.id, "before_change": 1, "after_change": 2,
                                       "create_time": update_time, "update_time": update_time}
                        record_serializer = PermissionRecordSerializer(data=record_dict)
                        record_serializer.is_valid(raise_exception=True)
                        record_serializer.save()
                        continue

                    # 没有就新建, 另外记录表也新增数据
                    permission_list = get_permission_combination(api_name, permission_type)
                    data_dict = dict(
                        api_name=api_name,
                        permission_list=permission_list,
                        executor=executor,
                        operator=operator,
                        permission_type=permission_type,
                        is_active=0,
                        category=category,
                        create_time=update_time,
                        update_time=update_time
                    )
                    permission_serializer = PermissionSerializer(data=data_dict)
                    permission_serializer.is_valid(raise_exception=True)
                    new_obj = permission_serializer.save()

                    record_dict = {"permission": new_obj.id, "before_change": 0, "after_change": 1,
                                   "create_time": update_time, "update_time": update_time}
                    record_serializer = PermissionRecordSerializer(data=record_dict)
                    record_serializer.is_valid(raise_exception=True)
                    record_serializer.save()

                return Response({"code": 1, "desc": f"权限分配成功"})
            except Exception as e:
                transaction.savepoint_rollback(save_point)
                return Response({"code": 0, "desc": f"权限分配失败：{e}"})

    # @method_decorator(login_auth)
    # @method_decorator(admin_auth)
    def get(self, request):
        """查询权限分配信息"""
        try:
            executor = request.query_params.get("executor", None)
            is_active = request.query_params.get("is_active", '未知')
            category = request.query_params.get('category', None)
            # 因为数据新建时默认是禁用的, 这里展示的时候也要优先展示禁用的并且按创建时间倒序排列
            permission_infos = Permission.objects.all().order_by('-is_active', '-create_time')
            if category:
                permission_infos = permission_infos.filter(category=category)
            if executor:
                permission_infos = permission_infos.filter(executor=executor)
            if is_active != '未知':
                permission_infos = permission_infos.filter(is_active=is_active)
            count = permission_infos.count()
            page = MyPageNumber()
            page_info = page.paginate_queryset(queryset=permission_infos, request=request, view=self)
            serializer = PermissionSerializer(page_info, many=True)

            return Response({"code": 1, "desc": "succeed", "data": serializer.data, "count": count})
        except Exception as e:
            return Response({"code": 1, "desc": "failed", "data": f"获取数据失败：{e}"})


class PermissionRecordListView(APIView):
    """查看权限分配记录"""

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def get(self, request):

        category = request.query_params.get('category', None)
        record_infos = PermissionRecord.objects.filter(category=category).order_by('-id')
        count = record_infos.count()
        page = MyPageNumber()
        page_info = page.paginate_queryset(queryset=record_infos, request=request, view=self)
        serializer = PermissionRecordSerializer(page_info, many=True)
        return Response({"code": 1, "desc": "succeed", "data": serializer.data, "count": count})


class PermissionChangeView(APIView):
    """修改权限状态"""

    @method_decorator(login_auth)
    @method_decorator(admin_auth)
    def put(self, request):
        update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                operator = get_username(request)
                pk = request.data.get("id", None)
                is_active = request.data.get("is_active", "未知")
                # 更新权限配置表对应数据的状态
                permission_obj = Permission.objects.get(id=pk)
                before_change = permission_obj.is_active
                permission_obj.is_active = is_active
                permission_obj.operator = operator
                permission_obj.update_time = update_time
                permission_obj.save(update_fields=['is_active', 'operator', 'update_time'])
                # 更新权限记录表对应的状态
                record = {"permission": pk, "before_change": before_change, "after_change": is_active,
                          "create_time": update_time, "update_time": update_time}
                record_serializer = PermissionRecordSerializer(data=record)
                record_serializer.is_valid(raise_exception=True)
                record_serializer.save()
                return Response({"code": 1, "desc": "权限状态修改成功"})
            except Exception as e:
                transaction.savepoint_rollback(save_point)
                return Response({"code": 0, "desc": f"权限状态修改失败：{e}"})
