import api from '../utils/request'

// 商品相关API
export const productAPI = {
  // 获取商品列表
  getProductList(params = {}) {
    return api.get('/products/', { params })
  },

  // 获取商品详情
  getProductDetail(id) {
    return api.get(`/products/${id}/`)
  },

  // 搜索商品
  searchProducts(params = {}) {
    return api.get('/products/search/', { params })
  },

  // 创建商品
  createProduct(data) {
    return api.post('/products/', data)
  },

  // 更新商品
  updateProduct(id, data) {
    return api.put(`/products/${id}/`, data)
  },

  // 删除商品
  deleteProduct(id) {
    return api.delete(`/products/${id}/`)
  },

  // 获取商品库存
  getProductStock(id) {
    return api.get(`/products/${id}/stock/`)
  },

  // 更新商品库存
  updateProductStock(id, data) {
    return api.post(`/products/${id}/update_stock/`, data)
  },

  // 获取商品库存日志
  getProductStockLogs(id, params = {}) {
    return api.get(`/products/${id}/stock_logs/`, { params })
  }
}

// 订单相关API
export const orderAPI = {
  // 获取订单列表
  getOrderList(params = {}) {
    return api.get('/orders/', { params })
  },

  // 获取订单详情
  getOrderDetail(id) {
    return api.get(`/orders/${id}/`)
  },

  // 创建订单
  createOrder(data) {
    return api.post('/orders/', data)
  },

  // 批量创建订单
  batchCreateOrders(data) {
    return api.post('/orders/batch_create/', data)
  },

  // 更新订单状态
  updateOrderStatus(id, data) {
    return api.post(`/orders/${id}/update_status/`, data)
  },

  // 取消订单
  cancelOrder(id) {
    return api.post(`/orders/${id}/cancel/`)
  },

  // 获取订单统计
  getOrderStats(params = {}) {
    return api.get('/orders/stats/', { params })
  }
}

// 库存日志相关API
export const stockLogAPI = {
  // 获取库存日志列表
  getStockLogList(params = {}) {
    return api.get('/stock-logs/', { params })
  },

  // 获取库存日志详情
  getStockLogDetail(id) {
    return api.get(`/stock-logs/${id}/`)
  }
}
