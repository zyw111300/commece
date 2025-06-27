<template>
  <div class="batch-order">
    <div class="page-header">
      <h2>批量下单</h2>
    </div>

    <el-card>
      <div class="order-form">
        <!-- 商品选择区域 -->
        <div class="product-selection">
          <h3>选择商品</h3>
          <div class="search-product">
            <el-input
              v-model="productSearch"
              placeholder="搜索商品名称"
              style="width: 300px"
              @input="searchProducts"
            />
            <el-button @click="handleProductSearch" style="margin-left: 10px">搜索</el-button>
            <el-button @click="resetProductSearch" style="margin-left: 10px">重置</el-button>
          </div>
          
          <el-table
            :data="filteredProducts"
            v-loading="productLoading"
            style="width: 100%; margin-top: 15px"
            max-height="300"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="商品名称" min-width="200" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                ¥{{ parseFloat(row.price || 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="stock_quantity" label="库存" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="addToCart(row)"
                  :disabled="row.stock_quantity <= 0"
                >
                  添加
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 商品列表分页 -->
          <div class="product-pagination">
            <el-pagination
              v-model:current-page="productPagination.page"
              v-model:page-size="productPagination.size"
              :page-sizes="[10, 20, 50]"
              :total="productPagination.total"
              layout="total, sizes, prev, pager, next"
              @size-change="handleProductSizeChange"
              @current-change="handleProductCurrentChange"
              small
            />
          </div>
        </div>

        <!-- 购物车区域 -->
        <div class="cart-section">
          <h3>购物车</h3>
          <el-table
            :data="cartItems"
            style="width: 100%"
          >
            <el-table-column prop="name" label="商品名称" min-width="200" />
            <el-table-column prop="price" label="单价" width="100">
              <template #default="{ row }">
                ¥{{ parseFloat(row.price || 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="数量" width="150">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.quantity"
                  :min="1"
                  :max="row.stock_quantity"
                  size="small"
                  @change="updateCartItem(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="小计" width="100">
              <template #default="{ row }">
                <span style="color: #f56c6c; font-weight: bold;">
                  ¥{{ (parseFloat(row.price || 0) * parseInt(row.quantity || 0, 10)).toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row, $index }">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeFromCart($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 合计 -->
          <div class="cart-total">
            <span class="total-label">总计：</span>
            <span class="total-amount">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
        </div>

        <!-- 订单信息 -->
        <div class="order-info">
          <h3>订单信息</h3>
          <el-form :model="orderForm" label-width="100px">
            <el-form-item label="备注">
              <el-input
                v-model="orderForm.notes"
                type="textarea"
                :rows="3"
                placeholder="请输入订单备注"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 提交按钮 -->
        <div class="submit-section">
          <el-button
            type="primary"
            size="large"
            @click="submitOrder"
            :loading="submitting"
            :disabled="cartItems.length === 0"
          >
            提交订单
          </el-button>
          <el-button size="large" @click="clearCart">
            清空购物车
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { productAPI, orderAPI } from '../api'
import { ElMessage } from 'element-plus'
import { useCartStore } from '../store/cartStore'

export default {
  name: 'BatchOrder',
  setup() {
    const cartStore = useCartStore()
    const productLoading = ref(false)
    const submitting = ref(false)
    const productSearch = ref('')
    const allProducts = ref([])
    const cartItems = ref([])
    
    // 商品分页
    const productPagination = reactive({
      page: 1,
      size: 10,
      total: 0
    })
    
    const orderForm = reactive({
      notes: ''
    })

    // 过滤后的商品列表
    const filteredProducts = computed(() => {
      return allProducts.value
    })

    // 总金额
    const totalAmount = computed(() => {
      return cartItems.value.reduce((total, item) => {
        return total + (parseFloat(item.price || 0) * parseInt(item.quantity || 0, 10))
      }, 0)
    })

    // 获取商品列表
    const fetchProducts = async () => {
      productLoading.value = true
      try {
        let response
        
        // 如果有搜索关键词，使用搜索API
        if (productSearch.value && productSearch.value.trim()) {
          const searchParams = {
            keyword: productSearch.value.trim(),
            page: productPagination.page,
            size: productPagination.size
          }
          response = await productAPI.searchProducts(searchParams)
        } else {
          // 否则使用普通列表API
          const params = {
            page: productPagination.page,
            size: productPagination.size
          }
          response = await productAPI.getProductList(params)
        }
        
        allProducts.value = response.data.results || []
        productPagination.total = response.data.count || 0
      } catch (error) {
        console.error('获取商品列表失败:', error)
        ElMessage.error('获取商品列表失败')
      } finally {
        productLoading.value = false
      }
    }

    // 搜索商品
    const searchProducts = () => {
      // 实时搜索已移除，改为点击搜索按钮
    }

    // 处理商品搜索
    const handleProductSearch = () => {
      productPagination.page = 1
      fetchProducts()
    }

    // 重置商品搜索
    const resetProductSearch = () => {
      productSearch.value = ''
      productPagination.page = 1
      fetchProducts()
    }

    // 商品分页大小改变
    const handleProductSizeChange = (size) => {
      productPagination.size = size
      productPagination.page = 1
      fetchProducts()
    }

    // 商品当前页改变
    const handleProductCurrentChange = (page) => {
      productPagination.page = page
      fetchProducts()
    }

    // 添加到购物车
    const addToCart = (product) => {
      const existingIndex = cartItems.value.findIndex(item => item.id === product.id)
      
      if (existingIndex !== -1) {
        // 如果商品已存在，增加数量
        const existingItem = cartItems.value[existingIndex]
        if (existingItem.quantity < product.stock_quantity) {
          existingItem.quantity += 1
          ElMessage.success('商品数量已增加')
        } else {
          ElMessage.warning('库存不足')
        }
      } else {
        // 添加新商品
        cartItems.value.push({
          id: product.id,
          name: product.name,
          price: product.price,
          stock_quantity: product.stock_quantity,
          quantity: 1
        })
        ElMessage.success('商品已添加到购物车')
      }
      
      // 同时添加到全局购物车store
      cartStore.addToCart(product, 1)
    }

    // 更新购物车商品
    const updateCartItem = (item) => {
      if (item.quantity > item.stock_quantity) {
        item.quantity = item.stock_quantity
        ElMessage.warning('数量不能超过库存')
      }
    }

    // 从购物车删除
    const removeFromCart = (index) => {
      cartItems.value.splice(index, 1)
      ElMessage.success('商品已从购物车删除')
    }

    // 清空购物车
    const clearCart = () => {
      cartItems.value = []
      cartStore.clearCart() // 同时清空全局购物车store
      ElMessage.success('购物车已清空')
    }

    // 提交订单
    const submitOrder = async () => {
      if (cartItems.value.length === 0) {
        ElMessage.warning('购物车为空')
        return
      }

      submitting.value = true
      try {
        const orderData = {
          user_id: 1, // 固定用户ID
          order_items: cartItems.value.map(item => ({
            product_id: item.id,
            quantity: parseInt(item.quantity, 10),
            price: Number(item.price)
          })),
          notes: orderForm.notes
        }
        // 打印orderData调试
        console.log('提交订单数据:', orderData)
        const resp = await orderAPI.batchCreateOrders(orderData)
        ElMessage.success('订单提交成功')
        // 清空购物车和表单
        cartItems.value = []
        cartStore.clearCart() // 同时清空全局购物车store
        orderForm.notes = ''
        // 重新获取商品列表（更新库存）
        await fetchProducts()
      } catch (error) {
        // 打印后端返回的详细错误
        if (error.response && error.response.data) {
          console.error('后端返回:', error.response.data)
          ElMessage.error('提交订单失败: ' + (error.response.data.detail || JSON.stringify(error.response.data)))
        } else {
          console.error('提交订单失败:', error)
          ElMessage.error('提交订单失败')
        }
      } finally {
        submitting.value = false
      }
    }

    onMounted(() => {
      fetchProducts()
      // 从全局购物车store初始化本地购物车
      if (cartStore.items.length > 0) {
        cartItems.value = [...cartStore.items]
        ElMessage.info(`已从购物车加载 ${cartStore.items.length} 个商品`)
      }
    })

    return {
      productLoading,
      submitting,
      productSearch,
      allProducts,
      filteredProducts,
      cartItems,
      orderForm,
      totalAmount,
      productPagination,
      searchProducts,
      handleProductSearch,
      resetProductSearch,
      handleProductSizeChange,
      handleProductCurrentChange,
      addToCart,
      updateCartItem,
      removeFromCart,
      clearCart,
      submitOrder
    }
  }
}
</script>

<style scoped>
.batch-order {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.order-form {
  max-width: 1200px;
}

.product-selection,
.cart-section,
.order-info {
  margin-bottom: 30px;
}

.product-selection h3,
.cart-section h3,
.order-info h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 18px;
}

.search-product {
  margin-bottom: 15px;
}

.product-pagination {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.cart-total {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 15px;
  padding: 15px 0;
  border-top: 1px solid #ebeef5;
}

.total-label {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-right: 10px;
}

.total-amount {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}

.submit-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
