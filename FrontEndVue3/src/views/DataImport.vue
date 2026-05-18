<template>
  <div class="amod-page data-import-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">数据导入</div>
        <div class="amod-subtitle">上传文件后可自动导入轨迹数据，并展示导入日志</div>
      </div>
    </div>

    <DatasetUploadPanel @uploaded="loadLogs" @imported="loadLogs" />

    <el-card class="amod-card" shadow="never">
      <template #header>
        <div class="panel-title">导入日志</div>
      </template>

      <el-table :data="filteredLogs" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_name" label="文件名" min-width="220" />
        <el-table-column prop="import_count" label="导入数量" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="tagType(scope.row.import_status)">{{ scope.row.import_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_info" label="错误信息" min-width="240" show-overflow-tooltip />
        <el-table-column prop="import_time" label="导入时间" min-width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import DatasetUploadPanel from '@/components/DatasetUploadPanel.vue'
import request from '@/utils/request'
import { formatDateTime, unwrapListResponse } from '@/utils/response'

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

onMounted(loadLogs)
</script>

<style scoped>
.data-import-page {
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

.upload-state {
  margin: 18px 0 8px;
}

.upload-text {
  margin-top: 8px;
  color: var(--amod-text-soft);
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
}
</style>
