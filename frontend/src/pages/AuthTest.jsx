import React, { useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { Box, Typography, Button, Alert, Card, CardContent } from '@mui/material'
import { useApi } from '../hooks/useApi'

const AuthTest = () => {
  const { isSignedIn, orgId, getToken, user } = useAuth()
  const [tokenInfo, setTokenInfo] = useState(null)
  const [apiTestResult, setApiTestResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const api = useApi()

  const testToken = async () => {
    try {
      const token = await getToken({ skipCache: true })
      setTokenInfo({
        token: token ? `${token.substring(0, 20)}...` : 'No token',
        length: token ? token.length : 0
      })
    } catch (error) {
      setTokenInfo({ error: error.message })
    }
  }

  const testApiCall = async () => {
    setLoading(true)
    try {
      // Test the auth endpoint first
      const result = await api.auth.health()
      setApiTestResult({ success: true, data: result })
    } catch (error) {
      setApiTestResult({ success: false, error: error.message })
    } finally {
      setLoading(false)
    }
  }

  const testAuthDebug = async () => {
    setLoading(true)
    try {
      console.log('Testing auth debug...')
      const result = await api.debug.testAuth()
      setApiTestResult({ success: true, data: result, type: 'auth-debug' })
    } catch (error) {
      console.error('Auth debug error:', error)
      setApiTestResult({ success: false, error: error.message, type: 'auth-debug' })
    } finally {
      setLoading(false)
    }
  }

  const testCrawlList = async () => {
    setLoading(true)
    try {
      console.log('Testing crawl list...')
      const result = await api.crawls.list(5, 0)
      setApiTestResult({ success: true, data: result, type: 'crawl-list' })
    } catch (error) {
      console.error('Crawl list error:', error)
      setApiTestResult({ success: false, error: error.message, type: 'crawl-list' })
    } finally {
      setLoading(false)
    }
  }

  const testCrawlCreation = async () => {
    setLoading(true)
    try {
      console.log('Testing crawl creation...')
      console.log('Auth state:', { isSignedIn, orgId })
      
      // Get token and log it
      const token = await getToken({ skipCache: true })
      console.log('Token for crawl request:', token ? `${token.substring(0, 20)}...` : 'No token')
      
      const result = await api.crawls.create({
        domain: 'example.com',
        config: {
          max_depth: 1,
          max_pages: 1,
          delay: 1.0
        }
      })
      setApiTestResult({ success: true, data: result, type: 'crawl' })
    } catch (error) {
      console.error('Crawl creation error:', error)
      setApiTestResult({ success: false, error: error.message, type: 'crawl' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Authentication Test
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Auth Status
          </Typography>
          <Typography>Signed In: {isSignedIn ? '✅ Yes' : '❌ No'}</Typography>
          <Typography>Organization ID: {orgId || '❌ None'}</Typography>
          <Typography>User: {user?.emailAddresses?.[0]?.emailAddress || 'Unknown'}</Typography>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Token Test
          </Typography>
          <Button variant="outlined" onClick={testToken} sx={{ mb: 2 }}>
            Get Token
          </Button>
          {tokenInfo && (
            <Box>
              {tokenInfo.error ? (
                <Alert severity="error">{tokenInfo.error}</Alert>
              ) : (
                <Alert severity="success">
                  Token: {tokenInfo.token} (Length: {tokenInfo.length})
                </Alert>
              )}
            </Box>
          )}
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            API Test
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Button 
              variant="contained" 
              onClick={testApiCall} 
              disabled={loading}
              sx={{ mr: 2, mb: 1 }}
            >
              Test Auth Health
            </Button>
            <Button 
              variant="contained" 
              onClick={testAuthDebug} 
              disabled={loading}
              color="warning"
              sx={{ mr: 2, mb: 1 }}
            >
              Debug Auth Token
            </Button>
            <Button 
              variant="contained" 
              onClick={testCrawlCreation} 
              disabled={loading}
              color="secondary"
              sx={{ mr: 2, mb: 1 }}
            >
              Test Crawl Creation
            </Button>
            <Button 
              variant="outlined" 
              onClick={testCrawlList} 
              disabled={loading}
              sx={{ mb: 1 }}
            >
              Test Crawl List
            </Button>
          </Box>
          {apiTestResult && (
            <Alert severity={apiTestResult.success ? 'success' : 'error'}>
              {apiTestResult.success ? (
                <Box>
                  <Typography variant="subtitle2">Success!</Typography>
                  <pre style={{ fontSize: '12px', marginTop: '8px' }}>
                    {JSON.stringify(apiTestResult.data, null, 2)}
                  </pre>
                </Box>
              ) : (
                <Box>
                  <Typography variant="subtitle2">Error:</Typography>
                  <Typography variant="body2">{apiTestResult.error}</Typography>
                </Box>
              )}
            </Alert>
          )}
        </CardContent>
      </Card>

      <Alert severity="info">
        Use this page to debug authentication issues. 
        If any of these tests fail, the problem is with your auth setup.
        <br /><br />
        <strong>Quick Fix:</strong> If you're getting 401 errors, try refreshing the page to get a new token.
      </Alert>
    </Box>
  )
}

export default AuthTest