<template>
  <el-card class="amod-card upload-panel" shadow="never">
    <template #header>
      <div class="panel-header">
        <div>
          <div class="panel-title">XLSX 文件上传</div>
          <div class="panel-subtitle">支持拖拽或点击上传 xlsx 文件，上传完成后自动导入数据库</div>
        </div>
        <div class="header-actions">
          <el-button @click="downloadTemplate">下载模板</el-button>
        </div>
      </div>
    </template>

    <el-upload
      drag
      multiple
      :show-file-list="false"
      :before-upload="beforeUpload"
      :http-request="handleUploadRequest"
      class="upload-zone"
      accept=".xlsx,.xls"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text-main">将文件拖到这里，或点击选择文件</div>
      <div class="upload-text-sub">支持多文件上传，仅支持 xlsx / xls，单文件不超过 10MB</div>
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

    <div v-if="uploadResults.length > 0" class="result-box">
      <div style="font-weight: 700; margin-bottom: 8px;">上传结果 ({{ uploadResults.length }} 个文件)</div>
      <div v-for="(r, i) in uploadResults" :key="i" style="font-size: 13px; color: var(--amod-text-soft);">
        {{ r.file }}：{{ formatFileResult(r) }}
      </div>
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
  baseURL: import.meta.env.DEV ? (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') : '',
  timeout: 60000,  // 导入可能耗时，增大超时
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

const progress = ref(0)
const progressState = ref('')   // '' | 'uploading' | 'importing' | 'success' | 'error'
const uploading = ref(false)
const uploadedFile = ref(null)
const lastImportResult = ref(null)
const uploadResults = ref([])
const totalFiles = ref(0)
const completedFiles = ref(0)
const pendingCount = ref(0)
const slotIndex = ref(0)       // 同步递增，给每个文件分配唯一的进度槽位
const currentFileName = ref('')
// 导入串行队列：所有文件并行上传，但导入必须一个接一个（SQLite 不允许并发写）
let importChain = Promise.resolve()

const progressStatus = computed(() => {
  if (progressState.value === 'success') return 'success'
  if (progressState.value === 'error') return 'exception'
  return undefined
})

const progressText = computed(() => {
  const successCount = uploadResults.value.filter(r => r.ok).length
  const failCount = uploadResults.value.filter(r => !r.ok).length

  if (progressState.value === 'success') {
    let msg = `全部完成：${uploadResults.value.length} 个文件`
    if (successCount > 0) msg += `，${successCount} 个导入成功`
    if (failCount > 0) msg += `，${failCount} 个导入失败`
    return msg
  }
  if (progressState.value === 'error' && completedFiles.value >= totalFiles.value) {
    return `完成：${successCount} 个成功，${failCount} 个失败`
  }
  if (uploading.value) {
    return `${currentFileName.value}：${progressState.value === 'importing' ? '正在导入' : '正在上传'}（${completedFiles.value + 1}/${totalFiles.value}）`
  }
  return '拖拽或点击上方区域开始上传（支持多文件）'
})

const importResultTitle = computed(() => {
  if (!lastImportResult.value) return ''
  return lastImportResult.value.ok ? '处理完成' : '处理失败'
})

/** 判断单个文件的导入结果并格式化显示 */
function formatFileResult(r) {
  if (r.ok === false) return r.message || '导入失败'
  if (r.ok === true && r.duplicate) return '已存在，跳过'
  if (r.ok === true) return `成功（${r.success_count ?? 0} 条）`
  return '未知状态'
}

function beforeUpload(file) {
  const allowed = ['xlsx', 'xls']
  const fileExt = file.name.split('.').pop()?.toLowerCase() || ''
  const isAllowed = allowed.includes(fileExt)
  const isUnderLimit = file.size / 1024 / 1024 <= 10

  if (!isAllowed) {
    ElMessage.warning('仅支持 xlsx、xls 文件')
    return false
  }
  if (!isUnderLimit) {
    ElMessage.warning('文件大小不能超过 10MB')
    return false
  }
  pendingCount.value++
  return true
}

async function handleUploadRequest(options) {
  const formData = new FormData()
  formData.append('file', options.file)

  // 首个文件开始上传时初始化队列
  if (slotIndex.value === 0 && completedFiles.value === 0) {
    totalFiles.value = pendingCount.value
    pendingCount.value = 0
    progress.value = 0
    progressState.value = 'uploading'
    uploading.value = true
    lastImportResult.value = null
    slotIndex.value = 0
  }

  // 同步占位：每个文件立即分配唯一的槽位（在任何 await 之前）
  const mySlot = slotIndex.value
  slotIndex.value++

  currentFileName.value = options.file.name

  // 当前文件在整体进度中的区间：上传占60%，导入占40%
  const step = 100 / totalFiles.value
  const stepStart = mySlot * step
  const uploadEnd = stepStart + step * 0.6
  const importEnd = stepStart + step

  try {
    // ===== 阶段1：并行上传文件（进度 stepStart~uploadEnd） =====
    progressState.value = 'uploading'
    const uploadRes = await uploadClient.post('/api/upload-file/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total) {
          const pct = event.loaded / event.total
          progress.value = Math.round(stepStart + (uploadEnd - stepStart) * pct)
        }
      },
    })

    const fileInfo = uploadRes.data || uploadRes

    // MD5重复，跳过导入
    if (fileInfo.duplicate) {
      completedFiles.value++
      uploadResults.value.push({ file: options.file.name, ok: true, duplicate: true })
      ElMessage.success(`${options.file.name} 文件已存在，跳过`)
      if (completedFiles.value >= totalFiles.value) {
        progress.value = 100
        const hasError = uploadResults.value.some(r => r.ok === false)
        progressState.value = hasError ? 'error' : 'success'
        uploading.value = false
      }
      options.onSuccess?.(uploadRes)
      return
    }

    // ===== 阶段2：串行导入（挂到 importChain，一个接一个避免 SQLite 锁） =====
    await new Promise((resolveImport) => {
      importChain = importChain.then(async () => {
        progressState.value = 'importing'
        currentFileName.value = options.file.name

        let simProgress = uploadEnd
        const simTimer = setInterval(() => {
          const remaining = importEnd - simProgress
          if (remaining > 0.3) {
            simProgress += remaining * 0.12
            progress.value = Math.round(simProgress)
          }
        }, 150)

        try {
          const importRes = await uploadClient.post('/api/import-file/', { file_id: fileInfo.id })
          clearInterval(simTimer)

          const importResult = importRes.data || importRes

          let ok = false
          let detail = {}

          if (importResult && importResult.success_count !== undefined) {
            ok = importResult.success_count > 0
            detail = {
              ok,
              success_count: importResult.success_count,
              failure_count: importResult.failure_count || 0,
              cost_seconds: importResult.cost_seconds || 0,
            }
          } else if (importResult && importResult.message) {
            ok = false
            detail = { ok: false, message: importResult.message }
          } else {
            ok = true
            detail = { ok: true, message: '上传成功' }
          }

          completedFiles.value++
          uploadResults.value.push({ file: options.file.name, ...detail })
          emit('uploaded', fileInfo)
          emit('imported', importResult)

          if (ok) {
            ElMessage.success(`${options.file.name} 导入成功（${detail.success_count ?? 0} 条）`)
          } else {
            ElMessage.warning(`${options.file.name} ${detail.message || '导入失败'}`)
          }

          options.onSuccess?.(importRes)
        } catch (error) {
          clearInterval(simTimer)
          completedFiles.value++
          const errMsg = error?.response?.data?.message || error?.response?.data?.msg || error?.message || '未知错误'
          console.error('[upload-error]', options.file.name, error)
          uploadResults.value.push({ file: options.file.name, ok: false, message: errMsg })
          ElMessage.error(`${options.file.name} ${errMsg}`)
          options.onError?.(error)
        } finally {
          if (completedFiles.value >= totalFiles.value) {
            progress.value = 100
            const hasError = uploadResults.value.some(r => r.ok === false)
            progressState.value = hasError ? 'error' : 'success'
            uploading.value = false
            totalFiles.value = 0
            completedFiles.value = 0
            slotIndex.value = 0
            currentFileName.value = ''
          } else {
            progressState.value = 'uploading'
          }
          resolveImport()
        }
      }).catch(() => resolveImport())
    })
  } catch (error) {
    // 上传阶段错误
    completedFiles.value++
    const errMsg = error?.response?.data?.message || error?.response?.data?.msg || error?.message || '未知错误'
    console.error('[upload-error]', options.file.name, error)
    uploadResults.value.push({ file: options.file.name, ok: false, message: errMsg })
    ElMessage.error(`${options.file.name} ${errMsg}`)
    options.onError?.(error)
    if (completedFiles.value >= totalFiles.value) {
      progress.value = 100
      progressState.value = 'error'
      uploading.value = false
      totalFiles.value = 0
      completedFiles.value = 0
      slotIndex.value = 0
      currentFileName.value = ''
    }
  }
}

async function downloadTemplate() {
  try {
    const blob = await uploadClient.get('/api/upload-template/', {
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'track_upload_template.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('模板下载失败')
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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
