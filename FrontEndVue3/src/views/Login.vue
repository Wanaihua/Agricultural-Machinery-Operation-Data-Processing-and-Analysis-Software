<template>
  <div class="login-page">
    <div class="login-card amod-card">
      <div class="hero-panel">
        <div class="hero-badge">Vue3 + Element Plus + Leaflet</div>
        <h1>农机作业数据管理系统</h1>
        <p>轨迹分析、导入日志、用户权限和地图监控统一管理。</p>
      </div>

      <div class="form-panel">
        <div class="form-title">欢迎登录</div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="login-form">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" size="large" />
          </el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="handleLogin">登录</el-button>
          <div class="extra-link">
            <span>没有账号？</span>
            <el-link type="primary" @click="router.push('/register')">去注册</el-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res = await request.post('/user/login', form)
    if (res?.code === '200' || res?.code === 200) {
      localStorage.setItem('user', JSON.stringify(res.data || {}))
      localStorage.setItem('menus', JSON.stringify(res.data?.menus || []))
      if (res.data?.token) {
        localStorage.setItem('token', res.data.token)
      }
      ElMessage.success('登录成功')
      router.push('/home')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 20% 20%, rgba(47, 111, 78, 0.18), transparent 24%),
    radial-gradient(circle at 80% 12%, rgba(216, 155, 43, 0.2), transparent 22%),
    linear-gradient(135deg, #eaf2e8 0%, #f6f4ea 45%, #eef5f1 100%);
}

.login-card {
  width: min(1080px, 100%);
  min-height: 620px;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  overflow: hidden;
}

.hero-panel {
  padding: 56px;
  color: #fff;
  background:
    linear-gradient(160deg, rgba(17, 46, 34, 0.92), rgba(30, 93, 64, 0.86)),
    url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1400&q=80') center/cover;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  padding: 8px 14px;
  margin-bottom: 28px;
  background: rgba(255, 255, 255, 0.08);
}

.hero-panel h1 {
  margin: 0;
  font-size: 42px;
  line-height: 1.2;
}

.hero-panel p {
  max-width: 520px;
  margin-top: 18px;
  color: rgba(255, 255, 255, 0.82);
  font-size: 16px;
  line-height: 1.8;
}

.form-panel {
  padding: 56px 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.88);
}

.form-title {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 28px;
}

.login-form {
  width: 100%;
}

.submit-btn {
  width: 100%;
  height: 46px;
  margin-top: 8px;
  border-radius: 12px;
}

.extra-link {
  margin-top: 18px;
  display: flex;
  gap: 6px;
  justify-content: center;
  color: var(--amod-text-soft);
}

@media (max-width: 900px) {
  .login-card {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    min-height: 280px;
  }
}
</style>
