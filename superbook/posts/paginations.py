from rest_framework.pagination import PageNumberPagination


class PostPagination(PageNumberPagination):
    """
    Post Pagination class
    """

    page_size = 1
    page_query_param = "page"
