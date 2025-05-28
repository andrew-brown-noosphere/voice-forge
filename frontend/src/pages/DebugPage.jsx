import React, { useEffect, useState } from 'react'
import { Box, Typography, Alert, Button } from '@mui/material'
import { useApi } from '../hooks/useApi'

const DebugPage = () => {
  const [requestCount, setRequestCount] = useState(0)
  const [lastError, setLastError] = useState(null)
  const [logs, setLogs] = useState([])
  const api = useApi()

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`${timestamp}: ${message}`, ...prev].slice(0, 10))
  }

  const testSingleRequest = async () => {
    try {
      addLog('Testing single API request...')
      const data = await api.crawls.list(5, 0)
      addLog(`✅ Success: Got ${data.length} crawls`)
      setLastError(null)
    } catch (error) {
      addLog(`❌ Error: ${error.message}`)
      setLastError(error.message)
    }
  }

  // NO useEffect - completely manual testing
  
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        🐛 Debug Page - Manual Testing
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This page makes NO automatic requests. Use the button to test manually.
      </Alert>

      <Box sx={{ mb: 3 }}>
        <Button variant="contained" onClick={testSingleRequest} sx={{ mr: 2 }}>
          Test Single Request
        </Button>
        <Button variant="outlined" onClick={() => setLogs([])}>
          Clear Logs
        </Button>
      </Box>

      {lastError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Last Error: {lastError}
        </Alert>
      )}

      <Typography variant="h6" gutterBottom>
        Request Logs:
      </Typography>
      <Box sx={{ 
        backgroundColor: '#1a1a1a', 
        color: '#00ff00', 
        p: 2, 
        borderRadius: 1,
        fontFamily: 'monospace',
        height: '200px',
        overflow: 'auto'
      }}>
        {logs.length === 0 ? (
          <div style={{ color: '#888' }}>No requests made yet...</div>
        ) : (
          logs.map((log, i) => (
            <div key={i}>{log}</div>
          ))
        )}
      </Box>

      <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
        If your backend is still getting requests while viewing this page,
        the problem is NOT in your React components.
      </Typography>
    </Box>
  )
}

export default DebugPage
