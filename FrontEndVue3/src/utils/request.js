import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 15000,
})

request.interceptors.request.use(
  (config) => {
    config.headers = config.headers || {}
    config.headers['Content-Type'] = 'application/json;charset=utf-8'

    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const token = user.token || localStorage.getItem('token')
    if (token) {
      config.headers.token = token
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error),
)

request.interceptors.response.use(
  (response) => {
    const res = response.data

    if (response.config.responseType === 'blob') {
      return res
    }

    if (typeof res === 'string') {
      try {
        return res ? JSON.parse(res) : res
      } catch (error) {
        return res
      }
    }

    if (res && typeof res === 'object' && 'code' in res && res.code !== '200') {
      ElMessage.error(res.msg || '请求失败')
    }

    return res
  },
  (error) => {
    const message = error?.response?.data?.msg || error.message || '网络请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export default request
