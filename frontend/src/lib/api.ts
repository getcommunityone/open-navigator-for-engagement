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

// Add request interceptor for auth token and HTTPS enforcement
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // CRITICAL FIX: Force HTTPS in production to prevent mixed content errors
    // Axios converts relative paths to absolute URLs using current protocol
    // We must intercept and force HTTPS if page is loaded over HTTPS
    if (typeof window !== 'undefined' && window.location.protocol === 'https:' && config.url) {
      // If axios has converted to absolute URL with http://, upgrade to https://
      if (config.url.startsWith('http://')) {
        config.url = config.url.replace('http://', 'https://')
        console.log('🔒 [API] Upgraded request to HTTPS:', config.url)
      }
      // If baseURL was converted to http://, upgrade it too
      if (config.baseURL && config.baseURL.startsWith('http://')) {
        config.baseURL = config.baseURL.replace('http://', 'https://')
        console.log('🔒 [API] Upgraded baseURL to HTTPS:', config.baseURL)
      }
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
