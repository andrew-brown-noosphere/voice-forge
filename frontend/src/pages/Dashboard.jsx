import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Launch as LaunchIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import AnalyticsDashboard from '../components/AnalyticsDashboard'

const Dashboard = () => {
  const navigate = useNavigate()
  const api = useApi()
  
  // State management
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [crawls, setCrawls] = useState([])
  const [domains, setDomains] = useState([])
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [stats, setStats] = useState({
    totalCrawls: 0,
    activeCrawls: 0,
    completedCrawls: 0,
    totalDomains: 0
  })

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load recent crawls and domains in parallel
      const [crawlsData, domainsData] = await Promise.all([
        api.crawls.list(10, 0), // Get last 10 crawls
        api.domains.list()
      ])

      setCrawls(crawlsData)
      setDomains(domainsData)

      // Calculate stats
      const activeCrawls = crawlsData.filter(crawl => 
        ['running', 'pending', 'processing'].includes(crawl.state)
      ).length
      
      const completedCrawls = crawlsData.filter(crawl => 
        crawl.state === 'completed'
      ).length

      setStats({
        totalCrawls: crawlsData.length,
        activeCrawls,
        completedCrawls,
        totalDomains: domainsData.length
      })

    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      // Only show error if it's not a "no organization" error (which is handled by OrganizationGate)
      if (!err.message.includes('no organization')) {
        setError(`Failed to load dashboard: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  // Load data on component mount
  useEffect(() => {
    // Only load data once when component mounts
    let isMounted = true
    
    const loadData = async () => {
      if (isMounted) {
        await loadDashboardData()
      }
    }
    
    loadData()
    
    // Cleanup function
    return () => {
      isMounted = false
    }
  }, []) // Empty dependency array - only run once

  // Handle crawl deletion
  const handleDeleteCrawl = async (crawlId) => {
    try {
      // Show visual feedback during deletion
      const crawlIndex = crawls.findIndex(c => c.crawl_id === crawlId)
      if (crawlIndex !== -1) {
        // Temporarily mark as deleting
        const updatedCrawls = [...crawls]
        updatedCrawls[crawlIndex] = { ...updatedCrawls[crawlIndex], deleting: true }
        setCrawls(updatedCrawls)
      }
      
      await api.crawls.delete(crawlId) // Use the explicit delete method
      
      // Refresh data after deletion with a small delay
      setTimeout(async () => {
        try {
          await loadDashboardData()
        } catch (refreshErr) {
          console.error('Failed to refresh after deletion:', refreshErr)
          // If refresh fails, at least remove the deleted item locally
          setCrawls(prevCrawls => prevCrawls.filter(c => c.crawl_id !== crawlId))
        }
      }, 200)
      
    } catch (err) {
      console.error('Delete crawl error:', err)
      setError(`Failed to delete crawl: ${err.message}`)
      
      // Reset the deleting state on error
      setCrawls(prevCrawls => 
        prevCrawls.map(c => c.crawl_id === crawlId ? { ...c, deleting: false } : c)
      )
    }
  }

  // Get status color for chips
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'running':
      case 'processing':
        return 'primary'
      case 'pending':
        return 'warning'
      case 'failed':
      case 'cancelled':
        return 'error'
      default:
        return 'default'
    }
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return (
      <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading dashboard...</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AnalyticsIcon />}
            onClick={() => setShowAnalytics(!showAnalytics)}
          >
            {showAnalytics ? 'Hide Analytics' : 'Show Analytics'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDashboardData}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/crawls/new')}
          >
            New Crawl
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Analytics Dashboard */}
      {showAnalytics && (
        <Box sx={{ mb: 4 }}>
          <AnalyticsDashboard key="analytics-dashboard" />
        </Box>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Crawls
              </Typography>
              <Typography variant="h4">
                {stats.totalCrawls}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Crawls
              </Typography>
              <Typography variant="h4" color="primary">
                {stats.activeCrawls}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Completed
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats.completedCrawls}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Domains
              </Typography>
              <Typography variant="h4">
                {stats.totalDomains}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/crawls/new')}
                >
                  Start New Crawl
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<LaunchIcon />}
                  onClick={() => navigate('/content')}
                >
                  Search Content
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<PlayIcon />}
                  onClick={() => navigate('/generator')}
                >
                  Generate Content
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Crawled Domains
              </Typography>
              {domains.length > 0 ? (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {domains.slice(0, 5).map((domain, index) => (
                    <Chip 
                      key={index} 
                      label={domain} 
                      variant="outlined" 
                      size="small"
                    />
                  ))}
                  {domains.length > 5 && (
                    <Chip 
                      label={`+${domains.length - 5} more`} 
                      variant="outlined" 
                      size="small"
                      color="primary"
                    />
                  )}
                </Box>
              ) : (
                <Typography color="textSecondary">
                  No domains crawled yet
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Crawls Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Recent Crawls
            </Typography>
            <Button
              size="small"
              onClick={() => navigate('/crawls')}
            >
              View All
            </Button>
          </Box>

          {crawls.length > 0 ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Domain</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Started</TableCell>
                    <TableCell>Delete</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {crawls.slice(0, 5).map((crawl) => (
                    <TableRow key={crawl.crawl_id}>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {crawl.domain}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={crawl.state} 
                          color={getStatusColor(crawl.state)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ minWidth: 120 }}>
                        {crawl.progress ? (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={Math.min((crawl.progress.pages_crawled / Math.max(crawl.progress.pages_discovered, 1)) * 100, 100)} 
                              sx={{ width: 60, mr: 1 }}
                            />
                            <Typography variant="body2">
                              {Math.round(Math.min((crawl.progress.pages_crawled / Math.max(crawl.progress.pages_discovered, 1)) * 100, 100))}%
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="textSecondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(crawl.start_time)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Delete Crawl">
                          <IconButton 
                            size="small"
                            color="error"
                            disabled={crawl.deleting}
                            onClick={() => handleDeleteCrawl(crawl.crawl_id)}
                          >
                            {crawl.deleting ? (
                              <CircularProgress size={16} color="error" />
                            ) : (
                              <DeleteIcon fontSize="small" />
                            )}
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="textSecondary" gutterBottom>
                No crawls found
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/crawls/new')}
              >
                Start Your First Crawl
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default Dashboard