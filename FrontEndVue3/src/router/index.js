import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { hasRoutePermission } from '@/utils/menu'

const MainLayout = () => import('@/layouts/MainLayout.vue')

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { public: true } },
  { path: '/404', name: 'NotFound', component: () => import('@/views/NotFound.vue'), meta: { public: true } },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/home' },
      { path: 'track', redirect: 'track/list' },
      { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
      { path: 'track/list', name: 'TrackList', component: () => import('@/views/TrackList.vue') },
      { path: 'track/map/:id', name: 'TrackMap', component: () => import('@/views/TrackMap.vue'), props: true },
      { path: 'data/import', name: 'DataImport', component: () => import('@/views/DataImport.vue') },
      { path: 'user', name: 'UserManage', component: () => import('@/views/UserManage.vue') },
      { path: 'role', name: 'RoleManage', component: () => import('@/views/RoleManage.vue') },
      { path: 'menu', name: 'MenuManage', component: () => import('@/views/MenuManage.vue') },
      { path: 'file', name: 'FileManage', component: () => import('@/views/File.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  localStorage.setItem('currentPathName', to.name || '')

  if (to.meta.public) {
    next()
    return
  }

  const user = localStorage.getItem('user')
  if (!user) {
    next('/login')
    return
  }

  if (!hasRoutePermission(to.path)) {
    ElMessage.warning('当前账号没有访问该页面的权限')
    next('/404')
    return
  }

  next()
})

export default router
