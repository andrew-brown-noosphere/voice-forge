import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  CardContent,
  Chip,
  Avatar,
  LinearProgress,
  useTheme,
  alpha,
  Fade,
  Stack,
  IconButton,
  Tooltip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Snackbar,
  Alert
} from '@mui/material'
import {
  AutoAwesome as AutoAwesomeIcon,
  ContentCopy as ContentCopyIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Edit as EditIcon,
  Twitter as TwitterIcon,
  LinkedIn as LinkedInIcon,
  Facebook as FacebookIcon,
  Instagram as InstagramIcon,
  Email as EmailIcon,
  Article as ArticleIcon,
  Language as LanguageIcon,
  Support as SupportIcon,
  Psychology as PsychologyIcon,
  Tune as TuneIcon,
  Speed as SpeedIcon,
  Domain as DomainIcon,
  Category as CategoryIcon
} from '@mui/icons-material'

// Modern components
import {
  ModernCard,
  ModernTextField,
  ModernSelect,
  ModernButton,
  ModernAlert,
  ModernSectionHeader
} from '../components/ModernFormComponents'

// API service
import { useApi } from '../hooks/useApi'

// Platform options with icons
const platforms = [
  { value: 'twitter', label: 'Twitter', maxLength: 280, icon: TwitterIcon, color: '#1DA1F2' },
  { value: 'linkedin', label: 'LinkedIn', maxLength: 3000, icon: LinkedInIcon, color: '#0077B5' },
  { value: 'facebook', label: 'Facebook', maxLength: 2000, icon: FacebookIcon, color: '#1877F2' },
  { value: 'instagram', label: 'Instagram', maxLength: 2200, icon: InstagramIcon, color: '#E4405F' },
  { value: 'email', label: 'Email', maxLength: 5000, icon: EmailIcon, color: '#EA4335' },
  { value: 'blog', label: 'Blog Post', maxLength: 10000, icon: ArticleIcon, color: '#4285F4' },
  { value: 'website', label: 'Website', maxLength: 3000, icon: LanguageIcon, color: '#34A853' },
  { value: 'customer_support', label: 'Customer Support', maxLength: 1000, icon: SupportIcon, color: '#9333EA' },
]

// Tone options
const tones = [
  { value: 'professional', label: 'Professional', description: 'Formal and business-appropriate' },
  { value: 'casual', label: 'Casual', description: 'Relaxed and conversational' },
  { value: 'friendly', label: 'Friendly', description: 'Warm and approachable' },
  { value: 'enthusiastic', label: 'Enthusiastic', description: 'Energetic and exciting' },
  { value: 'informative', label: 'Informative', description: 'Educational and factual' },
  { value: 'persuasive', label: 'Persuasive', description: 'Compelling and convincing' },
  { value: 'authoritative', label: 'Authoritative', description: 'Expert and trustworthy' },
]

const ModernContentGenerator = () => {
  const theme = useTheme()
  const api = useApi()
  
  const [query, setQuery] = useState('')
  const [platform, setPlatform] = useState('')
  const [tone, setTone] = useState('')
  const [domains, setDomains] = useState([])
  const [selectedDomain, setSelectedDomain] = useState('')
  const [contentType, setContentType] = useState('')
  const [topK, setTopK] = useState(5)
  
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  const [generatedContent, setGeneratedContent] = useState(null)
  const [sourceChunks, setSourceChunks] = useState([])
  const [showSources, setShowSources] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Fetch domains on component mount with retry logic
  useEffect(() => {
    const fetchDomains = async (retryCount = 0) => {
      try {
        setLoading(true)
        const data = await api.domains.list()
        setDomains(data)
        if (data.length > 0) {
          setSelectedDomain(data[0])
        }
        // Clear any previous errors on success
        if (error && error.includes('domains')) {
          setError(null)
        }
      } catch (err) {
        console.error('Error fetching domains:', err)
        
        // Retry logic - try up to 2 more times with delay
        if (retryCount < 2 && !err.message.includes('Not authenticated') && !err.message.includes('401')) {
          console.log(`Retrying domains fetch (attempt ${retryCount + 2}/3)...`)
          setTimeout(() => fetchDomains(retryCount + 1), 1000 * (retryCount + 1))
          return
        }
        
        // Don't show error to user - domains are optional for content generation
        // The dropdown will just show "All Domains" and content generation will work fine
        console.log('Using all domains as fallback (domains API not available)')
        
        // Set empty domains array as fallback
        setDomains([])
      } finally {
        setLoading(false)
      }
    }
    
    // Only fetch if we have authentication
    if (api) {
      fetchDomains()
    }
  }, [api])

  const handleGenerate = async () => {
    if (!query || !platform || !tone) {
      setError('Please fill in all required fields')
      return
    }
    
    try {
      setGenerating(true)
      setError(null)
      setSuccess(null)
      
      console.log('Generating content with params:', {
        query,
        platform,
        tone,
        selectedDomain: selectedDomain || undefined,
        contentType: contentType || undefined,
        topK
      })
      
      const data = await api.rag.generateContent(
        query,
        platform,
        tone,
        selectedDomain || undefined,
        contentType || undefined,
        topK
      )
      
      console.log('Content generation response:', data)
      
      if (!data || !data.text) {
        throw new Error('Invalid response format - no content text received')
      }
      
      setGeneratedContent(data.text)
      setSourceChunks(data.source_chunks || [])
      setSuccess('Content generated successfully!')
    } catch (err) {
      console.error('Error generating content:', err)
      
      // Provide more specific error messages
      let errorMessage = 'Failed to generate content. '
      
      if (err.message.includes('401') || err.message.includes('Not authenticated')) {
        errorMessage += 'Authentication issue - please refresh the page and try again.'
      } else if (err.message.includes('404')) {
        errorMessage += 'Content generation service not found. Please check if the backend is running.'
      } else if (err.message.includes('500')) {
        errorMessage += 'Server error occurred. Please try again in a moment.'
      } else if (err.message.includes('timeout')) {
        errorMessage += 'Request timed out. Please try again.'
      } else if (err.message.includes('Invalid response')) {
        errorMessage += 'Received invalid response from server.'
      } else {
        errorMessage += `Error: ${err.message}`
      }
      
      setError(errorMessage)
    } finally {
      setGenerating(false)
    }
  }

  const handleCopyContent = () => {
    if (generatedContent) {
      navigator.clipboard.writeText(generatedContent)
      setSuccess('Content copied to clipboard!')
    }
  }

  const currentPlatform = platforms.find(p => p.value === platform) || {}
  const contentLength = generatedContent ? generatedContent.length : 0
  const characterLimit = currentPlatform.maxLength || 0
  const isOverLimit = characterLimit > 0 && contentLength > characterLimit
  const PlatformIcon = currentPlatform.icon

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          component="h1" 
          sx={{ 
            fontWeight: 800,
            background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}
        >
          ✨ Content Generator
        </Typography>
        <Typography variant="h6" color="textSecondary" sx={{ fontWeight: 400, mb: 3 }}>
          Generate brand-aligned content powered by your website and brand content
        </Typography>
      </Box>

      {/* Main Form */}
      <ModernCard sx={{ mb: 4 }} hover={false}>
        <CardContent sx={{ p: 4 }}>
          <ModernSectionHeader
            icon={EditIcon}
            title="Content Creation"
            description="Describe what you want to write and choose your platform"
            color="primary"
          />
          
          <Grid container spacing={4} sx={{ mt: 1 }}>
            {/* Query Input */}
            <Grid item xs={12}>
              <ModernTextField
                label="What would you like to write about?"
                placeholder="E.g., 'Write a post about our new product features' or 'Create a customer support response for shipping questions'"
                multiline
                rows={4}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                icon={EditIcon}
                required
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontSize: '1.1rem',
                    lineHeight: 1.6
                  }
                }}
              />
            </Grid>
            
            {/* Platform Selection */}
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.primary.main, 0.05),
                border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
                    <LanguageIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Platform & Format
                  </Typography>
                </Box>
                
                <ModernSelect
                  label="Target Platform"
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  options={platforms.map(p => ({
                    value: p.value,
                    label: `${p.label} ${p.maxLength ? `(${p.maxLength} chars)` : ''}`
                  }))}
                  required
                />
                
                {platform && currentPlatform && (
                  <Box sx={{ mt: 2, p: 2, borderRadius: 2, background: alpha(currentPlatform.color || theme.palette.primary.main, 0.1) }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {PlatformIcon && <PlatformIcon sx={{ fontSize: 20, color: currentPlatform.color }} />}
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {currentPlatform.label}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="textSecondary">
                      {currentPlatform.maxLength ? `Character limit: ${currentPlatform.maxLength}` : 'No character limit'}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
            
            {/* Tone Selection */}
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.secondary.main, 0.05),
                border: `1px solid ${alpha(theme.palette.secondary.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.secondary.main, 0.1), color: theme.palette.secondary.main }}>
                    <PsychologyIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Writing Style
                  </Typography>
                </Box>
                
                <ModernSelect
                  label="Tone of Voice"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  options={tones.map(t => ({
                    value: t.value,
                    label: t.label
                  }))}
                  required
                />
                
                {tone && (
                  <Box sx={{ mt: 2, p: 2, borderRadius: 2, background: alpha(theme.palette.secondary.main, 0.1) }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {tones.find(t => t.value === tone)?.label}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {tones.find(t => t.value === tone)?.description}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </ModernCard>

      {/* Advanced Options */}
      <ModernCard sx={{ mb: 4 }} hover={false}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            cursor: 'pointer',
            userSelect: 'none'
          }} onClick={() => setShowAdvanced(!showAdvanced)}>
            <ModernSectionHeader
              icon={TuneIcon}
              title="Advanced Options"
              description="Fine-tune your content generation settings"
              color="info"
            />
            <IconButton>
              <ExpandMoreIcon sx={{ 
                transform: showAdvanced ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.3s ease'
              }} />
            </IconButton>
          </Box>
          
          <Fade in={showAdvanced}>
            <Box sx={{ display: showAdvanced ? 'block' : 'none', mt: 3 }}>
              <Grid container spacing={4}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ 
                    p: 3, 
                    borderRadius: 3, 
                    background: alpha(theme.palette.success.main, 0.05),
                    border: `1px solid ${alpha(theme.palette.success.main, 0.1)}`,
                    height: '100%'
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), color: theme.palette.success.main }}>
                        <DomainIcon />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Domain Filter
                      </Typography>
                    </Box>
                    
                    <ModernSelect
                      label="Specific Domain"
                      value={selectedDomain}
                      onChange={(e) => setSelectedDomain(e.target.value)}
                      options={[
                        { value: '', label: 'All Domains' },
                        ...domains.map(domain => ({
                          value: domain,
                          label: domain
                        }))
                      ]}
                    />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                      Focus on content from a specific website
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box sx={{ 
                    p: 3, 
                    borderRadius: 3, 
                    background: alpha(theme.palette.warning.main, 0.05),
                    border: `1px solid ${alpha(theme.palette.warning.main, 0.1)}`,
                    height: '100%'
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Avatar sx={{ bgcolor: alpha(theme.palette.warning.main, 0.1), color: theme.palette.warning.main }}>
                        <CategoryIcon />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Content Type
                      </Typography>
                    </Box>
                    
                    <ModernSelect
                      label="Content Type Filter"
                      value={contentType}
                      onChange={(e) => setContentType(e.target.value)}
                      options={[
                        { value: '', label: 'All Content Types' },
                        { value: 'blog_post', label: 'Blog Post' },
                        { value: 'product_description', label: 'Product Description' },
                        { value: 'about_page', label: 'About Page' },
                        { value: 'landing_page', label: 'Landing Page' },
                        { value: 'article', label: 'Article' },
                        { value: 'news', label: 'News' },
                        { value: 'press_release', label: 'Press Release' },
                        { value: 'documentation', label: 'Documentation' },
                        { value: 'faq', label: 'FAQ' }
                      ]}
                    />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                      Filter by specific content categories
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box sx={{ 
                    p: 3, 
                    borderRadius: 3, 
                    background: alpha(theme.palette.error.main, 0.05),
                    border: `1px solid ${alpha(theme.palette.error.main, 0.1)}`,
                    height: '100%'
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Avatar sx={{ bgcolor: alpha(theme.palette.error.main, 0.1), color: theme.palette.error.main }}>
                        <SpeedIcon />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Retrieval Settings
                      </Typography>
                    </Box>
                    
                    <ModernTextField
                      label="Number of Sources"
                      type="number"
                      value={topK}
                      onChange={(e) => setTopK(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
                      inputProps={{ min: 1, max: 20 }}
                      helperText="How many content chunks to use (1-20)"
                    />
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </Fade>
        </CardContent>
      </ModernCard>

      {/* Generate Button */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <ModernButton
          variant="contained"
          size="large"
          icon={generating ? null : AutoAwesomeIcon}
          onClick={handleGenerate}
          disabled={generating || !query || !platform || !tone}
          gradient={true}
          glow={true}
          sx={{ 
            minWidth: 300,
            py: 2,
            fontSize: '1.1rem'
          }}
        >
          {generating ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress size={24} color="inherit" />
              Generating Content...
            </Box>
          ) : (
            'Generate Content'
          )}
        </ModernButton>
      </Box>

      {/* Generated Content */}
      {generatedContent && (
        <ModernCard hover={false}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), color: theme.palette.success.main, width: 48, height: 48 }}>
                  <AutoAwesomeIcon />
                </Avatar>
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                    Generated Content
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    {platform && (
                      <Chip 
                        label={platforms.find(p => p.value === platform)?.label || platform}
                        size="small"
                        color="primary"
                        sx={{ fontWeight: 600 }}
                      />
                    )}
                    {tone && (
                      <Chip 
                        label={tones.find(t => t.value === tone)?.label || tone}
                        size="small"
                        color="secondary"
                        sx={{ fontWeight: 600 }}
                      />
                    )}
                  </Stack>
                </Box>
              </Box>
              
              {characterLimit > 0 && (
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h6" color={isOverLimit ? "error" : "success.main"} sx={{ fontWeight: 700 }}>
                    {contentLength} / {characterLimit}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    characters
                  </Typography>
                </Box>
              )}
            </Box>
            
            {isOverLimit && (
              <ModernAlert
                severity="warning"
                title="Character Limit Exceeded"
                description={`Content exceeds the character limit for ${currentPlatform.label}. Consider shortening or using a different platform.`}
                sx={{ mb: 3 }}
              />
            )}
            
            {/* Progress Bar for Character Limit */}
            {characterLimit > 0 && (
              <Box sx={{ mb: 3 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min((contentLength / characterLimit) * 100, 100)}
                  color={isOverLimit ? "error" : "success"}
                  sx={{ 
                    height: 8, 
                    borderRadius: 4,
                    backgroundColor: alpha(theme.palette.text.secondary, 0.1),
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
            )}
            
            <ModernCard sx={{ mb: 3, background: alpha(theme.palette.background.default, 0.5) }} hover={false}>
              <CardContent sx={{ p: 3 }}>
                <Typography 
                  variant="body1" 
                  component="div" 
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.7,
                    fontSize: '1.1rem'
                  }}
                >
                  {generatedContent}
                </Typography>
              </CardContent>
            </ModernCard>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <ModernButton
                variant="contained"
                icon={ContentCopyIcon}
                onClick={handleCopyContent}
                color="success"
              >
                Copy to Clipboard
              </ModernButton>
            </Box>
            
            {/* Source Content */}
            {sourceChunks.length > 0 && (
              <Box sx={{ mt: 4 }}>
                <Divider sx={{ mb: 3 }} />
                
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  userSelect: 'none',
                  p: 2,
                  borderRadius: 2,
                  background: alpha(theme.palette.info.main, 0.05),
                  border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`
                }} onClick={() => setShowSources(!showSources)}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: alpha(theme.palette.info.main, 0.1), color: theme.palette.info.main }}>
                      <InfoIcon />
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Source References ({sourceChunks.length})
                    </Typography>
                  </Box>
                  <IconButton>
                    <ExpandMoreIcon sx={{ 
                      transform: showSources ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s ease'
                    }} />
                  </IconButton>
                </Box>
                
                <Fade in={showSources}>
                  <Box sx={{ display: showSources ? 'block' : 'none', mt: 3 }}>
                    <Grid container spacing={3}>
                      {sourceChunks.map((chunk, index) => (
                        <Grid item xs={12} md={6} key={chunk.chunk_id}>
                          <ModernCard hover={false}>
                            <CardContent sx={{ p: 3 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                                  Source {index + 1}
                                </Typography>
                                <Box sx={{ textAlign: 'right' }}>
                                  <Typography variant="h6" color="primary" sx={{ fontWeight: 700 }}>
                                    {(chunk.similarity * 100).toFixed(1)}%
                                  </Typography>
                                  <Typography variant="caption" color="textSecondary">
                                    relevance
                                  </Typography>
                                </Box>
                              </Box>
                              <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                                {chunk.text}
                              </Typography>
                            </CardContent>
                          </ModernCard>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </Fade>
              </Box>
            )}
          </CardContent>
        </ModernCard>
      )}
      
      {/* Snackbars */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setError(null)} 
          severity="error" 
          sx={{ 
            width: '100%',
            borderRadius: 3,
            backdropFilter: 'blur(8px)',
            background: alpha(theme.palette.error.main, 0.9),
            color: 'white'
          }}
        >
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSuccess(null)} 
          severity="success" 
          sx={{ 
            width: '100%',
            borderRadius: 3,
            backdropFilter: 'blur(8px)',
            background: alpha(theme.palette.success.main, 0.9),
            color: 'white'
          }}
        >
          {success}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default ModernContentGenerator