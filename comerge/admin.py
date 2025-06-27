from django.contrib import admin
from .models import Product, Order, OrderItem, StockLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock_quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'keywords')
    list_editable = ('price', 'stock_quantity', 'status')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'price', 'stock_quantity')
        }),
        ('搜索与状态', {
            'fields': ('keywords', 'status')
        }),
        ('系统信息', {
            'fields': ('version',),
            'classes': ('collapse',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'user_id', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_no', 'user_id')
    readonly_fields = ('order_no', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('订单信息', {
            'fields': ('order_no', 'user_id', 'total_amount', 'status')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'unit_price', 'total_price', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_no', 'product__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'change_type', 'quantity_before', 'quantity_after', 'change_quantity', 'created_at')
    list_filter = ('change_type', 'created_at')
    search_fields = ('product__name', 'order__order_no', 'reason')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('变更信息', {
            'fields': ('product', 'order', 'change_type', 'reason')
        }),
        ('数量信息', {
            'fields': ('quantity_before', 'quantity_after', 'change_quantity')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
