<template>
  <div class="amod-page crud-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">文件管理</div>
        <div class="amod-subtitle">上传的文件与资源管理</div>
      </div>
    </div>

    <el-card class="amod-card" shadow="never">
      <el-table :data="files" border stripe row-key="id">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" min-width="220" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="size" label="大小" width="120">
            <template #default="{ row }">{{ formatSize(row.size) }}</template>
          </el-table-column>
          <el-table-column prop="url" label="URL" min-width="180">
            <template #default="{ row }">
              <a :href="row.url" target="_blank">查看</a>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="download(row)">下载</el-button>
              <el-button type="danger" link @click="remove(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import request from '@/utils/request'
import { unwrapListResponse } from '@/utils/response'

const files = ref([])

async function load() {
  const res = await request.get('/api/file/')
  files.value = unwrapListResponse(res)
}

function formatSize(v) {
  if (!v && v !== 0) return '-'
  const n = Number(v)
  if (isNaN(n)) return String(v)
  if (n < 1024) return n + ' B'
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB'
  return (n / (1024 * 1024)).toFixed(2) + ' MB'
}

function download(row) {
  // open the file URL in a new tab; backend serves static files via absolute URL
  if (row.url) window.open(row.url, '_blank')
  else ElMessage.warning('没有可下载的文件地址')
}

async function remove(id) {
  try {
    await ElMessageBox.confirm('确定删除该文件吗？', '提示', { type: 'warning' })
    await request.delete(`/api/file/${id}/`)
    ElMessage.success('删除成功')
    await load()
  } catch (err) {
    // cancel 或 出错
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.crud-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
