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
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import InfoIcon from '@mui/icons-material/Info'
// CHANGED: Use the authenticated useApi hook instead of apiService
import { useApi } from '../hooks/useApi'

// Platform options
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

// Tone options
const tones = [
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'informative', label: 'Informative' },
  { value: 'persuasive', label: 'Persuasive' },
  { value: 'authoritative', label: 'Authoritative' },
]

const ContentGenerator = () => {
  // CHANGED: Use the authenticated API hook
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

  // Fetch domains on component mount
  useEffect(() => {
    const fetchDomains = async () => {
      try {
        // CHANGED: Use authenticated API instead of apiService
        const data = await api.domains.list()
        setDomains(data)
        if (data.length > 0) {
          setSelectedDomain(data[0])
        }
      } catch (err) {
        console.error('Error fetching domains:', err)
        setError('Failed to load domains. Please try again later.')
      }
    }
    
    fetchDomains()
  }, [api.domains])

  const handleGenerate = async () => {
    if (!query || !platform || !tone) {
      setError('Please fill in all required fields')
      return
    }
    
    try {
      setGenerating(true)
      setError(null)
      setSuccess(null)
      
      // CHANGED: Use authenticated API instead of apiService
      const data = await api.rag.generateContent(
        query,
        platform,
        tone,
        selectedDomain || undefined,
        contentType || undefined,
        topK
      )
      
      setGeneratedContent(data.text)
      setSourceChunks(data.source_chunks || [])
      setSuccess('Content generated successfully!')
    } catch (err) {
      console.error('Error generating content:', err)
      setError('Failed to generate content. Please try again later.')
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Content Generator
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Generate Brand-Aligned Content
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label="What would you like to write about?"
              placeholder="E.g., 'Write a post about our new product features'"
              variant="outlined"
              fullWidth
              multiline
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel id="platform-label">Platform</InputLabel>
              <Select
                labelId="platform-label"
                value={platform}
                label="Platform"
                onChange={(e) => setPlatform(e.target.value)}
              >
                {platforms.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label} {option.maxLength ? `(${option.maxLength} chars)` : ''}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel id="tone-label">Tone</InputLabel>
              <Select
                labelId="tone-label"
                value={tone}
                label="Tone"
                onChange={(e) => setTone(e.target.value)}
              >
                {tones.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Advanced Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel id="domain-label">Specific Domain</InputLabel>
                      <Select
                        labelId="domain-label"
                        value={selectedDomain}
                        label="Specific Domain"
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
                      label="Number of Chunks to Retrieve"
                      type="number"
                      variant="outlined"
                      fullWidth
                      value={topK}
                      onChange={(e) => setTopK(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
                      InputProps={{ inputProps: { min: 1, max: 20 } }}
                      helperText="1-20 chunks"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>
          
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <AutoAwesomeIcon />}
              onClick={handleGenerate}
              disabled={generating || !query || !platform || !tone}
              fullWidth
            >
              {generating ? 'Generating...' : 'Generate Content'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {generatedContent && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Generated Content
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

export default ContentGenerator
