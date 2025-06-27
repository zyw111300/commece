"""
订单工具类
负责订单相关的工具函数
"""

import uuid
from datetime import datetime
from rest_framework.pagination import PageNumberPagination


class OrderNumberGenerator:
    """订单号生成器"""

    @staticmethod
    def generate() -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_suffix = str(uuid.uuid4())[:6].upper()
        return f"ORD{timestamp}{unique_suffix}"


class CustomPageNumberPagination(PageNumberPagination):
    """自定义分页器"""
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 100
