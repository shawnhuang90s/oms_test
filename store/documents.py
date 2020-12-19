"""
@api {GET} /store/store_account/ 查询Redis中店铺账户信息
@apiVersion 1.0.0
@apiName redis_query
@apiGroup Store
@apiDescription 查询Redis中店铺账户信息

@apiParam {String} key 店铺ID

@apiParamExample {String} 请求参数示例
http://127.0.0.1:8080/store/store_account/?key=54

@apiSuccessExample {Json} 查询成功示例
HTTP 1.1/ 200K
{
    "url": "url_54",
    "app_key": "app_key_54",
    "app_secret": "app_secret_54",
    "access_token": "access_token_54"
}
@apiErrorExample 查询失败示例
HTTP 1.1/ 200K
"Redis中没有店铺ID:aa 对应的账户信息"
"""