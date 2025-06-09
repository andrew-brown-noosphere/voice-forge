import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  useTheme,
  alpha,
  IconButton,
  Tooltip,
  Collapse,
  Alert,
  Skeleton,
  Stack,
  Divider,
  Badge,
  CircularProgress,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormGroup
} from '@mui/material'
import {
  AutoAwesome as AutoAwesomeIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Star as StarIcon,
  Lightbulb as LightbulbIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Lock as LockIcon,
  LockOpen as LockOpenIcon,
  Add as AddIcon
} from '@mui/icons-material'

import { useApi } from '../hooks/useApi'

const IntelligentPromptSuggestions = ({ 
  onPromptSelect, 
  selectedDomain = null, 
  selectedPlatform = null,
  maxSuggestions = 1  // Changed from 5 to 1 for faster generation
}) => {
  const theme = useTheme()
  const api = useApi()
  
  const [prompts, setPrompts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState({})
  const [contentSummary, setContentSummary] = useState(null)
  const [personaContext, setPersonaContext] = useState(null)
  const [messagingInsights, setMessagingInsights] = useState(null)
  const [showDetails, setShowDetails] = useState(false)
  const [funnelStage, setFunnelStage] = useState('') // New state for funnel stage
  const [promptLocked, setPromptLocked] = useState(false) // Lock prompt to prevent regeneration
  const [lockedPrompt, setLockedPrompt] = useState(null) // Store the locked prompt
  const [selectedPlatforms, setSelectedPlatforms] = useState([]) // Multiple platform selection

  // Load intelligent prompts
  const loadPrompts = async (forceFresh = false) => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🧠 Loading intelligent prompts...', {
        domain: selectedDomain,
        platform: selectedPlatform,
        selectedPlatforms,
        maxSuggestions,
        forceFresh,
        funnelStage
      })
      
      // Only pass platform if it's a valid value, otherwise pass null
      const validPlatforms = ['twitter', 'instagram', 'facebook', 'linkedin', 'email', 'blog', 'website', 'customer_support']
      
      // Use selectedPlatform from props first, then fall back to first selected platform from multi-selector
      let effectivePlatform = selectedPlatform
      if (!effectivePlatform && selectedPlatforms.length > 0) {
        effectivePlatform = selectedPlatforms[0]
      }
      
      const platformParam = effectivePlatform && validPlatforms.includes(effectivePlatform) ? effectivePlatform : null
      
      console.log('📡 Platform resolution:', {
        selectedPlatform,
        selectedPlatforms,
        effectivePlatform,
        platformParam
      })
      
      const response = await api.prompts.generate(
        selectedDomain || null,
        platformParam,
        maxSuggestions,
        null, // focus_areas
        null, // persona_id - could be enhanced later
        true, // include_messaging_framework
        funnelStage || null, // funnel_stage
        forceFresh ? `${Date.now()}-${Math.random()}` : null // aggressive cache buster
      )
      
      console.log('✨ Intelligent prompts loaded:', response)
      console.log('🔍 Content Summary:', response.content_summary)
      console.log('🔍 Persona Context:', response.persona_context)
      console.log('🔍 Messaging Insights:', response.messaging_insights)
      console.log('🔍 Prompts received:', response.prompts)
      
      // Check if we're getting real content or fallback data
      if (response.prompts && response.prompts[0]) {
        const firstPrompt = response.prompts[0]
        console.log('🔍 First prompt analysis:', {
          title: firstPrompt.title,
          prompt: firstPrompt.prompt?.substring(0, 100) + '...',
          platform: firstPrompt.platform,
          confidence: firstPrompt.confidence,
          isGeneric: firstPrompt.prompt?.includes('Business Manager in Technology')
        })
      }
      
      setPrompts(response.prompts || [])
      setContentSummary(response.content_summary || null)
      setPersonaContext(response.persona_context || null)
      setMessagingInsights(response.messaging_insights || null)
      
    } catch (err) {
      console.error('❌ Error loading intelligent prompts:', err)
      
      // Show fallback prompts if the feature isn't available yet
      if (err.message.includes('404') || err.message.includes('not found')) {
        console.log('🔄 Feature not available, showing sample prompts')
        loadSamplePrompts()
      } else {
        setError(`Failed to load intelligent prompts: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  // Load sample prompts as fallback
  const loadSamplePrompts = async () => {
    try {
      const response = await api.prompts.getSample('software', 'developer')
      setPrompts(response.prompts || [])
      setContentSummary(response.content_summary || null)
      setPersonaContext(response.persona_context || null)
      setMessagingInsights(response.messaging_insights || null)
    } catch (err) {
      console.error('Failed to load sample prompts:', err)
      setError('Intelligent prompts are not available yet. Please enter your prompt manually.')
    }
  }

  // Load prompts on mount and when dependencies change (but only if not locked)
  useEffect(() => {
    if (!promptLocked) {
      loadPrompts()
    }
  }, [selectedDomain, selectedPlatform, selectedPlatforms, maxSuggestions, funnelStage])

  const handlePromptSelect = (prompt) => {
    console.log('📝 Selected prompt:', prompt)
    if (onPromptSelect) {
      onPromptSelect(prompt.prompt, {
        platform: prompt.platform,
        tone: prompt.tone,
        category: prompt.category,
        confidence: prompt.confidence,
        reasoning: prompt.reasoning,
        keywords: prompt.keywords,
        personaAlignment: prompt.persona_alignment,
        messagingFramework: prompt.messaging_framework
      })
    }
  }

  const handleLockPrompt = (prompt) => {
    setLockedPrompt(prompt)
    setPromptLocked(true)
    console.log('🔒 Prompt locked:', prompt.title)
  }

  const handleUnlockPrompt = () => {
    setPromptLocked(false)
    setLockedPrompt(null)
    console.log('🔓 Prompt unlocked - will regenerate on changes')
  }

  const handleGenerateNew = async () => {
    console.log('🔄 Generate New Prompt button clicked!')
    console.log('Current state before generation:', {
      promptLocked,
      lockedPrompt: lockedPrompt?.title,
      currentPrompts: prompts.length,
      loading,
      selectedDomain,
      selectedPlatform,
      funnelStage
    })
    
    // Clear all state completely
    setPromptLocked(false)
    setLockedPrompt(null)
    setPrompts([]) // Clear existing prompts to force fresh generation
    setError(null) // Clear any errors
    
    console.log('💫 Cleared state, generating fresh prompts...')
    
    // Add a small delay to ensure state is cleared
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Force reload prompts immediately with aggressive cache busting
    await loadPrompts(true) // Pass forceFresh = true
    
    console.log('✅ New prompt generation completed!')
  }

  // Platform options with emojis and descriptions
  const platformOptions = [
    { value: 'twitter', label: 'Twitter', emoji: '🐦', description: 'Short-form social posts (280 chars)' },
    { value: 'linkedin', label: 'LinkedIn', emoji: '💼', description: 'Professional networking content' },
    { value: 'facebook', label: 'Facebook', emoji: '📱', description: 'Social media posts and updates' },
    { value: 'instagram', label: 'Instagram', emoji: '📷', description: 'Visual content with captions' },
    { value: 'email', label: 'Email', emoji: '📧', description: 'Newsletter and email campaigns' },
    { value: 'blog', label: 'Blog', emoji: '📝', description: 'Long-form articles and posts' },
    { value: 'website', label: 'Website', emoji: '🌐', description: 'Website copy and landing pages' },
    { value: 'customer_support', label: 'Support', emoji: '🎆', description: 'Help docs and support content' }
  ]

  const handlePlatformChange = (platform) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platform)) {
        return prev.filter(p => p !== platform)
      } else {
        return [...prev, platform]
      }
    })
  }

  const handleSelectAllPlatforms = () => {
    if (selectedPlatforms.length === platformOptions.length) {
      setSelectedPlatforms([])
    } else {
      setSelectedPlatforms(platformOptions.map(p => p.value))
    }
  }

  const toggleExpanded = (promptIndex) => {
    setExpanded(prev => ({
      ...prev,
      [promptIndex]: !prev[promptIndex]
    }))
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success'
    if (confidence >= 0.6) return 'warning'
    return 'error'
  }

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High Confidence'
    if (confidence >= 0.6) return 'Medium Confidence'
    return 'Low Confidence'
  }

  const getFunnelStageLabel = (stage) => {
    const labels = {
      'tofu': '🔝 Awareness (TOFU)',
      'mofu': '🎯 Consideration (MOFU)', 
      'bofu': '🎬 Decision (BOFU)'
    }
    return labels[stage] || 'All Stages'
  }

  const getFunnelStageDescription = (stage) => {
    const descriptions = {
      'tofu': 'Educational content that builds awareness and identifies problems',
      'mofu': 'Solution-focused content for evaluation and consideration',
      'bofu': 'Product-specific content for decision-making and implementation'
    }
    return descriptions[stage] || 'Content for any stage of the buyer\'s journey'
  }

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
            <AutoAwesomeIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              ✨ Intelligent Prompt Suggestions
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Analyzing your content to generate smart prompts...
            </Typography>
          </Box>
        </Box>
        
        <Stack spacing={2}>
          {[1, 2, 3].map((i) => (
            <Card key={i} sx={{ borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Skeleton variant="text" width="40%" height={28} />
                  <Skeleton variant="circular" width={24} height={24} />
                </Box>
                <Skeleton variant="text" width="100%" height={20} />
                <Skeleton variant="text" width="80%" height={20} />
                <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                  <Skeleton variant="rounded" width={80} height={24} />
                  <Skeleton variant="rounded" width={60} height={24} />
                </Box>
              </CardContent>
            </Card>
          ))}
        </Stack>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="warning" 
          action={
            <Button size="small" onClick={loadPrompts} startIcon={<RefreshIcon />}>
              Retry
            </Button>
          }
          sx={{ borderRadius: 3 }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            Intelligent Prompts Unavailable
          </Typography>
          {error}
        </Alert>
      </Box>
    )
  }

  if (!prompts || prompts.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Avatar sx={{ 
          bgcolor: alpha(theme.palette.info.main, 0.1), 
          color: theme.palette.info.main,
          width: 64,
          height: 64,
          mx: 'auto',
          mb: 2
        }}>
          <LightbulbIcon sx={{ fontSize: 32 }} />
        </Avatar>
        <Typography variant="h6" color="textSecondary" sx={{ mb: 1 }}>
          No Intelligent Prompts Available
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          Try crawling some content first, or enter your prompt manually.
        </Typography>
        <Button variant="outlined" onClick={loadPrompts} startIcon={<RefreshIcon />}>
          Try Again
        </Button>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
            <AutoAwesomeIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              ✨ Intelligent Prompt Suggestions
              {promptLocked && (
                <Chip 
                  icon={<LockIcon />}
                  label="Locked" 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {promptLocked 
                ? 'Prompt locked - adjust funnel stage/platform without regenerating'
                : 'AI-generated prompts based on your content and messaging'
              }
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title={showDetails ? 'Hide Details' : 'Show Analysis Details'}>
            <IconButton size="small" onClick={() => setShowDetails(!showDetails)}>
              {showDetails ? <VisibilityOffIcon /> : <VisibilityIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Debug Content & API">
            <IconButton 
              size="small" 
              onClick={async () => {
                console.log('🔍 Checking content status...')
                try {
                  const domains = await api.domains.list()
                  console.log('🌍 Available domains:', domains)
                  
                  if (selectedDomain) {
                    const content = await api.content.search('', selectedDomain, null, 5)
                    console.log('📝 Content for domain:', selectedDomain, content)
                  }
                  
                  const crawls = await api.crawls.list(5)
                  console.log('🕷️ Recent crawls:', crawls)
                } catch (err) {
                  console.error('❌ Error checking content:', err)
                }
              }}
              sx={{ bgcolor: 'warning.main', color: 'warning.contrastText', '&:hover': { bgcolor: 'warning.dark' } }}
            >
              🔍
            </IconButton>
          </Tooltip>
          {promptLocked ? (
            <>
              <Tooltip title="Unlock Prompt (will regenerate on changes)">
                <IconButton size="small" onClick={handleUnlockPrompt}>
                  <LockOpenIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Generate New Prompt">
                <IconButton 
                  size="small" 
                  onClick={handleGenerateNew} 
                  disabled={loading}
                  sx={{
                    bgcolor: loading ? 'action.disabled' : 'primary.main',
                    color: loading ? 'text.disabled' : 'primary.contrastText',
                    '&:hover': {
                      bgcolor: loading ? 'action.disabled' : 'primary.dark'
                    }
                  }}
                >
                  {loading ? <CircularProgress size={16} /> : <AddIcon />}
                </IconButton>
              </Tooltip>
            </>
          ) : (
            <Tooltip title="Generate New Prompt">
              <IconButton size="small" onClick={loadPrompts} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Analysis Summary (collapsible) */}
      <Collapse in={showDetails}>
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            {contentSummary && (
              <Grid item xs={12} md={4}>
                <Card sx={{ borderRadius: 3, height: '100%' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <TrendingUpIcon sx={{ fontSize: 20, color: theme.palette.success.main }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Content Analysis
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Business Type: <strong>{contentSummary.business_type}</strong>
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Content Pieces: <strong>{contentSummary.total_content}</strong>
                    </Typography>
                    {contentSummary.key_topics && contentSummary.key_topics.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="textSecondary">
                          Key Topics:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {contentSummary.key_topics.slice(0, 3).map((topic, i) => (
                            <Chip key={i} label={topic} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}
            
            {personaContext && (
              <Grid item xs={12} md={4}>
                <Card sx={{ borderRadius: 3, height: '100%' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <PsychologyIcon sx={{ fontSize: 20, color: theme.palette.info.main }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Target Persona
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Role: <strong>{personaContext.role}</strong>
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Industry: <strong>{personaContext.industry}</strong>
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Company Size: <strong>{personaContext.company_size}</strong>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
            
            {messagingInsights && messagingInsights.framework_included && (
              <Grid item xs={12} md={4}>
                <Card sx={{ borderRadius: 3, height: '100%' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <StarIcon sx={{ fontSize: 20, color: theme.palette.warning.main }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Messaging Framework
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Confidence: <strong>{(messagingInsights.confidence_score * 100).toFixed(0)}%</strong>
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Framework: <strong>Integrated</strong>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
          <Divider sx={{ mt: 2 }} />
        </Box>
      </Collapse>

      {/* Prompt Suggestions */}
      <Stack spacing={2}>
        {promptLocked && lockedPrompt ? (
          // Show locked prompt
          <Card 
            sx={{ 
              borderRadius: 3,
              border: `2px solid ${theme.palette.primary.main}`,
              bgcolor: alpha(theme.palette.primary.main, 0.05),
              transition: 'all 0.2s ease'
            }}
          >
            <CardContent sx={{ p: 3 }}>
              {/* Header */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <LockIcon sx={{ fontSize: 20, color: theme.palette.primary.main }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {lockedPrompt.title}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {/* Prompt Text */}
              <Typography 
                variant="body1" 
                sx={{ 
                  p: 2, 
                  borderRadius: 2, 
                  background: alpha(theme.palette.background.default, 0.5),
                  border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                  lineHeight: 1.6,
                  mb: 2
                }}
              >
                {lockedPrompt.prompt}
              </Typography>
              
              <Alert severity="info" sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">
                    🔒 This prompt is locked. You can adjust settings without regenerating, or generate a completely new prompt.
                  </Typography>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={handleGenerateNew}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={16} /> : <AddIcon />}
                    sx={{ 
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      ml: 2,
                      mr: 1
                    }}
                  >
                    {loading ? 'Generating...' : 'Generate New'}
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      console.log('🔥 Hard reset clicked - changing parameters')
                      setFunnelStage(funnelStage === '' ? 'tofu' : funnelStage === 'tofu' ? 'mofu' : funnelStage === 'mofu' ? 'bofu' : '')
                      handleGenerateNew()
                    }}
                    disabled={loading}
                    sx={{ 
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      mr: 1
                    }}
                  >
                    Hard Reset
                  </Button>
                  <Button
                    variant="text"
                    size="small"
                    onClick={async () => {
                      console.log('🔍 Checking content status...')
                      try {
                        const domains = await api.domains.list()
                        console.log('🌍 Available domains:', domains)
                        
                        if (selectedDomain) {
                          const content = await api.content.search('', selectedDomain, null, 5)
                          console.log('📝 Content for domain:', selectedDomain, content)
                        }
                        
                        const crawls = await api.crawls.list(5)
                        console.log('🕷️ Recent crawls:', crawls)
                      } catch (err) {
                        console.error('❌ Error checking content:', err)
                      }
                    }}
                    sx={{ 
                      borderRadius: 2,
                      textTransform: 'none',
                      fontWeight: 600,
                      fontSize: '0.75rem'
                    }}
                  >
                    Debug Content
                  </Button>
                </Box>
              </Alert>
            </CardContent>
            
            <CardActions sx={{ px: 3, pb: 2, gap: 1 }}>
              <Button
                variant="contained"
                onClick={() => handlePromptSelect(lockedPrompt)}
                startIcon={<AutoAwesomeIcon />}
                sx={{ 
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  flex: 1
                }}
              >
                Use This Prompt
              </Button>
              <Button
                variant="outlined"
                onClick={handleUnlockPrompt}
                startIcon={<LockOpenIcon />}
                sx={{ 
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                Unlock
              </Button>
            </CardActions>
          </Card>
        ) : (
          // Show regular prompts with lock option
          prompts.map((prompt, index) => (
            <Card 
              key={index} 
              sx={{ 
                borderRadius: 3,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: theme.shadows[8],
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                      {prompt.title}
                    </Typography>
                  </Box>
                  
                  <IconButton 
                    size="small" 
                    onClick={() => toggleExpanded(index)}
                    sx={{ ml: 1 }}
                  >
                    {expanded[index] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>

                {/* Prompt Text */}
                <Typography 
                  variant="body1" 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2, 
                    background: alpha(theme.palette.background.default, 0.5),
                    border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                    lineHeight: 1.6,
                    mb: 2
                  }}
                >
                  {prompt.prompt}
                </Typography>

                {/* Expanded Details */}
                <Collapse in={expanded[index]}>
                  <Box sx={{ mt: 2, pt: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.3)}` }}>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      <strong>Reasoning:</strong> {prompt.reasoning}
                    </Typography>
                    
                    {prompt.keywords && prompt.keywords.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          <strong>Keywords:</strong>
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {prompt.keywords.map((keyword, i) => (
                            <Chip key={i} label={keyword} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </Box>
                    )}

                    {prompt.persona_alignment && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          <strong>Persona Alignment:</strong>
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={prompt.persona_alignment.overall_score * 100}
                          color={getConfidenceColor(prompt.persona_alignment.overall_score)}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                        <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                          {(prompt.persona_alignment.overall_score * 100).toFixed(0)}% match with target audience
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Collapse>
              </CardContent>
              
              <CardActions sx={{ px: 3, pb: 2, gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={() => handlePromptSelect(prompt)}
                  startIcon={<AutoAwesomeIcon />}
                  sx={{ 
                    borderRadius: 2,
                    textTransform: 'none',
                    fontWeight: 600,
                    flex: 1
                  }}
                >
                  Use This Prompt
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => handleLockPrompt(prompt)}
                  startIcon={<LockIcon />}
                  sx={{ 
                    borderRadius: 2,
                    textTransform: 'none',
                    fontWeight: 600
                  }}
                >
                  Lock
                </Button>
              </CardActions>
            </Card>
          ))
        )}
      </Stack>

      {/* Funnel Stage Selector - Moved here to be under the prompt */}
      <Box sx={{ mt: 4, mb: 3 }}>
        <FormControl component="fieldset">
          <FormLabel 
            component="legend" 
            sx={{ 
              fontWeight: 600, 
              color: 'text.primary',
              mb: 2,
              '&.Mui-focused': {
                color: 'text.primary',
              }
            }}
          >
            Content Stage
          </FormLabel>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Choose the buyer's journey stage to target with this content idea
          </Typography>
          <RadioGroup
            value={funnelStage}
            onChange={(e) => setFunnelStage(e.target.value)}
            sx={{ gap: 1 }}
          >
            <FormControlLabel 
              value="" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    All Stages
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Content for any stage of the buyer's journey
                  </Typography>
                </Box>
              }
              sx={{
                m: 0,
                p: 1.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: funnelStage === '' ? 'primary.main' : 'divider',
                bgcolor: funnelStage === '' ? alpha(theme.palette.primary.main, 0.08) : 'transparent',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: alpha(theme.palette.primary.main, 0.04)
                }
              }}
            />
            <FormControlLabel 
              value="tofu" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    🔝 Awareness (TOFU)
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Educational content that builds awareness and identifies problems
                  </Typography>
                </Box>
              }
              sx={{
                m: 0,
                p: 1.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: funnelStage === 'tofu' ? 'primary.main' : 'divider',
                bgcolor: funnelStage === 'tofu' ? alpha(theme.palette.primary.main, 0.08) : 'transparent',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: alpha(theme.palette.primary.main, 0.04)
                }
              }}
            />
            <FormControlLabel 
              value="mofu" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    🎯 Consideration (MOFU)
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Solution-focused content for evaluation and consideration
                  </Typography>
                </Box>
              }
              sx={{
                m: 0,
                p: 1.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: funnelStage === 'mofu' ? 'primary.main' : 'divider',
                bgcolor: funnelStage === 'mofu' ? alpha(theme.palette.primary.main, 0.08) : 'transparent',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: alpha(theme.palette.primary.main, 0.04)
                }
              }}
            />
            <FormControlLabel 
              value="bofu" 
              control={<Radio />} 
              label={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    🎬 Decision (BOFU)
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Product-specific content for decision-making and implementation
                  </Typography>
                </Box>
              }
              sx={{
                m: 0,
                p: 1.5,
                borderRadius: 2,
                border: '1px solid',
                borderColor: funnelStage === 'bofu' ? 'primary.main' : 'divider',
                bgcolor: funnelStage === 'bofu' ? alpha(theme.palette.primary.main, 0.08) : 'transparent',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: alpha(theme.palette.primary.main, 0.04)
                }
              }}
            />
          </RadioGroup>
        </FormControl>
      </Box>

      {/* Platform Selector - Multi-select checkboxes */}
      <Box sx={{ mt: 3, mb: 3 }}>
        <FormControl component="fieldset">
          <FormLabel 
            component="legend" 
            sx={{ 
              fontWeight: 600, 
              color: 'text.primary',
              mb: 2,
              '&.Mui-focused': {
                color: 'text.primary',
              }
            }}
          >
            Target Platforms
          </FormLabel>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Select multiple platforms to create content for ({selectedPlatforms.length} selected)
          </Typography>
          
          {/* Select All Toggle */}
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleSelectAllPlatforms}
              sx={{ 
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 500
              }}
            >
              {selectedPlatforms.length === platformOptions.length ? 'Deselect All' : 'Select All'}
            </Button>
          </Box>
          
          <FormGroup sx={{ gap: 1 }}>
            {platformOptions.map((platform) => (
              <FormControlLabel
                key={platform.value}
                control={
                  <Checkbox
                    checked={selectedPlatforms.includes(platform.value)}
                    onChange={() => handlePlatformChange(platform.value)}
                    color="primary"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {platform.emoji} {platform.label}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {platform.description}
                    </Typography>
                  </Box>
                }
                sx={{
                  m: 0,
                  p: 1.5,
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: selectedPlatforms.includes(platform.value) ? 'primary.main' : 'divider',
                  bgcolor: selectedPlatforms.includes(platform.value) ? alpha(theme.palette.primary.main, 0.08) : 'transparent',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    bgcolor: alpha(theme.palette.primary.main, 0.04)
                  }
                }}
              />
            ))}
          </FormGroup>
          
          {selectedPlatforms.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="textSecondary">
                Selected platforms:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                {selectedPlatforms.map((platform) => {
                  const platformData = platformOptions.find(p => p.value === platform)
                  return (
                    <Chip
                      key={platform}
                      label={`${platformData?.emoji} ${platformData?.label}`}
                      size="small"
                      color="primary"
                      variant="outlined"
                      onDelete={() => handlePlatformChange(platform)}
                    />
                  )
                })}
              </Box>
            </Box>
          )}
        </FormControl>
      </Box>

      {/* Footer */}
      <Box sx={{ 
        mt: 3, 
        p: 2, 
        borderRadius: 2, 
        background: alpha(theme.palette.info.main, 0.05),
        border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <InfoIcon sx={{ fontSize: 16, color: theme.palette.info.main }} />
          <Typography variant="caption" sx={{ fontWeight: 600 }}>
            How it works
          </Typography>
        </Box>
        <Typography variant="caption" color="textSecondary">
          These prompts are generated by analyzing your crawled website content, identifying your business type, 
          value propositions, and target audience to create highly relevant, brand-aligned content suggestions.
          Select a funnel stage above to get content optimized for Awareness (TOFU), Consideration (MOFU), or Decision (BOFU) stages.
        </Typography>
      </Box>
    </Box>
  )
}

export default IntelligentPromptSuggestions
