import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Badge,
  Avatar,
  Paper,
  Tabs,
  Tab,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Reddit as RedditIcon,
  Twitter as TwitterIcon,
  GitHub as GitHubIcon,
  LinkedIn as LinkedInIcon,
  TrendingUp as TrendingUpIcon,
  Comment as CommentIcon,
  ThumbUp as ThumbUpIcon,
  Psychology as PsychologyIcon,
  Launch as LaunchIcon,
  AutoAwesome as AutoAwesomeIcon,
  FilterList as FilterIcon,
  Source as SourceIcon
} from '@mui/icons-material'
import { useApi } from '../hooks/useApi'

const SIGNAL_TYPE_COLORS = {
  question: 'primary',
  complaint: 'error',
  feature_request: 'warning',
  competitive_mention: 'secondary',
  industry_trend: 'info',
  customer_success: 'success',
  discussion: 'default'
}

const SIGNAL_TYPE_LABELS = {
  question: 'Question',
  complaint: 'Complaint',
  feature_request: 'Feature Request',
  competitive_mention: 'Competitive Mention',
  industry_trend: 'Industry Trend',
  customer_success: 'Customer Success',
  discussion: 'Discussion'
}

const PLATFORM_CONFIGS = {
  reddit: {
    name: 'Reddit',
    icon: RedditIcon,
    color: '#FF4500',
    sources: {
      label: 'Subreddits (without r/)',
      placeholder: 'startups,SaaS,webdev,programming',
      help: 'Enter subreddit names separated by commas'
    },
    status: 'active'
  },
  twitter: {
    name: 'Twitter',
    icon: TwitterIcon,
    color: '#1DA1F2',
    sources: {
      label: 'Hashtags or Users',
      placeholder: '#saas,#startup,@username',
      help: 'Enter hashtags (with #) or usernames (with @) separated by commas'
    },
    status: 'coming_soon'
  },
  github: {
    name: 'GitHub',
    icon: GitHubIcon,
    color: '#333',
    sources: {
      label: 'Repositories',
      placeholder: 'facebook/react,microsoft/vscode',
      help: 'Enter repository names in owner/repo format separated by commas'
    },
    status: 'coming_soon'
  },
  linkedin: {
    name: 'LinkedIn',
    icon: LinkedInIcon,
    color: '#0077B5',
    sources: {
      label: 'Company Pages or Hashtags',
      placeholder: '#technology,company/microsoft',
      help: 'Enter hashtags (with #) or company pages separated by commas'
    },
    status: 'coming_soon'
  }
}

function Signals() {
  const navigate = useNavigate()
  const location = useLocation()
  const api = useApi()
  const [signals, setSignals] = useState([])
  const [supportedPlatforms, setSupportedPlatforms] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedPlatform, setSelectedPlatform] = useState('reddit')
  const [discoveryDialogOpen, setDiscoveryDialogOpen] = useState(false)
  const [responseDialogOpen, setResponseDialogOpen] = useState(false)
  const [selectedSignal, setSelectedSignal] = useState(null)
  const [generatedResponse, setGeneratedResponse] = useState(null)
  const [responseLoading, setResponseLoading] = useState(false)

  // Filter states
  const [filterPlatform, setFilterPlatform] = useState('all')
  const [filterSignalType, setFilterSignalType] = useState('all')

  // Discovery form state
  const [discoveryForm, setDiscoveryForm] = useState({
    platform: 'reddit',
    sources: 'startups,SaaS,webdev',
    keywords: 'api,integration,automation',
    timeFilter: 'week',
    maxItemsPerSource: 50,
    relevanceThreshold: 0.6
  })

  // Response form state
  const [responseForm, setResponseForm] = useState({
    tone: 'professional',
    responseType: 'comment_reply',
    includeContext: true
  })

  // Subreddit discovery state (removed - now using dedicated page)
  // const [subredditDiscoveryOpen, setSubredditDiscoveryOpen] = useState(false)
  // const [subredditRecommendations, setSubredditRecommendations] = useState(null)
  const [discoveryLoading, setDiscoveryLoading] = useState(false)
  const [selectedPersona, setSelectedPersona] = useState('')
  const [availablePersonas, setAvailablePersonas] = useState([])

  // Load signals and platform info on component mount
  useEffect(() => {
    loadSignals()
    loadSupportedPlatforms()
    loadAvailablePersonas()
    
    // Check for success messages from signal scan
    if (location.state?.message) {
      setError(location.state.message)
      // Clear the state to prevent showing message again
      window.history.replaceState({}, document.title)
    }
  }, [])

  const loadSignals = async () => {
    setLoading(true)
    setError(null)
    try {
      // Use new abstracted signals API
      const params = {
        limit: 20,
        offset: 0,
        ...(filterPlatform !== 'all' && { platform: filterPlatform }),
        ...(filterSignalType !== 'all' && { signal_type: filterSignalType })
      }
      
      const data = await api.signals.list(params)
      setSignals(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadSupportedPlatforms = async () => {
    try {
      const data = await api.signals.getSupportedPlatforms()
      setSupportedPlatforms(data.platforms)
    } catch (err) {
      console.warn('Could not load supported platforms:', err)
      // Use default platforms if API fails
      setSupportedPlatforms(Object.entries(PLATFORM_CONFIGS).map(([id, config]) => ({
        id,
        name: config.name,
        status: config.status
      })))
    }
  }

  const loadAvailablePersonas = async () => {
    try {
      // Load personas from Gypsum API
      const personas = await api.gypsum.getPersonas()
      setAvailablePersonas(personas)
      if (personas.length > 0) {
        setSelectedPersona(personas[0].persona_id)
      }
    } catch (err) {
      console.warn('Could not load personas:', err)
      // Set a default if no personas available
      setAvailablePersonas([])
    }
  }

  const handleDiscoverSignals = async () => {
    setLoading(true)
    setError(null)
    try {
      const sources = discoveryForm.sources.split(',').map(s => s.trim()).filter(s => s)
      const keywords = discoveryForm.keywords.split(',').map(k => k.trim()).filter(k => k)
      
      const request = {
        platform: discoveryForm.platform,
        sources,
        keywords,
        time_filter: discoveryForm.timeFilter,
        max_items_per_source: discoveryForm.maxItemsPerSource,
        relevance_threshold: discoveryForm.relevanceThreshold
      }
      
      const result = await api.signals.discover(request)
      
      setDiscoveryDialogOpen(false)
      // Reload signals to show new discoveries
      await loadSignals()
      
      // Show success message
      if (result.signals_found > 0) {
        setError(`Successfully discovered ${result.signals_found} new signals from ${result.platform}!`)
      } else {
        setError(`No new signals found on ${result.platform}. Try adjusting your keywords or time filter.`)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateResponse = async (signal) => {
    setSelectedSignal(signal)
    setResponseDialogOpen(true)
    setGeneratedResponse(null)
  }

  const generateResponse = async () => {
    setResponseLoading(true)
    setError(null)
    try {
      const response = await api.signals.generateResponse({
        signal_id: selectedSignal.signal_id,
        platform: selectedSignal.platform,
        tone: responseForm.tone,
        response_type: responseForm.responseType,
        include_context: responseForm.includeContext
      })
      
      setGeneratedResponse(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setResponseLoading(false)
    }
  }

  const handleSignalScan = async () => {
    // Navigate to the Signal Scan configuration page
    navigate('/signals/scan')
  }

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffDays > 0) {
      return `${diffDays}d ago`
    } else if (diffHours > 0) {
      return `${diffHours}h ago`
    } else {
      return 'Recently'
    }
  }

  const getPlatformIcon = (platform) => {
    const config = PLATFORM_CONFIGS[platform]
    if (config && config.icon) {
      const IconComponent = config.icon
      return <IconComponent sx={{ color: config.color }} />
    }
    return <TrendingUpIcon />
  }

  const getPlatformMetadata = (signal) => {
    if (signal.platform === 'reddit') {
      const reddit = signal.platform_metadata || {}
      return {
        source: `r/${reddit.subreddit || 'unknown'}`,
        metrics: `${reddit.score || 0} upvotes • ${reddit.num_comments || 0} comments`
      }
    } else if (signal.platform === 'twitter') {
      const metrics = signal.engagement_metrics || {}
      return {
        source: `@${signal.author || 'unknown'}`,
        metrics: `${metrics.likes || 0} likes • ${metrics.retweets || 0} retweets`
      }
    } else if (signal.platform === 'github') {
      const github = signal.platform_metadata || {}
      return {
        source: github.repository || 'unknown',
        metrics: `${github.issue_type || 'issue'}`
      }
    } else {
      return {
        source: signal.author || 'unknown',
        metrics: 'See details'
      }
    }
  }

  const filteredSignals = signals.filter(signal => {
    if (filterPlatform !== 'all' && signal.platform !== filterPlatform) return false
    if (filterSignalType !== 'all' && signal.signal_type !== filterSignalType) return false
    return true
  })

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingUpIcon color="primary" />
          Social Signals
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadSignals}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<SourceIcon />}
            onClick={() => navigate('/signals/sources')}
            sx={{ 
              bgcolor: 'secondary.50',
              borderColor: 'secondary.main',
              color: 'secondary.main',
              '&:hover': {
                bgcolor: 'secondary.100'
              }
            }}
          >
            Manage Sources
          </Button>
          <Button
            variant="outlined"
            startIcon={<PsychologyIcon />}
            onClick={handleSignalScan}
            disabled={discoveryLoading}
            sx={{ 
              bgcolor: 'primary.50',
              borderColor: 'primary.main',
              color: 'primary.main',
              '&:hover': {
                bgcolor: 'primary.100'
              }
            }}
          >
            {discoveryLoading ? 'Analyzing...' : '🔍 Signal Scan'}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setDiscoveryDialogOpen(true)}
            disabled={loading}
          >
            Discover Signals
          </Button>
        </Box>
      </Box>

      {/* Platform and Filter Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Filter Signals</Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Platform</InputLabel>
              <Select
                value={filterPlatform}
                onChange={(e) => setFilterPlatform(e.target.value)}
                label="Platform"
              >
                <MenuItem value="all">All Platforms</MenuItem>
                {Object.entries(PLATFORM_CONFIGS).map(([platform, config]) => (
                  <MenuItem key={platform} value={platform}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getPlatformIcon(platform)}
                      {config.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Signal Type</InputLabel>
              <Select
                value={filterSignalType}
                onChange={(e) => setFilterSignalType(e.target.value)}
                label="Signal Type"
              >
                <MenuItem value="all">All Types</MenuItem>
                {Object.entries(SIGNAL_TYPE_LABELS).map(([type, label]) => (
                  <MenuItem key={type} value={type}>{label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Typography variant="body2" color="textSecondary">
              Showing {filteredSignals.length} of {signals.length} signals
            </Typography>
          </Box>
        </Box>
      </Paper>

      {error && (
        <Alert 
          severity={error.includes('Successfully') ? 'success' : 'error'} 
          sx={{ mb: 2 }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Grid container spacing={3}>
        {filteredSignals.length === 0 && !loading ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <TrendingUpIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No signals found
              </Typography>
              <Typography color="textSecondary" paragraph>
                Start by discovering signals from your preferred platforms
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setDiscoveryDialogOpen(true)}
              >
                Discover Your First Signals
              </Button>
            </Paper>
          </Grid>
        ) : (
          filteredSignals.map((signal) => {
            const platformMeta = getPlatformMetadata(signal)
            
            return (
              <Grid item xs={12} md={6} lg={4} key={signal.signal_id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Chip
                        label={SIGNAL_TYPE_LABELS[signal.signal_type] || signal.signal_type}
                        color={SIGNAL_TYPE_COLORS[signal.signal_type] || 'default'}
                        size="small"
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        {getPlatformIcon(signal.platform)}
                        <Typography variant="caption" color="textSecondary">
                          {platformMeta.source}
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Typography variant="h6" component="h3" gutterBottom sx={{ fontSize: '1rem' }}>
                      {signal.title}
                    </Typography>
                    
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      {signal.content ? 
                        (signal.content.length > 150 ? 
                          `${signal.content.substring(0, 150)}...` : 
                          signal.content
                        ) : 
                        'No content'
                      }
                    </Typography>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        {platformMeta.metrics}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {formatTimeAgo(signal.discovered_at)}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Relevance:</strong> {Math.round(signal.relevance_score * 100)}%
                      </Typography>
                      <Typography variant="body2">
                        <strong>Engagement:</strong> {Math.round(signal.engagement_potential * 100)}%
                      </Typography>
                    </Box>
                    
                    <LinearProgress 
                      variant="determinate" 
                      value={signal.relevance_score * 100} 
                      sx={{ mb: 1 }}
                    />
                  </CardContent>
                  
                  <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      startIcon={<LaunchIcon />}
                      href={signal.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Original
                    </Button>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<AutoAwesomeIcon />}
                      onClick={() => handleGenerateResponse(signal)}
                    >
                      Generate Response
                    </Button>
                  </Box>
                </Card>
              </Grid>
            )
          })
        )}
      </Grid>

      {/* Discovery Dialog */}
      <Dialog open={discoveryDialogOpen} onClose={() => setDiscoveryDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Discover Social Signals</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <FormControl>
              <InputLabel>Platform</InputLabel>
              <Select
                value={discoveryForm.platform}
                onChange={(e) => {
                  const platform = e.target.value
                  setDiscoveryForm({ 
                    ...discoveryForm, 
                    platform,
                    sources: platform === 'reddit' ? 'startups,SaaS,webdev' :
                            platform === 'twitter' ? '#saas,#startup' :
                            platform === 'github' ? 'facebook/react,microsoft/vscode' :
                            '#technology,company/microsoft'
                  })
                }}
                label="Platform"
              >
                {Object.entries(PLATFORM_CONFIGS).map(([platform, config]) => (
                  <MenuItem key={platform} value={platform} disabled={config.status !== 'active'}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getPlatformIcon(platform)}
                      {config.name}
                      {config.status !== 'active' && (
                        <Chip size="small" label="Coming Soon" color="default" />
                      )}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label={PLATFORM_CONFIGS[discoveryForm.platform]?.sources.label || 'Sources'}
              value={discoveryForm.sources}
              onChange={(e) => setDiscoveryForm({ ...discoveryForm, sources: e.target.value })}
              placeholder={PLATFORM_CONFIGS[discoveryForm.platform]?.sources.placeholder}
              helperText={PLATFORM_CONFIGS[discoveryForm.platform]?.sources.help}
              fullWidth
            />
            
            <TextField
              label="Keywords (comma-separated)"
              value={discoveryForm.keywords}
              onChange={(e) => setDiscoveryForm({ ...discoveryForm, keywords: e.target.value })}
              placeholder="api,integration,automation,saas"
              helperText="Keywords to search for in posts"
              fullWidth
            />
            
            <FormControl>
              <InputLabel>Time Filter</InputLabel>
              <Select
                value={discoveryForm.timeFilter}
                onChange={(e) => setDiscoveryForm({ ...discoveryForm, timeFilter: e.target.value })}
                label="Time Filter"
              >
                <MenuItem value="day">Past Day</MenuItem>
                <MenuItem value="week">Past Week</MenuItem>
                <MenuItem value="month">Past Month</MenuItem>
                <MenuItem value="year">Past Year</MenuItem>
                <MenuItem value="all">All Time</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Max Items per Source"
              type="number"
              value={discoveryForm.maxItemsPerSource}
              onChange={(e) => setDiscoveryForm({ ...discoveryForm, maxItemsPerSource: parseInt(e.target.value) })}
              inputProps={{ min: 1, max: 100 }}
            />
            
            <TextField
              label="Relevance Threshold"
              type="number"
              value={discoveryForm.relevanceThreshold}
              onChange={(e) => setDiscoveryForm({ ...discoveryForm, relevanceThreshold: parseFloat(e.target.value) })}
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              helperText="Minimum relevance score (0-1) to include signals"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDiscoveryDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleDiscoverSignals} 
            disabled={loading || PLATFORM_CONFIGS[discoveryForm.platform]?.status !== 'active'}
          >
            {loading ? 'Discovering...' : 'Discover Signals'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Response Generation Dialog */}
      <Dialog open={responseDialogOpen} onClose={() => setResponseDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          Generate Response to Signal
        </DialogTitle>
        <DialogContent>
          {selectedSignal && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              {/* Signal Info */}
              <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {getPlatformIcon(selectedSignal.platform)}
                  <Typography variant="h6">{selectedSignal.title}</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {selectedSignal.content}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Chip label={getPlatformMetadata(selectedSignal).source} size="small" />
                  <Chip label={SIGNAL_TYPE_LABELS[selectedSignal.signal_type]} size="small" color="primary" />
                  <Typography variant="caption">
                    {getPlatformMetadata(selectedSignal).metrics}
                  </Typography>
                </Box>
              </Paper>
              
              {/* Response Settings */}
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControl sx={{ minWidth: 150 }}>
                  <InputLabel>Tone</InputLabel>
                  <Select
                    value={responseForm.tone}
                    onChange={(e) => setResponseForm({ ...responseForm, tone: e.target.value })}
                    label="Tone"
                  >
                    <MenuItem value="professional">Professional</MenuItem>
                    <MenuItem value="casual">Casual</MenuItem>
                    <MenuItem value="friendly">Friendly</MenuItem>
                    <MenuItem value="helpful">Helpful</MenuItem>
                    <MenuItem value="enthusiastic">Enthusiastic</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl sx={{ minWidth: 150 }}>
                  <InputLabel>Response Type</InputLabel>
                  <Select
                    value={responseForm.responseType}
                    onChange={(e) => setResponseForm({ ...responseForm, responseType: e.target.value })}
                    label="Response Type"
                  >
                    <MenuItem value="comment_reply">Comment Reply</MenuItem>
                    <MenuItem value="thread_start">New Thread</MenuItem>
                    <MenuItem value="dm">Direct Message</MenuItem>
                    {selectedSignal.platform === 'twitter' && (
                      <MenuItem value="quote_tweet">Quote Tweet</MenuItem>
                    )}
                  </Select>
                </FormControl>
              </Box>
              
              {!generatedResponse && (
                <Button
                  variant="contained"
                  onClick={generateResponse}
                  disabled={responseLoading}
                  startIcon={<PsychologyIcon />}
                >
                  {responseLoading ? 'Generating...' : 'Generate AI Response'}
                </Button>
              )}
              
              {responseLoading && <LinearProgress />}
              
              {/* Generated Response */}
              {generatedResponse && (
                <Paper sx={{ p: 2, bgcolor: 'primary.50', border: 1, borderColor: 'primary.200' }}>
                  <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
                    Generated Response (Confidence: {Math.round(generatedResponse.confidence_score * 100)}%)
                  </Typography>
                  <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                    {generatedResponse.generated_content}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => navigator.clipboard.writeText(generatedResponse.generated_content)}
                    >
                      Copy Response
                    </Button>
                    <Button
                      variant="contained"
                      size="small"
                      href={selectedSignal.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Post on {PLATFORM_CONFIGS[selectedSignal.platform]?.name}
                    </Button>
                  </Box>
                </Paper>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResponseDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Signals