import axios from 'axios'

// Environment-aware API base URL
// In development: API on localhost:8000/api
// In production (HF Spaces): Served via nginx at /api/
let API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://localhost:8000/api' : '/api')

// Fix mixed content: Force HTTPS if page is HTTPS and URL starts with http://
if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
  if (API_BASE_URL.startsWith('http://')) {
    API_BASE_URL = API_BASE_URL.replace('http://', 'https://')
    console.log('🔒 [API] Upgraded HTTP to HTTPS for mixed content security:', API_BASE_URL)
  }
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for auth token if needed
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - could clear token and redirect to login
      localStorage.removeItem('auth_token')
    }
    return Promise.reject(error)
  }
)

export default api
