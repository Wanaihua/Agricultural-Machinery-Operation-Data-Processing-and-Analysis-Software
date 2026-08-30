<template>
  <div class="sidebar-shell">
    <div class="brand-block">
      <img class="brand-logo" :src="brandLogo" alt="农机作业平台图标" />
      <div v-if="!collapsed" class="brand-text">
        <div class="brand-title">农机作业平台</div>
        <div class="brand-subtitle">AMOD Control Center</div>
      </div>
    </div>

    <el-menu
      class="sidebar-menu"
      :collapse="collapsed"
      :default-active="activePath"
      background-color="transparent"
      text-color="#e9f5ef"
      active-text-color="#ffd77b"
      router
    >
      <template v-for="item in menuTree" :key="item.id">
        <el-sub-menu v-if="item.children && item.children.length" :index="String(item.id)">
          <template #title>
            <component :is="resolveIcon(item.icon)" class="menu-icon" />
            <span>{{ item.name }}</span>
          </template>
          <el-menu-item v-for="child in item.children" :key="child.id" :index="normalizePath(child.path)">
            <component :is="resolveIcon(child.icon)" class="menu-icon" />
            <span>{{ child.name }}</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item v-else :index="normalizePath(item.path)">
          <component :is="resolveIcon(item.icon)" class="menu-icon" />
          <span>{{ item.name }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  House,
  User,
  Menu,
  Document,
  Tickets,
  Setting,
  Location,
  UploadFilled,
  Files as FilesIcon,
} from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import { getCurrentUser, isAdminUser } from '@/utils/auth'
import brandLogo from '@/images/AOMD_log.png'

const adminOnlyPaths = ['/user', '/role', '/menu', '/file']

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const route = useRoute()

function readMenus() {
  try {
    return JSON.parse(localStorage.getItem('menus') || '[]')
  } catch (error) {
    return []
  }
}

const menuTree = ref([])

function filterMenusByRole(menus) {
  if (isAdminUser(getCurrentUser())) {
    return menus
  }

  const walk = (items) => {
    return (items || [])
      .map((item) => {
        const normalized = normalizePath(item.path)
        const children = walk(item.children || [])

        if (item.children && item.children.length) {
          if (!children.length) {
            return null
          }
          return { ...item, children }
        }

        if (adminOnlyPaths.includes(normalized)) {
          return null
        }
        return item
      })
      .filter(Boolean)
  }

  return walk(menus)
}

function syncMenus() {
  menuTree.value = filterMenusByRole(readMenus())
}

function handleMenuUpdate() {
  syncMenus()
}

onMounted(() => {
  syncMenus()
  window.addEventListener('menus-updated', handleMenuUpdate)
  window.addEventListener('storage', handleMenuUpdate)
})

onBeforeUnmount(() => {
  window.removeEventListener('menus-updated', handleMenuUpdate)
  window.removeEventListener('storage', handleMenuUpdate)
})

const activePath = computed(() => route.path)

function normalizePath(path) {
  if (!path) {
    return '/home'
  }
  // map legacy /track menu to the list route
  if (path === '/track') return '/track/list'
  return path.startsWith('/') ? path : `/${path}`
}

function resolveIcon(icon) {
  const iconMap = {
    'el-icon-house': House,
    'el-icon-user': User,
    'el-icon-menu': Menu,
    'el-icon-document': Document,
    'el-icon-s-custom': User,
    'el-icon-s-grid': FilesIcon,
    'el-icon-s-shop': FilesIcon,
    'el-icon-position': Location,
    'el-icon-bank-card': FilesIcon,
    'el-icon-ticket': Tickets,
    'el-icon-setting': Setting,
    'el-icon-upload': UploadFilled,
    'el-icon-data-analysis': FilesIcon,
    'el-icon-files': FilesIcon,
  }
  return iconMap[icon] || Menu
}
</script>

<style scoped>
.sidebar-shell {
  height: 100%;
  color: #fff;
  background: linear-gradient(180deg, #113024 0%, #173c2f 36%, #1d4a46 100%);
}

.brand-block {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(90deg, rgba(8, 26, 18, 0.55), rgba(33, 84, 73, 0.3));
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.28);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
  color: #f5fff8;
}

.brand-subtitle {
  font-size: 12px;
  color: rgba(228, 241, 232, 0.72);
}

.sidebar-menu {
  border-right: none;
  padding: 12px 0;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: #edf7f1;
  --el-menu-active-color: #ffd77b;
}

.menu-icon {
  width: 1em;
  height: 1em;
  margin-right: 8px;
}

.sidebar-shell :deep(.el-menu-item),
.sidebar-shell :deep(.el-sub-menu__title) {
  border-radius: 10px;
  margin: 4px 8px;
}

.sidebar-shell :deep(.el-menu-item:hover),
.sidebar-shell :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-shell :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(76, 175, 80, 0.24), rgba(33, 150, 243, 0.12));
  color: #fff2c6;
}
</style>
