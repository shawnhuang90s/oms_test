from rest_framework.pagination import PageNumberPagination


class MyPageNumber(PageNumberPagination):

    page_size = 10  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = 1000  # 每页最大条数数限制
