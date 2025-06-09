import React, { useState, useEffect } from 'react'
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
  Paper
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Reddit as RedditIcon,
  TrendingUp as TrendingUpIcon,
  Comment as CommentIcon,
  ThumbUp as ThumbUpIcon,
  Psychology as PsychologyIcon,
  Launch as LaunchIcon,
  AutoAwesome as AutoAwesomeIcon
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

function RedditSignals() {
  const api = useApi()
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [discoveryDialogOpen, setDiscoveryDialogOpen] = useState(false)
  const [responseDialogOpen, setResponseDialogOpen] = useState(false)
  const [selectedSignal, setSelectedSignal] = useState(null)
  const [generatedResponse, setGeneratedResponse] = useState(null)
  const [responseLoading, setResponseLoading] = useState(false)

  // Discovery form state - Updated with buf.build defaults
  const [discoveryForm, setDiscoveryForm] = useState({
    subreddits: 'programming,golang,grpc,webdev,devtools,opensource',
    keywords: 'protobuf,grpc,protocol buffers,buf,api schema,code generation,microservices',
    timeFilter: 'week',
    maxPosts: 50,
    relevanceThreshold: 0.6
  })

  // Response form state
  const [responseForm, setResponseForm] = useState({
    tone: 'professional',
    responseType: 'comment_reply',
    includeContext: true
  })

  // Load signals on component mount and perform intelligent discovery
  useEffect(() => {
    const initializeRedditSignals = async () => {
      // First try to load existing signals
      await loadSignals()
      
      // Check if we need to discover new signals
      if (signals.length === 0) {
        console.log('🧠 No existing signals found. Starting intelligent discovery using Gypsum + content analysis...')
        await performIntelligentDiscovery()
      }
    }
    
    initializeRedditSignals()
  }, [])

  const loadSignals = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.redditSignals.list(20, 0)
      setSignals(data)
    } catch (err) {
      // Don't show error for empty signals - this is expected on first load
      if (!err.message.includes('404') && !err.message.includes('No signals found')) {
        setError(err.message)
      }
      setSignals([]) // Set empty array if no signals exist yet
    } finally {
      setLoading(false)
    }
  }

  const performIntelligentDiscovery = async () => {
    setLoading(true)
    setError('🧠 Using Gypsum personas to find relevant Reddit communities...')
    
    try {
      // Get Gypsum personas from the backend API
      console.log('👥 Fetching Gypsum personas from backend...')
      let personas = []
      try {
        personas = await api.gypsum.getPersonas()
        console.log('👥 Got personas from API:', personas)
      } catch (gypsumErr) {
        console.log('⚠️ Gypsum API failed, using fallback data:', gypsumErr.message)
        // Fallback to static data if API fails
        personas = [
          {
            role: 'Backend Developer',
            industry: 'Technology',
            pain_points: ['API integration complexity', 'Microservice communication', 'Schema management'],
            focus_areas: ['gRPC', 'Protocol Buffers', 'API Design']
          }
        ]
      }
      
      // Generate intelligent targeting from personas (no AI needed)
      const intelligentSubreddits = extractSubredditsFromPersonas(personas)
      const intelligentKeywords = extractKeywordsFromPersonas(personas)
      
      console.log('🎯 Targeting from Gypsum personas:', { intelligentSubreddits, intelligentKeywords })
      
      // Execute discovery
      const result = await api.redditSignals.discover(
        intelligentSubreddits,
        intelligentKeywords,
        'week',
        50,
        0.6
      )
      
      await loadSignals()
      setError(`Found ${result.signals_found || 0} discussions using Gypsum persona targeting.`)
      
    } catch (err) {
      console.error('Discovery failed:', err)
      setError(`Discovery failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }
  
  const extractSubredditsFromPersonas = (personas) => {
    const baseSubreddits = ['programming', 'golang', 'grpc', 'webdev', 'devtools', 'opensource']
    
    // Add persona-specific subreddits based on roles/industries
    if (personas?.length > 0) {
      personas.forEach(persona => {
        const role = persona.role?.toLowerCase() || ''
        const industry = persona.industry?.toLowerCase() || ''
        
        // Role-based subreddits
        if (role.includes('developer')) baseSubreddits.push('coding', 'programming')
        if (role.includes('architect')) baseSubreddits.push('softwarearchitecture', 'systemdesign')
        if (role.includes('devops')) baseSubreddits.push('devops', 'kubernetes', 'docker')
        if (role.includes('engineer')) baseSubreddits.push('engineering', 'softwareengineering')
        
        // Industry-based subreddits
        if (industry.includes('fintech')) baseSubreddits.push('fintech', 'payments')
        if (industry.includes('enterprise')) baseSubreddits.push('enterprise', 'b2b')
        if (industry.includes('startup')) baseSubreddits.push('startups', 'entrepreneur')
      })
    }
    
    return [...new Set(baseSubreddits)] // Remove duplicates
  }
  
  const extractKeywordsFromPersonas = (personas) => {
    const baseKeywords = ['protobuf', 'grpc', 'protocol buffers', 'buf', 'api schema', 'code generation']
    
    // Add persona-specific keywords
    if (personas?.length > 0) {
      personas.forEach(persona => {
        // Add pain points as keywords
        if (persona.pain_points) {
          persona.pain_points.forEach(pain => {
            const painLower = pain.toLowerCase()
            if (painLower.includes('api')) baseKeywords.push('api integration', 'api design')
            if (painLower.includes('scale')) baseKeywords.push('scalability', 'performance')
            if (painLower.includes('tool')) baseKeywords.push('developer tools', 'tooling')
            if (painLower.includes('microservice')) baseKeywords.push('microservices', 'distributed systems')
          })
        }
        
        // Add role-specific keywords
        const role = persona.role?.toLowerCase() || ''
        if (role.includes('backend')) baseKeywords.push('backend development', 'server')
        if (role.includes('frontend')) baseKeywords.push('frontend', 'ui')
        if (role.includes('full stack')) baseKeywords.push('full stack', 'web development')
      })
    }
    
    return [...new Set(baseKeywords)] // Remove duplicates
  }

  const handleDiscoverSignals = async () => {
    setLoading(true)
    setError(null)
    try {
      const subreddits = discoveryForm.subreddits.split(',').map(s => s.trim())
      const keywords = discoveryForm.keywords.split(',').map(k => k.trim())
      
      const result = await api.redditSignals.discover(
        subreddits,
        keywords,
        discoveryForm.timeFilter,
        discoveryForm.maxPosts,
        discoveryForm.relevanceThreshold
      )
      
      setDiscoveryDialogOpen(false)
      // Reload signals to show new discoveries
      await loadSignals()
      
      // Show success message
      setError(`Successfully discovered ${result.signals_found} new signals!`)
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
      const response = await api.redditSignals.generateResponse(
        selectedSignal.signal_id,
        'reddit',
        responseForm.tone,
        responseForm.responseType,
        responseForm.includeContext
      )
      
      setGeneratedResponse(response)
    } catch (err) {
      setError(err.message)
    } finally {
      setResponseLoading(false)
    }
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

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <RedditIcon color="primary" />
          Reddit Signals
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadSignals}
            disabled={loading}
          >
            Refresh
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
        {signals.length === 0 && !loading ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <RedditIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                Intelligent Reddit Discovery
              </Typography>
              <Typography color="textSecondary" paragraph sx={{ maxWidth: 600, mx: 'auto' }}>
                We automatically analyze your buf.build content, Gypsum personas, and messaging framework 
                to discover the most relevant Reddit communities and discussions.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', mt: 3 }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<AutoAwesomeIcon />}
                  onClick={performIntelligentDiscovery}
                  sx={{ px: 4 }}
                >
                  Start Intelligent Discovery
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<RefreshIcon />}
                  onClick={loadSignals}
                >
                  Refresh
                </Button>
              </Box>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                🧠 Uses your content analysis + Gypsum personas for intelligent targeting
              </Typography>
            </Paper>
          </Grid>
        ) : (
          signals.map((signal) => (
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
                      <Avatar sx={{ width: 20, height: 20, fontSize: 12, bgcolor: 'orange' }}>
                        r/
                      </Avatar>
                      <Typography variant="caption" color="textSecondary">
                        {signal.subreddit}
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
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <ThumbUpIcon sx={{ fontSize: 16, color: 'grey.600' }} />
                        <Typography variant="caption">{signal.score}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <CommentIcon sx={{ fontSize: 16, color: 'grey.600' }} />
                        <Typography variant="caption">{signal.num_comments}</Typography>
                      </Box>
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      {formatTimeAgo(signal.created_at)}
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
                    View on Reddit
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
          ))
        )}
      </Grid>

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
                <Typography variant="h6" gutterBottom>{selectedSignal.title}</Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {selectedSignal.content}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Chip label={`r/${selectedSignal.subreddit}`} size="small" />
                  <Chip label={SIGNAL_TYPE_LABELS[selectedSignal.signal_type]} size="small" color="primary" />
                  <Typography variant="caption">
                    {selectedSignal.score} upvotes • {selectedSignal.num_comments} comments
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
                      Post on Reddit
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

export default RedditSignals