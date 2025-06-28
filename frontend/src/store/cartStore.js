import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useCartStore = defineStore('cart', () => {
  // 购物车商品列表
  const items = ref([])

  // 从localStorage加载购物车数据
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('cart-items')
      if (stored) {
        const parsed = JSON.parse(stored)
        items.value = Array.isArray(parsed) ? parsed : []
      }
    } catch (error) {
      console.error('加载购物车数据失败:', error)
      items.value = []
    }
  }

  // 保存到localStorage
  const saveToStorage = () => {
    try {
      localStorage.setItem('cart-items', JSON.stringify(items.value))
    } catch (error) {
      console.error('保存购物车数据失败:', error)
    }
  }

  // 监听items变化，自动保存到localStorage
  watch(items, saveToStorage, { deep: true })

  // 添加商品到购物车
  function addToCart(product, quantity = 1) {
    const idx = items.value.findIndex(item => item.id === product.id)
    if (idx !== -1) {
      // 已存在则增加数量
      const item = items.value[idx]
      if (item.quantity + quantity <= product.stock_quantity) {
        item.quantity += quantity
      } else {
        item.quantity = product.stock_quantity
      }
    } else {
      items.value.push({
        id: product.id,
        name: product.name,
        price: product.price,
        stock_quantity: product.stock_quantity,
        quantity: quantity
      })
    }
  }

  // 移除商品
  function removeFromCart(productId) {
    items.value = items.value.filter(item => item.id !== productId)
  }

  // 清空购物车
  function clearCart() {
    items.value = []
  }

  // 购物车商品总数
  const totalCount = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))

  // 购物车总金额
  const totalAmount = computed(() => items.value.reduce((sum, item) => sum + item.price * item.quantity, 0))

  // 初始化时加载数据
  loadFromStorage()

  return {
    items,
    addToCart,
    removeFromCart,
    clearCart,
    totalCount,
    totalAmount
  }
})
