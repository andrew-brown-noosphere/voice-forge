import { useAuth } from '@clerk/clerk-react';
import { useCallback } from 'react';

// API base URL
const API_BASE_URL = 'http://localhost:8000';

/**
 * Simple, stable authenticated API hook
 */
export function useApi() {
  const { getToken, isSignedIn, orgId } = useAuth();

  const makeRequest = useCallback(async (url, options = {}) => {
    // Don't make requests if not signed in or no org
    if (!isSignedIn || !orgId) {
      throw new Error('Not authenticated or no organization selected');
    }

    try {
      // Get token (use cache to avoid rate limits)
      const token = await getToken();
      
      if (!token) {
        throw new Error('No token available');
      }

      // Debug: Log token info (first 20 chars only for security)
      console.log(`Making request to ${url} with token: ${token.substring(0, 20)}...`);

      // Make request
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          ...options.headers,
        },
      });

      // Handle response
      if (response.ok) {
        // Check if there's any content to parse
        const contentLength = response.headers.get('content-length');
        const hasContent = contentLength && parseInt(contentLength) > 0;
        
        if (hasContent) {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            return await response.json();
          } else {
            return await response.text();
          }
        } else {
          // Empty response (common for DELETE operations)
          return { success: true, status: response.status };
        }
      } else {
        const errorText = await response.text();
        
        // Special handling for auth errors
        if (response.status === 401) {
          console.error('Authentication failed - may need to refresh token or login');
          console.error('Response:', errorText);
        }
        
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
    } catch (error) {
      console.error('API Error:', error);
      
      // If it's an auth error, provide helpful guidance
      if (error.message.includes('401') || error.message.includes('Authentication')) {
        console.error('🔧 Auth troubleshooting:');
        console.error('1. Check if you are signed in:', isSignedIn);
        console.error('2. Check if organization is selected:', orgId);
        console.error('3. Try refreshing the page');
        console.error('4. Check browser console for more details');
      }
      
      throw error;
    }
  }, [getToken, isSignedIn, orgId]);

  // Return stable API object
  return {
    // General request method
    request: makeRequest,
    
    // Direct access to makeRequest for testing
    makeRequest,
    
    // Debug method to test auth
    debug: {
      testAuth: async () => {
        try {
          const token = await getToken();
          console.log('🔍 Current auth state:');
          console.log('- Signed in:', isSignedIn);
          console.log('- Org ID:', orgId);
          console.log('- Token preview:', token ? `${token.substring(0, 20)}...` : 'No token');
          
          if (token) {
            // Test the debug endpoint
            return await makeRequest('/auth/debug');
          } else {
            throw new Error('No token available');
          }
        } catch (error) {
          console.error('Debug test failed:', error);
          throw error;
        }
      },
      getCurrentToken: async () => {
        return await getToken();
      }
    },
    // Crawl operations
    crawls: {
      list: (limit = 10, offset = 0) => makeRequest(`/crawl?limit=${limit}&offset=${offset}`),
      get: (crawlId) => makeRequest(`/crawl/${crawlId}`),
      create: (crawlData) => makeRequest('/crawl', { method: 'POST', body: JSON.stringify(crawlData) }),
      cancel: (crawlId) => makeRequest(`/crawl/${crawlId}`, { method: 'DELETE' }),
      delete: (crawlId) => makeRequest(`/crawl/${crawlId}`, { method: 'DELETE' }), // Alias for clarity
      deleteAll: () => makeRequest('/crawl-all', { method: 'DELETE' }),
    },

    // Content operations
    content: {
      search: (query, domain, contentType, limit = 10, offset = 0) => makeRequest('/content/search', {
        method: 'POST',
        body: JSON.stringify({
          query: query || '',
          domain,
          content_type: contentType,
          limit,
          offset
        })
      }),
      get: (contentId) => makeRequest(`/content/${contentId}`),
    },

    // Domain operations
    domains: {
      list: () => makeRequest('/domains'),
    },

    // Auth operations
    auth: {
      me: () => makeRequest('/auth/me'),
      health: () => makeRequest('/auth/health'),
    },

    // RAG operations
    rag: {
      searchChunks: (query, domain, contentType, topK = 5) => makeRequest('/rag/chunks/search', {
        method: 'POST',
        body: JSON.stringify({
          query,
          domain,
          content_type: contentType,
          top_k: topK
        })
      }),
      generateContent: (query, platform, tone, domain, contentType, topK = 5) => makeRequest('/rag/generate', {
        method: 'POST',
        body: JSON.stringify({
          query,
          platform,
          tone,
          domain,
          content_type: contentType,
          top_k: topK
        })
      }),
      getContentChunks: (contentId) => makeRequest(`/rag/content/${contentId}/chunks`),
      processContent: (contentId) => makeRequest(`/rag/process/${contentId}`, { method: 'POST' }),
    },

    // Template operations
    templates: {
      list: (platform, tone, purpose, limit = 10, offset = 0) => makeRequest('/templates/search', {
        method: 'POST',
        body: JSON.stringify({
          platform,
          tone,
          purpose,
          limit,
          offset
        })
      }),
      get: (templateId) => makeRequest(`/templates/${templateId}`),
      create: (templateData) => makeRequest('/templates', { method: 'POST', body: JSON.stringify(templateData) }),
    },

    // Reddit Signal operations
    redditSignals: {
      discover: (subreddits, keywords, timeFilter = 'week', maxPostsPerSubreddit = 50, relevanceThreshold = 0.6) => makeRequest('/reddit-signals/discover', {
        method: 'POST',
        body: JSON.stringify({
          subreddits,
          keywords,
          time_filter: timeFilter,
          max_posts_per_subreddit: maxPostsPerSubreddit,
          relevance_threshold: relevanceThreshold
        })
      }),
      list: (limit = 20, offset = 0, signalType = null, subreddit = null) => {
        const params = new URLSearchParams({ limit, offset })
        if (signalType) params.append('signal_type', signalType)
        if (subreddit) params.append('subreddit', subreddit)
        return makeRequest(`/reddit-signals/signals?${params}`)
      },
      get: (signalId) => makeRequest(`/reddit-signals/signals/${signalId}`),
      generateResponse: (signalId, platform = 'reddit', tone = 'professional', responseType = 'comment_reply', includeContext = true) => makeRequest('/reddit-signals/generate-response', {
        method: 'POST',
        body: JSON.stringify({
          signal_id: signalId,
          platform,
          tone,
          response_type: responseType,
          include_context: includeContext
        })
      }),
      health: () => makeRequest('/reddit-signals/health'),
    },

    // Abstracted Signals operations (multi-platform)
    signals: {
      discover: (discoveryRequest) => makeRequest('/signals/discover', {
        method: 'POST',
        body: JSON.stringify(discoveryRequest)
      }),
      list: (params = {}) => {
        const searchParams = new URLSearchParams()
        Object.entries(params).forEach(([key, value]) => {
          if (value !== null && value !== undefined) {
            searchParams.append(key, value)
          }
        })
        return makeRequest(`/signals/list?${searchParams}`)
      },
      get: (signalId) => makeRequest(`/signals/${signalId}`),
      generateResponse: (responseRequest) => makeRequest('/signals/generate-response', {
        method: 'POST',
        body: JSON.stringify(responseRequest)
      }),
      getSupportedPlatforms: () => makeRequest('/signals/platforms/supported'),
      health: () => makeRequest('/signals/health'),
      
      // Signal Source Management
      getSources: () => makeRequest('/signals/sources'),
      createSource: (sourceData) => makeRequest('/signals/sources', {
        method: 'POST',
        body: JSON.stringify(sourceData)
      }),
      scanSource: (sourceId) => makeRequest(`/signals/sources/${sourceId}/scan`, {
        method: 'POST'
      }),
      updateSource: (sourceId, updates) => makeRequest(`/signals/sources/${sourceId}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
      }),
      deleteSource: (sourceId) => makeRequest(`/signals/sources/${sourceId}`, {
        method: 'DELETE'
      }),
      aiGuidedSetup: (setupData) => makeRequest('/signals/sources/ai-setup', {
        method: 'POST',
        body: JSON.stringify(setupData)
      }),
      getRecommendations: (sourceId) => makeRequest(`/signals/sources/${sourceId}/recommendations`),
      applyRecommendation: (sourceId, recId) => makeRequest(`/signals/sources/${sourceId}/recommendations/${recId}/apply`, {
        method: 'POST'
      }),
      
      // Content analysis and strategy
      getAnalysis: () => makeRequest('/signals/analysis'),
      generateStrategy: (strategyRequest) => makeRequest('/signals/strategy', {
        method: 'POST',
        body: JSON.stringify(strategyRequest)
      })
    },

    // Platform-specific methods
    platforms: {
      // Get platform status and configuration
      getStatus: (platform) => makeRequest(`/signals/platforms/${platform}/status`),
      
      // Configure platform credentials and settings
      configure: (platform, config) => makeRequest(`/signals/platforms/${platform}/configure`, {
        method: 'POST',
        body: JSON.stringify(config)
      }),
      
      // Test platform connection
      testConnection: (platform) => makeRequest(`/signals/platforms/${platform}/test-connection`, {
        method: 'POST'
      }),
      
      // Get platform-specific metrics
      getMetrics: (platform, timeframe = '24h') => makeRequest(`/signals/platforms/${platform}/metrics?timeframe=${timeframe}`),
      
      // Get platform activity/logs
      getActivity: (platform, limit = 50) => makeRequest(`/signals/platforms/${platform}/activity?limit=${limit}`)
    },

    // Gypsum Persona operations
    gypsum: {
      getPersonas: () => makeRequest('/gypsum/personas'),
      getPersona: (personaId) => makeRequest(`/gypsum/personas/${personaId}`),
      createPersona: (personaData) => makeRequest('/gypsum/personas', {
        method: 'POST',
        body: JSON.stringify(personaData)
      }),
      updatePersona: (personaId, updates) => makeRequest(`/gypsum/personas/${personaId}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
      }),
      deletePersona: (personaId) => makeRequest(`/gypsum/personas/${personaId}`, {
        method: 'DELETE'
      })
    },

    // Intelligent Prompt Generation operations
    prompts: {
      generate: (domain, platform, maxPrompts = 1, focusAreas, personaId, includeMessagingFramework = true, funnelStage, cacheBuster = null) => {
        // Build request body, filtering out null/undefined values
        const body = {
          max_prompts: maxPrompts,
          include_messaging_framework: includeMessagingFramework
        }
        
        // Only include non-null values
        if (domain) body.domain = domain
        if (platform) body.platform = platform
        if (focusAreas) body.focus_areas = focusAreas
        if (personaId) body.persona_id = personaId
        if (funnelStage) body.funnel_stage = funnelStage
        if (cacheBuster) body.timestamp = cacheBuster
        
        return makeRequest('/api/prompts/generate', {
          method: 'POST',
          body: JSON.stringify(body)
        })
      },
      getSample: (businessType, personaRole) => {
        const params = new URLSearchParams()
        if (businessType) params.append('business_type', businessType)
        if (personaRole) params.append('persona_role', personaRole)
        return makeRequest(`/api/prompts/sample?${params}`)
      },
      health: () => makeRequest('/api/prompts/health')
    },
  };
}
