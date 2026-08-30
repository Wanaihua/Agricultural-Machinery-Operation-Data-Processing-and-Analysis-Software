<template>
  <div class="amod-page crud-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">角色管理</div>
      </div>
    </div>

    <div class="toolbar-row">
      <div class="action-group">
        <el-input v-model="keyword" placeholder="搜索角色名" clearable class="search-input" />
        <el-button type="primary" @click="openCreate">新增角色</el-button>
      </div>
    </div>

    <el-card class="amod-card table-card" shadow="never">
      <el-table :data="pagedRoles" border stripe class="amod-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" min-width="140" />
        <el-table-column prop="flag" label="标识" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="220" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openPermission(scope.row)">分配菜单</el-button>
            <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-button link type="danger" @click="removeRole(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager-wrap">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredRoles.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑角色' : '新增角色'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="标识" prop="flag">
          <el-input v-model="form.flag" placeholder="例如：admin、user" />
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

      <el-dialog v-model="permissionVisible" title="菜单权限分配" width="640px" destroy-on-close>
      <el-tree
        :key="permissionTreeKey"
        ref="treeRef"
        :data="menuTree"
        node-key="id"
        show-checkbox
        :default-expanded-keys="expandedKeys"
        :props="treeProps"
      />

      <template #footer>
        <el-button @click="permissionVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPermission" @click="savePermissions">保存权限</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { unwrapListResponse } from '@/utils/response'

const roles = ref([])
const keyword = ref('')
const page = reactive({ current: 1, size: 10 })
const dialogVisible = ref(false)
const permissionVisible = ref(false)
const saving = ref(false)
const savingPermission = ref(false)
const formRef = ref()
const treeRef = ref()
const menuTree = ref([])
const checkedKeys = ref([])
const expandedKeys = ref([])
const currentRoleId = ref(null)
const permissionTreeKey = ref(0)

const treeProps = { children: 'children', label: 'name' }
const form = reactive({ id: null, name: '', flag: '', description: '' })
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  flag: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
}

const filteredRoles = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  if (!text) return roles.value
  return roles.value.filter((item) => String(item.name || '').toLowerCase().includes(text))
})

const pagedRoles = computed(() => {
  const start = (page.current - 1) * page.size
  return filteredRoles.value.slice(start, start + page.size)
})

function resetForm() {
  form.id = null
  form.name = ''
  form.flag = ''
  form.description = ''
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  form.id = row.id
  form.name = row.name || ''
  form.flag = row.flag || ''
  form.description = row.description || ''
  dialogVisible.value = true
}

async function loadRoles() {
  const res = await request.get('/api/role/')
  roles.value = unwrapListResponse(res)
}

async function loadMenuTree() {
  const res = await request.get('/api/menu/')
  const flatMenus = unwrapListResponse(res)
  menuTree.value = buildMenuTree(flatMenus)
  expandedKeys.value = flattenTreeIds(menuTree.value)
}

function buildMenuTree(items = []) {
  const map = new Map()
  const roots = []

  items.forEach((item) => {
    map.set(item.id, { ...item, children: [] })
  })

  map.forEach((node) => {
    const pid = node.pid && typeof node.pid === 'object' ? node.pid.id : node.pid
    if (pid && map.has(pid)) {
      map.get(pid).children.push(node)
    } else {
      roots.push(node)
    }
  })

  return roots
}

function flattenTreeIds(tree = []) {
  const ids = []
  const walk = (items) => {
    items.forEach((item) => {
      ids.push(item.id)
      if (Array.isArray(item.children) && item.children.length) {
        walk(item.children)
      }
    })
  }
  walk(tree)
  return ids.map((item) => String(item))
}

async function submitForm() {
  await formRef.value?.validate()
  saving.value = true
  try {
    const payload = {
      name: form.name,
      flag: form.flag,
      description: form.description,
    }

    if (form.id) {
      await request.put(`/api/role/${form.id}/`, payload)
      ElMessage.success('角色已更新')
    } else {
      await request.post('/api/role/', payload)
      ElMessage.success('角色已创建')
    }

    dialogVisible.value = false
    await loadRoles()
  } finally {
    saving.value = false
  }
}

async function removeRole(id) {
  await ElMessageBox.confirm('确定删除该角色吗？', '提示', { type: 'warning' })
  await request.delete(`/api/role/${id}/`)
  ElMessage.success('删除成功')
  await loadRoles()
}

async function openPermission(row) {
  currentRoleId.value = row.id
  checkedKeys.value = []
  expandedKeys.value = []
  permissionTreeKey.value += 1
  permissionVisible.value = true
  await loadMenuTree()

  const res = await request.get(`/role/roleMenu/${row.id}`)
  const selectedIds = (Array.isArray(res.data) ? res.data : unwrapListResponse(res))
    .map((item) => Number(item))
    .filter((item) => Number.isFinite(item))
  checkedKeys.value = selectedIds.map((item) => String(item))
  await nextTick()
  treeRef.value?.setCheckedKeys(selectedIds)
}

async function savePermissions() {
  savingPermission.value = true
  try {
    const keys = Array.from(new Set((treeRef.value?.getCheckedKeys(false) || [])
      .map((item) => Number(item))
      .filter((item) => Number.isFinite(item))))
    await request.post(`/role/roleMenu/${currentRoleId.value}`, keys)
    ElMessage.success('权限已保存')
    permissionVisible.value = false
    await refreshCurrentUserMenus()
  } finally {
    savingPermission.value = false
  }
}

async function refreshCurrentUserMenus() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const currentRoleKey = String(user.role?.flag || user.role?.name || user.role || '').toLowerCase()
  if (!currentRoleKey) {
    return
  }

  const roleRes = await request.get('/api/role/')
  const rolesList = unwrapListResponse(roleRes)
  const currentRole = rolesList.find((item) => String(item.flag || item.name || '').toLowerCase() === currentRoleKey)
  if (!currentRole || String(currentRole.id) !== String(currentRoleId.value)) {
    return
  }

  const [menuRes, roleMenuRes] = await Promise.all([
    request.get('/api/menu/'),
    request.get(`/role/roleMenu/${currentRole.id}`),
  ])
  const allMenus = unwrapListResponse(menuRes)
  const selectedIds = new Set((Array.isArray(roleMenuRes.data) ? roleMenuRes.data : unwrapListResponse(roleMenuRes)).map((item) => Number(item)))
  const menuMap = new Map(allMenus.map((item) => [Number(item.id), item]))
  const visibleIds = new Set()

  function includeAncestors(menuId) {
    const numericId = Number(menuId)
    if (!numericId || visibleIds.has(numericId)) {
      return
    }
    const menu = menuMap.get(numericId)
    if (!menu) {
      return
    }
    visibleIds.add(numericId)
    const pid = menu.pid && typeof menu.pid === 'object' ? menu.pid.id : menu.pid
    if (pid) {
      includeAncestors(pid)
    }
  }

  selectedIds.forEach((menuId) => includeAncestors(menuId))
  const visibleMenus = allMenus.filter((item) => visibleIds.has(Number(item.id)))
  localStorage.setItem('menus', JSON.stringify(buildMenuTree(visibleMenus)))
  window.dispatchEvent(new Event('menus-updated'))
}

onMounted(loadRoles)
</script>

<style scoped>
</style>
