from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 30


class NewsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'
    max_page_size = 1000000


class FeedbackPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 30


class SupportPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'limit'
    max_page_size = 10000000
