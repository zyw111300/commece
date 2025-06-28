"""
订单数据访问层
负责订单相关的数据库操作
"""

from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.paginator import Paginator
from ..models import Order, OrderItem
from ..utils.cache_manager import cache_manager
import logging

logger = logging.getLogger(__name__)


class OrderRepository:
    """订单数据访问类"""

    def __init__(self):
        self.cache = cache_manager

    def create_order(self, order_no: str, user_id: int) -> Order:
        """创建订单"""
        return Order.objects.create(
            order_no=order_no,
            user_id=user_id,
            total_amount=0,
            status='pending'
        )

    def update_order(self, order: Order, total_amount: float, status: str) -> bool:
        """更新订单"""
        try:
            order.total_amount = total_amount
            order.status = status
            order.save()

            # 清除相关缓存
            self._invalidate_order_cache(order.order_no)
            return True
        except Exception as e:
            logger.error(f"Update order error: {e}")
            return False

    def create_order_item(self, order: Order, product, quantity: int,
                          unit_price: float, status: str = 'success',
                          error_message: str = "") -> OrderItem:
        """创建订单项"""
        total_price = unit_price * quantity if status == 'success' else 0

        return OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            status=status,
            error_message=error_message
        )

    def _invalidate_order_cache(self, order_no: str):
        """清除订单相关缓存"""
        cache_keys = [
            f"order:detail:{order_no}",
        ]

        for key in cache_keys:
            self.cache.delete(key)

        # 清除列表缓存
        self.cache.delete_pattern("order:list")
