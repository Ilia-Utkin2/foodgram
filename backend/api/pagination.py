from rest_framework.pagination import LimitOffsetPagination


class RecipPagination(LimitOffsetPagination):

    efault_limit = 6  # Default limit
    limit_query_param = 'limit'  # Customize the limit query parameter
    offset_query_param = 'offset'  # Customize the offset query parameter
    max_limit = 100
