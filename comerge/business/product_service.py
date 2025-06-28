"""
商品业务服务层
负责商品相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from ..repositories.product_repository import ProductRepository
from ..models import Product
from ..exceptions import ProductNotActiveException
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """商品业务服务"""

    def __init__(self):
        self.repository = ProductRepository()

    def search_products(self, keyword: str, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """搜索商品"""
        if not keyword or not keyword.strip():
            raise ValueError("搜索关键词不能为空")
        
        if size > 100:
            size = 100
        
        return self.repository.search_products(keyword.strip(), page, size)

    def get_stock_logs(self, product_id: int, page: int = 1, size: int = 20):
        """获取商品库存日志"""
        # 验证商品是否存在
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotActiveException(f"商品ID: {product_id}")

        return self.repository.get_stock_logs(product_id, page, size)
