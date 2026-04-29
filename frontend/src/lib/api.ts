import axios from 'axios'

// Environment-aware API base URL
// In development: API on localhost:8000/api
// In production (HF Spaces): Served via nginx at /api/
let API_BASE_URL: string

// Determine the correct API base URL
if (import.meta.env.PROD) {
  // Production: ALWAYS use relative path - IGNORE all environment variables
  // This prevents HuggingFace Spaces build secrets from injecting HTTP URLs
  API_BASE_URL = '/api'
  console.log('🌐 [API] Production mode: HARDCODED relative path:', API_BASE_URL)
} else {
  // Development: Use environment variable or default to localhost
  const envUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  // Even in dev, strip http:// if page is https://
  if (typeof window !== 'undefined' && window.location.protocol === 'https:' && envUrl.startsWith('http://')) {
    API_BASE_URL = envUrl.replace('http://', 'https://')
    console.log('🔧 [API] Development mode (upgraded to HTTPS):', API_BASE_URL)
  } else {
    API_BASE_URL = envUrl
    console.log('🔧 [API] Development mode:', API_BASE_URL)
  }
}

console.log('📡 [API] Final base URL:', API_BASE_URL)
console.log('🔒 [API] Page protocol:', typeof window !== 'undefined' ? window.location.protocol : 'N/A')

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
    // DIAGNOSTIC LOGGING - See exactly what axios is doing
    console.log('🔍 [INTERCEPTOR] Raw config.url:', config.url)
    console.log('🔍 [INTERCEPTOR] Raw config.baseURL:', config.baseURL)
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // AGGRESSIVE FIX: Check if baseURL got expanded to absolute URL
    if (config.baseURL && typeof config.baseURL === 'string') {
      // If baseURL became absolute, force it back to relative
      if (config.baseURL.includes('://')) {
        const urlObj = new URL(config.baseURL)
        config.baseURL = urlObj.pathname
        console.warn('⚠️ [INTERCEPTOR] baseURL was absolute, forced to relative:', config.baseURL)
      }
    }
    
    // Check the final combined URL that axios will use
    const finalUrl = config.url ? (config.baseURL || '') + config.url : config.baseURL
    console.log('🔍 [INTERCEPTOR] Final combined URL:', finalUrl)
    
    // NUCLEAR OPTION: Block ALL HTTP in production
    if (import.meta.env.PROD) {
      // Check config.url (the specific endpoint being called)
      if (config.url && config.url.startsWith('http://')) {
        console.error('❌ [INTERCEPTOR] BLOCKED HTTP in config.url:', config.url)
        config.url = config.url.replace('http://', 'https://')
        console.warn('🔒 [INTERCEPTOR] FORCED HTTP→HTTPS on config.url:', config.url)
      }
      
      // Check config.baseURL (should be /api but double-check)
      if (config.baseURL && config.baseURL.startsWith('http://')) {
        console.error('❌ [INTERCEPTOR] BLOCKED HTTP in config.baseURL:', config.baseURL)
        config.baseURL = config.baseURL.replace('http://', 'https://')
        console.warn('🔒 [INTERCEPTOR] FORCED HTTP→HTTPS on config.baseURL:', config.baseURL)
      }
      
      // Final check: If baseURL is somehow not relative, force it
      if (config.baseURL && !config.baseURL.startsWith('/') && !config.baseURL.startsWith('https://')) {
        console.error('❌ [INTERCEPTOR] Invalid baseURL, forcing /api:', config.baseURL)
        config.baseURL = '/api'
      }
    }
    
    console.log('✅ [INTERCEPTOR] Final config.url:', config.url)
    console.log('✅ [INTERCEPTOR] Final config.baseURL:', config.baseURL)
    
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
