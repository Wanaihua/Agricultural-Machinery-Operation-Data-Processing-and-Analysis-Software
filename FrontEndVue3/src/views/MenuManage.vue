<template>
  <div class="amod-page crud-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">菜单管理</div>
        <div class="amod-subtitle">维护侧边栏菜单与父子层级关系</div>
      </div>
      <div class="action-group">
        <el-input v-model="keyword" placeholder="搜索菜单名" clearable class="search-input" />
        <el-button type="primary" @click="openCreate">新增菜单</el-button>
      </div>
    </div>

    <el-card class="amod-card" shadow="never">
      <el-table :data="pagedMenus" border stripe row-key="id">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="path" label="路径" min-width="140" />
        <el-table-column label="图标" width="110">
          <template #default="scope">
            <component :is="resolveIcon(scope.row.icon)" class="menu-icon" />
            <span class="icon-label">{{ scope.row.icon }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column label="父级" min-width="120">
          <template #default="scope">{{ parentName(scope.row.pid) }}</template>
        </el-table-column>
        <el-table-column prop="page_path" label="页面路径" min-width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" @click="removeMenu(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager-wrap">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredMenus.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑菜单' : '新增菜单'" width="620px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="路径" prop="path">
          <el-input v-model="form.path" placeholder="例如 /track/list" />
        </el-form-item>
        <el-form-item label="页面路径" prop="page_path">
          <el-input v-model="form.page_path" placeholder="例如 TrackList" />
        </el-form-item>
        <el-form-item label="父级菜单" prop="pid">
          <el-select v-model="form.pid" clearable placeholder="无父级" style="width: 100%">
            <el-option label="无父级" :value="null" />
            <el-option v-for="item in menus" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-select v-model="form.icon" placeholder="请选择图标" style="width: 100%">
            <el-option v-for="item in iconOptions" :key="item.value" :label="item.name" :value="item.value">
              <component :is="resolveIcon(item.value)" class="menu-icon" />
              <span class="icon-label">{{ item.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataLine,
  Document,
  Files,
  House,
  Location,
  Menu,
  Setting,
  Tickets,
  User,
  UploadFilled,
} from '@element-plus/icons-vue'
import request from '@/utils/request'
import { unwrapListResponse } from '@/utils/response'

const menus = ref([])
const dictIcons = ref([])
const keyword = ref('')
const page = reactive({ current: 1, size: 10 })
const dialogVisible = ref(false)
const saving = ref(false)
const formRef = ref()
const form = reactive({ id: null, name: '', path: '', page_path: '', icon: '', description: '', pid: null })

const rules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
}

const iconOptions = computed(() => {
  return dictIcons.value.length
    ? dictIcons.value
    : [
        { name: '主页', value: 'el-icon-house' },
        { name: '用户', value: 'el-icon-user' },
        { name: '菜单', value: 'el-icon-menu' },
        { name: '文件', value: 'el-icon-document' },
        { name: '数据导入', value: 'el-icon-upload' },
      ]
})

const filteredMenus = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  if (!text) return menus.value
  return menus.value.filter((item) => String(item.name || '').toLowerCase().includes(text))
})

const pagedMenus = computed(() => {
  const start = (page.current - 1) * page.size
  return filteredMenus.value.slice(start, start + page.size)
})

function resetForm() {
  form.id = null
  form.name = ''
  form.path = ''
  form.page_path = ''
  form.icon = ''
  form.description = ''
  form.pid = null
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  form.id = row.id
  form.name = row.name || ''
  form.path = row.path || ''
  form.page_path = row.page_path || row.pagePath || ''
  form.icon = row.icon || ''
  form.description = row.description || ''
  form.pid = row.pid || null
  dialogVisible.value = true
}

async function loadData() {
  const [menuRes, dictRes] = await Promise.all([request.get('/api/menu/'), request.get('/api/dict/')])
  menus.value = unwrapListResponse(menuRes)
  dictIcons.value = unwrapListResponse(dictRes).filter((item) => item.type === 'icon')
}

function parentName(pid) {
  if (!pid) return '无'
  const parent = menus.value.find((item) => item.id === pid || item.id === pid?.id)
  return parent?.name || pid
}

function resolveIcon(icon) {
  const iconMap = {
    'el-icon-house': House,
    'el-icon-user': User,
    'el-icon-menu': Menu,
    'el-icon-document': Document,
    'el-icon-s-custom': User,
    'el-icon-s-grid': Files,
    'el-icon-s-shop': Files,
    'el-icon-position': Location,
    'el-icon-bank-card': DataLine,
    'el-icon-ticket': Tickets,
    'el-icon-setting': Setting,
    'el-icon-upload': UploadFilled,
    'el-icon-data-analysis': DataLine,
  }
  return iconMap[icon] || Menu
}

async function submitForm() {
  await formRef.value?.validate()
  saving.value = true
  try {
    const payload = {
      name: form.name,
      path: form.path,
      page_path: form.page_path,
      icon: form.icon,
      description: form.description,
      pid: form.pid,
    }

    if (form.id) {
      await request.put(`/api/menu/${form.id}/`, payload)
      ElMessage.success('菜单已更新')
    } else {
      await request.post('/api/menu/', payload)
      ElMessage.success('菜单已创建')
    }

    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function removeMenu(id) {
  await ElMessageBox.confirm('确定删除该菜单吗？', '提示', { type: 'warning' })
  await request.delete(`/api/menu/${id}/`)
  ElMessage.success('删除成功')
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.crud-page {
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

.action-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.pager-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}

.menu-icon {
  width: 1em;
  height: 1em;
  margin-right: 6px;
}

.icon-label {
  margin-left: 4px;
}
</style>
