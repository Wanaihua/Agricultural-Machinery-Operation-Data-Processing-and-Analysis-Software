<template>
  <div class="workload-analysis">
    <!-- 查询条件 -->
    <div class="search-bar">
      <el-card class="search-card">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="作业幅宽(米)">
            <el-input-number
              v-model="searchForm.workWidth"
              :min="0.1"
              :max="20"
              :step="0.1"
              :precision="1"
            />
          </el-form-item>
          <el-form-item label="轨迹ID(可选)">
            <el-input-number
              v-model="searchForm.trackId"
              :min="1"
              placeholder="留空查询全部"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="analyzeWorkload" :loading="loading">
              <el-icon><Search /></el-icon> 开始分析
            </el-button>
            <el-button @click="resetSearch">
              <el-icon><Refresh /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 汇总统计卡片 -->
    <div class="summary-cards" v-if="summaryData">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="card-content">
              <div class="card-icon" style="background-color: #409EFF">
                <el-icon :size="28"><Timer /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ summaryData.total_time.formatted }}</div>
                <div class="card-label">总作业时长</div>
                <div class="card-sub">{{ summaryData.total_time.seconds.toFixed(1) }}秒</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="card-content">
              <div class="card-icon" style="background-color: #67C23A">
                <el-icon :size="28"><Location /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ summaryData.total_distance.kilometers }}公里</div>
                <div class="card-label">总作业行程</div>
                <div class="card-sub">{{ summaryData.total_distance.meters }}米</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="card-content">
              <div class="card-icon" style="background-color: #E6A23C">
                <el-icon :size="28"><MapLocation /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ summaryData.total_area.mu }}亩</div>
                <div class="card-label">总作业面积</div>
                <div class="card-sub">{{ summaryData.total_area.square_meters }}㎡</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="card-content">
              <div class="card-icon" style="background-color: #F56C6C">
                <el-icon :size="28"><Odometer /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ summaryData.average_velocity.km_per_h }}km/h</div>
                <div class="card-label">平均作业速度</div>
                <div class="card-sub">{{ summaryData.average_velocity.m_per_s }}米/秒</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 10px">
        <el-col :span="12">
          <el-card class="info-card">
            <template #header><el-icon><DataAnalysis /></el-icon> 统计概览</template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="总轨迹数">{{ summaryData.total_tracks }}</el-descriptions-item>
              <el-descriptions-item label="作业幅宽">{{ summaryData.work_width }}米</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 单条轨迹分析结果 -->
    <div class="detail-result" v-if="trackData">
      <el-card class="result-card">
        <template #header><el-icon><Document /></el-icon> 轨迹 #{{ trackData.track_id }} 分析结果</template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="作业总时长">
            <el-tag type="primary">{{ trackData.total_time.formatted }}</el-tag>
            <span class="sub-text">({{ trackData.total_time.seconds.toFixed(1) }}秒)</span>
          </el-descriptions-item>
          <el-descriptions-item label="作业总行程">
            <el-tag type="success">{{ trackData.total_distance.kilometers }}公里</el-tag>
            <span class="sub-text">({{ trackData.total_distance.meters }}米)</span>
          </el-descriptions-item>
          <el-descriptions-item label="作业面积">
            <el-tag type="warning">{{ trackData.work_area.mu }}亩</el-tag>
            <span class="sub-text">({{ trackData.work_area.square_meters }}㎡)</span>
          </el-descriptions-item>
          <el-descriptions-item label="平均作业速度">
            <el-tag type="danger">{{ trackData.average_velocity.km_per_h }}km/h</el-tag>
            <span class="sub-text">({{ trackData.average_velocity.m_per_s }}米/秒)</span>
          </el-descriptions-item>
          <el-descriptions-item label="作业幅宽">{{ trackData.work_width }}米</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 全部轨迹列表 -->
    <div class="track-list" v-if="trackListData && trackListData.length > 0">
      <el-card>
        <template #header><el-icon><Grid /></el-icon> 全部轨迹分析结果</template>
        <el-table :data="trackListData" border stripe style="width: 100%">
          <el-table-column prop="track_id" label="轨迹ID" width="100" />
          <el-table-column label="作业时长" width="150">
            <template #default="scope">
              {{ scope.row.total_time.formatted }}
            </template>
          </el-table-column>
          <el-table-column label="作业行程" width="150">
            <template #default="scope">
              {{ scope.row.total_distance.kilometers }}公里
            </template>
          </el-table-column>
          <el-table-column label="作业面积" width="150">
            <template #default="scope">
              {{ scope.row.work_area.mu }}亩
            </template>
          </el-table-column>
          <el-table-column label="平均速度" width="150">
            <template #default="scope">
              {{ scope.row.average_velocity.km_per_h }}km/h
            </template>
          </el-table-column>
          <el-table-column label="作业幅宽" width="120">
            <template #default="scope">
              {{ scope.row.work_width }}米
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && !summaryData && !trackData && !trackListData">
      <el-empty description="请设置查询条件后点击'开始分析'">
        <template #image>
          <el-icon :size="80" color="#c0c4cc"><DataAnalysis /></el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Refresh, Timer, Location, MapLocation, Odometer,
  DataAnalysis, Document, Grid
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const searchForm = ref({
  workWidth: 2.0,
  trackId: null
})
const loading = ref(false)
const summaryData = ref(null)
const trackData = ref(null)
const trackListData = ref(null)

const analyzeWorkload = async () => {
  loading.value = true
  summaryData.value = null
  trackData.value = null
  trackListData.value = null

  const workWidth = searchForm.value.workWidth

  try {
    if (searchForm.value.trackId) {
      // 分析单条轨迹
      const res = await request.get(`/api/analysis/track/${searchForm.value.trackId}/`, {
        params: { work_width: workWidth }
      })
      if (res.code === '200') {
        trackData.value = res.data
        ElMessage.success('分析完成')
      } else {
        ElMessage.error('分析失败：' + (res.msg || '未知错误'))
      }
    } else {
      // 分析全部轨迹并获取汇总
      const [summaryRes, listRes] = await Promise.all([
        request.get('/api/analysis/summary/', { params: { work_width: workWidth } }),
        request.get('/api/analysis/all-tracks/', { params: { work_width: workWidth } })
      ])
      if (summaryRes.code === '200') {
        summaryData.value = summaryRes.data
        ElMessage.success('汇总分析完成')
      } else {
        ElMessage.error('分析失败：' + (summaryRes.msg || '未知错误'))
      }
      if (listRes.code === '200') {
        trackListData.value = listRes.data
      }
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('请求失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.value = { workWidth: 2.0, trackId: null }
  summaryData.value = null
  trackData.value = null
  trackListData.value = null
}
</script>

<style scoped>
.workload-analysis {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-card {
  background: #f5f7fa;
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  height: 120px;
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: white;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.card-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 3px;
}

.card-sub {
  font-size: 12px;
  color: #c0c4cc;
}

.info-card {
  margin-bottom: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.sub-text {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

.track-list {
  margin-bottom: 20px;
}

.empty-state {
  margin-top: 100px;
}
</style>
