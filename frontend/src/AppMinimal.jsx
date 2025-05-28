import React from 'react'
import { ClerkProvider, SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import { Box, Typography, Alert } from '@mui/material'

// Get Clerk publishable key from environment
const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!CLERK_PUBLISHABLE_KEY) {
  throw new Error("Missing Clerk Publishable Key")
}

// Minimal app that makes NO API calls
function MinimalApp() {
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <SignedIn>
        <Box sx={{ p: 4 }}>
          <Typography variant="h2" gutterBottom>
            🚨 DEBUG MODE
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            This is a minimal app with NO API calls. If requests are still happening, 
            the problem is outside your React components (browser extensions, service workers, etc.)
          </Alert>
          <Typography variant="h4" gutterBottom>
            VoiceForge - Minimal Debug Version
          </Typography>
          <Typography variant="body1">
            This version makes absolutely no API calls. If your backend is still getting 
            requests while this is running, the issue is:
          </Typography>
          <ul>
            <li>Browser extensions making requests</li>
            <li>Service workers</li>
            <li>Browser dev tools auto-refresh</li>
            <li>Some other tab or application</li>
          </ul>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Check your browser console and network tab. No requests should be happening.
          </Typography>
        </Box>
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </ClerkProvider>
  )
}

export default MinimalApp
