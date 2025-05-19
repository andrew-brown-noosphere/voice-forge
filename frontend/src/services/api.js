import axios from 'axios'

// Get API URL from environment variable or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API service methods
const apiService = {
  // Crawl operations
  createCrawl: async (domain, config) => {
    const response = await api.post('/crawl', { domain, config })
    return response.data
  },

  getCrawlStatus: async (crawlId) => {
    const response = await api.get(`/crawl/${crawlId}`)
    return response.data
  },

  listCrawls: async (limit = 10, offset = 0) => {
    const response = await api.get(`/crawl?limit=${limit}&offset=${offset}`)
    return response.data
  },

  cancelCrawl: async (crawlId) => {
    const response = await api.delete(`/crawl/${crawlId}`)
    return response.data
  },

  // Content operations
  searchContent: async (query, domain, contentType, limit = 10, offset = 0) => {
    const params = { query, limit, offset }
    if (domain) params.domain = domain
    if (contentType) params.content_type = contentType

    const response = await api.post('/content/search', params)
    return response.data
  },

  getContent: async (contentId) => {
    const response = await api.get(`/content/${contentId}`)
    return response.data
  },

  // Domain operations
  listDomains: async () => {
    const response = await api.get('/domains')
    return response.data
  },
}

export default apiService
