from django.db import models
from django.utils import timezone
import uuid


class Product(models.Model):
    """商品模型"""
    STATUS_CHOICES = [
        ('active', '在售'),
        ('inactive', '下架'),
        ('out_of_stock', '缺货'),
    ]

    name = models.CharField(max_length=255, verbose_name='商品名称')
    description = models.TextField(blank=True, verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='库存数量')
    keywords = models.CharField(max_length=255, blank=True, verbose_name='搜索关键词')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    version = models.PositiveIntegerField(default=1, verbose_name='版本号')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 添加对字段的索引来提高查询性能
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['status']),
            models.Index(fields=['keywords']),
        ]

    def __str__(self):
        return self.name


class Order(models.Model):
    """订单模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('completed', '已完成'),
        ('partial', '部分成功'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单号')
    user_id = models.PositiveIntegerField(verbose_name='用户ID')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['order_no']),
            models.Index(fields=['user_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.order_no


class OrderItem(models.Model):
    """订单明细模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('success', '成功'),
        ('failed', '失败'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.order.order_no} - {self.product.name}"


class StockLog(models.Model):
    """库存变更日志模型"""
    CHANGE_TYPE_CHOICES = [
        ('decrease', '减少'),
        ('increase', '增加'),
        ('adjust', '调整'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPE_CHOICES)
    quantity_before = models.PositiveIntegerField(verbose_name='变更前库存')
    quantity_after = models.PositiveIntegerField(verbose_name='变更后库存')
    change_quantity = models.IntegerField(verbose_name='变更数量')
    reason = models.CharField(max_length=255, blank=True, verbose_name='原因')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_logs'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['order']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.change_type}"
