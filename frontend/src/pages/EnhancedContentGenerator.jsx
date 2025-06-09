import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Divider,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Snackbar,
  Switch,
  FormControlLabel,
  Tab,
  Tabs,
  Avatar,
  alpha,
  useTheme
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import InfoIcon from '@mui/icons-material/Info'
import PersonIcon from '@mui/icons-material/Person'
import BusinessIcon from '@mui/icons-material/Business'
import EditIcon from '@mui/icons-material/Edit'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
// Import Clerk hooks
import { useUser, useOrganization } from '@clerk/clerk-react'
// Import existing VoiceForge API
import { useApi } from '../hooks/useApi'
// Import new Gypsum integration
import { gypsumClient } from '../services/gypsum'
// Import Intelligent Prompt Suggestions
import IntelligentPromptSuggestions from '../components/IntelligentPromptSuggestions'

// Platform options (existing VoiceForge)
const platforms = [
  { value: 'twitter', label: 'Twitter', maxLength: 280 },
  { value: 'linkedin', label: 'LinkedIn', maxLength: 3000 },
  { value: 'facebook', label: 'Facebook', maxLength: 2000 },
  { value: 'instagram', label: 'Instagram', maxLength: 2200 },
  { value: 'email', label: 'Email', maxLength: 5000 },
  { value: 'blog', label: 'Blog Post', maxLength: 10000 },
  { value: 'website', label: 'Website', maxLength: 3000 },
  { value: 'customer_support', label: 'Customer Support', maxLength: 1000 },
]

// Tone options (existing VoiceForge)
const tones = [
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'informative', label: 'Informative' },
  { value: 'persuasive', label: 'Persuasive' },
  { value: 'authoritative', label: 'Authoritative' },
]

const EnhancedContentGenerator = () => {
  const theme = useTheme()
  // Clerk authentication
  const { user } = useUser()
  const { organization } = useOrganization()
  
  // TEMPORARY: Use demo user ID for demo - revert to org ID later
  // const gypsumUserId = organization?.id || user?.id || 'demo-user'
  const gypsumUserId = '123e4567-e89b-12d3-a456-426614174000' // Demo user - Gypsum returns demo data for any user
  
  // Existing VoiceForge state
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

  // NEW: Gypsum integration state
  const [gypsumContext, setGypsumContext] = useState(null)
  const [gypsumPersonas, setGypsumPersonas] = useState([])
  const [selectedPersonas, setSelectedPersonas] = useState([])
  const [selectedPainPoints, setSelectedPainPoints] = useState([])
  const [gypsumConnected, setGypsumConnected] = useState(false)
  const [gypsumError, setGypsumError] = useState(null)
  const [gypsumLoading, setGypsumLoading] = useState(true)
  const [enhancedPrompt, setEnhancedPrompt] = useState('')
  
  // Tab management for prompt input vs intelligent suggestions
  const [inputTab, setInputTab] = useState(0) // 0 = manual input, 1 = intelligent suggestions

  // NEW: Add detailed connection test function
  const testGypsumConnection = async () => {
    console.log('🧪 Testing Gypsum connection manually...')
    
    // Test 1: Basic fetch to health endpoint
    try {
      console.log('Step 1: Testing basic fetch to health endpoint')
      const response = await fetch('http://localhost:2007/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      console.log('Health check response status:', response.status)
      console.log('Health check response ok:', response.ok)
      console.log('Health check response headers:', Object.fromEntries(response.headers.entries()))
      
      if (response.ok) {
        const contentType = response.headers.get('content-type')
        console.log('Content-Type:', contentType)
        
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json()
          console.log('Health check data:', data)
        } else {
          const text = await response.text()
          console.log('Health check returned non-JSON:')
          console.log(text.substring(0, 500) + '...') // First 500 chars
        }
        
        // Test 2: Try personas endpoint
        console.log('\nStep 2: Testing personas endpoint')
        const personasResponse = await fetch(`http://localhost:2007/api/personas/context?user_id=${gypsumUserId}`)
        console.log('Personas response status:', personasResponse.status)
        console.log('Personas content-type:', personasResponse.headers.get('content-type'))
        
        if (personasResponse.ok) {
          const personasContentType = personasResponse.headers.get('content-type')
          if (personasContentType && personasContentType.includes('application/json')) {
            const personasData = await personasResponse.json()
            console.log('\n📦 PERSONAS API RESPONSE:')
            console.log('Full response:', JSON.stringify(personasData, null, 2))
          } else {
            const personasText = await personasResponse.text()
            console.log('\n❌ PERSONAS API RETURNED HTML/TEXT:')
            console.log(personasText.substring(0, 500) + '...')
          }
        } else {
          const errorText = await personasResponse.text()
          console.log('Personas error response:', errorText.substring(0, 500) + '...')
        }
        
      } else {
        const errorText = await response.text()
        console.log('Health check failed with status:', response.status)
        console.log('Response:', errorText.substring(0, 500) + '...')
      }
    } catch (error) {
      console.log('Health check error type:', error.name)
      console.log('Health check error message:', error.message)
      console.log('Health check full error:', error)
    }
    
    // Test alternative endpoints
    console.log('\nStep 3: Testing alternative endpoint paths')
    const alternativePaths = [
      '/api/v1/personas/context',
      '/personas/context', 
      '/api/personas',
      '/personas'
    ]
    
    for (const path of alternativePaths) {
      try {
        const url = `http://localhost:2007${path}?user_id=${gypsumUserId}`
        console.log(`Testing: ${url}`)
        const response = await fetch(url)
        console.log(`${path}: Status ${response.status}, Content-Type: ${response.headers.get('content-type')}`)
      } catch (error) {
        console.log(`${path}: Error - ${error.message}`)
      }
    }
  }

  // NEW: Initialize Gypsum connection
  useEffect(() => {
    const initializeGypsum = async () => {
      try {
        setGypsumLoading(true)
        setGypsumError(null)
        console.log('🔌 Connecting to Gypsum...')
        console.log('🔍 Using organization/user ID:', gypsumUserId)
        
        const validation = await gypsumClient.validateConnection(gypsumUserId)
        console.log('🧪 Validation result:', validation)
        
        if (validation.connected && validation.userAccess) {
          console.log('✅ Gypsum connected successfully')
          setGypsumConnected(true)
          
          // Fetch context data with detailed logging
          console.log('📊 Fetching context data...')
          const context = await gypsumClient.fetchAllContext(gypsumUserId)
          console.log('📦 Full context received:', context)
          console.log('👥 Personas data:', context.personas)
          console.log('💬 Messaging data:', context.messaging)
          console.log('🎯 Positioning data:', context.positioning)
          
          setGypsumContext(context)
          
          // More detailed persona parsing
          const personas = context.personas?.personas || context.personas?.data || context.personas || []
          console.log('🔍 Extracted personas array:', personas)
          console.log('📏 Personas array length:', personas.length)
          
          setGypsumPersonas(personas)
          
          if (personas.length > 0) {
            console.log('🎯 Setting default personas:', [personas[0].id])
            setSelectedPersonas([personas[0].id])
          } else {
            console.warn('⚠️ No personas found in response')
            console.warn('Raw personas data structure:', JSON.stringify(context.personas, null, 2))
          }
          
          console.log(`📊 Loaded ${personas.length} personas from Gypsum`)
        } else {
          console.warn('⚠️ Gypsum connection failed:', JSON.stringify(validation, null, 2))
          console.warn('🔍 Debug info:')
          console.warn('- User ID being used:', gypsumUserId)
          console.warn('- Organization:', organization)
          console.warn('- User:', user)
          setGypsumError(`Connection failed: ${validation.error || JSON.stringify(validation)}`)
        }
      } catch (err) {
        console.warn('⚠️ Could not connect to Gypsum:', err.message)
        console.warn('Full error details:', err)
        setGypsumError(`Failed to connect: ${err.message}`)
      } finally {
        setGypsumLoading(false)
      }
    }

    initializeGypsum()
  }, [])

  // Existing VoiceForge domain fetching
  useEffect(() => {
    const fetchDomains = async () => {
      if (loading || !api) {
        return
      }
      
      try {
        setLoading(true)
        const data = await api.domains.list()
        setDomains(data || [])
        if (data && data.length > 0) {
          setSelectedDomain(data[0])
        }
      } catch (err) {
        console.warn('Could not fetch domains:', err.message)
        setDomains([])
      } finally {
        setLoading(false)
      }
    }
    
    const timeoutId = setTimeout(fetchDomains, 100)
    return () => clearTimeout(timeoutId)
  }, [])

  // NEW: Generate enhanced prompt when Gypsum options change
  useEffect(() => {
    if (gypsumConnected && gypsumContext && selectedPersonas.length > 0 && query && platform) {
      try {
        // Use the first selected persona for prompt generation (could be enhanced to merge multiple personas)
        const primaryPersona = selectedPersonas[0]
        
        // Add selected pain points to the additional instructions
        let additionalInstructions = `Original request: ${query}`
        if (selectedPainPoints.length > 0) {
          additionalInstructions += `\n\nFocus specifically on these pain points:\n${selectedPainPoints.map(point => `- ${point}`).join('\n')}`
        }
        if (selectedPersonas.length > 1) {
          additionalInstructions += `\n\nTarget multiple personas: ${selectedPersonas.map(id => {
            const persona = gypsumPersonas.find(p => p.id === id)
            return persona ? `${persona.role} (${persona.seniority_level})` : id
          }).join(', ')}`
        }
        
        const prompt = gypsumClient.generateEnhancedPrompt(
          gypsumContext,
          primaryPersona,
          `${platform} ${contentType || 'post'}`,
          additionalInstructions
        )
        setEnhancedPrompt(prompt)
      } catch (err) {
        console.warn('Could not generate enhanced prompt:', err.message)
        setEnhancedPrompt('')
      }
    } else {
      setEnhancedPrompt('')
    }
  }, [gypsumConnected, gypsumContext, selectedPersonas, selectedPainPoints, query, platform, contentType, gypsumPersonas])

  const handleGenerate = async () => {
    if (!query) {
      setError('Please enter what you would like to write about')
      return
    }
    
    try {
      setGenerating(true)
      setError(null)
      setSuccess(null)
      
      // Use enhanced prompt if Gypsum is connected and personas are selected, otherwise use original query
      const finalQuery = gypsumConnected && selectedPersonas.length > 0 && enhancedPrompt ? enhancedPrompt : query
      
      console.log('Generating content with params:', {
        query: gypsumConnected && selectedPersonas.length > 0 ? 'Enhanced with Gypsum context' : query,
        platform,
        tone,
        selectedDomain: selectedDomain || undefined,
        contentType: contentType || undefined,
        topK,
        gypsumEnhanced: gypsumConnected && selectedPersonas.length > 0
      })
      
      const data = await api.rag.generateContent(
        finalQuery,
        platform || 'general',
        tone || 'professional',
        selectedDomain || undefined,
        contentType || undefined,
        topK
      )
      
      if (!data || !data.text) {
        throw new Error('Invalid response format - no content text received')
      }
      
      setGeneratedContent(data.text)
      setSourceChunks(data.source_chunks || [])
      
      const successMessage = gypsumConnected && selectedPersonas.length > 0 
        ? `Persona-aware content generated successfully for ${selectedPersonas.length} persona(s)!` 
        : 'Content generated successfully!'
      setSuccess(successMessage)
      
    } catch (err) {
      console.error('Error generating content:', err)
      
      let errorMessage = 'Failed to generate content. '
      
      if (err.message.includes('401') || err.message.includes('Not authenticated')) {
        errorMessage += 'Authentication issue - please refresh the page and try again.'
      } else if (err.message.includes('404')) {
        errorMessage += 'Content generation service not found. Please check if the backend is running.'
      } else if (err.message.includes('500')) {
        errorMessage += 'Server error occurred. Please try again in a moment.'
      } else if (err.message.includes('timeout')) {
        errorMessage += 'Request timed out. Please try again.'
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
  const selectedPersonasData = gypsumPersonas.filter(p => selectedPersonas.includes(p.id))
  const allSelectedPainPoints = selectedPersonasData.flatMap(p => p.pain_points || [])
  const uniquePainPoints = [...new Set(allSelectedPainPoints)]

  // Custom TabPanel component
  const TabPanel = ({ children, value, index, ...other }) => {
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`prompt-tabpanel-${index}`}
        aria-labelledby={`prompt-tab-${index}`}
        {...other}
      >
        {value === index && children}
      </div>
    )
  }

  // Handle intelligent prompt selection
  const handlePromptSelect = (promptText, promptMeta) => {
    console.log('📝 Selected intelligent prompt:', { promptText, promptMeta })
    
    setQuery(promptText)
    
    // Auto-fill platform and tone if provided
    if (promptMeta?.platform && !platform) {
      setPlatform(promptMeta.platform)
    }
    if (promptMeta?.tone && !tone) {
      setTone(promptMeta.tone)
    }
    
    // Switch to manual input tab to show the filled prompt
    setInputTab(0)
    
    // Show success message
    setSuccess(`Intelligent prompt selected! Category: ${promptMeta?.category || 'General'}`)
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Enhanced Content Generator
      </Typography>
      
      {/* NEW: Gypsum Integration Status */}
      {gypsumLoading && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Box display="flex" alignItems="center">
            <CircularProgress size={16} sx={{ mr: 1 }} />
            Connecting to Gypsum Product Compass...
          </Box>
        </Alert>
      )}
      
      {!gypsumLoading && gypsumConnected && (
        <Alert severity="success" sx={{ mb: 2 }}>
          <Box display="flex" alignItems="center">
            <BusinessIcon sx={{ mr: 1 }} />
            Connected to Gypsum Product Compass - {gypsumPersonas.length} personas available for persona-aware content generation
          </Box>
        </Alert>
      )}
      
      {!gypsumLoading && !gypsumConnected && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Box>
            <Box display="flex" alignItems="center" mb={1}>
              <BusinessIcon sx={{ mr: 1 }} />
              Gypsum Product Compass not connected
            </Box>
            <Typography variant="body2">
              {gypsumError || 'Could not connect to Gypsum API on localhost:3001. Make sure Gypsum API server is running with "npm run dev:api" or "npm run dev:full"'}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
              You can still use basic content generation without persona targeting.
            </Typography>
          </Box>
        </Alert>
      )}
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Generate Brand-Aligned Content
        </Typography>
        
        {/* Tab Headers */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs 
            value={inputTab} 
            onChange={(e, newValue) => setInputTab(newValue)}
            aria-label="prompt input tabs"
            sx={{
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem'
              }
            }}
          >
            <Tab 
              icon={<EditIcon />} 
              iconPosition="start"
              label="Manual Input" 
              id="prompt-tab-0"
              aria-controls="prompt-tabpanel-0"
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<LightbulbIcon />} 
              iconPosition="start"
              label="✨ AI Prompt Suggestions" 
              id="prompt-tab-1"
              aria-controls="prompt-tabpanel-1"
              sx={{ minHeight: 64 }}
            />
          </Tabs>
        </Box>

        {/* Manual Input Tab */}
        <TabPanel value={inputTab} index={0}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
              <EditIcon />
            </Avatar>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Manual Content Creation
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Describe what you want to write and choose your platform
              </Typography>
            </Box>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="What would you like to write about?"
                placeholder="E.g., 'Write a post about our new product features' or try our AI suggestions above!"
                variant="outlined"
                fullWidth
                multiline
                rows={4}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontSize: '1.1rem',
                    lineHeight: 1.6
                  }
                }}
              />
              
              {!query && (
                <Alert 
                  severity="info" 
                  sx={{ 
                    mt: 2, 
                    borderRadius: 2,
                    '& .MuiAlert-message': {
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }
                  }}
                >
                  <LightbulbIcon sx={{ fontSize: 20 }} />
                  <Typography variant="body2">
                    <strong>Tip:</strong> Try the "✨ AI Prompt Suggestions" tab above for AI-generated prompts based on your content!
                  </Typography>
                </Alert>
              )}
            </Grid>
          </Grid>
        </TabPanel>

        {/* AI Prompt Suggestions Tab */}
        <TabPanel value={inputTab} index={1}>
          <IntelligentPromptSuggestions
            onPromptSelect={handlePromptSelect}
            selectedDomain={selectedDomain}
            selectedPlatform={platform}
            maxSuggestions={1}
          />
        </TabPanel>
      </Paper>
      
      {/* Persona Selection */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Multi-Select Personas Widget */}
          <Grid item xs={12}>
            <Card variant="outlined" sx={{ p: 2, opacity: gypsumConnected ? 1 : 0.7 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Target Personas (Multi-Select)
                {!gypsumConnected && <Chip label="Demo Mode" size="small" color="warning" sx={{ ml: 1 }} />}
                {gypsumConnected && <Chip label="Persona-Aware Content" size="small" color="success" sx={{ ml: 1 }} />}
              </Typography>
              
              {gypsumConnected ? (
                // Real Gypsum personas - Checkbox UI
                <>
                  <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                    Select one or more personas to target with your content:
                  </Typography>
                  
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    {gypsumPersonas.map((persona) => (
                      <Grid item xs={12} sm={6} md={4} key={persona.id}>
                        <Card 
                          variant="outlined" 
                          sx={{ 
                            p: 2, 
                            cursor: 'pointer',
                            border: selectedPersonas.includes(persona.id) ? 2 : 1,
                            borderColor: selectedPersonas.includes(persona.id) ? 'primary.main' : 'divider',
                            bgcolor: selectedPersonas.includes(persona.id) ? 'primary.50' : 'background.paper',
                            '&:hover': {
                              borderColor: 'primary.main',
                              bgcolor: 'primary.50'
                            }
                          }}
                          onClick={() => {
                            setSelectedPersonas(prev => 
                              prev.includes(persona.id)
                                ? prev.filter(id => id !== persona.id)
                                : [...prev, persona.id]
                            )
                          }}
                        >
                          <Box display="flex" alignItems="flex-start" gap={1}>
                            <Box sx={{ pt: 0.5 }}>
                              <input
                                type="checkbox"
                                checked={selectedPersonas.includes(persona.id)}
                                onChange={() => {}} // Handled by card click
                                style={{ 
                                  accentColor: 'var(--mui-palette-primary-main)',
                                  transform: 'scale(1.1)'
                                }}
                              />
                            </Box>
                            <Box flex={1}>
                              <Typography variant="subtitle2" fontWeight="bold">
                                {persona.role}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                {persona.seniority_level} • {persona.industry}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {persona.company_size}
                              </Typography>
                            </Box>
                          </Box>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                  
                  {selectedPersonas.length > 0 && (
                    <Box>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        <strong>Selected {selectedPersonas.length} persona(s):</strong> {selectedPersonasData.map(p => `${p.role} (${p.seniority_level})`).join(', ')}
                      </Typography>
                      
                      {uniquePainPoints.length > 0 && (
                        <Box mt={2}>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            <strong>Select Pain Points to Address:</strong>
                          </Typography>
                          <Box display="flex" flexWrap="wrap" gap={0.5}>
                            {uniquePainPoints.map((point, index) => (
                              <Chip 
                                key={index} 
                                label={point} 
                                size="small" 
                                variant={selectedPainPoints.includes(point) ? "filled" : "outlined"}
                                color={selectedPainPoints.includes(point) ? "primary" : "default"}
                                clickable
                                onClick={() => {
                                  setSelectedPainPoints(prev => 
                                    prev.includes(point) 
                                      ? prev.filter(p => p !== point)
                                      : [...prev, point]
                                  )
                                }}
                              />
                            ))}
                          </Box>
                          {selectedPainPoints.length > 0 && (
                            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                              Selected {selectedPainPoints.length} pain point(s) from {selectedPersonas.length} persona(s)
                            </Typography>
                          )}
                        </Box>
                      )}
                    </Box>
                  )}
                </>
              ) : (
                // Demo personas when not connected - Checkbox UI
                <>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      Start Gypsum to see your real personas. For now, here are some example personas:
                    </Typography>
                  </Alert>
                  
                  <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 2 }}>
                    Select one or more demo personas:
                  </Typography>
                  
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    {[
                      { id: 'demo-pmm', role: 'Product Marketing Manager', level: 'Senior', industry: 'Technology' },
                      { id: 'demo-md', role: 'Marketing Director', level: 'Executive', industry: 'SaaS' },
                      { id: 'demo-cmm', role: 'Content Marketing Manager', level: 'Mid-level', industry: 'Technology' }
                    ].map((persona) => (
                      <Grid item xs={12} sm={6} md={4} key={persona.id}>
                        <Card 
                          variant="outlined" 
                          sx={{ 
                            p: 2, 
                            cursor: 'pointer',
                            border: selectedPersonas.includes(persona.id) ? 2 : 1,
                            borderColor: selectedPersonas.includes(persona.id) ? 'primary.main' : 'divider',
                            bgcolor: selectedPersonas.includes(persona.id) ? 'primary.50' : 'background.paper',
                            '&:hover': {
                              borderColor: 'primary.main',
                              bgcolor: 'primary.50'
                            }
                          }}
                          onClick={() => {
                            setSelectedPersonas(prev => 
                              prev.includes(persona.id)
                                ? prev.filter(id => id !== persona.id)
                                : [...prev, persona.id]
                            )
                          }}
                        >
                          <Box display="flex" alignItems="flex-start" gap={1}>
                            <Box sx={{ pt: 0.5 }}>
                              <input
                                type="checkbox"
                                checked={selectedPersonas.includes(persona.id)}
                                onChange={() => {}} // Handled by card click
                                style={{ 
                                  accentColor: 'var(--mui-palette-primary-main)',
                                  transform: 'scale(1.1)'
                                }}
                              />
                            </Box>
                            <Box flex={1}>
                              <Typography variant="subtitle2" fontWeight="bold">
                                {persona.role}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                {persona.level} • {persona.industry}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                Demo Persona
                              </Typography>
                            </Box>
                          </Box>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                  
                  {selectedPersonas.length > 0 && (
                    <Box>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        <strong>Demo personas selected:</strong> {selectedPersonas.length}
                      </Typography>
                      
                      <Box mt={2}>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          <strong>Example Pain Points:</strong>
                        </Typography>
                        <Box display="flex" flexWrap="wrap" gap={0.5}>
                          {['Limited budget for tools', 'Need to prove ROI', 'Time constraints'].map((point, index) => (
                            <Chip 
                              key={index} 
                              label={point} 
                              size="small" 
                              variant="outlined"
                              disabled
                            />
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  )}
                </>
              )}
            </Card>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Content Settings */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Content Settings (Optional)
        </Typography>
        <Grid container spacing={3}>
          {/* Optional Settings */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="tone-label">Tone</InputLabel>
              <Select
                labelId="tone-label"
                value={tone}
                label="Tone"
                onChange={(e) => setTone(e.target.value)}
              >
                <MenuItem value="">Any Tone</MenuItem>
                {tones.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="domain-label">Domain Filter</InputLabel>
              <Select
                labelId="domain-label"
                value={selectedDomain}
                label="Domain Filter"
                onChange={(e) => setSelectedDomain(e.target.value)}
              >
                <MenuItem value="">All Domains</MenuItem>
                {domains.map((domain) => (
                  <MenuItem key={domain} value={domain}>
                    {domain}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="content-type-label">Content Type</InputLabel>
              <Select
                labelId="content-type-label"
                value={contentType}
                label="Content Type"
                onChange={(e) => setContentType(e.target.value)}
              >
                <MenuItem value="">All Content Types</MenuItem>
                <MenuItem value="blog_post">Blog Post</MenuItem>
                <MenuItem value="product_description">Product Description</MenuItem>
                <MenuItem value="about_page">About Page</MenuItem>
                <MenuItem value="landing_page">Landing Page</MenuItem>
                <MenuItem value="article">Article</MenuItem>
                <MenuItem value="news">News</MenuItem>
                <MenuItem value="press_release">Press Release</MenuItem>
                <MenuItem value="documentation">Documentation</MenuItem>
                <MenuItem value="faq">FAQ</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              label="Source Chunks"
              type="number"
              variant="outlined"
              fullWidth
              value={topK}
              onChange={(e) => setTopK(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
              InputProps={{ inputProps: { min: 1, max: 20 } }}
              helperText="1-20 chunks to retrieve"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <AutoAwesomeIcon />}
              onClick={handleGenerate}
              disabled={generating || !query?.trim()}
              fullWidth
            >
              {generating 
                ? 'Generating...' 
                : 'Generate Content'
              }
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* NEW: Debug Information */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              🔧 Debug Information
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Connection Status:</Typography>
                <Typography variant="body2">Gypsum Connected: {gypsumConnected ? '✅ Yes' : '❌ No'}</Typography>
                <Typography variant="body2">Gypsum Loading: {gypsumLoading ? '⏳ Yes' : '✅ No'}</Typography>
                <Typography variant="body2">Personas Available: {gypsumPersonas.length}</Typography>
                <Typography variant="body2">Selected Personas: {selectedPersonas.length}</Typography>
                <Typography variant="body2">Selected Pain Points: {selectedPainPoints.length}</Typography>
                <Typography variant="body2">Persona-Aware Mode: {gypsumConnected && selectedPersonas.length > 0 ? '✅ Enabled' : '❌ Disabled'}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>Configuration:</Typography>
                <Typography variant="body2">Gypsum API URL: http://localhost:3001</Typography>
                <Typography variant="body2">Demo User ID: {gypsumUserId}</Typography>
                {gypsumError && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    <Typography variant="body2">{gypsumError}</Typography>
                  </Alert>
                )}
                <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                  <Button 
                    size="small" 
                    variant="outlined" 
                    onClick={() => window.location.reload()}
                  >
                    Retry Connection
                  </Button>
                  <Button 
                    size="small" 
                    variant="outlined"
                    onClick={testGypsumConnection}
                  >
                    Test Connection
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Paper>
      
      {/* NEW: Enhanced Prompt Preview */}
      {gypsumConnected && selectedPersonas.length > 0 && enhancedPrompt && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">
                🎯 Enhanced Prompt Preview (Persona-Aware)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Alert severity="info" sx={{ mb: 2 }}>
                This enhanced prompt includes persona details, pain points, company messaging, and positioning from Gypsum
                {selectedPainPoints.length > 0 && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    ✨ Focusing on {selectedPainPoints.length} selected pain point(s)
                  </Typography>
                )}
              </Alert>
              <Card variant="outlined" sx={{ bgcolor: 'background.default' }}>
                <CardContent>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                    {enhancedPrompt}
                  </Typography>
                </CardContent>
              </Card>
            </AccordionDetails>
          </Accordion>
        </Paper>
      )}
      
      {generatedContent && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Generated Content
              {gypsumConnected && selectedPersonas.length > 0 && (
                <Chip 
                  label={`Persona-Aware (${selectedPersonas.length})`}
                  size="small"
                  color="primary"
                  sx={{ ml: 1 }}
                />
              )}
              {platform && (
                <Chip 
                  label={platforms.find(p => p.value === platform)?.label || platform}
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
              {tone && (
                <Chip 
                  label={tones.find(t => t.value === tone)?.label || tone}
                  size="small"
                  color="secondary"
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
            
            {characterLimit > 0 && (
              <Typography variant="body2" color={isOverLimit ? "error" : "textSecondary"}>
                {contentLength} / {characterLimit} characters
              </Typography>
            )}
          </Box>
          
          {isOverLimit && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Content exceeds the character limit for {currentPlatform.label}. Consider shortening or using a different platform.
            </Alert>
          )}
          
          <Card variant="outlined" sx={{ mb: 2, bgcolor: 'background.default' }}>
            <CardContent>
              <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                {generatedContent}
              </Typography>
            </CardContent>
            <CardActions sx={{ justifyContent: 'flex-end' }}>
              <Button
                startIcon={<ContentCopyIcon />}
                onClick={handleCopyContent}
              >
                Copy to Clipboard
              </Button>
            </CardActions>
          </Card>
          
          {sourceChunks.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              
              <Accordion expanded={showSources} onChange={() => setShowSources(!showSources)}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center">
                    <InfoIcon fontSize="small" sx={{ mr: 1 }} />
                    <Typography>
                      Source Content ({sourceChunks.length} references)
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {sourceChunks.map((chunk, index) => (
                      <Grid item xs={12} key={chunk.chunk_id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Box display="flex" justifyContent="space-between" mb={1}>
                              <Typography variant="subtitle2" fontWeight="bold">
                                Source {index + 1}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Relevance: {(chunk.similarity * 100).toFixed(1)}%
                              </Typography>
                            </Box>
                            <Typography variant="body2">
                              {chunk.text}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </>
          )}
        </Paper>
      )}
      
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccess(null)} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </Container>
  )
}

export default EnhancedContentGenerator