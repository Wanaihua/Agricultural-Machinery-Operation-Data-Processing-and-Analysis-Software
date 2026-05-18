<template>
  <div class="amod-page track-map-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">轨迹地图</div>
        <div class="amod-subtitle">轨迹线按作业状态着色，支持点位点击与高亮</div>
      </div>
      <el-button @click="$router.back()">返回列表</el-button>
    </div>

    <el-row :gutter="16" class="stat-grid">
      <el-col :xs="12" :md="8">
        <el-card class="amod-card stat-card" shadow="never">
          <div class="stat-label">作业时长</div>
          <div class="stat-value">{{ workStat.worktime }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="8">
        <el-card class="amod-card stat-card" shadow="never">
          <div class="stat-label">作业面积</div>
          <div class="stat-value">{{ workStat.workarea }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="8">
        <el-card class="amod-card stat-card" shadow="never">
          <div class="stat-label">平均速度</div>
          <div class="stat-value">{{ workStat.avgvelocity }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="content-grid">
      <el-col :xs="24" :lg="16">
        <el-card class="amod-card map-card" shadow="never">
          <template #header>
            <div class="panel-title">
              轨迹地图
              <span class="panel-subtitle">轨迹ID：{{ trackId }}</span>
            </div>
          </template>

          <div class="map-wrap">
            <div v-if="points.length" class="map-stage">
              <div id="leaflet-map" class="map-stage"></div>
            </div>

            <el-empty v-else description="暂无轨迹点位数据" />

            <div v-if="points.length" class="map-loading-tip">
              在线切片已加载，轨迹叠加显示
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="amod-card detail-card" shadow="never">
          <template #header>
            <div class="panel-title">点位详情</div>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="轨迹ID">{{ trackId }}</el-descriptions-item>
            <el-descriptions-item label="点位数量">{{ points.length }}</el-descriptions-item>
            <el-descriptions-item label="当前点位">
              {{ activePoint ? activePoint.id : '未选中' }}
            </el-descriptions-item>
            <el-descriptions-item label="经度">{{ activePoint?.lon || '--' }}</el-descriptions-item>
            <el-descriptions-item label="纬度">{{ activePoint?.lat || '--' }}</el-descriptions-item>
            <el-descriptions-item label="速度">{{ activePoint?.velocity || '--' }}</el-descriptions-item>
            <el-descriptions-item label="耕深">{{ activePoint?.depth || '--' }}</el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <div class="legend-title">状态图例</div>
          <div class="legend-row">
            <span class="legend-dot legend-green"></span>
            正常作业
          </div>
          <div class="legend-row">
            <span class="legend-dot legend-gray"></span>
            闲置/停止
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import { unwrapListResponse, unwrapObjectResponse } from '@/utils/response'
import L from 'leaflet'

const route = useRoute()
const trackId = computed(() => route.params.id)
  const points = ref([])
const activePoint = ref(null)
const activeSegmentIndex = ref(-1)
const track = ref({})
const backgroundVisible = ref(true)
const workStat = reactive({ worktime: '--', workarea: '--', avgvelocity: '--' })
const backgroundImageUrl = computed(() => {
  if (!trackId.value) {
    return ''
  }
  return encodeURI(`http://127.0.0.1:8000/datasets/遥感图/${trackId.value}.png`)
})

const trackBounds = computed(() => {
  if (!points.value.length) {
    return null
  }

  const lats = points.value.map((point) => Number(point.lat))
  const lons = points.value.map((point) => Number(point.lon))
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const minLon = Math.min(...lons)
  const maxLon = Math.max(...lons)
  const latPad = Math.max((maxLat - minLat) * 0.2, 0.001)
  const lonPad = Math.max((maxLon - minLon) * 0.2, 0.001)

  return [
    [minLat - latPad, minLon - lonPad],
    [maxLat + latPad, maxLon + lonPad],
  ]
})

const overlayPoints = computed(() => {
  if (!trackBounds.value || !points.value.length) {
    return []
  }

  const [[south, west], [north, east]] = trackBounds.value
  const latSpan = Math.max(north - south, 1e-9)
  const lonSpan = Math.max(east - west, 1e-9)

  return points.value.map((point) => ({
    id: point.id,
    raw: point,
    segmentIndex: point.segmentIndex,
    x: ((Number(point.lon) - west) / lonSpan) * 100,
    y: (1 - (Number(point.lat) - south) / latSpan) * 100,
    workstatus: point.workstatus,
  }))
})

const overlaySegments = computed(() => {
  if (!overlayPoints.value.length) {
    return []
  }

  const result = []
  let current = [overlayPoints.value[0]]

  overlayPoints.value.slice(1).forEach((point) => {
    const previous = current[current.length - 1]
    if (point.segmentIndex !== previous.segmentIndex) {
      if (current.length > 1) {
        result.push(buildSegment(current, result.length))
      }
      current = [point]
      return
    }

    current.push(point)
  })

  if (current.length > 1) {
    result.push(buildSegment(current, result.length))
  }

  return result
})

let map = null
let overlayLayer = null

function ensureMap() {
  if (map) return
  try {
    const container = document.getElementById('leaflet-map')
    if (!container) {
      console.warn('leaflet container not found, delaying init')
      return
    }
    map = L.map('leaflet-map', { zoomControl: true, preferCanvas: true })
    L.tileLayer('https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', {
      attribution: '',
      maxZoom: 18,
    }).addTo(map)
    overlayLayer = L.layerGroup().addTo(map)
  } catch (e) {
    console.error('init leaflet failed', e)
  }
}

function renderLeaflet() {
  if (!points.value.length) return
  ensureMap()
  if (!map) {
    console.warn('map not initialized yet, skip renderLeaflet')
    return
  }
  if (!overlayLayer) overlayLayer = L.layerGroup().addTo(map)
  overlayLayer.clearLayers()

  // add segments
  const segments = []
  let current = [points.value[0]]
  points.value.slice(1).forEach((p) => {
    const prev = current[current.length - 1]
    if (p.segmentIndex !== prev.segmentIndex) {
      if (current.length > 0) segments.push(current.slice())
      current = [p]
      return
    }
    current.push(p)
  })
  if (current.length) segments.push(current)

  segments.forEach((seg) => {
    const latlngs = seg.map((p) => [Number(p.lat), Number(p.lon)])
    const status = seg[0]?.workstatus
    const color = status === 0 ? 'rgba(132,138,146,0.9)' : 'rgba(104,223,58,0.95)'
    L.polyline(latlngs, { color, weight: 4, opacity: 0.85 }).addTo(overlayLayer)
  })

  // add points
  points.value.forEach((p) => {
    const marker = L.circleMarker([Number(p.lat), Number(p.lon)], {
      radius: 4,
      fillColor: p.workstatus === 0 ? '#8a8f98' : '#48e11e',
      color: '#fff',
      weight: 0.6,
      opacity: 0.95,
      fillOpacity: 0.95,
    })
    marker.on('click', () => selectPoint(p))
    marker.addTo(overlayLayer)
  })

  // fit to bounds
  const bounds = trackBounds.value
  if (bounds && map) {
    map.fitBounds(bounds)
  }
}

onMounted(() => {
  // create map container when mounted (tile layer will be set when rendering)
  ensureMap()
})

onBeforeUnmount(() => {
  try {
    if (map) {
      map.remove()
      map = null
      overlayLayer = null
    }
  } catch (e) {
    console.error('destroy map', e)
  }
})

function buildSegment(segmentPoints, index) {
  const status = segmentPoints[0]?.workstatus
  const pointsString = segmentPoints.map((point) => `${point.x},${point.y}`).join(' ')
  const highlighted = index === activeSegmentIndex.value

  return {
    key: `${index}-${status}`,
    points: pointsString,
    className: status === 0
      ? highlighted ? 'track-line-active track-line-gray' : 'track-line-gray'
      : highlighted ? 'track-line-active track-line-green' : 'track-line-green',
  }
}

function selectPoint(point) {
  activePoint.value = point
  activeSegmentIndex.value = Number(point.segmentIndex ?? -1)
}

async function loadTrackData() {
  backgroundVisible.value = true
  const id = trackId.value
  const [trackRes, pointsRes, workRes, rateRes] = await Promise.allSettled([
    request.get(`/api/track/${id}/`),
    request.get(`/api/track/${id}/trackpoints/`),
    request.get(`/api/work/${id}/`),
    request.get(`/api/rate/${id}/`),
  ])

  track.value = trackRes.status === 'fulfilled' ? unwrapObjectResponse(trackRes.value) || {} : {}

  const rawPoints = pointsRes.status === 'fulfilled' ? unwrapListResponse(pointsRes.value) : []
  const sortedPoints = rawPoints
    .filter((item) => item && item.lat !== null && item.lon !== null)
    .sort((a, b) => new Date(a.gpstime || 0) - new Date(b.gpstime || 0))

  let segmentIndex = 0
  points.value = sortedPoints.map((item, index) => {
    if (index > 0 && item.workstatus !== sortedPoints[index - 1].workstatus) {
      segmentIndex += 1
    }

    return {
      ...item,
      id: item.id ?? index,
      segmentIndex,
    }
  })

  if (points.value.length) {
    activePoint.value = points.value[0]
    activeSegmentIndex.value = Number(points.value[0].segmentIndex ?? 0)
  }

  const work = workRes.status === 'fulfilled' ? unwrapObjectResponse(workRes.value) || {} : {}
  const rate = rateRes.status === 'fulfilled' ? unwrapObjectResponse(rateRes.value) || {} : {}

  workStat.worktime = work.worktime ?? '--'
  workStat.workarea = work.workarea ?? '--'
  workStat.avgvelocity = work.avgvelocity ?? '--'

  if (rate.passrate !== undefined) {
    workStat.passrate = rate.passrate
  }
  // wait for DOM to render map container, then render overlays
  await nextTick()
  renderLeaflet()
}

watch(
  () => route.params.id,
  () => loadTrackData(),
  { immediate: true },
)
</script>

<style scoped>
.track-map-page {
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

.stat-grid,
.content-grid {
  margin: 0 !important;
}

.stat-card {
  min-height: 112px;
}

.stat-label {
  color: var(--amod-text-soft);
}

.stat-value {
  margin-top: 14px;
  font-size: 28px;
  font-weight: 800;
  color: var(--amod-primary);
}

.map-card,
.detail-card {
  min-height: 680px;
}

.map-wrap {
  height: 620px;
  position: relative;
}

.map-stage {
  height: 100%;
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  background: linear-gradient(135deg, #d9e7d3, #eef4e9);
}

.map-background {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: fill;
}

.map-background-fallback {
  background:
    linear-gradient(90deg, rgba(255,255,255,0.18) 1px, transparent 1px),
    linear-gradient(rgba(255,255,255,0.16) 1px, transparent 1px),
    linear-gradient(135deg, #a8c39a, #6d8f66);
  background-size: 12% 100%, 100% 12%, cover;
}

.map-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.track-line-gray,
.track-line-green {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.track-line-gray {
  stroke: rgba(132, 138, 146, 0.78);
  stroke-width: 0.5;
}

.track-line-green {
  stroke: rgba(104, 223, 58, 0.86);
  stroke-width: 0.55;
}

.track-line-active {
  stroke-width: 0.9;
  filter: drop-shadow(0 0 0.18rem rgba(255, 255, 255, 0.55));
}

.point-green,
.point-gray {
  opacity: 0.95;
  stroke: rgba(255, 255, 255, 0.88);
  stroke-width: 0.18;
  cursor: pointer;
}

.point-green {
  fill: #48e11e;
}

.point-gray {
  fill: #8a8f98;
}

.map-meta {
  position: absolute;
  left: 16px;
  top: 16px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(14, 26, 18, 0.58);
  color: #fff;
  font-size: 12px;
  backdrop-filter: blur(6px);
}

.map-loading-tip {
  position: absolute;
  left: 16px;
  bottom: 16px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(18, 28, 22, 0.72);
  color: #fff;
  font-size: 12px;
  pointer-events: none;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
}

.panel-subtitle {
  color: var(--amod-text-soft);
  font-size: 13px;
  font-weight: 400;
}

.popup-box {
  line-height: 1.8;
}

.legend-title {
  font-weight: 700;
  margin-bottom: 10px;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  color: var(--amod-text-soft);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-green {
  background: #2f6f4e;
}

.legend-gray {
  background: #8a8f98;
}
</style>
