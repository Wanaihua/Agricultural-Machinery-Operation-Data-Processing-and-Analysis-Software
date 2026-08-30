<template>
  <div class="amod-page track-map-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">轨迹地图</div>
      </div>
      <div class="page-actions">
        <el-button :type="isPlaying ? 'danger' : 'success'" @click="togglePlayback">
          {{ isPlaying ? '停止展示' : '动态运行展示' }}
        </el-button>
        <el-button :type="isMeasuring ? 'warning' : 'primary'" @click="toggleMeasureMode">
          {{ isMeasuring ? '结束测距' : '测距' }}
        </el-button>
        <el-button v-if="isMeasuring || measurePoints.length" @click="clearMeasure">
          清空测距
        </el-button>
        <el-tag v-if="measurePoints.length" type="warning" effect="plain" class="measure-tag">
          {{ formattedMeasureDistance }}
        </el-tag>
        <el-button @click="$router.back()">返回列表</el-button>
      </div>
    </div>

    <el-row :gutter="16" class="stat-grid">
      <el-col :xs="12" :md="6">
        <el-card class="amod-card stat-card" shadow="never">
          <div class="stat-label">作业时长</div>
          <div class="stat-value">{{ workStat.worktime }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card class="amod-card stat-card" shadow="never">
          <div class="stat-label">作业总行程</div>
          <div class="stat-value">{{ workStat.worklength }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card class="amod-card stat-card" shadow="never">
          <div class="stat-label">作业面积</div>
          <div class="stat-value">{{ workStat.workarea }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
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

            <div v-if="points.length && isMeasuring" class="measure-tip">
              测距中：左键添加点位，右键撤回上一个点
            </div>

            <div v-if="measurePoints.length" class="measure-summary">
              <div class="measure-summary-title">测距结果</div>
              <div>点位数：{{ measurePoints.length }}</div>
              <div>总距离：{{ formattedMeasureDistance }}</div>
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
            <el-descriptions-item label="经度">{{ formatPointValue(activePoint?.lon) }}</el-descriptions-item>
            <el-descriptions-item label="纬度">{{ formatPointValue(activePoint?.lat) }}</el-descriptions-item>
            <el-descriptions-item label="速度">{{ formatPointValue(activePoint?.velocity) }}</el-descriptions-item>
            <el-descriptions-item label="耕深">{{ formatPointValue(activePoint?.depth) }}</el-descriptions-item>
            <el-descriptions-item label="平均耕深">{{ averageDepth }}</el-descriptions-item>
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
const isPlaying = ref(false)
const isMeasuring = ref(false)
const measurePoints = ref([])
const measureDistance = ref(0)
const playbackTimer = ref(null)
const playbackIndex = ref(0)
const playbackTrailPoints = ref([])
const workStat = reactive({ worktime: '--', worklength: '--', workarea: '--', avgvelocity: '--' })
const averageDepth = computed(() => calcAvgDepthFromPoints(points.value))
const backgroundImageUrl = computed(() => {
  if (!trackId.value) {
    return ''
  }
  const base = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''
  return encodeURI(`${base}/datasets/遥感图/${trackId.value}.png`)
})

const trackBounds = computed(() => {
  if (!points.value.length) {
    return null
  }

  const mapPoints = points.value.map((point) => toMapPoint(point))
  const lats = mapPoints.map((point) => Number(point.lat))
  const lons = mapPoints.map((point) => Number(point.lon))
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
let playbackLayer = null
let measureLayer = null
let measureLine = null
let satelliteTileLayer = null
let vectorTileLayer = null
let currentBaseLayer = 'satellite'

function outOfChina(lon, lat) {
  return lon < 72.004 || lon > 137.8347 || lat < 0.8293 || lat > 55.8271
}

function transformLat(x, y) {
  let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x))
  ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0
  ret += (20.0 * Math.sin(y * Math.PI) + 40.0 * Math.sin(y / 3.0 * Math.PI)) * 2.0 / 3.0
  ret += (160.0 * Math.sin(y / 12.0 * Math.PI) + 320 * Math.sin(y * Math.PI / 30.0)) * 2.0 / 3.0
  return ret
}

function transformLon(x, y) {
  let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x))
  ret += (20.0 * Math.sin(6.0 * x * Math.PI) + 20.0 * Math.sin(2.0 * x * Math.PI)) * 2.0 / 3.0
  ret += (20.0 * Math.sin(x * Math.PI) + 40.0 * Math.sin(x / 3.0 * Math.PI)) * 2.0 / 3.0
  ret += (150.0 * Math.sin(x / 12.0 * Math.PI) + 300.0 * Math.sin(x / 30.0 * Math.PI)) * 2.0 / 3.0
  return ret
}

function wgs84ToGcj02(lon, lat) {
  const lng = Number(lon)
  const latNum = Number(lat)
  if (outOfChina(lng, latNum)) {
    return { lon: lng, lat: latNum }
  }

  const a = 6378245.0
  const ee = 0.00669342162296594323
  let dLat = transformLat(lng - 105.0, latNum - 35.0)
  let dLon = transformLon(lng - 105.0, latNum - 35.0)
  const radLat = (latNum / 180.0) * Math.PI
  let magic = Math.sin(radLat)
  magic = 1 - ee * magic * magic
  const sqrtMagic = Math.sqrt(magic)
  dLat = (dLat * 180.0) / (((a * (1 - ee)) / (magic * sqrtMagic)) * Math.PI)
  dLon = (dLon * 180.0) / ((a / sqrtMagic) * Math.cos(radLat) * Math.PI)
  return { lon: lng + dLon, lat: latNum + dLat }
}

function toMapPoint(point) {
  return wgs84ToGcj02(point.lon, point.lat)
}

function ensureMap() {
  if (map) return
  try {
    const container = document.getElementById('leaflet-map')
    if (!container) {
      console.warn('leaflet container not found, delaying init')
      return
    }
    map = L.map('leaflet-map', { zoomControl: true, preferCanvas: false })

    satelliteTileLayer = L.tileLayer('https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', {
      attribution: '',
      maxZoom: 18,
    })

    vectorTileLayer = L.tileLayer('https://webst01.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}', {
      attribution: '',
      maxZoom: 18,
    })

    satelliteTileLayer.addTo(map)
    currentBaseLayer = 'satellite'

    overlayLayer = L.layerGroup().addTo(map)
    playbackLayer = L.layerGroup().addTo(map)
    measureLayer = L.layerGroup().addTo(map)
    map.on('click', handleMeasureClick)
    map.on('contextmenu', handleMeasureUndo)

    addBaseMapToggle()
  } catch (e) {
    console.error('init leaflet failed', e)
  }
}

function addBaseMapToggle() {
  var ToggleControl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd: function () {
      var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control amod-basemap-toggle')

      var link = L.DomUtil.create('a', '', container)
      link.href = '#'
      link.title = '当前：卫星地图'

      var icon = L.DomUtil.create('span', 'amod-basemap-icon', link)
      icon.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/></svg>'

      function updateUI() {
        if (currentBaseLayer === 'satellite') {
          container.classList.add('amod-basemap-satellite')
          container.classList.remove('amod-basemap-vector')
          link.title = '当前：卫星地图 — 点击切换矢量地图'
        } else {
          container.classList.add('amod-basemap-vector')
          container.classList.remove('amod-basemap-satellite')
          link.title = '当前：矢量地图 — 点击切换卫星地图'
        }
      }

      L.DomEvent.disableClickPropagation(container)
      L.DomEvent.on(link, 'click', function (e) {
        L.DomEvent.preventDefault(e)
        if (currentBaseLayer === 'satellite') {
          map.removeLayer(satelliteTileLayer)
          vectorTileLayer.addTo(map)
          currentBaseLayer = 'vector'
        } else {
          map.removeLayer(vectorTileLayer)
          satelliteTileLayer.addTo(map)
          currentBaseLayer = 'satellite'
        }
        updateUI()
      })

      updateUI()
      return container
    },
  })
  new ToggleControl().addTo(map)
}

function ensurePlaybackLayer() {
  ensureMap()
  if (!map) return null
  if (!playbackLayer) {
    playbackLayer = L.layerGroup().addTo(map)
  }
  return playbackLayer
}

function updatePlaybackLayer(point) {
  const layer = ensurePlaybackLayer()
  if (!layer) return

  layer.clearLayers()
  // ensure points have mapPoint computed
  const trail = playbackTrailPoints.value.map((item) => ({
    ...item,
    mapPoint: item.mapPoint || toMapPoint(item),
  }))

  if (!point) return
  const current = { ...point, mapPoint: point.mapPoint || toMapPoint(point) }

  if (trail.length > 1) {
    const trailLatLngs = trail
      .filter((item) => item?.mapPoint)
      .map((item) => [Number(item.mapPoint.lat), Number(item.mapPoint.lon)])

    if (trailLatLngs.length > 1) {
      L.polyline(trailLatLngs, {
        color: '#d89b2b',
        weight: 5,
        opacity: 0.95,
      }).addTo(layer)
    }
  }

  // current marker
  L.circleMarker([Number(current.mapPoint.lat), Number(current.mapPoint.lon)], {
    radius: 8,
    color: '#ffffff',
    weight: 2,
    fillColor: '#d89b2b',
    fillOpacity: 1,
  }).addTo(layer)
}

function getMapLatLngFromEvent(event) {
  const original = event?.latlng || event?.target?.getLatLng?.()
  if (!original) return null
  const lat = Number(original.lat)
  const lon = Number(original.lng ?? original.lon)
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null
  return { lat, lon }
}

function formatMeasureDistance(distanceMeters) {
  if (!Number.isFinite(distanceMeters) || distanceMeters <= 0) {
    return '0 m'
  }
  if (distanceMeters >= 1000) {
    return `${(distanceMeters / 1000).toFixed(3)} km`
  }
  return `${distanceMeters.toFixed(1)} m`
}

const formattedMeasureDistance = computed(() => formatMeasureDistance(measureDistance.value))

function rebuildMeasureLayer() {
  if (!measureLayer) return
  measureLayer.clearLayers()

  const latlngs = measurePoints.value.map((point) => [point.lat, point.lon])
  if (latlngs.length > 1) {
    measureLine = L.polyline(latlngs, {
      color: '#f0a500',
      weight: 5,
      opacity: 0.95,
      lineCap: 'round',
      lineJoin: 'round',
      dashArray: '8 8',
    }).addTo(measureLayer)
  } else {
    measureLine = null
  }

  measurePoints.value.forEach((point, index) => {
    const marker = L.circleMarker([point.lat, point.lon], {
      radius: 7,
      color: '#ffffff',
      weight: 2,
      fillColor: '#f0a500',
      fillOpacity: 1,
    })
    marker.bindTooltip(`${index + 1}`, {
      permanent: true,
      direction: 'center',
      className: 'measure-label',
      offset: [0, 0],
    })
    marker.addTo(measureLayer)
  })
}

function recalcMeasureDistance() {
  let total = 0
  for (let i = 1; i < measurePoints.value.length; i += 1) {
    const prev = measurePoints.value[i - 1]
    const current = measurePoints.value[i]
    total += L.latLng(prev.lat, prev.lon).distanceTo(L.latLng(current.lat, current.lon))
  }
  measureDistance.value = total
}

function addMeasurePoint(lat, lon) {
  measurePoints.value = [...measurePoints.value, { lat: Number(lat), lon: Number(lon) }]
  recalcMeasureDistance()
  rebuildMeasureLayer()
}

function undoMeasurePoint() {
  if (!measurePoints.value.length) return
  measurePoints.value = measurePoints.value.slice(0, -1)
  recalcMeasureDistance()
  rebuildMeasureLayer()
}

function clearMeasure() {
  measurePoints.value = []
  measureDistance.value = 0
  measureLine = null
  if (measureLayer) {
    measureLayer.clearLayers()
  }
}

function startMeasureMode() {
  stopPlayback()
  isMeasuring.value = true
  ensureMap()
}

function stopMeasureMode() {
  isMeasuring.value = false
}

function toggleMeasureMode() {
  if (isMeasuring.value) {
    stopMeasureMode()
    return
  }
  startMeasureMode()
}

function handleMeasureClick(event) {
  if (!isMeasuring.value) return
  const latlng = getMapLatLngFromEvent(event)
  if (!latlng) return
  addMeasurePoint(latlng.lat, latlng.lon)
}

function handleMeasureUndo(event) {
  if (!isMeasuring.value) return
  if (event?.originalEvent?.preventDefault) {
    event.originalEvent.preventDefault()
  }
  undoMeasurePoint()
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

  const mapPoints = points.value.map((point) => ({
    ...point,
    mapPoint: toMapPoint(point),
  }))

  // add segments
  const segments = []
  let current = [mapPoints[0]]
  mapPoints.slice(1).forEach((p) => {
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
    const latlngs = seg.map((p) => [Number(p.mapPoint.lat), Number(p.mapPoint.lon)])
    const status = seg[0]?.workstatus
    const color = status === 0 ? 'rgba(132,138,146,0.9)' : 'rgba(104,223,58,0.95)'
    if (isPlaying.value) {
      // during playback show a faint full-track baseline; the real-time trail is drawn in playbackLayer
      L.polyline(latlngs, { color: '#c8d1c6', weight: 2, opacity: 0.12 }).addTo(overlayLayer)
    } else {
      L.polyline(latlngs, { color, weight: 4, opacity: 0.85 }).addTo(overlayLayer)
    }
  })

  // add points
  mapPoints.forEach((p) => {
    const marker = L.circleMarker([Number(p.mapPoint.lat), Number(p.mapPoint.lon)], {
      radius: 4,
      fillColor: p.workstatus === 0 ? '#8a8f98' : '#48e11e',
      color: '#fff',
      weight: 0.6,
      opacity: isPlaying.value ? 0.6 : 0.95,
      fillOpacity: isPlaying.value ? 0.4 : 0.95,
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
  ensureMap()
  if (points.value.length) {
    renderLeaflet()
  }
})

onBeforeUnmount(() => {
  try {
    stopPlayback()
    clearMeasure()
    if (map) {
      map.off('click', handleMeasureClick)
      map.off('contextmenu', handleMeasureUndo)
      map.remove()
      map = null
      overlayLayer = null
      playbackLayer = null
      measureLayer = null
      satelliteTileLayer = null
      vectorTileLayer = null
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
  updatePlaybackLayer(point)
}

function stopPlayback() {
  isPlaying.value = false
  playbackIndex.value = 0
  playbackTrailPoints.value = []
  if (playbackTimer.value) {
    clearInterval(playbackTimer.value)
    playbackTimer.value = null
  }
  if (playbackLayer) {
    playbackLayer.clearLayers()
  }
}

function startPlayback() {
  if (!points.value.length) {
    return
  }

  stopPlayback()
  isPlaying.value = true
  playbackIndex.value = 0
  playbackTrailPoints.value = []
  selectPoint(points.value[0])
  playbackTrailPoints.value = [points.value[0]]

  playbackTimer.value = setInterval(() => {
    if (!points.value.length) {
      stopPlayback()
      return
    }

    playbackIndex.value += 1
    if (playbackIndex.value >= points.value.length) {
      stopPlayback()
      return
    }

    const point = points.value[playbackIndex.value]
    playbackTrailPoints.value = points.value.slice(0, playbackIndex.value + 1)
    selectPoint(point)
    if (map && point?.mapPoint) {
      map.panTo([Number(point.mapPoint.lat), Number(point.mapPoint.lon)], { animate: true, duration: 0.1 })
    }
  }, 0.1)
}

function togglePlayback() {
  if (isPlaying.value) {
    stopPlayback()
    return
  }

  startPlayback()
}

function formatStatNumber(value, digits = 4) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '--'
  return num.toFixed(digits)
}

function formatPointValue(value) {
  if (value === null || value === undefined || value === '') return '--'
  const num = Number(value)
  return Number.isFinite(num) ? num : value
}

function calcAvgVelocityFromPoints(pointsList) {
  const values = pointsList
    .map((item) => Number(item.velocity))
    .filter((value) => Number.isFinite(value) && value !== 0)
  if (!values.length) return '--'
  return formatStatNumber(values.reduce((sum, value) => sum + value, 0) / values.length, 3)
}

function calcAvgDepthFromPoints(pointsList) {
  const values = pointsList
    .map((item) => Number(item.depth))
    .filter((value) => Number.isFinite(value) && value !== 0)
  if (!values.length) return '--'
  return formatStatNumber(values.reduce((sum, value) => sum + value, 0) / values.length, 2)
}

async function loadTrackData() {
  backgroundVisible.value = true
  stopPlayback()
  const id = trackId.value
  const [trackRes, pointsRes, rateRes, analysisRes] = await Promise.allSettled([
    request.get(`/api/track/${id}/`),
    request.get(`/api/track/${id}/trackpoints/`),
    request.get(`/api/rate/${id}/`),
    request.get(`/api/analysis/track/${id}/`, { params: { work_width: 2.0 } }),
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

  const rate = rateRes.status === 'fulfilled' ? unwrapObjectResponse(rateRes.value) || {} : {}

  // 优先使用分析API的精确计算结果
  if (analysisRes.status === 'fulfilled' && analysisRes.value?.code === '200') {
    const d = analysisRes.value.data
    workStat.worktime = d.total_time.formatted || '--'
    workStat.worklength = d.total_distance.kilometers !== undefined
      ? `${d.total_distance.kilometers} km`
      : '--'
    workStat.workarea = d.work_area.square_meters !== undefined
      ? `${d.work_area.square_meters}㎡ ≈${d.work_area.mu}亩`
      : '--'
    workStat.avgvelocity = d.average_velocity.km_per_h !== undefined
      ? `${d.average_velocity.km_per_h} km/h`
      : '--'
  } else {
    // 回退到旧 work 表
    workStat.worktime = '--'
    workStat.worklength = '--'
    workStat.workarea = '--'
    workStat.avgvelocity = calcAvgVelocityFromPoints(points.value)
  }

  if (rate.passrate !== undefined) {
    workStat.passrate = rate.passrate
  }
  // wait for DOM to render map container, then render overlays
  await nextTick()
  renderLeaflet()
  if (points.value.length) {
    updatePlaybackLayer(points.value[0])
  }
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

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.measure-tag {
  font-weight: 700;
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
  font-size: 22px;
  font-weight: 800;
  color: var(--amod-primary);
  white-space: nowrap;
}

.stat-sub {
  font-size: 14px;
  color: var(--amod-text-soft);
  margin-top: 4px;
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

.measure-tip {
  position: absolute;
  right: 16px;
  bottom: 16px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(240, 165, 0, 0.92);
  color: #fff;
  font-size: 12px;
  pointer-events: none;
  z-index: 500;
}

.measure-summary {
  position: absolute;
  right: 16px;
  top: 16px;
  min-width: 180px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.78);
  color: #fff;
  backdrop-filter: blur(6px);
  z-index: 500;
}

.measure-summary-title {
  font-weight: 700;
  margin-bottom: 6px;
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

:deep(.amod-basemap-toggle) {
  border: 2px solid rgba(0,0,0,0.12);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 5px rgba(0,0,0,0.15);
}

:deep(.amod-basemap-toggle a) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: #fff;
  color: #555;
  transition: all .15s ease;
}

:deep(.amod-basemap-toggle a:hover) {
  background: #f5f5f5;
  color: #333;
}

:deep(.amod-basemap-satellite a) {
  color: #555;
}

:deep(.amod-basemap-vector a) {
  color: #409eff;
}
</style>
