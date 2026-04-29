// Native fetch-based API client - No axios dependency!
// Handles relative URLs correctly without HTTP/HTTPS conversion issues

// Environment-aware API base URL
let API_BASE_URL: string

if (import.meta.env.PROD) {
  // Production: Use relative path - fetch handles this correctly!
  API_BASE_URL = '/api'
  console.log('🌐 [API] Production mode: Relative path (fetch handles correctly):', API_BASE_URL)
} else {
  // Development: Use environment variable or default to localhost
  API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  console.log('🔧 [API] Development mode:', API_BASE_URL)
}

console.log('📡 [API] Final base URL:', API_BASE_URL)
console.log('🔒 [API] Page protocol:', typeof window !== 'undefined' ? window.location.protocol : 'N/A')

// Fetch wrapper that mimics axios interface
class APIClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<{ data: T; status: number; statusText: string }> {
    // Build full URL
    const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`
    
    console.log('🔍 [FETCH] Request URL:', fullUrl)
    console.log('🔍 [FETCH] Method:', options.method || 'GET')
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }
    
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    try {
      const response = await fetch(fullUrl, {
        ...options,
        headers,
      })

      // Handle 401 unauthorized
      if (response.status === 401) {
        localStorage.removeItem('auth_token')
      }

      // Parse response
      let data: T
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        data = (await response.text()) as unknown as T
      }

      if (!response.ok) {
        throw {
          response: {
            data,
            status: response.status,
            statusText: response.statusText,
          },
          message: `HTTP ${response.status}: ${response.statusText}`,
        }
      }

      console.log('✅ [FETCH] Success:', response.status)
      return {
        data,
        status: response.status,
        statusText: response.statusText,
      }
    } catch (error) {
      console.error('❌ [FETCH] Error:', error)
      throw error
    }
  }

  async get<T>(url: string, config?: { params?: Record<string, any> }) {
    // Build query string
    let fullUrl = url
    if (config?.params) {
      const params = new URLSearchParams()
      Object.entries(config.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value))
        }
      })
      const queryString = params.toString()
      if (queryString) {
        fullUrl = `${url}?${queryString}`
      }
    }

    return this.request<T>(fullUrl, { method: 'GET' })
  }

  async post<T>(url: string, data?: any) {
    return this.request<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(url: string, data?: any) {
    return this.request<T>(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(url: string) {
    return this.request<T>(url, { method: 'DELETE' })
  }

  async patch<T>(url: string, data?: any) {
    return this.request<T>(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  }
}

// Create and export the API client instance
const api = new APIClient(API_BASE_URL)

export default api
