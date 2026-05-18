<template>
  <el-container class="layout-shell">
    <el-aside class="layout-aside" :width="asideWidth">
      <SidebarMenu :collapsed="collapsed" />
    </el-aside>

    <el-container>
      <el-header class="layout-header amod-surface">
        <AppHeader :collapsed="collapsed" @toggle-collapse="toggleCollapse" @logout="logout" />
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import SidebarMenu from '@/components/SidebarMenu.vue'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()
const collapsed = ref(false)
const asideWidth = computed(() => (collapsed.value ? '72px' : '240px'))

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

function logout() {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  localStorage.removeItem('menus')
  router.push('/login')
}
</script>

<style scoped>
.layout-shell {
  min-height: 100vh;
}

.layout-aside {
  transition: width 0.25s ease;
  background: linear-gradient(180deg, #18392b 0%, #214c38 50%, #10261d 100%);
  box-shadow: 2px 0 14px rgba(15, 23, 42, 0.2);
  overflow: hidden;
}

.layout-header {
  height: 64px;
  margin: 14px 16px 0;
  border-radius: 18px;
}

.layout-main {
  padding: 16px;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.18s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
