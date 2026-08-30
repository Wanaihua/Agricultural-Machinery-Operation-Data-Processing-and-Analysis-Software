<template>
  <div class="amod-page home-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">系统概览</div>
      </div>
    </div>

    <el-row :gutter="16" class="metric-grid">
      <el-col v-for="item in metrics" :key="item.label" :xs="12" :sm="12" :md="6">
        <el-card class="metric-card amod-card" shadow="never">
          <div class="metric-label">{{ item.label }}</div>
          <div class="metric-value">{{ item.value }}</div>
          <div class="metric-hint">{{ item.hint }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="panel-grid">
      <el-col :xs="24" :lg="14">
        <el-card class="amod-card table-card" shadow="never">
          <template #header>
            <div class="panel-title">最近轨迹</div>
          </template>
          <el-table :data="recentTracks" border stripe class="amod-table">
            <el-table-column prop="trackid" label="轨迹ID" width="100" />
            <el-table-column prop="starttime" label="起始时间" :formatter="formatStart" />
            <el-table-column prop="endtime" label="结束时间" :formatter="formatEnd" />
            <el-table-column prop="width" label="幅宽" width="100" :formatter="formatWidth" />
            <el-table-column prop="totalpoints" label="总点数" width="100" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="amod-card guide-card" shadow="never">
          <template #header>
            <div class="panel-title">使用指引</div>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="1" placement="top">
              登录后从左侧菜单进入轨迹列表或地图页。
            </el-timeline-item>
            <el-timeline-item timestamp="2" placement="top">
              使用数据导入页上传 Excel，后端记录导入日志。
            </el-timeline-item>
            <el-timeline-item timestamp="3" placement="top">
              在角色管理里分配菜单权限，侧边栏会按菜单动态渲染。
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import request from '@/utils/request'
import { formatDateTime, formatNumberFixed, unwrapListResponse } from '@/utils/response'

const counts = ref({ tracks: 0, users: 0, roles: 0, files: 0 })
const recentTracks = ref([])

const metrics = computed(() => [
  { label: '轨迹总数', value: counts.value.tracks },
  { label: '用户总数', value: counts.value.users },
  { label: '角色总数', value: counts.value.roles },
  { label: '文件总数', value: counts.value.files },
])

async function loadDashboard() {
  const [tracksRes, usersRes, rolesRes, filesRes] = await Promise.all([
    request.get('/api/track/'),
    request.get('/api/user/'),
    request.get('/api/role/'),
    request.get('/api/file/'),
  ])

  const tracks = unwrapListResponse(tracksRes)
  counts.value = {
    tracks: tracks.length,
    users: unwrapListResponse(usersRes).length,
    roles: unwrapListResponse(rolesRes).length,
    files: unwrapListResponse(filesRes).length,
  }
  recentTracks.value = tracks.slice(0, 8)
}

function formatStart(row, column, cellValue) {
  return formatDateTime(cellValue)
}

function formatEnd(row, column, cellValue) {
  return formatDateTime(cellValue)
}

function formatWidth(row, column, cellValue) {
  return formatNumberFixed(cellValue, 4)
}

onMounted(loadDashboard)
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
}

.metric-grid,
.panel-grid {
  margin: 0 !important;
}

.metric-card {
  min-height: 150px;
}

.metric-label {
  color: var(--amod-text-soft);
  font-size: 14px;
}

.metric-value {
  margin-top: 12px;
  font-size: 34px;
  font-weight: 800;
  color: var(--amod-primary);
}

.metric-hint {
  margin-top: 8px;
  color: var(--amod-text-soft);
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
}

.guide-card {
  min-height: 100%;
}
</style>
