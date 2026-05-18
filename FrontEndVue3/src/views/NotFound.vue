<template>
  <div class="notfound-page">
    <el-result icon="warning" title="404" sub-title="页面不存在或无权限访问">
      <template #extra>
        <el-button type="primary" @click="$router.push('/home')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.notfound-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #edf3eb 0%, #f8f7ef 100%);
}
</style>
