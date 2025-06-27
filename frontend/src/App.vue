<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航 -->
      <el-header>
        <div class="header-content">
          <h1 class="logo">电商平台</h1>
          <el-menu
            :default-active="$route.path"
            class="el-menu-demo"
            mode="horizontal"
            router
            style="flex:1;min-width:0;"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/orders">订单管理</el-menu-item>
            <el-menu-item index="/batch-order">
              批量下单
              <el-badge :value="cartCount" class="cart-badge" v-if="cartCount > 0" style="margin-left:6px;">
                <i class="el-icon-shopping-cart-2" />
              </el-badge>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { createPinia } from 'pinia'
import { useCartStore } from './store/cartStore'
import { computed } from 'vue'

export default {
  name: 'App',
  setup() {
    // pinia store
    const cartStore = useCartStore()
    // 购物车商品总数
    const cartCount = computed(() => cartStore.totalCount)
    return {
      cartCount
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.el-header {
  background-color: #545c64;
  color: #fff;
  padding: 0;
}

.cart-badge {
  vertical-align: middle;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.logo {
  margin: 0 30px 0 0;
  font-size: 20px;
  font-weight: bold;
}

.el-menu.el-menu-demo {
  background-color: transparent;
  border: none;
}

.el-menu--horizontal > .el-menu-item {
  color: #fff;
  border-bottom: 2px solid transparent;
}

.el-menu--horizontal > .el-menu-item:hover,
.el-menu--horizontal > .el-menu-item.is-active {
  background-color: #434a50;
  border-bottom-color: #409eff;
}

.el-main {
  padding: 20px;
  min-height: calc(100vh - 60px);
}
</style>
