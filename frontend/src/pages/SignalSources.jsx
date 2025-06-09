import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Divider,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material'
import {
  Add as AddIcon,
  Search as SearchIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlayArrow as ScanIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  Reddit as RedditIcon,
  Twitter as TwitterIcon,
  GitHub as GitHubIcon,
  LinkedIn as LinkedInIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material'
import { useApi } from '../hooks/useApi'

const PLATFORM_CONFIGS = {
  reddit: {
    name: 'Reddit',
    icon: RedditIcon,
    color: '#FF4500',
    sourceType: 'subreddit'
  },
  twitter: {
    name: 'Twitter',
    icon: TwitterIcon,
    color: '#1DA1F2',
    sourceType: 'hashtag'
  },
  github: {
    name: 'GitHub',
    icon: GitHubIcon,
    color: '#333',
    sourceType: 'repository'
  },
  linkedin: {
    name: 'LinkedIn',
    icon: LinkedInIcon,
    color: '#0077B5',
    sourceType: 'company'
  }
}

function SignalSources() {
  const navigate = useNavigate()
  const location = useLocation()
  const api = useApi()
  
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [scanningSource, setScanningSource] = useState(null)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, source: null })

  useEffect(() => {
    loadSources()
    
    // Check for success messages from signal scan
    if (location.state?.message) {
      setError(null)
      // Show success message by setting it as a positive message
      if (location.state.message.includes('complete') || location.state.message.includes('Saved')) {
        setSuccessMessage(location.state.message)
      } else {
        setError(location.state.message)
      }
      // Clear the state to prevent showing message again
      window.history.replaceState({}, document.title)
    }
  }, [])

  const loadSources = async () => {
    try {
      setLoading(true)
      const data = await api.signals.getSources()
      setSources(data)
      setError(null)
    } catch (err) {
      console.error('Failed to load signal sources:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleScanSource = async (source) => {
    try {
      setScanningSource(source.source_id)
      console.log(`🔍 Scanning source: ${source.platform}/${source.source_name}`)
      
      const result = await api.signals.scanSource(source.source_id)
      
      console.log('✅ Scan result:', result)
      
      // Show success message
      setError(null)
      
      // Refresh sources to update last_crawled_at
      await loadSources()
      
      // Navigate to signals page to see results
      navigate('/signals', {
        state: {
          message: `🔍 Scan complete! Found ${result.signals_found} signals from ${source.platform}/${source.source_name}`,
          source: source.source_name
        }
      })
    } catch (err) {
      console.error('Failed to scan source:', err)
      setError(`Failed to scan ${source.source_name}: ${err.message}`)
    } finally {
      setScanningSource(null)
    }
  }

  const handleToggleSource = async (source) => {
    try {
      await api.signals.updateSource(source.source_id, {
        is_active: !source.is_active
      })
      await loadSources()
    } catch (err) {
      console.error('Failed to toggle source:', err)
      setError(`Failed to update ${source.source_name}: ${err.message}`)
    }
  }

  const handleDeleteSource = async () => {
    try {
      const source = deleteDialog.source
      await api.signals.deleteSource(source.source_id)
      await loadSources()
      setDeleteDialog({ open: false, source: null })
    } catch (err) {
      console.error('Failed to delete source:', err)
      setError(`Failed to delete source: ${err.message}`)
    }
  }

  const getPlatformIcon = (platform) => {
    const IconComponent = PLATFORM_CONFIGS[platform]?.icon || TrendingUpIcon
    return <IconComponent sx={{ color: PLATFORM_CONFIGS[platform]?.color }} />
  }

  const formatLastCrawled = (lastCrawledAt) => {
    if (!lastCrawledAt) return 'Never'
    
    const date = new Date(lastCrawledAt)
    const now = new Date()
    const diffMs = now - date
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const getSourcePerformance = (source) => {
    const metrics = source.performance_metrics || {}
    return {
      totalSignals: metrics.total_signals || 0,
      avgRelevance: metrics.avg_relevance_score || 0,
      lastSignals: metrics.signals_last_week || 0
    }
  }

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon color="primary" />
            Signal Sources
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage your persistent signal monitoring sources and run scans to discover new signals
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadSources}
          disabled={loading}
        >
          Refresh
        </Button>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/signals/scan')}
        >
          Add Sources
        </Button>
      </Box>

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Sources List */}
      {sources.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No signal sources configured
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Add sources to start monitoring communities and discovering signals automatically
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/signals/scan')}
            >
              Add Your First Sources
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {sources.map((source) => {
            const performance = getSourcePerformance(source)
            const isScanning = scanningSource === source.source_id
            
            return (
              <Grid item xs={12} md={6} lg={4} key={source.source_id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'background.paper' }}>
                        {getPlatformIcon(source.platform)}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {source.platform === 'reddit' ? 'r/' : ''}{source.source_name}
                          <Chip 
                            label={source.is_active ? 'Active' : 'Inactive'} 
                            size="small"
                            color={source.is_active ? 'success' : 'default'}
                          />
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {PLATFORM_CONFIGS[source.platform]?.name} • {source.crawl_frequency}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Keywords */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="textSecondary">Keywords:</Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                        {source.keywords?.slice(0, 3).map((keyword, index) => (
                          <Chip key={index} label={keyword} size="small" variant="outlined" />
                        ))}
                        {source.keywords?.length > 3 && (
                          <Chip label={`+${source.keywords.length - 3} more`} size="small" variant="outlined" />
                        )}
                      </Box>
                    </Box>

                    {/* Performance Metrics */}
                    <Box sx={{ mb: 2 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6">{performance.totalSignals}</Typography>
                            <Typography variant="caption">Total Signals</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6">{performance.lastSignals}</Typography>
                            <Typography variant="caption">This Week</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6">{Math.round(performance.avgRelevance * 100)}%</Typography>
                            <Typography variant="caption">Avg Relevance</Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>

                    {/* Last Crawled */}
                    <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 2 }}>
                      <ScheduleIcon fontSize="small" />
                      Last scan: {formatLastCrawled(source.last_crawled_at)}
                    </Typography>

                    {/* Actions */}
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={isScanning ? <CircularProgress size={16} /> : <ScanIcon />}
                        onClick={() => handleScanSource(source)}
                        disabled={!source.is_active || isScanning}
                        sx={{ flexGrow: 1 }}
                      >
                        {isScanning ? 'Scanning...' : 'Scan Now'}
                      </Button>
                      
                      <Tooltip title={source.is_active ? 'Deactivate' : 'Activate'}>
                        <IconButton
                          onClick={() => handleToggleSource(source)}
                          color={source.is_active ? 'primary' : 'default'}
                        >
                          <Switch checked={source.is_active} size="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Delete source">
                        <IconButton
                          onClick={() => setDeleteDialog({ open: true, source })}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )
          })}
        </Grid>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, source: null })}
      >
        <DialogTitle>Delete Signal Source</DialogTitle>
        <DialogContent>
          Are you sure you want to delete the signal source{' '}
          <strong>{deleteDialog.source?.platform}/{deleteDialog.source?.source_name}</strong>?
          This will stop monitoring this source and cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, source: null })}>
            Cancel
          </Button>
          <Button onClick={handleDeleteSource} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SignalSources
