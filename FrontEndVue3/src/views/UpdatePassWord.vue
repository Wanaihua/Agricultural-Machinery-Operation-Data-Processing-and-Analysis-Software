<template>
  <div class="amod-page update-password-page">
    <el-card class="amod-card" shadow="never">
      <template #header>
        <div class="card-title">修改密码</div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px" class="password-form">
        <el-form-item label="原密码" prop="oldPass">
          <el-input v-model="form.oldPass" type="password" show-password autocomplete="off" />
        </el-form-item>
        <el-form-item label="新密码" prop="pass">
          <el-input v-model="form.pass" type="password" show-password autocomplete="off" />
        </el-form-item>
        <el-form-item label="确认密码" prop="checkPass">
          <el-input v-model="form.checkPass" type="password" show-password autocomplete="off" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref()
const user = JSON.parse(localStorage.getItem('user') || '{}')

const form = reactive({
  oldPass: '',
  pass: '',
  checkPass: '',
})

const validatePass = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'))
    return
  }
  if (form.checkPass) {
    formRef.value?.validateField('checkPass')
  }
  callback()
}

const validatePass2 = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
    return
  }
  if (value !== form.pass) {
    callback(new Error('两次输入密码不一致'))
    return
  }
  callback()
}

const rules = {
  oldPass: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  pass: [{ validator: validatePass, trigger: 'blur' }],
  checkPass: [{ validator: validatePass2, trigger: 'blur' }],
}

async function submitForm() {
  await formRef.value?.validate(async (valid) => {
    if (!valid) return

    const res = await request.post('/user/updatePassword', {
      username: user.username,
      oldPassword: form.oldPass,
      newPassword: form.pass,
    })

    if (res?.code === '200') {
      ElMessage.success('密码修改成功，请重新登录')
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('menus')
      await router.push('/login')
      return
    }

    ElMessage.error(res?.msg || '修改失败')
  })
}

function resetForm() {
  formRef.value?.resetFields()
}
</script>

<style scoped>
.update-password-page {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
}

.amod-card {
  width: 420px;
  min-height: 420px;
  margin-left: 8px;
}

.password-form {
  width: 100%;
  padding-top: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
}

.password-form :deep(.el-form-item__label) {
  text-align: left;
}
</style>
