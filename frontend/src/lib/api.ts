import axios from 'axios'

// Environment-aware API base URL
// In development: API on localhost:8000/api
// In production (HF Spaces): Served via nginx at /api/
let API_BASE_URL: string

// Determine the correct API base URL
if (import.meta.env.PROD) {
  // Production: ALWAYS use relative path to inherit protocol from page
  // This prevents mixed content errors - if page is HTTPS, API calls will be HTTPS
  API_BASE_URL = '/api'
  console.log('🌐 [API] Production mode: Using relative path (inherits protocol from page):', API_BASE_URL)
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
    
    // BULLETPROOF HTTPS ENFORCEMENT: Never allow HTTP requests in production
    // This catches ANY case where HTTP might sneak in (cached URLs, env vars, etc.)
    if (import.meta.env.PROD && typeof window !== 'undefined') {
      // Force HTTPS on the final request URL
      if (config.url && config.url.startsWith('http://')) {
        config.url = config.url.replace('http://', 'https://')
        console.warn('🔒 [API] FORCED HTTP→HTTPS upgrade on URL:', config.url)
      }
      
      // Force HTTPS on baseURL if it somehow got set to HTTP
      if (config.baseURL && config.baseURL.startsWith('http://')) {
        config.baseURL = config.baseURL.replace('http://', 'https://')
        console.warn('🔒 [API] FORCED HTTP→HTTPS upgrade on baseURL:', config.baseURL)
      }
      
      // If page is HTTPS and we're making a relative request, ensure it stays HTTPS
      if (window.location.protocol === 'https:') {
        // Build the absolute URL to check
        const absoluteURL = new URL(config.url || '', config.baseURL || window.location.origin)
        if (absoluteURL.protocol === 'http:') {
          absoluteURL.protocol = 'https:'
          config.url = absoluteURL.href
          console.warn('🔒 [API] FORCED HTTP→HTTPS upgrade on final URL:', config.url)
        }
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
