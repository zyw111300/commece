<template>
  <div class="product-detail">
    <div class="page-header">
      <el-button @click="goBack" type="primary" plain>
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
    </div>

    <el-card v-loading="loading">
      <template v-if="product">
        <div class="product-info">
          <div class="product-basic">
            <h1>{{ product.name }}</h1>
            <div class="product-meta">
              <div class="price">
                <span class="label">价格：</span>
                <span class="value">¥{{ product.price }}</span>
              </div>
              <div class="stock">
                <span class="label">库存：</span>
                <el-tag :type="product.stock_quantity > 10 ? 'success' : 'warning'">
                  {{ product.stock_quantity }} 件
                </el-tag>
              </div>
              <div class="status">
                <span class="label">状态：</span>
                <el-tag :type="product.status === 'active' ? 'success' : 'info'">
                  {{ product.status === 'active' ? '上架' : '下架' }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="product-description">
            <h3>商品描述</h3>
            <p>{{ product.description || '暂无描述' }}</p>
          </div>

          <div class="product-details">
            <h3>商品详情</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="商品ID">{{ product.id }}</el-descriptions-item>
              <el-descriptions-item label="SKU">{{ product.sku || '暂无' }}</el-descriptions-item>
              <el-descriptions-item label="关键词">{{ product.keywords || '暂无' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(product.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ formatDate(product.updated_at) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 用户操作：加入购物车和去购买 -->
          <div class="user-operations">
            <h3>购买操作</h3>
            <div class="user-form">
              <el-input-number
                v-model="buyQuantity"
                :min="1"
                :max="product.stock_quantity"
                style="width: 150px"
                placeholder="购买数量"
              />
              <el-button
                type="primary"
                @click="addToCart"
                style="margin-left: 10px"
                :disabled="product.stock_quantity <= 0"
              >
                <el-icon><ShoppingCart /></el-icon>
                加入购物车
              </el-button>
              <el-button
                type="success"
                @click="buyNow"
                style="margin-left: 10px"
                :disabled="product.stock_quantity <= 0"
              >
                立即购买
              </el-button>
            </div>
          </div>

          <!-- 库存日志 -->
          <div class="stock-logs">
            <h3>库存日志</h3>
            <el-button @click="fetchStockLogs" :loading="stockLogsLoading" style="margin-bottom: 15px">
              刷新日志
            </el-button>
            <el-table
              :data="stockLogs"
              v-loading="stockLogsLoading"
              style="width: 100%"
              max-height="400"
              empty-text="暂无库存日志"
            >
              <el-table-column prop="id" label="日志ID" width="80" />
              <el-table-column prop="change_type" label="变更类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.change_type === 'increase' ? 'success' : 'danger'">
                    {{ row.change_type === 'increase' ? '增加' : '减少' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="change_quantity" label="变更数量" width="100">
                <template #default="{ row }">
                  <span :style="{ color: row.change_type === 'increase' ? '#67c23a' : '#f56c6c' }">
                    {{ row.change_type === 'increase' ? '+' : '-' }}{{ Math.abs(row.change_quantity) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="quantity_after" label="变更后库存" width="120">
                <template #default="{ row }">
                  {{ row.quantity_after }}
                </template>
              </el-table-column>
              <el-table-column prop="reason" label="变更原因" min-width="150">
                <template #default="{ row }">
                  {{ row.reason ? row.reason.replace(/\s*-\s*ORD[0-9A-Z]+$/, '') : '' }}
                </template>
              </el-table-column>
              <el-table-column prop="order_id" label="关联订单" min-width="180">
                <template #default="{ row }">
                  <span style="word-break: break-all;">{{
                    row.order_id
                      ? row.order_id
                      : (row.reason && row.reason.match(/ORD[0-9A-Z]+/) ? row.reason.match(/ORD[0-9A-Z]+/)[0] : '无')
                  }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>

            <!-- 库存日志分页 -->
            <div class="stock-logs-pagination" v-if="stockLogsPagination.total > 0">
              <el-pagination
                v-model:current-page="stockLogsPagination.page"
                v-model:page-size="stockLogsPagination.size"
                :page-sizes="[10, 20, 50]"
                :total="stockLogsPagination.total"
                layout="total, sizes, prev, pager, next"
                @size-change="handleStockLogsPageSizeChange"
                @current-change="handleStockLogsPageChange"
                small
              />
            </div>
          </div>
        </div>
      </template>
    </el-card>
  </div>
</template>


<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { productAPI } from '../api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ShoppingCart } from '@element-plus/icons-vue'
import { useCartStore } from '../store/cartStore'

export default {
  name: 'ProductDetail',
  components: {
    ArrowLeft,
    ShoppingCart
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const cartStore = useCartStore()
    const loading = ref(false)
    const stockLoading = ref(false)
    const stockLogsLoading = ref(false)
    const product = ref(null)
    const buyQuantity = ref(1)
    const stockLogs = ref([])
    
    // 库存日志分页
    const stockLogsPagination = reactive({
      page: 1,
      size: 10,
      total: 0
    })

    // 获取商品详情
    const fetchProductDetail = async () => {
      loading.value = true
      try {
        const response = await productAPI.getProductDetail(route.params.id)
        product.value = response.data
        // 获取商品详情成功后，自动获取库存日志
        await fetchStockLogs()
      } catch (error) {
        console.error('获取商品详情失败:', error)
        ElMessage.error('获取商品详情失败')
      } finally {
        loading.value = false
      }
    }

    // 获取库存日志
    const fetchStockLogs = async () => {
      if (!route.params.id) return
      
      stockLogsLoading.value = true
      try {
        const params = {
          page: stockLogsPagination.page,
          size: stockLogsPagination.size
        }
        const response = await productAPI.getProductStockLogs(route.params.id, params)
        // 兼容后端返回格式，确保为数组
        let logs = []
        if (response.data.results && Array.isArray(response.data.results.data)) {
          logs = response.data.results.data
        } else if (Array.isArray(response.data.data)) {
          logs = response.data.data
        } else {
          logs = []
        }
        stockLogs.value = logs
        stockLogsPagination.total = response.data.count || 0
      } catch (error) {
        console.error('获取库存日志失败:', error)
        ElMessage.error('获取库存日志失败')
      } finally {
        stockLogsLoading.value = false
      }
    }

    // 库存日志分页大小改变
    const handleStockLogsPageSizeChange = (size) => {
      stockLogsPagination.size = size
      stockLogsPagination.page = 1
      fetchStockLogs()
    }

    // 库存日志当前页改变
    const handleStockLogsPageChange = (page) => {
      stockLogsPagination.page = page
      fetchStockLogs()
    }


    // 加入购物车
    const addToCart = () => {
      if (!product.value) return
      if (buyQuantity.value < 1) return
      if (buyQuantity.value > product.value.stock_quantity) {
        ElMessage.warning('数量不能超过库存')
        return
      }
      cartStore.addToCart(product.value, buyQuantity.value)
      ElMessage.success(`已加入购物车：${product.value.name} x${buyQuantity.value}`)
    }

    // 立即购买
    const buyNow = () => {
      if (!product.value) return
      if (buyQuantity.value < 1) return
      if (buyQuantity.value > product.value.stock_quantity) {
        ElMessage.warning('数量不能超过库存')
        return
      }
      // 先添加到购物车
      cartStore.addToCart(product.value, buyQuantity.value)
      ElMessage.success(`已添加到购物车，跳转到下单页面`)
      // 跳转到批量下单页面
      router.push('/batch-order')
    }

    // 返回列表
    const goBack = () => {
      router.push('/')
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      fetchProductDetail()
    })

    return {
      loading,
      stockLoading,
      stockLogsLoading,
      product,
      buyQuantity,
      stockLogs,
      stockLogsPagination,
      addToCart,
      buyNow,
      goBack,
      formatDate,
      fetchStockLogs,
      handleStockLogsPageSizeChange,
      handleStockLogsPageChange
    }
  }
}
</script>

<style scoped>
.product-detail {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.product-info {
  max-width: 1000px;
}

.product-basic {
  margin-bottom: 30px;
}

.product-basic h1 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 28px;
}

.product-meta {
  display: flex;
  gap: 30px;
  align-items: center;
}

.product-meta .label {
  font-weight: bold;
  color: #606266;
}

.product-meta .value {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
}

.product-description,
.product-details,
.user-operations,
.stock-operations {
  margin-bottom: 30px;
}

.product-description h3,
.product-details h3,
.user-operations h3,
.stock-operations h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 18px;
}

.product-description p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.stock-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.user-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.stock-logs {
  margin-bottom: 30px;
}

.stock-logs h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 18px;
}

.stock-logs-pagination {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}
</style>
