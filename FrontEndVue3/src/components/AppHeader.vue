<template>
  <div class="header-shell">
    <div class="header-left">
      <el-button text class="collapse-btn" @click="$emit('toggle-collapse')">
        <el-icon :size="18">
          <Fold v-if="!collapsed" />
          <Expand v-else />
        </el-icon>
      </el-button>

      <div class="breadcrumb-wrap">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>

    <div class="header-right">
      <el-tag type="success" effect="plain" class="role-tag">{{ roleName }}</el-tag>

      <el-dropdown trigger="click">
        <div class="user-box">
          <el-avatar :size="34" :src="avatarUrl">{{ nickname.slice(0, 1) }}</el-avatar>
          <div class="user-meta">
            <div class="user-name">{{ nickname }}</div>
            <div class="user-sub">{{ username }}</div>
          </div>
          <el-icon class="arrow-icon"><ArrowDown /></el-icon>
        </div>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="$emit('logout')">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowDown, Expand, Fold } from '@element-plus/icons-vue'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-collapse', 'logout'])

const route = useRoute()
const user = JSON.parse(localStorage.getItem('user') || '{}')

const username = computed(() => user.username || '未登录用户')
const nickname = computed(() => user.nickname || user.username || '未命名')
const avatarUrl = computed(() => user.avatar_url || user.avatarUrl || '')
const roleName = computed(() => user.role?.name || user.roleName || user.role || '访客')
const currentTitle = computed(() => route.meta.title || route.name || '工作台')
</script>

<style scoped>
.header-shell {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 0 4px;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.collapse-btn {
  color: var(--amod-primary);
}

.breadcrumb-wrap {
  padding-left: 4px;
}

.role-tag {
  border-radius: 999px;
}

.user-box {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-weight: 700;
}

.user-sub {
  font-size: 12px;
  color: var(--amod-text-soft);
}

.arrow-icon {
  color: var(--amod-text-soft);
}
</style>
