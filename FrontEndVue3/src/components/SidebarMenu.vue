<template>
  <div class="sidebar-shell">
    <div class="brand-block">
      <svg class="brand-logo" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect width="48" height="48" rx="8" fill="#4CAF50" />
        <path d="M14 24l6 6 14-18" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
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
import { computed } from 'vue'
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

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const route = useRoute()

const menuTree = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('menus') || '[]')
  } catch (error) {
    return []
  }
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
}

.brand-block {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.12);
  padding: 4px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
}

.brand-subtitle {
  font-size: 12px;
  opacity: 0.7;
}

.sidebar-menu {
  border-right: none;
  padding: 12px 0;
}

.menu-icon {
  width: 1em;
  height: 1em;
  margin-right: 8px;
}
</style>
