import axios from 'axios'

// Environment-aware API base URL
// In development: API on localhost:8000/api
// In production (HF Spaces): Served via nginx at /api/
let API_BASE_URL: string

// Determine the correct API base URL
if (import.meta.env.PROD) {
  // Production: Use protocol-relative or HTTPS-forced URL
  if (typeof window !== 'undefined') {
    // Force HTTPS in production
    API_BASE_URL = `${window.location.protocol}//${window.location.host}/api`
    console.log('🌐 [API] Production mode: Using same-origin HTTPS URL:', API_BASE_URL)
  } else {
    // SSR fallback
    API_BASE_URL = '/api'
    console.log('🌐 [API] Production mode (SSR): Using relative path /api')
  }
} else {
  // Development: Use environment variable or default to localhost
  API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  console.log('🔧 [API] Development mode: Using', API_BASE_URL)
}

console.log('📡 [API] Final base URL:', API_BASE_URL)

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
