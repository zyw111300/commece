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
    
    def get_by_order_no(self, order_no: str) -> Optional[Order]:
        """根据订单号获取订单"""
        cache_key = f"order:detail:{order_no}"
        
        def _get_order():
            try:
                return Order.objects.prefetch_related('items__product').get(
                    order_no=order_no
                )
            except Order.DoesNotExist:
                return None
        
        return self.cache.get_or_set(cache_key, _get_order, timeout=3600)
    
    def get_orders(self, user_id: Optional[int] = None, status: Optional[str] = None,
                   page: int = 1, size: int = 20) -> Dict[str, Any]:
        """获取订单列表"""
        cache_key = f"order:list:{user_id}:{status}:{page}:{size}"
        
        def _get_orders():
            try:
                queryset = Order.objects.all()
                
                if user_id:
                    queryset = queryset.filter(user_id=user_id)
                if status:
                    queryset = queryset.filter(status=status)
                
                queryset = queryset.order_by('-created_at')
                
                paginator = Paginator(queryset, size)
                page_obj = paginator.get_page(page)
                
                return {
                    'orders': list(page_obj),
                    'total': paginator.count,
                    'page': page,
                    'size': size,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            except Exception as e:
                logger.error(f"Get orders error: {e}")
                return {
                    'orders': [],
                    'total': 0,
                    'page': page,
                    'size': size,
                    'total_pages': 0,
                    'has_next': False,
                    'has_previous': False,
                }
        
        return self.cache.get_or_set(cache_key, _get_orders, timeout=600)
    
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
