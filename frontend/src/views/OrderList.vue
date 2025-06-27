<template>
  <div class="order-list">
    <div class="page-header">
      <h2>订单管理</h2>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-select v-model="searchForm.status" placeholder="订单状态" style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="pending" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        
        <el-button @click="handleSearch" :loading="loading" style="margin-left: 10px">
          搜索
        </el-button>
        <el-button @click="resetSearch" style="margin-left: 10px">重置</el-button>
      </div>
    </div>

    <!-- 订单列表 -->
    <el-table
      :data="orderList"
      v-loading="loading"
      style="width: 100%"
    >
      <el-table-column prop="id" label="订单ID" width="100" />
      <el-table-column prop="order_number" label="订单号" width="200" />
      <el-table-column prop="total_amount" label="总金额" width="120">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ parseFloat(row.total_amount || 0).toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="商品信息" min-width="300">
        <template #default="{ row }">
          <div v-if="row.items && row.items.length > 0">
            <div v-for="item in row.items" :key="item.id" class="order-item">
              <span>{{ item.product_name }}</span>
              <span class="item-quantity">x{{ item.quantity }}</span>
              <span class="item-price">¥{{ parseFloat(item.unit_price || 0).toFixed(2) }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'pending'"
            type="success"
            size="small"
            @click="updateStatus(row.id, 'confirmed')"
          >
            确认
          </el-button>
          <el-button
            v-if="row.status === 'confirmed'"
            type="primary"
            size="small"
            @click="updateStatus(row.id, 'shipped')"
          >
            发货
          </el-button>
          <el-button
            v-if="row.status === 'shipped'"
            type="info"
            size="small"
            @click="updateStatus(row.id, 'completed')"
          >
            完成
          </el-button>
          <el-button
            v-if="['pending', 'confirmed'].includes(row.status)"
            type="danger"
            size="small"
            @click="cancelOrder(row.id)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { orderAPI } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'OrderList',
  setup() {
    const loading = ref(false)
    const orderList = ref([])
    
    const searchForm = reactive({
      status: ''
    })
    
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })

    // 获取订单列表
    const fetchOrderList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          size: pagination.size,
          ...searchForm
        }
        
        const response = await orderAPI.getOrderList(params)
        orderList.value = response.data.results || []
        pagination.total = response.data.count || 0
      } catch (error) {
        console.error('获取订单列表失败:', error)
        ElMessage.error('获取订单列表失败')
      } finally {
        loading.value = false
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      fetchOrderList()
    }

    // 重置搜索
    const resetSearch = () => {
      searchForm.status = ''
      pagination.page = 1
      fetchOrderList()
    }

    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.size = size
      pagination.page = 1
      fetchOrderList()
    }

    // 当前页改变
    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchOrderList()
    }

    // 更新订单状态
    const updateStatus = async (orderId, status) => {
      try {
        await orderAPI.updateOrderStatus(orderId, { status })
        ElMessage.success('订单状态更新成功')
        fetchOrderList()
      } catch (error) {
        console.error('更新订单状态失败:', error)
        ElMessage.error('更新订单状态失败')
      }
    }

    // 取消订单
    const cancelOrder = async (orderId) => {
      try {
        await ElMessageBox.confirm('确定要取消这个订单吗？', '确认', {
          type: 'warning'
        })

        await orderAPI.cancelOrder(orderId)
        ElMessage.success('订单已取消')
        fetchOrderList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('取消订单失败:', error)
          ElMessage.error('取消订单失败')
        }
      }
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const statusMap = {
        pending: 'warning',
        confirmed: 'primary',
        shipped: 'info',
        completed: 'success',
        cancelled: 'danger'
      }
      return statusMap[status] || 'info'
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        pending: '待处理',
        confirmed: '已确认',
        shipped: '已发货',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || status
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      fetchOrderList()
    })

    return {
      loading,
      orderList,
      searchForm,
      pagination,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      updateStatus,
      cancelOrder,
      getStatusType,
      getStatusText,
      formatDate
    }
  }
}
</script>

<style scoped>
.order-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 20px 0;
  color: #303133;
}

.search-area {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.order-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.item-quantity {
  color: #909399;
  font-size: 12px;
}

.item-price {
  color: #f56c6c;
  font-weight: bold;
  margin-left: auto;
}
</style>
