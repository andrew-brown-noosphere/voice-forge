import axios from 'axios'

// Get API URL from environment variable or use default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 45000, // 45 seconds for AI generation
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

  deleteAllCrawls: async () => {
    const response = await api.delete('/crawl-all')
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

  // NEW: RAG operations
  searchChunks: async (query, domain, contentType, topK = 5) => {
    const params = { query, top_k: topK }
    if (domain) params.domain = domain
    if (contentType) params.content_type = contentType

    const response = await api.post('/rag/chunks/search', params)
    return response.data
  },

  getContentChunks: async (contentId) => {
    const response = await api.get(`/rag/content/${contentId}/chunks`)
    return response.data
  },

  processContentForRag: async (contentId) => {
    const response = await api.post(`/rag/process/${contentId}`)
    return response.data
  },

  generateContent: async (query, platform, tone, domain, contentType, topK = 5) => {
    const params = { 
      query, 
      platform, 
      tone,
      top_k: topK
    }
    
    if (domain) params.domain = domain
    if (contentType) params.content_type = contentType

    const response = await api.post('/rag/generate', params)
    return response.data
  },

  // Template operations
  createTemplate: async (template) => {
    const response = await api.post('/templates', template)
    return response.data
  },

  getTemplate: async (templateId) => {
    const response = await api.get(`/templates/${templateId}`)
    return response.data
  },

  searchTemplates: async (platform, tone, purpose, limit = 10, offset = 0) => {
    const params = { limit, offset }
    if (platform) params.platform = platform
    if (tone) params.tone = tone
    if (purpose) params.purpose = purpose

    const response = await api.post('/templates/search', params)
    return response.data
  },

  // Reddit Signal operations
  discoverRedditSignals: async (subreddits, keywords, timeFilter = 'week', maxPostsPerSubreddit = 50, relevanceThreshold = 0.6) => {
    const params = {
      subreddits,
      keywords,
      time_filter: timeFilter,
      max_posts_per_subreddit: maxPostsPerSubreddit,
      relevance_threshold: relevanceThreshold
    }
    const response = await api.post('/reddit-signals/discover', params)
    return response.data
  },

  generateSignalResponse: async (signalId, platform = 'reddit', tone = 'professional', responseType = 'comment_reply', includeContext = true) => {
    const params = {
      signal_id: signalId,
      platform,
      tone,
      response_type: responseType,
      include_context: includeContext
    }
    const response = await api.post('/reddit-signals/generate-response', params)
    return response.data
  },

  listRedditSignals: async (limit = 20, offset = 0, signalType = null, subreddit = null) => {
    const params = new URLSearchParams({ limit, offset })
    if (signalType) params.append('signal_type', signalType)
    if (subreddit) params.append('subreddit', subreddit)
    
    const response = await api.get(`/reddit-signals/signals?${params}`)
    return response.data
  },

  getRedditSignal: async (signalId) => {
    const response = await api.get(`/reddit-signals/signals/${signalId}`)
    return response.data
  },

  checkRedditSignalsHealth: async () => {
    const response = await api.get('/reddit-signals/health')
    return response.data
  },
}

export default apiService
