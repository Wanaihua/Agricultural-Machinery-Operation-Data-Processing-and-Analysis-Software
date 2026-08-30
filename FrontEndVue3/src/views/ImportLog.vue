<template>
  <div class="amod-page crud-page data-import-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">上传日志</div>
      </div>
      <div class="page-actions">
        <!-- 返回上传 按钮已移除：上传日志页为只读日志视图 -->
      </div>
    </div>

    <el-card class="amod-card table-card" shadow="never">
      <el-table :data="filteredLogs" border stripe class="amod-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="文件名" min-width="220">
          <template #default="{ row }">
            {{ row.file_name }}.xlsx
          </template>
        </el-table-column>
        <el-table-column prop="admin_name" label="上传人" width="120" />
        <el-table-column prop="import_count" label="处理数量" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="tagType(scope.row.import_status)">{{ scope.row.import_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_info" label="错误信息" min-width="240" show-overflow-tooltip />
        <el-table-column prop="import_time" label="处理时间" min-width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { formatDateTime, unwrapListResponse } from '@/utils/response'

const router = useRouter()
const logs = ref([])

const filteredLogs = computed(() => {
  return logs.value.map((item) => ({
    ...item,
    import_time: formatDateTime(item.import_time),
  }))
})

async function loadLogs() {
  const res = await request.get('/api/import_log/')
  logs.value = unwrapListResponse(res).slice().reverse()
}

function tagType(status) {
  if (!status) return 'info'
  const value = String(status).toLowerCase()
  if (value.includes('success') || value.includes('完成')) return 'success'
  if (value.includes('fail') || value.includes('error')) return 'danger'
  return 'warning'
}

function goImportPage() {
  router.push('/data/import')
}

onMounted(loadLogs)
</script>

<style scoped>
.data-import-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>