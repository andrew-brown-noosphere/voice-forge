import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel
} from '@mui/material'
import {
  Storage as StorageIcon,
  Analytics as AnalyticsIcon,
  Language as LanguageIcon,
  Speed as SpeedIcon,
  CloudSync as CloudSyncIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts'
import { useApi } from '../hooks/useApi'

// Word Cloud Component (simple implementation)
const SimpleWordCloud = ({ words, width = 400, height = 300 }) => {
  if (!words || words.length === 0) {
    return (
      <Box sx={{ 
        width, 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: 'background.paper',
        borderRadius: 1,
        border: '1px solid',
        borderColor: 'divider'
      }}>
        <Typography color="textSecondary">No word data available</Typography>
      </Box>
    )
  }

  const maxValue = Math.max(...words.map(w => w.value))
  const minValue = Math.min(...words.map(w => w.value))

  return (
    <Box sx={{ 
      width, 
      height, 
      display: 'flex', 
      flexWrap: 'wrap', 
      alignItems: 'center', 
      justifyContent: 'center',
      gap: 1,
      p: 2,
      backgroundColor: 'background.paper',
      borderRadius: 1,
      border: '1px solid',
      borderColor: 'divider',
      overflow: 'hidden'
    }}>
      {words.slice(0, 50).map((word, index) => {
        const fontSize = Math.max(
          12,
          Math.min(
            32,
            12 + (word.value - minValue) / (maxValue - minValue) * 20
          )
        )
        
        const colors = [
          '#1976d2', '#d32f2f', '#2e7d32', '#ed6c02', 
          '#9c27b0', '#00796b', '#5d4037', '#616161'
        ]
        
        return (
          <Typography
            key={index}
            component="span"
            sx={{
              fontSize: `${fontSize}px`,
              color: colors[index % colors.length],
              fontWeight: Math.floor(fontSize / 4) * 100 + 300,
              cursor: 'default',
              userSelect: 'none',
              '&:hover': {
                opacity: 0.7
              }
            }}
            title={`${word.text}: ${word.value} occurrences`}
          >
            {word.text}
          </Typography>
        )
      })}
    </Box>
  )
}

const AnalyticsDashboard = () => {
  const api = useApi()
  const [analytics, setAnalytics] = useState(null)
  const [wordCloudData, setWordCloudData] = useState(null)
  const [topDomains, setTopDomains] = useState([])
  const [contentTrends, setContentTrends] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [lastLoadTime, setLastLoadTime] = useState(null)

  const loadAnalytics = async () => {
    // Don't reload if data is fresh (less than 30 seconds old)
    const now = Date.now()
    if (lastLoadTime && (now - lastLoadTime) < 30000) {
      console.log('Analytics data is fresh, skipping reload')
      return
    }

    try {
      setLoading(true)
      setError(null)

      // Load dashboard data first to check if we have content
      const dashboardData = await api.request('/analytics/dashboard')
      
      // If no content, skip expensive analytics calls
      if (!dashboardData?.overview?.total_content_items) {
        setAnalytics(dashboardData || { overview: { total_content_items: 0, total_pages_crawled: 0, total_chunks: 0 } })
        setWordCloudData({ words: [], total_words: 0, unique_words: 0 })
        setTopDomains([])
        setContentTrends({ content_trend: [], crawl_trend: [] })
        setLastLoadTime(now)
        return
      }

      // Load remaining analytics data in parallel
      const [wordCloudResponse, domainsData, trendsData] = await Promise.all([
        api.request('/analytics/wordcloud?limit=100'),
        api.request('/analytics/top-domains?limit=10'),
        api.request('/analytics/content-trends?days=30')
      ])

      setAnalytics(dashboardData)
      setWordCloudData(wordCloudResponse)
      setTopDomains(domainsData)
      setContentTrends(trendsData)
      setLastLoadTime(now)

    } catch (err) {
      console.error('Failed to load analytics:', err)
      // Only show error if it's not an auth/org error
      if (!err.message.includes('organization') && !err.message.includes('401')) {
        setError(`Failed to load analytics: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Only load analytics once when component mounts
    let isMounted = true
    
    const loadData = async () => {
      if (isMounted && !analytics) {
        await loadAnalytics()
      }
    }
    
    loadData()
    
    // Cleanup function
    return () => {
      isMounted = false
    }
  }, []) // Empty dependency array - only run once

  if (loading) {
    return (
      <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading analytics...</Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" action={
          <IconButton color="inherit" size="small" onClick={loadAnalytics}>
            <RefreshIcon />
          </IconButton>
        }>
          {error}
        </Alert>
      </Box>
    )
  }

  const colors = ['#1976d2', '#d32f2f', '#2e7d32', '#ed6c02', '#9c27b0', '#00796b']

  // Prepare chart data
  const contentTypeChartData = Object.entries(analytics?.distributions?.content_types || {}).map(([type, count], index) => ({
    name: type,
    value: count,
    fill: colors[index % colors.length]
  }))

  const domainChartData = Object.entries(analytics?.distributions?.domains || {}).slice(0, 8).map(([domain, count], index) => ({
    name: domain.length > 20 ? domain.substring(0, 20) + '...' : domain,
    value: count,
    fill: colors[index % colors.length]
  }))

  const crawlStatusData = Object.entries(analytics?.distributions?.crawl_statuses || {}).map(([status, count], index) => ({
    name: status,
    value: count,
    fill: colors[index % colors.length]
  }))

  return (
    <Box sx={{ p: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            📊 Analytics Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Comprehensive insights into your crawled data and content
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={showAdvanced}
                onChange={(e) => setShowAdvanced(e.target.checked)}
              />
            }
            label="Advanced View"
          />
          <IconButton onClick={loadAnalytics} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Overview Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <StorageIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" color="primary">
                {analytics?.overview?.total_pages_crawled?.toLocaleString() || 0}
              </Typography>
              <Typography color="textSecondary">Pages Crawled</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AnalyticsIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" color="success.main">
                {analytics?.overview?.total_content_items?.toLocaleString() || 0}
              </Typography>
              <Typography color="textSecondary">Content Items</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CloudSyncIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" color="info.main">
                {analytics?.overview?.total_chunks?.toLocaleString() || 0}
              </Typography>
              <Typography color="textSecondary">Text Chunks</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <AssessmentIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" color="warning.main">
                {analytics?.dataset_metrics?.total_text_mb || 0}MB
              </Typography>
              <Typography color="textSecondary">Dataset Size</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <SpeedIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
              <Typography variant="h4" color="secondary.main">
                {analytics?.embeddings?.embedding_coverage_percent || 0}%
              </Typography>
              <Typography color="textSecondary">AI Ready</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Word Cloud */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🌤️ Content Word Cloud
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Most frequently used words across your crawled content
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <SimpleWordCloud 
                  words={wordCloudData?.words || []} 
                  width={600} 
                  height={300} 
                />
              </Box>
              {wordCloudData && (
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 3 }}>
                  <Chip 
                    size="small" 
                    label={`${wordCloudData.total_words} total words`} 
                    variant="outlined" 
                  />
                  <Chip 
                    size="small" 
                    label={`${wordCloudData.unique_words} unique words`} 
                    variant="outlined" 
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Processing Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">AI Processing</Typography>
                  <Typography variant="body2">{analytics?.dataset_metrics?.processing_rate_percent || 0}%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={analytics?.dataset_metrics?.processing_rate_percent || 0}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Embedding Coverage</Typography>
                  <Typography variant="body2">{analytics?.embeddings?.embedding_coverage_percent || 0}%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={analytics?.embeddings?.embedding_coverage_percent || 0}
                  color="secondary"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Processed</Typography>
                  <Typography variant="h6">{analytics?.processing?.processed_content || 0}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Pending</Typography>
                  <Typography variant="h6">{analytics?.processing?.unprocessed_content || 0}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>📄 Content Types</Typography>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={contentTypeChartData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {contentTypeChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>🌐 Top Domains</Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={domainChartData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={80} />
                    <RechartsTooltip />
                    <Bar dataKey="value" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>⚡ Crawl Status</Typography>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={crawlStatusData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {crawlStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Advanced Analytics */}
      {showAdvanced && (
        <>
          {/* Content Trends */}
          {contentTrends && (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📈 Content Creation Trends (Last 30 Days)
                    </Typography>
                    <Box sx={{ height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={contentTrends.content_trend}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="content_count" 
                            stroke="#1976d2" 
                            name="Content Items"
                          />
                          <Line 
                            type="monotone" 
                            dataKey="unique_domains" 
                            stroke="#d32f2f" 
                            name="Unique Domains"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Top Domains Detailed */}
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    🏆 Top Domains - Detailed View
                  </Typography>
                  <Grid container spacing={2}>
                    {topDomains.slice(0, 6).map((domain, index) => (
                      <Grid item xs={12} md={6} lg={4} key={index}>
                        <Paper sx={{ p: 2, height: '100%' }}>
                          <Typography variant="subtitle2" noWrap title={domain.domain}>
                            {domain.domain}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2" color="textSecondary">Content</Typography>
                              <Typography variant="body2">{domain.content_count}</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2" color="textSecondary">Size</Typography>
                              <Typography variant="body2">{domain.total_mb}MB</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2" color="textSecondary">Processed</Typography>
                              <Typography variant="body2">{domain.processing_rate}%</Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={domain.processing_rate}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                          </Box>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  )
}

export default AnalyticsDashboard