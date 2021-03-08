def get_username(request):
    """从 COOKIES 中获取用户名"""
    try:
        cookie = request.COOKIES
        if "messages" not in cookie.keys():
            return None
        messages = cookie["messages"].split("$")[1]
        try:
            info = messages.split('."]')[0].split(", ")[1]
        except Exception:
            info = messages.split('."]')[0].split("as ")[1]
        username = info.encode("utf-8").decode("unicode_escape")
    except Exception:
        return None

    return username
