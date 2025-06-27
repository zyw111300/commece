import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '../views/ProductList.vue'
import ProductDetail from '../views/ProductDetail.vue'
import OrderList from '../views/OrderList.vue'
import BatchOrder from '../views/BatchOrder.vue'

const routes = [
  {
    path: '/',
    name: 'ProductList',
    component: ProductList
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: ProductDetail,
    props: true
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: OrderList
  },
  {
    path: '/batch-order',
    name: 'BatchOrder',
    component: BatchOrder
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
