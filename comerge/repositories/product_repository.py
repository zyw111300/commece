"""
商品数据访问层
负责商品相关的数据库操作
"""

from typing import List, Optional, Dict, Any
from django.db.models import Q, QuerySet, F
from django.core.paginator import Paginator
from django.db import transaction
from ..models import Product, StockLog
from ..utils.cache_manager import cache_manager
from ..exceptions import (
    InsufficientStockException,
    ProductNotActiveException,
    ConcurrentUpdateException
)
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    """商品数据访问类"""

    def __init__(self):
        self.cache = cache_manager

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """根据ID获取商品"""
        cache_key = f"product:detail:{product_id}"

        def _get_product():
            try:
                return Product.objects.select_related().get(
                    id=product_id,
                    status='active'
                )
            except Product.DoesNotExist:
                return None

        return self.cache.get_or_set(cache_key, _get_product, timeout=3600)

    def search_products(self, keyword: str, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """搜索商品"""
        cache_key = f"product:search:{keyword}:{page}:{size}"

        def _search_products():
            try:
                queryset = Product.objects.filter(
                    Q(name__icontains=keyword) |
                    Q(keywords__icontains=keyword) |
                    Q(description__icontains=keyword),
                    status='active'
                ).order_by('-created_at')

                paginator = Paginator(queryset, size)
                page_obj = paginator.get_page(page)

                return {
                    'products': list(page_obj),
                    'total': paginator.count,
                    'page': page,
                    'size': size,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            except Exception as e:
                logger.error(f"Search products error: {e}")
                return {
                    'products': [],
                    'total': 0,
                    'page': page,
                    'size': size,
                    'total_pages': 0,
                    'has_next': False,
                    'has_previous': False,
                }

        return self.cache.get_or_set(cache_key, _search_products, timeout=1800)

    def get_with_lock(self, product_id: int) -> Optional[Product]:
        """获取商品并加锁（用于库存操作）"""  # 使用select_for_update来加锁
        try:
            return Product.objects.select_for_update().get(
                id=product_id,
                status='active'
            )
        except Product.DoesNotExist:
            return None

    # 使用事务来确保库存更新的原子性
    @transaction.atomic
    def update_stock(self, product: Product, quantity_change: int, reason: str = "") -> bool:
        """更新库存"""
        try:
            old_stock = product.stock_quantity
            product.stock_quantity += quantity_change
            product.version += 1
            product.save()

            # 记录库存日志
            StockLog.objects.create(
                product=product,
                change_type='decrease' if quantity_change < 0 else 'increase',
                quantity_before=old_stock,
                quantity_after=product.stock_quantity,
                change_quantity=quantity_change,
                reason=reason
            )

            # 清除相关缓存
            self._invalidate_product_cache(product.id)
            return True

        except Exception as e:
            logger.error(f"Update stock error: {e}")
            return False

    def get_stock_logs(self, product_id: int, page: int = 1, size: int = 20) -> QuerySet:
        """获取商品库存日志"""
        return StockLog.objects.filter(
            product_id=product_id
        ).order_by('-created_at')

    def _invalidate_product_cache(self, product_id: int):
        """清除商品相关缓存"""
        cache_keys = [
            f"product:detail:{product_id}",
        ]

        for key in cache_keys:
            self.cache.delete(key)

        # 清除列表和搜索缓存
        self.cache.delete_pattern("product:list")
        self.cache.delete_pattern("product:search")
