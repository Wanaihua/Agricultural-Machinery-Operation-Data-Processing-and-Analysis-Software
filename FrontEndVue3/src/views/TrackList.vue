<template>
  <div class="amod-page track-list-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">轨迹列表</div>
      </div>
    </div>

    <div class="toolbar-row">
      <div class="action-group">
        <el-button type="primary" @click="loadTracks">刷新数据</el-button>
        <el-button type="warning" @click="goUploadPage">上传轨迹</el-button>
      </div>
    </div>

    <el-card class="amod-card filter-card" shadow="never">
      <el-form :inline="true" :model="filters">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.timeRange"
            type="daterange"
            value-format="YYYY-MM-DD HH:mm:ss"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            clearable
          />
        </el-form-item>
        <el-form-item label="最小幅宽">
          <el-input-number v-model="filters.minWidth" :min="0" :step="0.1" controls-position="right" />
        </el-form-item>
        <el-form-item label="最大幅宽">
          <el-input-number v-model="filters.maxWidth" :min="0" :step="0.1" controls-position="right" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="amod-card table-card" shadow="never">
      <div class="batch-actions" v-if="selectedIds.length">
        <span>已选 {{ selectedIds.length }} 项</span>
        <el-button v-if="isAdmin" type="danger" size="small" @click="batchDelete">批量删除</el-button>
        <el-button size="small" @click="toggleSelect">反选</el-button>
        <el-button size="small" @click="clearSelection">取消选择</el-button>
      </div>
      <el-table
        :data="pagedTracks"
        border stripe
        class="amod-table"
        @selection-change="onSelectionChange"
        ref="tableRef"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="trackid" label="轨迹ID" width="100" />
        <el-table-column label="文件名" width="120">
          <template #default="{ row }">
            {{ row.file_name ? row.file_name + '.xlsx' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="starttime" label="起始时间" min-width="180" :formatter="formatStart" />
        <el-table-column prop="endtime" label="结束时间" min-width="180" :formatter="formatEnd" />
        <el-table-column prop="width" label="幅宽" width="120" :formatter="formatWidth" />
        <el-table-column prop="totalpoints" label="总点数" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="goMap(scope.row.trackid)">查看轨迹</el-button>
            <el-button v-if="isAdmin" type="danger" link @click="deleteTrack(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager-wrap">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredTracks.length"
          @size-change="syncPagedData"
          @current-change="syncPagedData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { formatDateTime, formatNumberFixed, unwrapListResponse } from '@/utils/response'
import { getCurrentUser, isAdminUser } from '@/utils/auth'

const router = useRouter()
const tracks = ref([])
const page = reactive({ current: 1, size: 10 })
const filters = reactive({ timeRange: [], minWidth: undefined, maxWidth: undefined })
const isAdmin = computed(() => isAdminUser(getCurrentUser()))
const selectedIds = ref([])
const tableRef = ref(null)

const filteredTracks = computed(() => {
  return tracks.value.filter((item) => {
    const startTime = item.starttime ? new Date(item.starttime).getTime() : null
    const endTime = item.endtime ? new Date(item.endtime).getTime() : null
    const [begin, end] = filters.timeRange || []
    const beginTime = begin ? new Date(begin).getTime() : null
    const endRangeTime = end ? new Date(end).getTime() : null

    const width = Number(item.width || 0)
    const widthOk = (filters.minWidth === undefined || filters.minWidth === null || width >= Number(filters.minWidth)) &&
      (filters.maxWidth === undefined || filters.maxWidth === null || width <= Number(filters.maxWidth))

    const timeOk = !beginTime || !endRangeTime || ((startTime >= beginTime) && (endTime <= endRangeTime))

    return widthOk && timeOk
  })
})

const pagedTracks = computed(() => {
  const start = (page.current - 1) * page.size
  return filteredTracks.value.slice(start, start + page.size)
})

function formatStart(row, column, value) {
  return formatDateTime(value)
}

function formatEnd(row, column, value) {
  return formatDateTime(value)
}

function formatWidth(row, column, value) {
  return formatNumberFixed(value, 4)
}

async function loadTracks() {
  const res = await request.get('/api/track/')
  tracks.value = unwrapListResponse(res)
  syncPagedData()
}

function syncPagedData() {
  const maxPage = Math.max(1, Math.ceil(filteredTracks.value.length / page.size))
  if (page.current > maxPage) {
    page.current = maxPage
  }
}

function applyFilters() {
  page.current = 1
  syncPagedData()
}

function resetFilters() {
  filters.timeRange = []
  filters.minWidth = undefined
  filters.maxWidth = undefined
  page.current = 1
  syncPagedData()
}

function goMap(trackId) {
  router.push(`/track/map/${trackId}`)
}

async function deleteTrack(row) {
  if (!isAdmin.value) {
    ElMessage.warning('当前账号无删除权限')
    return
  }

  const confirmed = confirm(`确认删除轨迹 ${row.trackid} 吗？此操作会同时删除轨迹点、作业统计和通行率数据。`)
  if (!confirmed) return

  try {
    await request.delete(`/api/track/${row.trackid}/`)
    ElMessage.success(`已删除轨迹 ${row.trackid}`)
    await loadTracks()
  } catch (error) {
    console.error(error)
    if (error?.response?.status === 404) {
      ElMessage.warning(`轨迹 ${row.trackid} 已不存在，列表已刷新`)
      await loadTracks()
      return
    }
    ElMessage.error(error?.response?.data?.msg || error?.response?.data?.message || '删除失败')
  }
}

onMounted(loadTracks)

function goUploadPage() {
  router.push('/data/import')
}

function onSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.trackid)
}

function toggleSelect() {
  const table = tableRef.value
  if (!table) return
  pagedTracks.value.forEach(row => {
    const isSelected = selectedIds.value.includes(row.trackid)
    table.toggleRowSelection(row, !isSelected)
  })
}

function clearSelection() {
  tableRef.value?.clearSelection()
}

async function batchDelete() {
  if (!isAdmin.value) {
    ElMessage.warning('当前账号无删除权限')
    return
  }
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条轨迹吗？`, '提示', { type: 'warning' })
    for (const id of selectedIds.value) {
      await request.delete(`/api/track/${id}/`)
    }
    ElMessage.success('批量删除成功')
    clearSelection()
    await loadTracks()
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.track-list-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card {
  padding-bottom: 8px;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--amod-text-soft);
}
</style>
