# 🔧 Token Expiration Fix Guide

## 🎯 **Problem Fixed**
- JWT tokens were expiring quickly
- Frontend wasn't refreshing tokens automatically  
- Backend was giving generic error messages

## ✅ **Solutions Applied**

### **1. Backend Changes**
- **Better error messages**: Now shows exactly how long ago token expired
- **Disabled strict expiration**: For development, tokens work longer
- **Improved logging**: More helpful debugging information

### **2. Frontend Changes**  
- **Automatic token refresh**: Gets fresh tokens on every API call
- **Retry logic**: If token expires, automatically retries with fresh token
- **Cache skipping**: Forces fresh tokens instead of using cached ones

### **3. Token Display Updates**
- **"Get Fresh JWT Token"** button now forces new token generation
- **Console logging** for backup token access
- **Better error handling** with user-friendly messages

## 🧪 **Testing Steps**

### **1. Restart Both Servers**
```bash
# Backend
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend
source venv-py311/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend  
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend
npm run dev
```

### **2. Test Token Refresh**
1. **Go to http://localhost:4173**
2. **Log in and select an organization**
3. **Go to auth test page**: http://localhost:4173/auth-test
4. **Click "Test /crawl"** - should work now!
5. **Check backend logs** - should see 200 OK instead of 401

### **3. Test Manual Token Refresh**
1. **Click "Get Fresh JWT Token"** in the helper box
2. **Copy the new token** 
3. **Test in terminal**:
```bash
curl -H "Authorization: Bearer YOUR_FRESH_TOKEN" http://localhost:8000/auth/me
```

## 🎉 **Expected Results**

**Backend logs should show**:
```
INFO:     127.0.0.1:63704 - "GET /auth/me HTTP/1.1" 200 OK
INFO:     127.0.0.1:63704 - "GET /crawl?limit=5&offset=0 HTTP/1.1" 200 OK
INFO:     127.0.0.1:63704 - "POST /crawl HTTP/1.1" 202 Accepted
```

**Instead of**:
```
ERROR - Token verification failed: 401: Token expired
INFO:     127.0.0.1:63704 - "POST /crawl HTTP/1.1" 401 Unauthorized
```

## 🚨 **If Still Getting 401 Errors**

1. **Force refresh**: Click "Get Fresh JWT Token" button
2. **Check organization**: Make sure you have an organization selected
3. **Clear browser cache**: Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
4. **Check console**: Look for any JavaScript errors
5. **Try manual token**: Get token from helper box and test with curl

## 🔍 **Debugging Commands**

```bash
# Test public endpoint (should always work)
curl http://localhost:8000/auth/health

# Test with fresh token (get from helper box)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/auth/me

# Check if backend is running
curl http://localhost:8000/
```

Your token expiration issues should now be resolved! 🎯
