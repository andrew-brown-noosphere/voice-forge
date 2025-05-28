# 🔐 Getting JWT Tokens for Multi-Tenant Testing

## 🚀 Quick Start

### **Step 1: Start Your Frontend with Token Display**

```bash
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend
npm run dev
```

Open http://localhost:4173 and log in.

### **Step 2: Get Your JWT Token**

You'll now see a **"🔐 Auth Debug Info"** box in the top-right corner of your app:

1. **Select an organization** using the Clerk organization switcher
2. **Click "Get JWT Token"** in the debug box
3. **Click "📋 Copy Token"** to copy the JWT token
4. **Use the token for API testing**

### **Step 3: Test Multi-Tenant Backend**

```bash
# Test auth endpoint (replace YOUR_JWT_TOKEN with the copied token)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/auth/me

# Expected response:
{
  "user_id": "user_2abc123def",
  "org_id": "org_2xyz789abc", 
  "org_role": "admin",
  "email": "you@company.com",
  "name": "Your Name",
  "has_org_access": true,
  "is_org_admin": true
}
```

### **Step 4: Test Organization-Scoped API**

```bash
# Create a crawl (will be scoped to your organization)
curl -X POST \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"domain": "https://example.com", "config": {"max_pages": 5}}' \
     http://localhost:8000/crawl

# List your organization's crawls
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/crawl
```

## 🧪 Testing Multi-Tenant Isolation

### **Test Different Organizations:**

1. **Create/join multiple organizations** in Clerk
2. **Switch between organizations** using the organization switcher
3. **Get JWT tokens for each organization** (the `org_id` will be different)
4. **Verify data isolation** - users can only see their organization's data

### **Example Multi-Org Test:**

```bash
# Organization A token
ORG_A_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Organization B token  
ORG_B_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Create crawl in Org A
curl -X POST \
     -H "Authorization: Bearer $ORG_A_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"domain": "https://org-a-site.com", "config": {"max_pages": 5}}' \
     http://localhost:8000/crawl

# Try to list crawls as Org B (should not see Org A's crawl)
curl -H "Authorization: Bearer $ORG_B_TOKEN" http://localhost:8000/crawl
```

## 🔍 Alternative Methods

### **Browser Developer Tools:**
1. Open Dev Tools (F12) → Application → Cookies
2. Look for `__session` cookie value

### **Browser Console:**
```javascript
// Run this in your browser console
window.Clerk.session.getToken().then(token => {
    console.log('JWT Token:', token);
});
```

### **Using Clerk's getToken in React:**
```javascript
import { useAuth } from '@clerk/clerk-react';

function MyComponent() {
  const { getToken } = useAuth();
  
  const handleGetToken = async () => {
    const token = await getToken();
    console.log('Token:', token);
  };
  
  return <button onClick={handleGetToken}>Get Token</button>;
}
```

## 🗑️ Cleanup

**Remove the TokenDisplay component before production:**

1. Remove the `TokenDisplay` import from `App.jsx`
2. Remove the `<TokenDisplay />` component from `AuthenticatedApp`
3. Delete the `/components/TokenDisplay.jsx` file

## 🎯 Expected Behavior

With a valid JWT token, you should be able to:

✅ **Access protected endpoints** (`/auth/me`, `/crawl`, `/content/search`, etc.)  
✅ **See organization-scoped data** (only your org's crawls, content, etc.)  
✅ **Perform organization-scoped operations** (create crawls, search content, etc.)  
❌ **Access other organizations' data** (should return empty/401/403)  

**Your multi-tenant backend is working if each organization can only see their own data!** 🎉
