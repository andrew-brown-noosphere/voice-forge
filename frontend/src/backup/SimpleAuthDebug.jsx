import React, { useState } from 'react';
import { Box, Typography, Button, Alert, CircularProgress } from '@mui/material';
import { useAuth } from '@clerk/clerk-react';

const SimpleAuthDebug = () => {
  const { getToken, userId, orgId } = useAuth();
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testRawFetch = async () => {
    setLoading(true);
    setResult('');
    
    try {
      // Get token first
      const token = await getToken({ skipCache: true });
      console.log('🔐 Token obtained:', token ? 'YES' : 'NO');
      console.log('🔐 Token length:', token ? token.length : 0);
      console.log('🔐 Full token:', token);
      
      if (!token) {
        setResult('❌ No token available');
        return;
      }

      // Make raw fetch request
      const response = await fetch('http://localhost:8000/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const data = await response.json();
        setResult(`✅ SUCCESS: ${JSON.stringify(data, null, 2)}`);
      } else {
        const errorText = await response.text();
        setResult(`❌ FAILED: ${response.status} - ${errorText}`);
      }
      
    } catch (error) {
      console.error('🔥 Error:', error);
      setResult(`💥 ERROR: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        🔍 Raw Authentication Debug
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Typography><strong>User ID:</strong> {userId || 'None'}</Typography>
        <Typography><strong>Org ID:</strong> {orgId || 'None'}</Typography>
      </Box>

      <Button 
        variant="contained" 
        onClick={testRawFetch}
        disabled={loading || !userId || !orgId}
        sx={{ mb: 2 }}
      >
        {loading ? <CircularProgress size={20} /> : 'Test Raw Auth'}
      </Button>

      {!orgId && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          ⚠️ No organization selected. Use the organization switcher in the header.
        </Alert>
      )}

      {result && (
        <Box sx={{ 
          background: '#f5f5f5', 
          p: 2, 
          borderRadius: 1, 
          fontFamily: 'monospace',
          fontSize: '12px',
          whiteSpace: 'pre-wrap',
          maxHeight: '300px',
          overflow: 'auto'
        }}>
          {result}
        </Box>
      )}
    </Box>
  );
};

export default SimpleAuthDebug;
