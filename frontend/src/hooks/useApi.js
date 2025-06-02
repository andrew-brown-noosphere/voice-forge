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
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return await response.json();
        }
        return response;
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
  };
}
