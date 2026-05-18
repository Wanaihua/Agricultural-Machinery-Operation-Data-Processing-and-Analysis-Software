<template>
  <el-card class="amod-card upload-panel" shadow="never">
    <template #header>
      <div class="panel-header">
        <div>
          <div class="panel-title">文件上传与数据导入</div>
          <div class="panel-subtitle">支持拖拽或点击上传，完成后可自动触发轨迹导入</div>
        </div>
        <el-switch v-model="autoImport" active-text="自动导入" inactive-text="仅上传" />
      </div>
    </template>

    <el-upload
      drag
      :show-file-list="false"
      :before-upload="beforeUpload"
      :http-request="handleUploadRequest"
      class="upload-zone"
      accept=".xlsx,.xls,.csv,.png,.jpg,.jpeg"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text-main">将文件拖到这里，或点击选择文件</div>
      <div class="upload-text-sub">仅支持 xlsx / xls / csv / png / jpg / jpeg，单文件不超过 10MB</div>
    </el-upload>

    <div class="progress-wrap">
      <el-progress :percentage="progress" :status="progressStatus" :stroke-width="12" />
      <div class="progress-tip">{{ progressText }}</div>
    </div>

    <el-descriptions v-if="uploadedFile" class="result-box" :column="1" border>
      <el-descriptions-item label="文件ID">{{ uploadedFile.id }}</el-descriptions-item>
      <el-descriptions-item label="文件名">{{ uploadedFile.name }}</el-descriptions-item>
      <el-descriptions-item label="地址">{{ uploadedFile.url }}</el-descriptions-item>
      <el-descriptions-item label="大小(kb)">{{ uploadedFile.size }}</el-descriptions-item>
    </el-descriptions>

    <div class="action-row" v-if="uploadedFile && !autoImport">
      <el-button type="primary" :loading="importing" @click="triggerImport">触发数据导入</el-button>
    </div>

    <el-alert
      v-if="lastImportResult"
      :title="importResultTitle"
      :type="lastImportResult.ok ? 'success' : 'error'"
      :closable="false"
      show-icon
      class="result-alert"
    >
      <template #default>
        <div class="result-detail">
          <div>成功条数：{{ lastImportResult.data?.success_count ?? 0 }}</div>
          <div>失败条数：{{ lastImportResult.data?.failure_count ?? 0 }}</div>
          <div>耗时：{{ lastImportResult.data?.cost_seconds ?? 0 }} 秒</div>
        </div>
      </template>
    </el-alert>
  </el-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const emit = defineEmits(['uploaded', 'imported'])

const uploadClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
})

uploadClient.interceptors.request.use((config) => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const token = user.token || localStorage.getItem('token')
  config.headers = config.headers || {}
  if (token) {
    config.headers.token = token
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

uploadClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error?.response?.data?.message || error?.response?.data?.msg || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

const autoImport = ref(true)
const progress = ref(0)
const progressState = ref('')
const uploading = ref(false)
const importing = ref(false)
const uploadedFile = ref(null)
const lastImportResult = ref(null)

const progressStatus = computed(() => {
  if (progressState.value === 'success') return 'success'
  if (progressState.value === 'error') return 'exception'
  return undefined
})

const progressText = computed(() => {
  if (progressState.value === 'success' && uploadedFile.value) {
    return `文件已上传：${uploadedFile.value.name}`
  }
  if (progressState.value === 'error') {
    return '上传失败，请检查文件格式或后端接口。'
  }
  if (uploading.value) {
    return `上传进度 ${progress.value}%`
  }
  return '拖拽或点击上方区域开始上传。'
})

const importResultTitle = computed(() => {
  if (!lastImportResult.value) {
    return ''
  }
  return lastImportResult.value.ok ? '导入完成' : '导入失败'
})

function beforeUpload(file) {
  const allowed = ['xlsx', 'xls', 'csv', 'png', 'jpg', 'jpeg']
  const fileExt = file.name.split('.').pop()?.toLowerCase() || ''
  const isAllowed = allowed.includes(fileExt)
  const isUnderLimit = file.size / 1024 / 1024 <= 10

  if (!isAllowed) {
    ElMessage.warning('仅支持 xlsx、xls、csv、png、jpg、jpeg 文件')
    return false
  }
  if (!isUnderLimit) {
    ElMessage.warning('文件大小不能超过 10MB')
    return false
  }
  return true
}

async function handleUploadRequest(options) {
  const formData = new FormData()
  formData.append('file', options.file)

  progress.value = 0
  progressState.value = 'uploading'
  uploading.value = true
  lastImportResult.value = null

  try {
    const result = await uploadClient.post('/api/upload-file/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total) {
          progress.value = Math.round((event.loaded / event.total) * 100)
        }
      },
    })

    uploadedFile.value = result.data || result
    progress.value = 100
    progressState.value = 'success'
    ElMessage.success('文件上传成功')
    emit('uploaded', uploadedFile.value)

    if (autoImport.value) {
      await triggerImport()
    }

    options.onSuccess?.(result)
  } catch (error) {
    progressState.value = 'error'
    options.onError?.(error)
  } finally {
    uploading.value = false
  }
}

async function triggerImport() {
  if (!uploadedFile.value?.id) {
    ElMessage.warning('请先上传文件')
    return
  }

  importing.value = true
  try {
    const result = await uploadClient.post('/api/import-data/', {
      file_id: uploadedFile.value.id,
      admin_id: JSON.parse(localStorage.getItem('user') || '{}').id || 1,
    })
    lastImportResult.value = { ok: true, data: result.data || result }
    ElMessage.success('数据导入完成')
    emit('imported', lastImportResult.value.data)
  } catch (error) {
    const payload = error?.response?.data || {}
    lastImportResult.value = { ok: false, data: payload.data || {} }
    ElMessage.error(payload.message || payload.msg || '导入失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.upload-panel {
  border-radius: 18px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
}

.panel-subtitle {
  margin-top: 4px;
  color: var(--amod-text-soft);
  font-size: 13px;
}

.upload-zone {
  width: 100%;
}

.upload-zone :deep(.el-upload-dragger) {
  width: 100%;
  height: 220px;
  border-radius: 18px;
  border: 1px dashed rgba(47, 111, 78, 0.35);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(247, 250, 244, 0.92));
}

.upload-icon {
  font-size: 52px;
  color: var(--amod-primary);
  margin-top: 26px;
}

.upload-text-main {
  margin-top: 12px;
  font-size: 18px;
  font-weight: 700;
}

.upload-text-sub {
  margin-top: 8px;
  color: var(--amod-text-soft);
}

.progress-wrap {
  margin-top: 18px;
}

.progress-tip {
  margin-top: 8px;
  color: var(--amod-text-soft);
}

.result-box {
  margin-top: 18px;
}

.action-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.result-alert {
  margin-top: 16px;
}

.result-detail {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
</style>
