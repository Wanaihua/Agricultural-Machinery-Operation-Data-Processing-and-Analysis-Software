<template>
  <div class="amod-page track-list-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">轨迹列表</div>
        <div class="amod-subtitle">支持按时间和幅宽筛选，点击轨迹可进入地图页</div>
      </div>
      <el-button type="primary" @click="loadTracks">刷新数据</el-button>
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

    <el-card class="amod-card" shadow="never">
      <el-table :data="pagedTracks" border stripe>
        <el-table-column prop="trackid" label="轨迹ID" width="100" />
        <el-table-column prop="starttime" label="起始时间" min-width="180" :formatter="formatStart" />
        <el-table-column prop="endtime" label="结束时间" min-width="180" :formatter="formatEnd" />
        <el-table-column prop="width" label="幅宽" width="120" />
        <el-table-column prop="totalpoints" label="总点数" width="120" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="goMap(scope.row.trackid)">查看轨迹</el-button>
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
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { formatDateTime, unwrapListResponse } from '@/utils/response'

const router = useRouter()
const tracks = ref([])
const page = reactive({ current: 1, size: 10 })
const filters = reactive({ timeRange: [], minWidth: undefined, maxWidth: undefined })

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

onMounted(loadTracks)
</script>

<style scoped>
.track-list-page {
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

.filter-card {
  padding-bottom: 8px;
}

.pager-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}
</style>
