from django.apps import apps


def get_fields_verbose_name(app_name, model_name):
    """
    获取模型类的字段名和 verbose_name 对应的内容
    :param app_name: 子应用名称
    :param model_name: 模型类名称
    :return: {字段名：verbose_name}
    """
    model_obj = apps.get_model(app_name, model_name)
    mapping_dict = dict()
    for field in model_obj._meta.fields:
        mapping_dict[field.name] = field.verbose_name

    return mapping_dict
