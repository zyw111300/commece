"""
订单业务服务层
负责订单相关的业务逻辑处理
"""

from typing import List, Dict, Any, Optional
from django.db import transaction
from ..repositories.product_repository import ProductRepository
from ..repositories.order_repository import OrderRepository
from ..models import Order, OrderItem
from ..utils.order_utils import OrderNumberGenerator
import logging

logger = logging.getLogger(__name__)


class OrderService:
    """订单业务服务"""

    def __init__(self):
        self.product_repo = ProductRepository()
        self.order_repo = OrderRepository()
        self.order_generator = OrderNumberGenerator()

    def create_batch_order(self, user_id: int, order_items: List[Dict]) -> Dict[str, Any]:
        """批量创建订单"""
        # 验证参数
        if not user_id:
            raise ValueError("用户ID不能为空")

        if not order_items:
            raise ValueError("订单项不能为空")

        if len(order_items) > 50:
            raise ValueError("单次最多只能下单50个商品")

        # 生成订单号
        order_no = self.order_generator.generate()

        # 处理订单
        return self._process_batch_order(user_id, order_no, order_items)

    def _process_batch_order(self, user_id: int, order_no: str, order_items: List[Dict]) -> Dict[str, Any]:
        """处理批量订单"""
        results = {
            'order_no': order_no,
            'success_items': [],
            'failed_items': [],
            'total_amount': 0,
            'status': 'pending'
        }

        # 创建订单主记录
        order = self.order_repo.create_order(order_no, user_id)

        try:
            with transaction.atomic():
                for item_data in order_items:
                    result = self._process_single_item(order, item_data)

                    if result['success']:
                        results['success_items'].append(result)
                        results['total_amount'] += float(result['total_price'])
                    else:
                        results['failed_items'].append(result)

                # 确定订单状态
                if results['failed_items'] and results['success_items']:
                    status = 'partial'
                elif results['failed_items'] and not results['success_items']:
                    status = 'failed'
                else:
                    status = 'completed'

                # 更新订单
                self.order_repo.update_order(order, results['total_amount'], status)
                results['status'] = status

        except Exception as e:
            logger.error(f"Batch order processing error: {e}")
            self.order_repo.update_order(order, 0, 'failed')
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def _process_single_item(self, order: Order, item_data: Dict) -> Dict[str, Any]:
        """处理单个订单项"""
        product_id = item_data['product_id']
        quantity = item_data['quantity']

        try:
            # 获取商品并加锁
            product = self.product_repo.get_with_lock(product_id)
            if not product:
                # 商品不存在，创建失败记录
                self.order_repo.create_order_item(
                    order, None, quantity, 0, 'failed', '商品不存在或已下架'
                )
                return {
                    'success': False,
                    'product_id': product_id,
                    'quantity': quantity,
                    'error_message': '商品不存在或已下架'
                }

            # 检查库存
            if product.stock_quantity < quantity:
                # 库存不足，创建失败记录
                order_item = self.order_repo.create_order_item(
                    order, product, quantity, product.price, 'failed',
                    f'库存不足，当前库存：{product.stock_quantity}，需要：{quantity}'
                )

                return {
                    'success': False,
                    'product_id': product_id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'error_message': f'库存不足，当前库存：{product.stock_quantity}，需要：{quantity}',
                    'order_item_id': order_item.id
                }

            # 扣减库存
            stock_updated = self.product_repo.update_stock(
                product, -quantity, f'订单扣减 - {order.order_no}'
            )

            if not stock_updated:
                raise Exception("库存更新失败")

            # 创建成功的订单项
            total_price = product.price * quantity
            order_item = self.order_repo.create_order_item(
                order, product, quantity, product.price, 'success'
            )

            return {
                'success': True,
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': str(product.price),
                'total_price': str(total_price),
                'order_item_id': order_item.id
            }

        except Exception as e:
            logger.error(f"Process single item error: {e}")
            return {
                'success': False,
                'product_id': product_id,
                'quantity': quantity,
                'error_message': str(e)
            }
