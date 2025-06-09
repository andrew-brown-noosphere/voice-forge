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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  Reddit as RedditIcon,
  Twitter as TwitterIcon,
  GitHub as GitHubIcon,
  LinkedIn as LinkedInIcon,
  PlayArrow as PlayArrowIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material'
import { useApi } from '../hooks/useApi'

const PLATFORM_CONFIGS = {
  reddit: {
    name: 'Reddit',
    icon: RedditIcon,
    color: '#FF4500',
    sources: {
      label: 'Subreddits (without r/)',
      placeholder: 'startups,SaaS,webdev',
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

const steps = [
  'Select Platform',
  'Configure Sources',
  'Set Keywords',
  'Review & Launch'
]

function SignalScanConfig() {
  const navigate = useNavigate()
  const location = useLocation()
  const api = useApi()
  
  const [activeStep, setActiveStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)

  // Configuration state
  const [config, setConfig] = useState({
    platform: 'reddit',
    sources: [],
    keywords: [],
    timeFilter: 'week',
    maxItemsPerSource: 50,
    relevanceThreshold: 0.6,
    autoScan: false
  })

  // Form state
  const [newSource, setNewSource] = useState('')
  const [newKeyword, setNewKeyword] = useState('')

  useEffect(() => {
    // Check if we have recommendations passed from the Signal Scan button
    if (location.state?.recommendations) {
      setRecommendations(location.state.recommendations)
      applyRecommendations(location.state.recommendations)
    } else {
      // Load recommendations on mount
      loadRecommendations()
    }
  }, [])

  const loadRecommendations = async () => {
    setLoadingRecommendations(true)
    try {
      // Try to get content analysis and recommendations
      const analysis = await api.signals.getAnalysis()
      setRecommendations(analysis)
      
      // Auto-apply some recommendations
      if (analysis.recommended_keywords) {
        setConfig(prev => ({
          ...prev,
          keywords: analysis.recommended_keywords.slice(0, 5) // Take first 5
        }))
      }
      
      if (analysis.recommended_sources?.reddit) {
        setConfig(prev => ({
          ...prev,
          sources: analysis.recommended_sources.reddit.slice(0, 3) // Take first 3
        }))
      }
    } catch (error) {
      console.warn('Could not load recommendations:', error)
      // Set some intelligent defaults
      setRecommendations({
        recommended_keywords: ['api', 'integration', 'automation', 'saas', 'tool'],
        recommended_sources: {
          reddit: ['startups', 'SaaS', 'webdev']
        },
        fallback: true
      })
    } finally {
      setLoadingRecommendations(false)
    }
  }

  const applyRecommendations = (recs) => {
    if (recs.platform_strategies?.reddit?.recommended_sources) {
      setConfig(prev => ({
        ...prev,
        sources: recs.platform_strategies.reddit.recommended_sources.map(s => s.source || s).slice(0, 5)
      }))
    }
    
    if (recs.platform_strategies?.reddit?.search_queries) {
      setConfig(prev => ({
        ...prev,
        keywords: recs.platform_strategies.reddit.search_queries.map(q => q.query || q).slice(0, 8)
      }))
    }
  }

  const addSource = () => {
    if (newSource.trim() && !config.sources.includes(newSource.trim())) {
      setConfig(prev => ({
        ...prev,
        sources: [...prev.sources, newSource.trim()]
      }))
      setNewSource('')
    }
  }

  const removeSource = (source) => {
    setConfig(prev => ({
      ...prev,
      sources: prev.sources.filter(s => s !== source)
    }))
  }

  const addKeyword = () => {
    if (newKeyword.trim() && !config.keywords.includes(newKeyword.trim())) {
      setConfig(prev => ({
        ...prev,
        keywords: [...prev.keywords, newKeyword.trim()]
      }))
      setNewKeyword('')
    }
  }

  const removeKeyword = (keyword) => {
    setConfig(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keyword)
    }))
  }

  const addRecommendedKeyword = (keyword) => {
    if (!config.keywords.includes(keyword)) {
      setConfig(prev => ({
        ...prev,
        keywords: [...prev.keywords, keyword]
      }))
    }
  }

  const addRecommendedSource = (source) => {
    if (!config.sources.includes(source)) {
      setConfig(prev => ({
        ...prev,
        sources: [...prev.sources, source]
      }))
    }
  }

  const handleNext = () => {
    setActiveStep(prev => prev + 1)
  }

  const handleBack = () => {
    setActiveStep(prev => prev - 1)
  }

  const handleLaunchScan = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const request = {
        platform: config.platform,
        sources: config.sources,
        keywords: config.keywords,
        time_filter: config.timeFilter,
        max_items_per_source: config.maxItemsPerSource,
        relevance_threshold: config.relevanceThreshold
      }
      
      const result = await api.signals.discover(request)
      
      // Navigate back to signals page with success message
      navigate('/signals', { 
        state: { 
          scanResult: result,
          message: `Successfully discovered ${result.signals_found} signals from ${result.platform}!`
        }
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getPlatformIcon = (platform) => {
    const IconComponent = PLATFORM_CONFIGS[platform]?.icon || TrendingUpIcon
    return <IconComponent sx={{ color: PLATFORM_CONFIGS[platform]?.color }} />
  }

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              {Object.entries(PLATFORM_CONFIGS).map(([platformId, platformConfig]) => (
                <Grid item xs={12} sm={6} key={platformId}>
                  <Card 
                    sx={{ 
                      cursor: platformConfig.status === 'active' ? 'pointer' : 'not-allowed',
                      border: config.platform === platformId ? 2 : 1,
                      borderColor: config.platform === platformId ? 'primary.main' : 'divider',
                      opacity: platformConfig.status === 'active' ? 1 : 0.6
                    }}
                    onClick={() => {
                      if (platformConfig.status === 'active') {
                        setConfig(prev => ({ ...prev, platform: platformId }))
                      }
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {getPlatformIcon(platformId)}
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6">{platformConfig.name}</Typography>
                          <Typography variant="body2" color="textSecondary">
                            {platformConfig.sources.help}
                          </Typography>
                        </Box>
                        {platformConfig.status !== 'active' && (
                          <Chip label="Coming Soon" size="small" />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )

      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Configure {PLATFORM_CONFIGS[config.platform]?.name} Sources
            </Typography>
            
            {/* Recommended Sources */}
            {recommendations && (
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.50' }}>
                <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LightbulbIcon color="primary" fontSize="small" />
                  Recommended Sources
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {(recommendations.recommended_sources?.[config.platform] || 
                    recommendations.platform_strategies?.[config.platform]?.recommended_sources?.map(s => s.source || s) ||
                    ['startups', 'SaaS', 'webdev']).map((source, index) => (
                    <Chip
                      key={index}
                      label={source}
                      onClick={() => addRecommendedSource(source)}
                      color={config.sources.includes(source) ? 'primary' : 'default'}
                      variant={config.sources.includes(source) ? 'filled' : 'outlined'}
                      size="small"
                    />
                  ))}
                </Box>
              </Paper>
            )}

            {/* Add Source */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                label={PLATFORM_CONFIGS[config.platform]?.sources.label}
                value={newSource}
                onChange={(e) => setNewSource(e.target.value)}
                placeholder={PLATFORM_CONFIGS[config.platform]?.sources.placeholder}
                onKeyPress={(e) => e.key === 'Enter' && addSource()}
                fullWidth
              />
              <Button variant="contained" onClick={addSource} startIcon={<AddIcon />}>
                Add
              </Button>
            </Box>

            {/* Current Sources */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Selected Sources ({config.sources.length})
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {config.sources.map((source, index) => (
                  <Chip
                    key={index}
                    label={source}
                    onDelete={() => removeSource(source)}
                    color="primary"
                  />
                ))}
              </Box>
            </Box>
          </Box>
        )

      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Set Keywords to Monitor
            </Typography>
            
            {/* Recommended Keywords */}
            {recommendations && (
              <Paper sx={{ p: 2, mb: 3, bgcolor: 'success.50' }}>
                <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LightbulbIcon color="success" fontSize="small" />
                  Recommended Keywords
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {(recommendations.recommended_keywords || 
                    recommendations.platform_strategies?.[config.platform]?.search_queries?.map(q => q.query || q) ||
                    ['api', 'integration', 'automation', 'saas']).map((keyword, index) => (
                    <Chip
                      key={index}
                      label={keyword}
                      onClick={() => addRecommendedKeyword(keyword)}
                      color={config.keywords.includes(keyword) ? 'success' : 'default'}
                      variant={config.keywords.includes(keyword) ? 'filled' : 'outlined'}
                      size="small"
                    />
                  ))}
                </Box>
              </Paper>
            )}

            {/* Add Keyword */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                label="Keywords"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="Enter keywords to search for"
                onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
                fullWidth
              />
              <Button variant="contained" onClick={addKeyword} startIcon={<AddIcon />}>
                Add
              </Button>
            </Box>

            {/* Current Keywords */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Selected Keywords ({config.keywords.length})
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {config.keywords.map((keyword, index) => (
                  <Chip
                    key={index}
                    label={keyword}
                    onDelete={() => removeKeyword(keyword)}
                    color="success"
                  />
                ))}
              </Box>
            </Box>
          </Box>
        )

      case 3:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Review Your Signal Scan Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getPlatformIcon(config.platform)}
                      Platform
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {PLATFORM_CONFIGS[config.platform]?.name}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Sources ({config.sources.length})
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {config.sources.slice(0, 3).map((source, index) => (
                        <Chip key={index} label={source} size="small" />
                      ))}
                      {config.sources.length > 3 && (
                        <Chip label={`+${config.sources.length - 3} more`} size="small" variant="outlined" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Keywords ({config.keywords.length})
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {config.keywords.slice(0, 6).map((keyword, index) => (
                        <Chip key={index} label={keyword} size="small" color="success" />
                      ))}
                      {config.keywords.length > 6 && (
                        <Chip label={`+${config.keywords.length - 6} more`} size="small" variant="outlined" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Advanced Settings */}
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Advanced Settings
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <FormControl fullWidth>
                      <InputLabel>Time Filter</InputLabel>
                      <Select
                        value={config.timeFilter}
                        onChange={(e) => setConfig(prev => ({ ...prev, timeFilter: e.target.value }))}
                        label="Time Filter"
                      >
                        <MenuItem value="day">Past Day</MenuItem>
                        <MenuItem value="week">Past Week</MenuItem>
                        <MenuItem value="month">Past Month</MenuItem>
                        <MenuItem value="year">Past Year</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Max Items per Source"
                      type="number"
                      value={config.maxItemsPerSource}
                      onChange={(e) => setConfig(prev => ({ ...prev, maxItemsPerSource: parseInt(e.target.value) }))}
                      inputProps={{ min: 1, max: 100 }}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      label="Relevance Threshold"
                      type="number"
                      value={config.relevanceThreshold}
                      onChange={(e) => setConfig(prev => ({ ...prev, relevanceThreshold: parseFloat(e.target.value) }))}
                      inputProps={{ min: 0, max: 1, step: 0.1 }}
                      fullWidth
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Box>
        )

      default:
        return null
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <IconButton onClick={() => navigate('/signals')}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUpIcon color="primary" />
            Signal Scan Configuration
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Configure your signal scanning parameters based on your content and marketing positioning
          </Typography>
        </Box>
        {loadingRecommendations && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PsychologyIcon color="primary" />
            <Typography variant="body2">Loading recommendations...</Typography>
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Stepper */}
      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
              <StepContent>
                {renderStepContent(index)}
                
                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                  >
                    Back
                  </Button>
                  
                  {index === steps.length - 1 ? (
                    <Button
                      variant="contained"
                      onClick={handleLaunchScan}
                      disabled={loading || config.sources.length === 0}
                      startIcon={<PlayArrowIcon />}
                    >
                      {loading ? 'Launching...' : 'Launch Signal Scan'}
                    </Button>
                  ) : (
                    <Button
                      variant="contained"
                      onClick={handleNext}
                      disabled={
                        (index === 1 && config.sources.length === 0) ||
                        (index === 2 && config.keywords.length === 0)
                      }
                    >
                      Next
                    </Button>
                  )}
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>
    </Box>
  )
}

export default SignalScanConfig
