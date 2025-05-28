import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  Stop as StopIcon,
  Launch as LaunchIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material'
import { useParams, useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'

const CrawlDetails = () => {
  const { id: crawlId } = useParams()
  const navigate = useNavigate()
  const api = useApi()
  
  // State management
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [crawl, setCrawl] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [cancelDialog, setCancelDialog] = useState(false)
  const [deleting, setDeleting] = useState(false)

  // Auto-refresh for active crawls
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Load crawl details
  const loadCrawlDetails = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true)
      } else {
        setRefreshing(true)
      }
      setError(null)

      const crawlData = await api.crawls.get(crawlId)
      setCrawl(crawlData)

      // Auto-refresh if crawl is still active
      const isActive = ['running', 'pending', 'processing'].includes(crawlData.status)
      setAutoRefresh(isActive)

    } catch (err) {
      console.error('Failed to load crawl details:', err)
      setError(`Failed to load crawl details: ${err.message}`)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  // Load data on component mount
  useEffect(() => {
    if (crawlId) {
      loadCrawlDetails()
    }
  }, [crawlId])

  // Auto-refresh effect for active crawls
  useEffect(() => {
    let interval
    if (autoRefresh && crawl) {
      interval = setInterval(() => {
        loadCrawlDetails(false) // Refresh without showing loading spinner
      }, 5000) // Refresh every 5 seconds
    }
    
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [autoRefresh, crawl])

  // Handle crawl cancellation
  const handleCancelCrawl = async () => {
    try {
      await api.crawls.cancel(crawlId)
      setCancelDialog(false)
      // Refresh data after cancellation
      loadCrawlDetails(false)
    } catch (err) {
      setError(`Failed to cancel crawl: ${err.message}`)
    }
  }

  // Handle crawl deletion
  const handleDeleteCrawl = async () => {
    try {
      setDeleting(true)
      await api.crawls.cancel(crawlId) // This might be delete endpoint
      navigate('/crawls') // Navigate back to crawl list
    } catch (err) {
      setError(`Failed to delete crawl: ${err.message}`)
      setDeleting(false)
    }
  }

  // Get status color and icon
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon />
      case 'running':
      case 'processing':
        return <PlayArrowIcon />
      case 'failed':
      case 'cancelled':
        return <ErrorIcon />
      default:
        return <InfoIcon />
    }
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  // Format duration
  const formatDuration = (startTime, endTime) => {
    if (!startTime) return 'N/A'
    
    const start = new Date(startTime)
    const end = endTime ? new Date(endTime) : new Date()
    const duration = end - start
    
    const hours = Math.floor(duration / (1000 * 60 * 60))
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((duration % (1000 * 60)) / 1000)
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    } else {
      return `${seconds}s`
    }
  }

  if (loading) {
    return (
      <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading crawl details...</Typography>
      </Box>
    )
  }

  if (!crawl) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">
          Crawl not found or you don't have permission to view it.
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/crawls')}
          sx={{ mt: 2 }}
        >
          Back to Crawls
        </Button>
      </Box>
    )
  }

  const isActive = ['running', 'pending', 'processing'].includes(crawl.status)
  const canCancel = isActive

  return (
    <Box sx={{ p: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => navigate('/crawls')} sx={{ mr: 2 }}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" component="h1">
              Crawl Details
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              {crawl.domain}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={refreshing ? <CircularProgress size={16} /> : <RefreshIcon />}
            onClick={() => loadCrawlDetails(false)}
            disabled={refreshing}
          >
            Refresh
          </Button>
          
          {canCancel && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<StopIcon />}
              onClick={() => setCancelDialog(true)}
            >
              Cancel Crawl
            </Button>
          )}
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Auto-refresh indicator */}
      {autoRefresh && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>Auto-refreshing every 5 seconds while crawl is active</span>
            <Button size="small" onClick={() => setAutoRefresh(false)}>
              Stop Auto-refresh
            </Button>
          </Box>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Status and Progress Card */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Status & Progress
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {getStatusIcon(crawl.status)}
                  <Chip 
                    label={crawl.status.charAt(0).toUpperCase() + crawl.status.slice(1)} 
                    color={getStatusColor(crawl.status)}
                    sx={{ ml: 1 }}
                  />
                </Box>
                
                {crawl.progress !== undefined && (
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Progress</Typography>
                      <Typography variant="body2">{Math.round(crawl.progress * 100)}%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={crawl.progress * 100} 
                    />
                  </Box>
                )}
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Timing Information */}
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Started
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(crawl.started_at)}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    {crawl.completed_at ? 'Completed' : 'Duration'}
                  </Typography>
                  <Typography variant="body1">
                    {crawl.completed_at 
                      ? formatDate(crawl.completed_at)
                      : formatDuration(crawl.started_at, crawl.completed_at)
                    }
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Total Duration
                  </Typography>
                  <Typography variant="body1">
                    {formatDuration(crawl.started_at, crawl.completed_at)}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Configuration Card */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Domain
                  </Typography>
                  <Typography variant="body1" noWrap>
                    {crawl.domain}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Max Depth
                  </Typography>
                  <Typography variant="body1">
                    {crawl.config?.max_depth || 'N/A'}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Max Pages
                  </Typography>
                  <Typography variant="body1">
                    {crawl.config?.max_pages || 'N/A'}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Delay (seconds)
                  </Typography>
                  <Typography variant="body1">
                    {crawl.config?.delay || 'N/A'}
                  </Typography>
                </Grid>
              </Grid>

              {crawl.config?.patterns && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    URL Patterns
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {crawl.config.patterns.map((pattern, index) => (
                      <Chip 
                        key={index} 
                        label={pattern} 
                        variant="outlined" 
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Crawl Statistics
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="h4" color="primary">
                    {crawl.pages_crawled || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Pages Crawled
                  </Typography>
                </Grid>
                
                <Grid item xs={6} sm={3}>
                  <Typography variant="h4" color="success.main">
                    {crawl.pages_processed || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Pages Processed
                  </Typography>
                </Grid>
                
                <Grid item xs={6} sm={3}>
                  <Typography variant="h4" color="error.main">
                    {crawl.errors_count || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Errors
                  </Typography>
                </Grid>
                
                <Grid item xs={6} sm={3}>
                  <Typography variant="h4">
                    {crawl.content_extracted || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Content Items
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Error Log */}
        {crawl.errors && crawl.errors.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error">
                  Errors ({crawl.errors.length})
                </Typography>
                
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Time</TableCell>
                        <TableCell>URL</TableCell>
                        <TableCell>Error</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {crawl.errors.slice(0, 10).map((error, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            {formatDate(error.timestamp)}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {error.url}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="error">
                              {error.message}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                
                {crawl.errors.length > 10 && (
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Showing first 10 of {crawl.errors.length} errors
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Actions
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<LaunchIcon />}
                  onClick={() => navigate('/content')}
                >
                  View Extracted Content
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/generator')}
                >
                  Generate Content
                </Button>
                
                {!isActive && (
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={deleting ? <CircularProgress size={16} /> : <DeleteIcon />}
                    onClick={handleDeleteCrawl}
                    disabled={deleting}
                  >
                    Delete Crawl
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cancel Confirmation Dialog */}
      <Dialog
        open={cancelDialog}
        onClose={() => setCancelDialog(false)}
      >
        <DialogTitle>
          Cancel Crawl
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to cancel this crawl? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialog(false)}>
            Keep Running
          </Button>
          <Button onClick={handleCancelCrawl} color="error" variant="contained">
            Cancel Crawl
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default CrawlDetails