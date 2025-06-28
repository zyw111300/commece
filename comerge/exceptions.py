"""
自定义异常类
"""


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)


class InsufficientStockException(BusinessException):
    """库存不足异常"""

    def __init__(self, product_name: str, available_stock: int, required_stock: int):
        message = f"商品 {product_name} 库存不足，可用库存: {available_stock}，需要库存: {required_stock}"
        super().__init__(message, "INSUFFICIENT_STOCK")
        self.product_name = product_name
        self.available_stock = available_stock
        self.required_stock = required_stock


class ProductNotActiveException(BusinessException):
    """商品未激活异常"""

    def __init__(self, product_name: str):
        message = f"商品 {product_name} 已下架或不可用"
        super().__init__(message, "PRODUCT_NOT_ACTIVE")


class ConcurrentUpdateException(BusinessException):
    """并发更新异常"""

    def __init__(self, message: str = "并发更新失败，请重试"):
        super().__init__(message, "CONCURRENT_UPDATE_ERROR")
