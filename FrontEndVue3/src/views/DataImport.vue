<template>
  <div class="amod-page crud-page data-import-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">数据上传</div>
      </div>
      <div class="page-actions">
        <!-- 上传日志入口已移除（日志独立管理） -->
      </div>
    </div>
    <DatasetUploadPanel @uploaded="loadLogs" @imported="loadLogs" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DatasetUploadPanel from '@/components/DatasetUploadPanel.vue'
const router = useRouter()

function loadLogs() {}

function goImportLog() {
  router.push('/import-log')
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
