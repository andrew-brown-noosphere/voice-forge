import React from 'react'
import { ClerkProvider, SignedIn, SignedOut, RedirectToSignIn, OrganizationSwitcher, UserButton } from '@clerk/clerk-react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, AppBar, Toolbar, Typography } from '@mui/material'
import { Outlet } from 'react-router-dom'

// Components - import only the sidebar, not the full layout
import AppSidebar from './components/AppSidebar'
import { SimpleTokenDisplay } from './components/SimpleTokenDisplay'
import OrganizationGate from './components/OrganizationGate'

import DebugPage from './pages/DebugPage'

// Pages
import Dashboard from './pages/Dashboard'
import NewCrawl from './pages/NewCrawl'
import CrawlDetails from './pages/CrawlDetails'
import CrawlList from './pages/CrawlList'
import ContentSearch from './pages/ContentSearch'
import ContentDetails from './pages/ContentDetails'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'
import ContentGenerator from './pages/ContentGenerator'
import TemplateList from './pages/TemplateList'
import TemplateEditor from './pages/TemplateEditor'
import GeneratedContentList from './pages/GeneratedContentList'
import AuthTest from './pages/AuthTest'

// Get Clerk publishable key from environment
const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!CLERK_PUBLISHABLE_KEY) {
  throw new Error("Missing Clerk Publishable Key")
}

// Custom Layout component without header (since we use Clerk's header)
function ClerkLayout() {
  const [open, setOpen] = React.useState(true)

  const toggleDrawer = () => {
    setOpen(!open)
  }

  return (
    <>
      <AppSidebar open={open} toggleDrawer={toggleDrawer} />
      <Box
        component="main"
        sx={{
          backgroundColor: (theme) => theme.palette.background.default,
          flexGrow: 1,
          height: '100vh',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar /> {/* Spacer for the fixed header */}
        <Box sx={{ p: 3, flexGrow: 1 }}>
          <Outlet />
        </Box>
      </Box>
    </>
  )
}

// Main App component
function App() {
  return (
    <ClerkProvider 
      publishableKey={CLERK_PUBLISHABLE_KEY}
      appearance={{
        elements: {
          organizationSwitcher: {
            width: '200px'
          }
        }
      }}
    >
      <SignedIn>
        <AuthenticatedApp />
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </ClerkProvider>
  )
}

// Authenticated app with Clerk header + sidebar
function AuthenticatedApp() {
  return (
    <OrganizationGate>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Token Display for Testing - Remove in production */}
      <SimpleTokenDisplay />
      
      {/* Clerk Authentication Header */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            VoiceForge
          </Typography>
          
          {/* Organization Switcher */}
          <Box sx={{ mr: 2 }}>
            <OrganizationSwitcher 
              hidePersonal={true}
              createOrganizationUrl="/dashboard"
              createOrganizationMode="navigation"
              organizationProfileMode="modal"
              afterCreateOrganizationUrl="/dashboard"
              afterSelectOrganizationUrl="/dashboard"
              skipInvitationScreen={false}
              appearance={{
                elements: {
                  organizationSwitcherTrigger: {
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)'
                    }
                  },
                  organizationSwitcherTriggerIcon: {
                    color: 'white'
                  }
                }
              }}
            />
          </Box>
          
          {/* User Button */}
          <UserButton 
            afterSignOutUrl="/"
            userProfileMode="modal"
          />
        </Toolbar>
      </AppBar>
      
      {/* Layout with Sidebar but no header */}
      <Box sx={{ display: 'flex', flexGrow: 1, pt: '64px' }}> {/* pt: '64px' accounts for header height */}
        <Routes>
          <Route path="/" element={<ClerkLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            
            {/* Crawl routes */}
            <Route path="crawls" element={<CrawlList />} />
            <Route path="crawls/new" element={<NewCrawl />} />
            <Route path="crawls/:id" element={<CrawlDetails />} />
            
            {/* Content routes */}
            <Route path="content" element={<ContentSearch />} />
            <Route path="content/:id" element={<ContentDetails />} />
            
            {/* RAG routes */}
            <Route path="generator" element={<ContentGenerator />} />
            <Route path="templates" element={<TemplateList />} />
            <Route path="templates/new" element={<TemplateEditor />} />
            <Route path="templates/:id" element={<TemplateEditor />} />
            <Route path="generated" element={<GeneratedContentList />} />
            
            {/* Auth test route */}
            <Route path="auth-test" element={<AuthTest />} />
            
            {/* Debug route */}
            <Route path="debug" element={<DebugPage />} />
            
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Box>
    </Box>
    </OrganizationGate>
  )
}

export default App
