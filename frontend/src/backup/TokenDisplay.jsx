import { useAuth } from '@clerk/clerk-react';
import { useState } from 'react';

export function TokenDisplay() {
  const { getToken, userId, orgId } = useAuth();
  const [token, setToken] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGetToken = async () => {
    try {
      const jwt = await getToken();
      setToken(jwt);
      console.log('JWT Token:', jwt);
    } catch (error) {
      console.error('Error getting token:', error);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: '#f0f0f0', 
      padding: '15px', 
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      maxWidth: '400px',
      fontSize: '12px',
      zIndex: 1000
    }}>
      <h4>🔐 Auth Debug Info</h4>
      <p><strong>User ID:</strong> {userId}</p>
      <p><strong>Org ID:</strong> {orgId || 'No organization selected'}</p>
      
      <button 
        onClick={handleGetToken}
        style={{ 
          background: '#007bff', 
          color: 'white', 
          border: 'none', 
          padding: '8px 12px', 
          borderRadius: '4px',
          cursor: 'pointer',
          marginRight: '8px'
        }}
      >
        Get JWT Token
      </button>

      {token && (
        <div style={{ marginTop: '10px' }}>
          <button 
            onClick={copyToClipboard}
            style={{ 
              background: copied ? '#28a745' : '#6c757d', 
              color: 'white', 
              border: 'none', 
              padding: '4px 8px', 
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '10px',
              marginBottom: '8px'
            }}
          >
            {copied ? '✅ Copied!' : '📋 Copy Token'}
          </button>
          
          <div style={{ 
            background: '#ffffff', 
            padding: '8px', 
            borderRadius: '4px', 
            border: '1px solid #ddd',
            wordBreak: 'break-all',
            fontSize: '10px',
            maxHeight: '100px',
            overflow: 'auto'
          }}>
            {token}
          </div>
          
          <div style={{ marginTop: '8px', fontSize: '10px', color: '#666' }}>
            <strong>Test command:</strong>
            <div style={{ 
              background: '#000', 
              color: '#0f0', 
              padding: '4px', 
              borderRadius: '4px',
              marginTop: '4px',
              fontFamily: 'monospace'
            }}>
              curl -H "Authorization: Bearer {token}" http://localhost:8000/auth/me
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
