from rest_framework import serializers
from .models import Product, Order, OrderItem, StockLog


class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock_quantity',
                  'keywords', 'status', 'version', 'created_at', 'updated_at']
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']

    def validate_price(self, value):
        """验证价格"""
        if value <= 0:
            raise serializers.ValidationError("价格必须大于0")
        return value

    def validate_stock_quantity(self, value):
        """验证库存数量"""
        if value < 0:
            raise serializers.ValidationError("库存数量不能为负数")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """商品列表序列化器"""

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock_quantity', 'status']


class ProductSearchSerializer(serializers.Serializer):
    """商品搜索参数序列化器"""
    keyword = serializers.CharField(required=True, min_length=1, max_length=100)
    page = serializers.IntegerField(default=1, min_value=1)
    size = serializers.IntegerField(default=20, min_value=1, max_value=100)


# 用来输出信息
class OrderItemSerializer(serializers.ModelSerializer):
    """订单明细序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price',
                  'total_price', 'status', 'error_message', 'created_at']
        read_only_fields = ['id', 'product_name', 'total_price', 'created_at']

    def validate_quantity(self, value):
        """验证数量"""
        if value <= 0:
            raise serializers.ValidationError("数量必须大于0")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order_no', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'order_number', 'user_id', 'total_amount', 'status',
                  'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'order_no', 'order_number', 'total_amount', 'created_at', 'updated_at']


# 用来输入校验
class BatchOrderItemSerializer(serializers.Serializer):
    """批量下单明细序列化器"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        """验证商品ID是否存在"""
        from .models import Product
        try:
            Product.objects.get(id=value, status='active')
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"商品ID {value} 不存在或已下架")
        return value


class BatchOrderSerializer(serializers.Serializer):
    """批量下单序列化器"""
    user_id = serializers.IntegerField()
    order_items = BatchOrderItemSerializer(many=True)

    def validate_order_items(self, value):
        """验证订单项"""
        if not value:
            raise serializers.ValidationError("订单项不能为空")
        if len(value) > 50:  # 限制单次最多50个商品
            raise serializers.ValidationError("单次最多只能下单50个商品")
        return value


class StockLogSerializer(serializers.ModelSerializer):
    """库存日志序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True)

    class Meta:
        model = StockLog
        fields = ['id', 'product', 'product_name', 'order', 'order_no',
                  'change_type', 'quantity_before', 'quantity_after',
                  'change_quantity', 'reason', 'created_at']
        read_only_fields = ['id', 'product_name', 'order_no', 'created_at']
