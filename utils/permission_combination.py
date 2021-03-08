def get_permission_combination(api_name, permission_type):
    """获取权限组合ID示例"""
    # 查看权限配置
    if permission_type == 0:
        if api_name == "海外仓备货申请页":
            permission_list = '1'
        elif api_name == "海外仓备货进度查看":
            permission_list = '4+5'
        elif api_name == "海外仓备货审核":
            permission_list = '8'
        elif api_name == "海外仓备货公式配置":
            permission_list = '13+15'
        elif api_name == "海外仓备货系数设置":
            permission_list = '19+22+25'
        elif api_name == "海外仓备货预算分配":
            permission_list = '27+28'
        elif api_name == "待分配调拨清单":
            permission_list = '32'
        elif api_name == "待创建调拨清单":
            permission_list = '45'
        elif api_name == "已创建调拨清单":
            permission_list = '43'
        elif api_name == "备货已结案清单":
            permission_list = '41'
        elif api_name == 'FBA仓备货申请页':
            permission_list = '49'
        elif api_name == 'FBA仓备审核和进度':
            permission_list = '52+54'
        elif api_name == 'FBA仓备货时效统计表':
            permission_list = '60'
        elif api_name == 'FBA仓备货预算分配':
            permission_list = '61+62'
        elif api_name == 'FBA审核流程配置':
            permission_list = '64+65'
        elif api_name == 'FBA仓预算权限配置':
            permission_list = '72'
        else:
            permission_list = ''
    # 操作权限配置(包含查看权限)
    else:
        if api_name == "海外仓备货申请页":
            permission_list = '1+2+3+4'
        elif api_name == "海外仓备货进度查看":
            permission_list = '4+5+6+7'
        elif api_name == "海外仓备货审核":
            permission_list = '8+9+10+11+29'
        elif api_name == "海外仓备货公式配置":
            permission_list = '12+13+14+15'
        elif api_name == "海外仓备货系数设置":
            permission_list = '16+17+19+20+21+22'
        elif api_name == "海外仓备货预算分配":
            permission_list = '26+27+28'
        elif api_name == "待分配调拨清单":
            permission_list = '31+32+33+34+35+36'
        elif api_name == "待创建调拨清单":
            permission_list = '45+46+47+48'
        elif api_name == "已创建调拨清单":
            permission_list = '43+44'
        elif api_name == "备货已结案清单":
            permission_list = '41+42'
        elif api_name == 'FBA仓备货申请页':
            permission_list = '49+50+51'
        elif api_name == 'FBA仓备审核和进度':
            permission_list = '52+54+55+56+57+58+59'
        elif api_name == 'FBA仓备货时效统计表':
            permission_list = '60'
        elif api_name == 'FBA仓备货预算分配':
            permission_list = '61+62+63'
        elif api_name == 'FBA审核流程配置':
            permission_list = '64+65+66+67+68+69'
        elif api_name == 'FBA仓预算权限配置':
            permission_list = '71+72+73'
        else:
            permission_list = ''

    return permission_list
