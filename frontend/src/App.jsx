import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'

// Layout
import Layout from './components/Layout'

// Pages
import Dashboard from './pages/Dashboard'
import NewCrawl from './pages/NewCrawl'
import CrawlDetails from './pages/CrawlDetails'
import ContentSearch from './pages/ContentSearch'
import ContentDetails from './pages/ContentDetails'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="crawls/new" element={<NewCrawl />} />
          <Route path="crawls/:id" element={<CrawlDetails />} />
          <Route path="content" element={<ContentSearch />} />
          <Route path="content/:id" element={<ContentDetails />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Box>
  )
}

export default App
