import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 直接根路径
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data || config.params)
    return config
  },
  error => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.data)
    return response
  },
  error => {
    console.error('Response Error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

export default api
