import axios, { type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { useUserStore } from '@/stores/user'

const request = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL as string) || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 需要统一响应格式的接口路径（这些接口返回 { code, data, message }）
const NEED_WRAPPED_PATHS = ['/api/student', '/api/admin', '/api/interviewer']

// 不需要统一响应格式的接口路径（直接返回数据）
const DIRECT_RETURN_PATHS = ['/api/admin/signup/applications', '/api/admin/dashboard', '/api/admin/clubs', '/api/interviewer/invitations', '/api/interviewer/signup/applications', '/api/interview/my-tasks', '/api/interview/sessions', '/api/interview/clubs', '/api/score-templates']

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data, config } = response
    const url = (config.url || '')

    // 判断是否直接返回数据（不需要统一格式处理）
    const isDirectReturn = DIRECT_RETURN_PATHS.some(path => url.startsWith(path))
    if (isDirectReturn) {
      return data
    }

    // 判断是否需要统一响应格式处理
    const needsWrapped = NEED_WRAPPED_PATHS.some(path => url.startsWith(path))

    if (needsWrapped) {
      // 如果返回的是数组，直接返回（兼容某些接口直接返回数组）
      if (Array.isArray(data)) {
        return data
      }
      // 统一响应格式: { code: 200, data: xxx, message: "" }
      if (data.code === 200 || data.success) {
        return data.data || data
      }
      return Promise.reject(new Error(data.message || '请求失败'))
    }

    // 直接返回原始数据（如 /auth/* 接口）
    return data
  },
  (error: AxiosError) => {
    const { response } = error
    if (response) {
      // 尝试从响应体获取 detail 字段
      const errorData = response.data as any
      const errorDetail = errorData?.detail

      // FastAPI 422 错误是数组格式，需要特殊处理
      let errorMessage = ''
      if (response.status === 422 && Array.isArray(errorDetail)) {
        // 提取所有验证错误
        errorMessage = errorDetail.map((item: any) => {
          const loc = item.loc?.join('.') || '未知字段'
          return `${loc}: ${item.msg}`
        }).join('; ')
      } else {
        errorMessage = errorDetail || errorData?.message || '请求失败'
      }

      switch (response.status) {
        case 401:
          const userStore = useUserStore()
          userStore.logout()
          window.location.href = '/login'
          return Promise.reject(new Error('登录已过期，请重新登录'))
        case 403:
          return Promise.reject(new Error('没有权限访问'))
        case 404:
          return Promise.reject(new Error('请求的资源不存在'))
        case 422:
          return Promise.reject(new Error(errorMessage || '参数验证失败'))
        case 500:
          return Promise.reject(new Error(errorMessage || '服务器错误'))
        default:
          return Promise.reject(new Error(errorMessage || '请求失败'))
      }
    }
    return Promise.reject(new Error('网络连接异常'))
  }
)

export default request

// 封装 GET 请求
export function get<T = any>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
  return request.get(url, { params, ...config })
}

// 封装 POST 请求
export function post<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
  return request.post(url, data, config)
}

// 封装 PUT 请求
export function put<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
  return request.put(url, data, config)
}

// 封装 DELETE 请求
export function del<T = any>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
  return request.delete(url, { params, ...config })
}
