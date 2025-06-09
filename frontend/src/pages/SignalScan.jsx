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
  LinearProgress,
  Paper,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Divider,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  Reddit as RedditIcon,
  Twitter as TwitterIcon,
  GitHub as GitHubIcon,
  LinkedIn as LinkedInIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Launch as LaunchIcon
} from '@mui/icons-material'
import { useApi } from '../hooks/useApi'

const PLATFORM_CONFIGS = {
  reddit: {
    name: 'Reddit',
    icon: RedditIcon,
    color: '#FF4500',
    status: 'active',
    description: 'Find relevant subreddits based on your content themes'
  },
  twitter: {
    name: 'Twitter',
    icon: TwitterIcon,
    color: '#1DA1F2',
    status: 'coming_soon',
    description: 'Discover hashtags and communities'
  },
  github: {
    name: 'GitHub',
    icon: GitHubIcon,
    color: '#333',
    status: 'coming_soon',
    description: 'Find relevant repositories and discussions'
  },
  linkedin: {
    name: 'LinkedIn',
    icon: LinkedInIcon,
    color: '#0077B5',
    status: 'coming_soon',
    description: 'Discover professional communities and topics'
  }
}

function SignalScan() {
  const navigate = useNavigate()
  const location = useLocation()
  const api = useApi()
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [discoveries, setDiscoveries] = useState({})
  const [selectedSources, setSelectedSources] = useState({})
  const [scanComplete, setScanComplete] = useState(false)
  const [selectedPersona, setSelectedPersona] = useState('')
  const [availablePersonas, setAvailablePersonas] = useState([])
  const [customSolution, setCustomSolution] = useState('')

  const generateIntelligentFallback = async (platform) => {
    // This shouldn't be needed now - we'll use the proper ContentDrivenSignalAI pipeline
    console.log('⚠️ Using fallback - ContentDrivenSignalAI pipeline may have failed')
    return [
      { name: 'programming', reasoning: 'ContentDrivenSignalAI analysis unavailable', priority: 'low' },
      { name: 'webdev', reasoning: 'ContentDrivenSignalAI analysis unavailable', priority: 'low' }
    ]
  }
  
  const parseAICommunitySuggestions = (aiResponse) => {
    try {
      // Parse AI response to extract community suggestions
      const lines = aiResponse.split('\n').filter(line => line.trim())
      const communities = []
      
      let currentCommunity = {}
      
      for (const line of lines) {
        const trimmed = line.trim()
        
        // Look for subreddit names (various formats)
        const subredditMatch = trimmed.match(/(?:r\/)?([a-zA-Z][a-zA-Z0-9_]{2,20})(?:\s|$|:|-)/)
        if (subredditMatch && !trimmed.toLowerCase().includes('reddit')) {
          if (currentCommunity.name) {
            communities.push({ ...currentCommunity })
          }
          currentCommunity = {
            name: subredditMatch[1],
            reasoning: '',
            priority: 'medium'
          }
        }
        
        // Look for reasoning/description
        if (currentCommunity.name && (trimmed.includes('because') || trimmed.includes('relevant') || trimmed.includes('discusses'))) {
          currentCommunity.reasoning = trimmed.replace(/^[^a-zA-Z]*/, '').substring(0, 150)
        }
        
        // Look for priority indicators
        if (trimmed.toLowerCase().includes('high priority') || trimmed.toLowerCase().includes('most important')) {
          currentCommunity.priority = 'high'
        } else if (trimmed.toLowerCase().includes('low priority')) {
          currentCommunity.priority = 'low'
        }
      }
      
      // Add the last community
      if (currentCommunity.name) {
        communities.push(currentCommunity)
      }
      
      // Ensure we have reasoning for all communities
      return communities.map(community => ({
        name: community.name,
        reasoning: community.reasoning || `Community focused on ${community.name}-related discussions`,
        priority: community.priority || 'medium'
      })).slice(0, 7) // Limit to 7 communities
      
    } catch (parseError) {
      console.warn('Failed to parse AI community suggestions:', parseError)
      return []
    }
  }

  useEffect(() => {
    loadAvailablePersonas()
    // Auto-start scan if we have recommendations passed
    if (location.state?.autoStart) {
      handleStartScan()
    }
  }, [])

  const loadAvailablePersonas = async () => {
    try {
      const personas = await api.gypsum.getPersonas()
      setAvailablePersonas(personas)
      if (personas.length > 0) {
        setSelectedPersona(personas[0].id)
      }
    } catch (err) {
      console.warn('Could not load personas:', err)
      setAvailablePersonas([])
    }
  }

  const handleStartScan = async () => {
    setLoading(true)
    setError(null)
    setDiscoveries({})
    setSelectedSources({})  // Explicitly clear selected sources
    setScanComplete(false)

    try {
      // Get content analysis and recommendations for each platform
      const analysisPromises = Object.keys(PLATFORM_CONFIGS).map(async (platform) => {
        if (PLATFORM_CONFIGS[platform].status !== 'active') {
          return [platform, { status: 'not_available', sources: [] }]
        }

        try {
          console.log(`🔍 Using ContentDrivenSignalAI pipeline for ${platform}...`)
          console.log(`🎯 Solution focus: ${customSolution || 'analyze all content'}`)
          console.log(`📋 Selected persona: ${selectedPersona || 'none (will use general analysis)'}`)
          
          // Build solution-focused context for ContentDrivenSignalAI
          const marketingContext = customSolution ? {
            solution_focus: customSolution,
            analysis_mode: 'solution_specific'
          } : {
            analysis_mode: 'comprehensive_content_analysis'
          }
          
          // Use your ContentDrivenSignalAI pipeline with solution focus
          const strategy = await api.signals.generateStrategy({
            persona_id: selectedPersona || null,
            platforms: [platform],
            marketing_context: marketingContext,
            options: {
              focus_areas: ['community_discovery', 'source_recommendation'],
              analysis_depth: 'comprehensive',
              include_reasoning: true,
              content_driven: true // Use existing VoiceForge content analysis
            }
          })
          
          console.log(`✅ ContentDrivenSignalAI strategy for ${platform}:`, strategy)
          
          const platformStrategy = strategy.platform_strategies?.[platform]
          if (platformStrategy?.recommended_sources) {
            console.log(`📊 Raw recommended_sources for ${platform}:`, platformStrategy.recommended_sources)
            
            const sources = platformStrategy.recommended_sources.map((source, index) => {
              // Handle different possible formats from ContentDrivenSignalAI
              let sourceName, sourceReasoning, sourcePriority
              
              if (typeof source === 'string') {
                // Simple string format
                sourceName = source
                sourceReasoning = `Recommended by ContentDrivenSignalAI based on your content analysis`
                sourcePriority = index < 3 ? 'high' : 'medium'
              } else if (typeof source === 'object' && source !== null) {
                // Object format - extract the actual values safely
                sourceName = source.source || source.name || source.subreddit || String(source)
                sourceReasoning = source.reasoning || source.description || `Recommended by ContentDrivenSignalAI`
                sourcePriority = source.priority || (index < 3 ? 'high' : 'medium')
              } else {
                // Fallback for any other format
                sourceName = `source_${index}`
                sourceReasoning = 'ContentDrivenSignalAI recommendation'
                sourcePriority = 'medium'
              }
              
              return {
                name: String(sourceName), // Ensure it's always a string
                reasoning: String(sourceReasoning), // Ensure it's always a string
                priority: String(sourcePriority), // Ensure it's always a string
                engagement_score: source.engagement_score || 0.8,
                relevance_score: source.relevance_score || 0.9,
                subscribers: source.subscribers || 'Unknown',
                activity_level: source.activity_level || 'Active'
              }
            })
            
            return [platform, {
              status: 'success',
              sources,
              strategy_confidence: strategy.strategy_confidence || 0.85,
              content_analysis: strategy.content_analysis
            }]
          }
        } catch (err) {
          console.warn(`❌ ContentDrivenSignalAI failed for ${platform}:`, err)
        }

        // Fallback only if ContentDrivenSignalAI completely fails
        try {
          const fallbackSources = await generateIntelligentFallback(platform)
          return [platform, {
            status: 'fallback',
            sources: fallbackSources
          }]
        } catch (fallbackError) {
          console.warn(`❌ Fallback analysis failed for ${platform}:`, fallbackError)
          return [platform, {
            status: 'minimal_fallback',
            sources: [
              { name: 'programming', reasoning: 'All analysis methods failed', priority: 'low' }
            ]
          }]
        }
      })

      const results = await Promise.all(analysisPromises)
      const newDiscoveries = Object.fromEntries(results)
      
      setDiscoveries(newDiscoveries)
      setScanComplete(true)
      
      // Clear previous selections and initialize with new high priority ones
      const initialSelected = {}
      Object.entries(newDiscoveries).forEach(([platform, data]) => {
        initialSelected[platform] = data.sources
          .filter(source => source.priority === 'high')
          .map(source => source.name)
      })
      setSelectedSources(initialSelected)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleSourceSelection = (platform, sourceName) => {
    setSelectedSources(prev => ({
      ...prev,
      [platform]: prev[platform]?.includes(sourceName)
        ? prev[platform].filter(s => s !== sourceName)
        : [...(prev[platform] || []), sourceName]
    }))
  }

  const handleStartMonitoring = async () => {
    setLoading(true)
    setError(null)

    try {
      console.log('🚀 Starting intelligent signal discovery...')
      console.log('📋 Selected persona:', selectedPersona)
      console.log('🎯 Solution focus:', customSolution)
      console.log('📍 Selected sources:', selectedSources)
      
      // Use the new intelligent discovery endpoint that combines strategy + actual data
      const platformsWithSources = Object.keys(selectedSources).filter(
        platform => selectedSources[platform]?.length > 0
      )
      
      if (platformsWithSources.length === 0) {
        setError('Please select at least one source to monitor')
        return
      }
      
      // Build marketing context if solution is specified
      const marketingContext = customSolution ? {
        solution_focus: customSolution,
        analysis_mode: 'solution_specific'
      } : {
        analysis_mode: 'comprehensive_content_analysis'
      }
      
      // Call the new intelligent discovery endpoint using the correct API method
      const result = await api.request('/signals/discover-intelligent', {
        method: 'POST',
        body: JSON.stringify({
          persona_id: selectedPersona || null,
          platforms: platformsWithSources,
          marketing_context: marketingContext,
          options: {
            focus_areas: ['community_discovery', 'signal_discovery'],
            analysis_depth: 'comprehensive',
            include_reasoning: true,
            content_driven: true
          },
          time_filter: 'week',
          max_items_per_source: 50,
          relevance_threshold: 0.6
        })
      })
      
      console.log('✅ Intelligent discovery result:', result)
      
      const totalSignals = result.signals_found || 0
      const totalSources = Object.values(selectedSources).flat().length
      
      // Navigate back to signals page with success message
      navigate('/signals/sources', {
        state: {
          message: `🧠 Intelligent discovery complete! Saved ${totalSources} AI-selected sources for ongoing monitoring. Found ${totalSignals} initial signals.`,
          discoveryType: 'intelligent',
          strategy: {
            persona: selectedPersona ? availablePersonas.find(p => p.id === selectedPersona)?.role : 'General Analysis',
            solution: customSolution || 'All content themes',
            platforms: platformsWithSources
          }
        }
      })
    } catch (err) {
      console.error('❌ Intelligent discovery failed:', err)
      setError(err.response?.data?.detail || err.message || 'Discovery failed')
    } finally {
      setLoading(false)
    }
  }

  const getPlatformIcon = (platform) => {
    const IconComponent = PLATFORM_CONFIGS[platform]?.icon || TrendingUpIcon
    return <IconComponent sx={{ color: PLATFORM_CONFIGS[platform]?.color }} />
  }

  const totalSelectedSources = Object.values(selectedSources).reduce(
    (sum, sources) => sum + (sources?.length || 0), 0
  )

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <IconButton onClick={() => navigate('/signals')}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SearchIcon color="primary" />
            Signal Scan
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Discover relevant communities and sources to monitor based on your marketing positioning
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Content-Driven Signal Discovery */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          🎯 Content-Driven Signal Discovery
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          Use your existing VoiceForge content to discover relevant communities and discussion topics.
        </Typography>
        
        <Grid container spacing={3}>
          {/* Solution Focus Input */}
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="What specific solution or topic should we focus on?"
              placeholder="e.g., 'API security solutions' or 'code signing certificates' or 'leave blank to analyze all content'"
              value={customSolution}
              onChange={(e) => setCustomSolution(e.target.value)}
              multiline
              rows={2}
              helperText="Describe your specific solution focus, or leave blank to analyze all your content for signal opportunities"
            />
          </Grid>
          
          {/* Persona Selection */}
          <Grid item xs={12} md={4}>
            {availablePersonas.length > 0 ? (
              <FormControl fullWidth>
                <InputLabel>Target Persona (Optional)</InputLabel>
                <Select
                  value={selectedPersona}
                  onChange={(e) => setSelectedPersona(e.target.value)}
                  label="Target Persona (Optional)"
                >
                  <MenuItem value="">All Audiences</MenuItem>
                  {availablePersonas.map((persona) => (
                    <MenuItem key={persona.id} value={persona.id}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ width: 24, height: 24 }}>
                          {persona.role?.[0]?.toUpperCase()}
                        </Avatar>
                        <Typography variant="body2">{persona.role}</Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <Alert severity="info">
                <Typography variant="body2">
                  🧠 Using general audience targeting
                </Typography>
              </Alert>
            )}
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 3, p: 2, bgcolor: 'info.50', borderRadius: 1 }}>
          <Typography variant="caption" color="info.main" fontWeight="bold">
            💡 How it works
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {customSolution 
              ? `We'll analyze your content for "${customSolution}" and find communities discussing related challenges and opportunities.`
              : 'We\'ll analyze all your VoiceForge content to identify your key solutions and find relevant communities automatically.'
            }
            {selectedPersona && availablePersonas.length > 0 && (
              <> The results will be tailored for {availablePersonas.find(p => p.id === selectedPersona)?.role || 'your selected persona'}.</>
            )}
          </Typography>
        </Box>
      </Paper>

      {/* Scan Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Platform Discovery
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {scanComplete 
                ? `Scan complete! Found communities across ${Object.keys(discoveries).length} platforms.`
                : 'Analyze your content and discover relevant communities to monitor for signals.'
              }
            </Typography>
          </Box>
          <Button
            variant="contained"
            onClick={handleStartScan}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            size="large"
          >
            {loading ? 'Scanning...' : scanComplete ? 'Rescan with New Settings' : 'Start Discovery Scan'}
          </Button>
        </Box>
      </Paper>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Discovery Results */}
      {scanComplete && Object.keys(discoveries).length > 0 && (
        <Grid container spacing={3}>
          {Object.entries(discoveries).map(([platform, data]) => (
            <Grid item xs={12} key={platform}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    {getPlatformIcon(platform)}
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6">
                        {PLATFORM_CONFIGS[platform]?.name} Communities
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {data.sources.length} relevant communities discovered
                      </Typography>
                    </Box>
                    <Chip 
                      label={`${selectedSources[platform]?.length || 0} selected`}
                      color={selectedSources[platform]?.length > 0 ? 'primary' : 'default'}
                    />
                  </Box>

                  {data.sources.length > 0 ? (
                    <List>
                      {data.sources.map((source, index) => (
                        <React.Fragment key={source.name}>
                          <ListItem>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                              <Box sx={{ flexGrow: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                  <Typography variant="subtitle1" fontWeight="bold">
                                    {platform === 'reddit' ? 'r/' : ''}{String(source.name || 'unknown')}
                                  </Typography>
                                  <Chip 
                                    label={String(source.priority || 'medium')} 
                                    size="small"
                                    color={source.priority === 'high' ? 'error' : source.priority === 'medium' ? 'warning' : 'default'}
                                  />
                                </Box>
                                <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                                  {String(source.reasoning || 'No reasoning provided')}
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 2 }}>
                                  <Typography variant="caption">
                                    Relevance: {Math.round((source.relevance_score || 0.9) * 100)}%
                                  </Typography>
                                  <Typography variant="caption">
                                    Activity: {String(source.activity_level || 'Active')}
                                  </Typography>
                                </Box>
                              </Box>
                              <Button
                                variant={selectedSources[platform]?.includes(source.name) ? 'contained' : 'outlined'}
                                onClick={() => toggleSourceSelection(platform, source.name)}
                                startIcon={selectedSources[platform]?.includes(source.name) ? <CheckCircleIcon /> : <AddIcon />}
                              >
                                {selectedSources[platform]?.includes(source.name) ? 'Selected' : 'Select'}
                              </Button>
                            </Box>
                          </ListItem>
                          {index < data.sources.length - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                  ) : (
                    <Typography color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
                      No communities found for this platform
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Start Monitoring */}
      {scanComplete && totalSelectedSources > 0 && (
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'success.50', border: 1, borderColor: 'success.200' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6" gutterBottom sx={{ color: 'success.main' }}>
                Ready to Start Monitoring
              </Typography>
              <Typography variant="body2">
                You've selected {totalSelectedSources} communities across{' '}
                {Object.keys(selectedSources).filter(p => selectedSources[p]?.length > 0).length} platforms.
                Start monitoring to begin collecting signals from these sources.
              </Typography>
            </Box>
            <Button
              variant="contained"
              color="success"
              onClick={handleStartMonitoring}
              disabled={loading}
              startIcon={<LaunchIcon />}
              size="large"
            >
              {loading ? 'Starting...' : 'Start Monitoring'}
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  )
}

export default SignalScan
