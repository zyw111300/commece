from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'comerge'

# DRF路由器
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'stock-logs', views.StockLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
