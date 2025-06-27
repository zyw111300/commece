<template>
  <div class="product-list">
    <div class="page-header">
      <h2>商品列表</h2>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-input
          v-model="searchForm.keyword"
          placeholder="请输入商品名称或关键词"
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch" :loading="loading">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
        
        <el-select v-model="searchForm.status" placeholder="商品状态" style="width: 120px; margin-left: 10px">
          <el-option label="全部" value="" />
          <el-option label="上架" value="active" />
          <el-option label="下架" value="inactive" />
        </el-select>
        
        <el-button @click="resetSearch" style="margin-left: 10px">重置</el-button>
      </div>
    </div>

    <!-- 商品列表 -->
    <el-table
      :data="productList"
      v-loading="loading"
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="商品名称" min-width="200" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: bold;">¥{{ row.price }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="stock_quantity" label="库存" width="100">
        <template #default="{ row }">
          <el-tag :type="row.stock_quantity > 10 ? 'success' : 'warning'">
            {{ row.stock_quantity }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="加入购物车" width="150">
        <template #default="{ row }">
          <el-button
            type="success"
            size="small"
            @click.stop="addToCart(row)"
            :disabled="row.stock_quantity <= 0"
          >
            <el-icon><ShoppingCart /></el-icon>
            加入购物车
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click.stop="viewDetail(row.id)"
          >
            查看详情
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
import { useRouter } from 'vue-router'
import { productAPI } from '../api'
import { ElMessage } from 'element-plus'
import { Search, ShoppingCart } from '@element-plus/icons-vue'
import { useCartStore } from '../store/cartStore'

export default {
  name: 'ProductList',
  components: {
    Search,
    ShoppingCart
  },
  setup() {
    const router = useRouter()
    const cartStore = useCartStore()
    const loading = ref(false)
    const productList = ref([])
    
    const searchForm = reactive({
      keyword: '',
      status: ''
    })
    
    const pagination = reactive({
      page: 1,
      size: 20,
      total: 0
    })

    // 获取商品列表
    const fetchProductList = async () => {
      loading.value = true
      try {
        let response
        
        // 如果有搜索关键词，使用搜索API
        if (searchForm.keyword && searchForm.keyword.trim()) {
          const searchParams = {
            keyword: searchForm.keyword.trim(),
            page: pagination.page,
            size: pagination.size
          }
          response = await productAPI.searchProducts(searchParams)
        } else {
          // 否则使用普通列表API
          const params = {
            page: pagination.page,
            size: pagination.size,
            status: searchForm.status
          }
          response = await productAPI.getProductList(params)
        }
        
        productList.value = response.data.results || []
        pagination.total = response.data.count || 0
      } catch (error) {
        console.error('获取商品列表失败:', error)
        ElMessage.error('获取商品列表失败')
      } finally {
        loading.value = false
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      fetchProductList()
    }

    // 重置搜索
    const resetSearch = () => {
      searchForm.keyword = ''
      searchForm.status = ''
      pagination.page = 1
      fetchProductList()
    }

    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.size = size
      pagination.page = 1
      fetchProductList()
    }

    // 当前页改变
    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchProductList()
    }

    // 点击行
    const handleRowClick = (row) => {
      viewDetail(row.id)
    }

    // 查看详情
    const viewDetail = (id) => {
      router.push(`/product/${id}`)
    }

    // 加入购物车
    const addToCart = (product) => {
      cartStore.addToCart(product, 1)
      ElMessage.success(`${product.name} 已加入购物车`)
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      fetchProductList()
    })

    return {
      loading,
      productList,
      searchForm,
      pagination,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleRowClick,
      viewDetail,
      addToCart,
      formatDate
    }
  }
}
</script>

<style scoped>
.product-list {
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

.el-table {
  cursor: pointer;
}

.el-table .el-table__row:hover {
  background-color: #f5f7fa;
}
</style>
