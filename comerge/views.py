from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from comerge.utils.order_utils import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Order, OrderItem, StockLog
from .serializer import (
    ProductSerializer, ProductListSerializer, ProductSearchSerializer,
    OrderSerializer, BatchOrderSerializer, StockLogSerializer
)
from .business.product_service import ProductService
from .business.order_service import OrderService
from .exceptions import (
    BusinessException,
    InsufficientStockException,
    ProductNotActiveException,
    ConcurrentUpdateException
)
import logging

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """商品ViewSet - 只负责HTTP请求处理"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'price']
    ordering_fields = ['price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']  # 默认按创建时间降序

    def get_serializer_class(self):
        """根据action选择不同的序列化器"""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        """获取查询集，只返回活跃商品"""
        return Product.objects.filter(status='active')

    @action(detail=False, methods=['get'])
    def search(self, request):
        """商品搜索API"""
        try:
            product_service = ProductService()
            serializer = ProductSearchSerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response({
                    'code': 400,
                    'message': '参数错误',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data
            result = product_service.search_products(
                validated_data['keyword'],
                validated_data['page'],
                validated_data['size']
            )

            # 使用DRF分页和序列化器
            paginator = self.pagination_class()
            page_obj = paginator.paginate_queryset(result['products'], request)
            if page_obj is not None:
                product_serializer = ProductListSerializer(page_obj, many=True)
                return paginator.get_paginated_response({
                    'code': 200,
                    'message': '搜索成功',
                    'data': product_serializer.data
                })

            product_serializer = ProductListSerializer(result['products'], many=True)
            return Response({
                'code': 200,
                'message': '搜索成功',
                'data': {
                    'products': product_serializer.data,
                    'total': result['total'],
                    'page': result['page'],
                    'size': result['size'],
                    'total_pages': result['total_pages'],
                    'has_next': result['has_next'],
                    'has_previous': result['has_previous'],
                }
            })

        except ProductNotActiveException as e:
            return Response({
                'code': 404,
                'message': e.message,
                'code_type': e.code
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                'code': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Search products error: {e}")
            return Response({
                'code': 500,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def stock_logs(self, request, pk=None):
        """获取商品库存变更日志"""
        try:
            product_service = ProductService()
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 20))

            logs_queryset = product_service.get_stock_logs(int(pk), page, size)

            # 使用DRF分页
            paginator = self.pagination_class()
            page_obj = paginator.paginate_queryset(logs_queryset, request)
            if page_obj is not None:
                serializer = StockLogSerializer(page_obj, many=True)
                return paginator.get_paginated_response({
                    'code': 200,
                    'message': '获取成功',
                    'data': serializer.data
                })

            serializer = StockLogSerializer(logs_queryset, many=True)
            return Response({
                'code': 200,
                'message': '获取成功',
                'data': serializer.data
            })

        except ProductNotActiveException as e:
            return Response({
                'code': 404,
                'message': e.message,
                'code_type': e.code
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                'code': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Get stock logs error: {e}")
            return Response({
                'code': 500,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderViewSet(viewsets.ModelViewSet):
    """订单ViewSet - 只负责HTTP请求处理"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'user_id']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    lookup_field = 'order_no'
    lookup_url_kwarg = 'order_no'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_service = OrderService()

    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """批量创建订单API"""
        try:
            serializer = BatchOrderSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'code': 400,
                    'message': '参数错误',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data
            result = self.order_service.create_batch_order(
                validated_data['user_id'],
                validated_data['order_items']
            )

            return Response({
                'code': 200,
                'message': '订单创建成功',
                'data': result
            })

        except InsufficientStockException as e:
            return Response({
                'code': 400,
                'message': e.message,
                'code_type': e.code,
                'product_name': e.product_name,
                'available_stock': e.available_stock,
                'required_stock': e.required_stock
            }, status=status.HTTP_400_BAD_REQUEST)
        except ProductNotActiveException as e:
            return Response({
                'code': 404,
                'message': e.message,
                'code_type': e.code
            }, status=status.HTTP_404_NOT_FOUND)
        except ConcurrentUpdateException as e:
            return Response({
                'code': 409,
                'message': e.message,
                'code_type': e.code
            }, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({
                'code': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Create batch order error: {e}")
            return Response({
                'code': 500,
                'message': '服务器内部错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
