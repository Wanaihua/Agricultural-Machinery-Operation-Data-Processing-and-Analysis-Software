<template>
  <div class="amod-page crud-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">文件管理</div>
      </div>
    </div>

    <el-card class="amod-card table-card" shadow="never">
      <div class="batch-actions" v-if="selectedIds.length">
        <span>已选 {{ selectedIds.length }} 项</span>
        <el-button type="danger" size="small" @click="batchRemove">批量删除</el-button>
        <el-button size="small" @click="toggleSelect">反选</el-button>
        <el-button size="small" @click="clearSelection">取消选择</el-button>
      </div>
      <el-table
        :data="files"
        border stripe row-key="id"
        class="amod-table"
        @selection-change="onSelectionChange"
        ref="tableRef"
      >
          <el-table-column type="selection" width="50" />
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
const selectedIds = ref([])
const tableRef = ref(null)

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
  if (row.url) window.open(row.url, '_blank')
  else ElMessage.warning('没有可下载的文件地址')
}

function onSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.id)
}

function toggleSelect() {
  const table = tableRef.value
  if (!table) return
  files.value.forEach(row => {
    const isSelected = selectedIds.value.includes(row.id)
    table.toggleRowSelection(row, !isSelected)
  })
}

function clearSelection() {
  tableRef.value?.clearSelection()
}

async function remove(id) {
  try {
    await ElMessageBox.confirm('确定删除该文件吗？', '提示', { type: 'warning' })
    await request.delete(`/api/file/${id}/`)
    ElMessage.success('删除成功')
    await load()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

async function batchRemove() {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个文件吗？`, '提示', { type: 'warning' })
    for (const id of selectedIds.value) {
      await request.delete(`/api/file/${id}/`)
    }
    ElMessage.success('批量删除成功')
    clearSelection()
    await load()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.batch-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--amod-text-soft);
}
</style>
