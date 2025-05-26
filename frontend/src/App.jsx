import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'

// Layout
import Layout from './components/Layout'

// Pages
import Dashboard from './pages/Dashboard'
import NewCrawl from './pages/NewCrawl'
import CrawlDetails from './pages/CrawlDetails'
import CrawlList from './pages/CrawlList'
import ContentSearch from './pages/ContentSearch'
import ContentDetails from './pages/ContentDetails'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

// New RAG Pages
import ContentGenerator from './pages/ContentGenerator'
import TemplateList from './pages/TemplateList'
import TemplateEditor from './pages/TemplateEditor'
import GeneratedContentList from './pages/GeneratedContentList'

function App() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          
          {/* Crawl routes */}
          <Route path="crawls" element={<CrawlList />} />
          <Route path="crawls/new" element={<NewCrawl />} />
          <Route path="crawls/:id" element={<CrawlDetails />} />
          
          {/* Content routes */}
          <Route path="content" element={<ContentSearch />} />
          <Route path="content/:id" element={<ContentDetails />} />
          
          {/* New RAG routes */}
          <Route path="generator" element={<ContentGenerator />} />
          <Route path="templates" element={<TemplateList />} />
          <Route path="templates/new" element={<TemplateEditor />} />
          <Route path="templates/:id" element={<TemplateEditor />} />
          <Route path="generated" element={<GeneratedContentList />} />
          
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Box>
  )
}

export default App
