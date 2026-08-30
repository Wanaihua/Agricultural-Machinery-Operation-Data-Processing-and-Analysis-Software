<template>
  <div class="amod-page crud-page">
    <div class="page-head">
      <div>
        <div class="amod-page-title">用户管理</div>
      </div>
    </div>

    <div class="toolbar-row">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="用户名">
          <el-input v-model="filters.username" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="filters.email" clearable />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="filters.address" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button class="ml-10" type="primary" @click="openCreate">新增</el-button>
          <el-button type="danger" @click="deleteBatch">批量删除</el-button>
        </el-form-item>
      </el-form>

    </div>

    <el-card class="amod-card table-card" shadow="never">
      <el-table
        :data="pagedUsers"
        border
        stripe
        class="user-table"
        empty-text="暂无用户数据"
        :header-cell-class-name="headerBg"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="电话" min-width="140" />
        <el-table-column prop="address" label="地址" min-width="180" />
        <el-table-column label="角色" min-width="120">
          <template #default="scope">{{ roleName(scope.row.role) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button text type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-button text type="danger" @click="removeUser(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pager-wrap">
        <el-pagination
          v-model:current-page="page.current"
          v-model:page-size="page.size"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredUsers.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用户' : '新增用户'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" class="w-full">
            <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
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
import request from '@/utils/request'
import { unwrapListResponse } from '@/utils/response'

const users = ref([])
const roles = ref([])
const keyword = ref('')
const filters = reactive({ username: '', email: '', address: '' })
const selection = ref([])
const page = reactive({ current: 1, size: 10 })
const dialogVisible = ref(false)
const saving = ref(false)
const formRef = ref()
const form = reactive({ id: null, username: '', password: '', nickname: '', email: '', phone: '', address: '', role: null })
const headerBg = 'headerBg'

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  // password required only on create; on edit allow empty to keep existing password
  password: [
    { validator: (rule, value, callback) => {
        if (!form.id && !value) callback(new Error('请输入密码'))
        else callback()
      }, trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const roleMap = computed(() => {
  return roles.value.reduce((map, item) => {
    map[item.id] = item.name
    return map
  }, {})
})

const filteredUsers = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  return users.value.filter((item) => {
    if (text) {
      const matched = [item.username, item.nickname, item.email].some((value) => String(value || '').toLowerCase().includes(text))
      if (!matched) return false
    }
    if (filters.username && !String(item.username || '').toLowerCase().includes(String(filters.username).toLowerCase())) return false
    if (filters.email && !String(item.email || '').toLowerCase().includes(String(filters.email).toLowerCase())) return false
    if (filters.address && !String(item.address || '').toLowerCase().includes(String(filters.address).toLowerCase())) return false
    return true
  })
})

const pagedUsers = computed(() => {
  const start = (page.current - 1) * page.size
  return filteredUsers.value.slice(start, start + page.size)
})

function roleName(roleValue) {
  if (typeof roleValue === 'object' && roleValue) {
    return roleValue.name || roleValue.id || '--'
  }
  return roleMap.value[roleValue] || roleValue || '--'
}

function resetForm() {
  form.id = null
  form.username = ''
  form.password = ''
  form.nickname = ''
  form.email = ''
  form.phone = ''
  form.address = ''
  form.role = null
}

function applyFilters() {
  page.current = 1
}

function applyKeyword() {
  page.current = 1
}

function clearKeyword() {
  keyword.value = ''
  page.current = 1
}

function resetFilters() {
  filters.username = ''
  filters.email = ''
  filters.address = ''
  page.current = 1
}

function handleSelectionChange(val) {
  selection.value = val
}

function deleteBatch() {
  if (!selection.value || selection.value.length === 0) {
    ElMessage.warning('请至少选择一条数据')
    return
  }
  ElMessageBox.confirm('确定要删除选中的用户吗？', '提示', { type: 'warning' }).then(async () => {
  const ids = selection.value.map((r) => r.id)
  await request.post('/user/deleteBatch', ids).catch(() => {})
    ElMessage.success('删除成功')
    await loadData()
  }).catch(() => {})
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  form.id = row.id
  form.username = row.username || ''
  // do NOT pre-fill password for security
  form.password = ''
  form.nickname = row.nickname || ''
  form.email = row.email || ''
  form.phone = row.phone || ''
  form.address = row.address || ''
  form.role = typeof row.role === 'object' ? row.role?.id || null : row.role || null
  dialogVisible.value = true
}

async function loadData() {
  // use legacy endpoints to ensure roles/menu come from same source as login
  const [userRes, roleRes] = await Promise.all([request.get('/api/user/'), request.get('/role')])
  users.value = unwrapListResponse(userRes)
  roles.value = unwrapListResponse(roleRes)
}

async function submitForm() {
  await formRef.value?.validate()
  saving.value = true
  try {
    const payload = {
      username: form.username,
      nickname: form.nickname,
      email: form.email,
      phone: form.phone,
      address: form.address,
      role: form.role,
    }
    // include password only when provided (create or explicit change)
    if (form.password) payload.password = form.password

    if (form.id) {
      await request.put(`/api/user/${form.id}/`, payload)
      ElMessage.success('用户已更新')
    } else {
      // for create ensure password is present (validated earlier)
      await request.post('/api/user/', { ...payload, password: form.password })
      ElMessage.success('用户已创建')
    }

    dialogVisible.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function removeUser(id) {
  await ElMessageBox.confirm('确定删除该用户吗？', '提示', { type: 'warning' })
  await request.delete(`/api/user/${id}/`)
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

.search-input {
  width: 240px;
}

.toolbar-row {
  padding: 12px 0 4px;
}

.table-card {
  padding-top: 4px;
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-form :deep(.el-form-item__label) {
  color: #1f2937;
  font-weight: 500;
}

.user-table :deep(.headerBg) {
  background: #f3f6f1 !important;
  color: #2f6f4e;
  font-weight: 700;
}

.user-table :deep(.el-table__header-wrapper th) {
  height: 46px;
}

.user-table :deep(.el-table__body td) {
  padding-top: 12px;
  padding-bottom: 12px;
}

.user-table :deep(.el-table__row:hover > td) {
  background: #f8fbf6 !important;
}

.pager-wrap {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
}
</style>
