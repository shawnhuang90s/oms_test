import socket


def get_ip():
    """查询项目所在服务器的 IP 地址"""
    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_obj.connect(('8.8.8.8', 80))
        ip = socket_obj.getsockname()[0]
    finally:
        socket_obj.close()

    return ip


if __name__ == '__main__':
    r = get_ip()
    print(f"项目所在服务器的 IP 地址：{r}")
