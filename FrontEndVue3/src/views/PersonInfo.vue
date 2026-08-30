<template>
  <div class="amod-page person-info-page">
    <el-card class="amod-card" shadow="never">
      <template #header>
        <div class="card-title">个人信息</div>
      </template>

      <el-form ref="formRef" :model="form" label-width="96px" class="person-form">
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="/file/upload"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            accept="image/*"
          >
            <img v-if="form.avatarUrl" :src="form.avatarUrl" class="avatar" />
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>

        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="off" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" autocomplete="off" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" autocomplete="off" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" autocomplete="off" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" autocomplete="off" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="save">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const formRef = ref(null)
const user = JSON.parse(localStorage.getItem('user') || '{}')
const form = ref({ id: null, username: '', nickname: '', phone: '', email: '', address: '', avatarUrl: '' })

async function loadUser() {
  try {
    const res = await request.get(`/user/username/${user.username}`)
    const data = res?.data || {}
    form.value = {
      id: data.id,
      username: data.username || user.username,
      nickname: data.nickname || '',
      phone: data.phone || '',
      email: data.email || '',
      address: data.address || '',
      avatarUrl: data.avatarUrl || '',
    }
  } catch (error) {
    console.error(error)
  }
}

function handleAvatarSuccess(resp) {
  const url = resp?.data || resp || ''
  form.value.avatarUrl = typeof url === 'string' ? url : url.url || url.path || ''
}

async function save() {
  try {
    const res = await request.post('/user', form.value)
    if (res && res.code === '200') {
      ElMessage.success('保存成功')
      const cached = JSON.parse(localStorage.getItem('user') || '{}')
      localStorage.setItem('user', JSON.stringify({ ...cached, ...form.value }))
      window.dispatchEvent(new Event('menus-updated'))
      return
    }
    ElMessage.error(res?.msg || '保存失败')
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  }
}

onMounted(loadUser)
</script>

<style scoped>
.person-info-page {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
}

.amod-card {
  width: 420px;
  min-height: 420px;
  margin-left: 8px;
}

.person-form {
  width: 100%;
}

.avatar-uploader {
  text-align: left;
  padding-bottom: 10px;
}

.avatar-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  width: 144px;
  height: 144px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #fff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.avatar {
  width: 144px;
  height: 144px;
  object-fit: cover;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
}

.person-form :deep(.el-form-item__label) {
  text-align: left;
}
</style>