import { useAuth } from '@clerk/clerk-react';
import { useState } from 'react';

export function SimpleTokenDisplay() {
  const { getToken, userId, orgId } = useAuth();
  const [token, setToken] = useState('');
  const [isVisible, setIsVisible] = useState(true);

  const handleGetToken = async () => {
    try {
      // Get a fresh token, skipping cache
      const jwt = await getToken({ skipCache: true });
      setToken(jwt);
      // Also log to console for backup
      console.log('🔐 Fresh JWT Token:', jwt);
      console.log('📋 Copy this token for testing:', jwt);
    } catch (error) {
      console.error('Error getting token:', error);
      alert('Error getting token. Check console for details.');
    }
  };

  const copyToken = () => {
    navigator.clipboard.writeText(token);
    alert('Token copied to clipboard!');
  };

  if (!isVisible) {
    return (
      <button 
        onClick={() => setIsVisible(true)}
        style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          background: '#007bff',
          color: 'white',
          border: 'none',
          padding: '8px 12px',
          borderRadius: '4px',
          cursor: 'pointer',
          zIndex: 10000
        }}
      >
        Show Token Helper
      </button>
    );
  }

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'white',
      border: '2px solid #007bff',
      borderRadius: '8px',
      padding: '15px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
      maxWidth: '350px',
      fontSize: '13px',
      zIndex: 10000,
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h4 style={{ margin: 0, color: '#007bff' }}>🔐 JWT Token Helper</h4>
        <button 
          onClick={() => setIsVisible(false)}
          style={{ 
            background: 'none', 
            border: 'none', 
            fontSize: '16px', 
            cursor: 'pointer',
            color: '#666'
          }}
        >
          ✕
        </button>
      </div>
      
      <div style={{ marginBottom: '10px', fontSize: '12px', color: '#666' }}>
        <div><strong>User:</strong> {userId ? userId.substring(0, 12) + '...' : 'Not logged in'}</div>
        <div><strong>Org:</strong> {orgId ? orgId.substring(0, 12) + '...' : 'No organization'}</div>
      </div>

      <button 
        onClick={handleGetToken}
        style={{
          background: '#28a745',
          color: 'white',
          border: 'none',
          padding: '10px 15px',
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '10px',
          width: '100%',
          fontSize: '13px',
          fontWeight: 'bold'
        }}
      >
        🎯 Get Fresh JWT Token
      </button>

      {token && (
        <div>
          <button 
            onClick={copyToken}
            style={{
              background: '#ffc107',
              color: 'black',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              marginBottom: '10px',
              width: '100%',
              fontSize: '12px'
            }}
          >
            📋 Copy Token to Clipboard
          </button>
          
          <div style={{
            background: '#f8f9fa',
            border: '1px solid #dee2e6',
            borderRadius: '4px',
            padding: '8px',
            fontSize: '10px',
            wordBreak: 'break-all',
            maxHeight: '80px',
            overflow: 'auto',
            marginBottom: '10px'
          }}>
            {token.substring(0, 50)}...
          </div>

          <div style={{ fontSize: '11px', color: '#666' }}>
            <strong>Test command:</strong>
            <div style={{
              background: '#000',
              color: '#0f0',
              padding: '8px',
              borderRadius: '4px',
              marginTop: '5px',
              fontFamily: 'monospace',
              fontSize: '9px'
            }}>
              curl -H "Authorization: Bearer [token]" http://localhost:8000/auth/me
            </div>
          </div>
        </div>
      )}
      
      <div style={{ fontSize: '10px', color: '#999', marginTop: '10px' }}>
        💡 Token also logged to browser console
      </div>
    </div>
  );
}
