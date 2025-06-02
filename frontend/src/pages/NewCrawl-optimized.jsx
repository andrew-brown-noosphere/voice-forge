/**
 * Enhanced NewCrawl.jsx with optimized defaults for targeted crawling
 * Automatically configures for /product and /blog paths with crawler-friendly settings
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Divider,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  FormGroup,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  InputAdornment,
  Chip,
  Stack,
  Tooltip
} from '@mui/material'
import LanguageIcon from '@mui/icons-material/Language'
import SpeedIcon from '@mui/icons-material/Speed'
import SettingsIcon from '@mui/icons-material/Settings'
import InfoIcon from '@mui/icons-material/Info'

// API service
import { useApi } from '../hooks/useApi'

const NewCrawl = () => {
  const navigate = useNavigate()
  const [activeStep, setActiveStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  
  // Use the new authenticated API
  const api = useApi()
  
  // Form data with OPTIMIZED DEFAULTS
  const [domain, setDomain] = useState('')
  const [config, setConfig] = useState({
    max_depth: 3,
    max_pages: null,  // 🔧 FIX: Set to unlimited for full site crawling
    respect_robots_txt: true,
    delay: 2.0,     // 🎯 Increased to 2 seconds to avoid blocking
    timeout: 15,    // 🎯 Reduced from 30 to 15 seconds
    follow_external_links: false,
    exclude_patterns: [
      '.*/contact.*',     // 🎯 Skip contact pages (slow)
      '.*/login.*',       // 🎯 Skip login pages
      '.*/register.*',    // 🎯 Skip registration
      '.*/checkout.*',    // 🎯 Skip checkout flows
      '.*/cart.*',        // 🎯 Skip shopping cart
      '.*/admin.*',       // 🎯 Skip admin areas
      '.*\\.pdf$',        // 🎯 Skip PDF files
      '.*\\.jpg$',        // 🎯 Skip images
      '.*\\.png$',
      '.*\\.css$',        // 🎯 Skip stylesheets
      '.*\\.js$',         // 🎯 Skip JavaScript files
    ],
    include_patterns: [],  // 🔧 FIX: Start with no include patterns - let user add them if needed
    // 🎯 FIXED: Realistic browser User-Agent instead of crawler signature
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  })
  
  // Exclude patterns
  const [excludePattern, setExcludePattern] = useState('')
  
  // Include patterns
  const [includePattern, setIncludePattern] = useState('')
  
  // Handle form change
  const handleChange = (field) => (event) => {
    setConfig({
      ...config,
      [field]: field === 'max_depth' || field === 'max_pages' || field === 'timeout'
        ? parseInt(event.target.value, 10)
        : field === 'delay'
          ? parseFloat(event.target.value)
          : event.target.checked !== undefined
            ? event.target.checked
            : event.target.value,
    })
  }
  
  // Handle slider change
  const handleSliderChange = (field) => (event, value) => {
    setConfig({
      ...config,
      [field]: value,
    })
  }
  
  // Add exclude pattern
  const addExcludePattern = () => {
    if (excludePattern && !config.exclude_patterns.includes(excludePattern)) {
      setConfig({
        ...config,
        exclude_patterns: [...config.exclude_patterns, excludePattern],
      })
      setExcludePattern('')
    }
  }
  
  // Remove exclude pattern
  const removeExcludePattern = (pattern) => {
    setConfig({
      ...config,
      exclude_patterns: config.exclude_patterns.filter((p) => p !== pattern),
    })
  }
  
  // Add include pattern
  const addIncludePattern = () => {
    if (includePattern && !config.include_patterns.includes(includePattern)) {
      setConfig({
        ...config,
        include_patterns: [...config.include_patterns, includePattern],
      })
      setIncludePattern('')
    }
  }
  
  // Remove include pattern
  const removeIncludePattern = (pattern) => {
    setConfig({
      ...config,
      include_patterns: config.include_patterns.filter((p) => p !== pattern),
    })
  }
  
  // 🎯 NEW: Quick preset buttons
  const applyPreset = (presetType) => {
    if (presetType === 'product-blog') {
      setConfig({
        ...config,
        include_patterns: [
          '.*/product/?$',
          '.*/product/.*',
          '.*/blog/?$',
          '.*/blog/.*',
        ],
        exclude_patterns: [
          '.*/contact.*',
          '.*/login.*',
          '.*/register.*',
          '.*/checkout.*',
          '.*/cart.*',
          '.*/admin.*',
          '.*\\.pdf$',
          '.*\\.jpg$',
          '.*\\.png$',
          '.*\\.css$',
          '.*\\.js$',
        ]
      });
    } else if (presetType === 'full-site') {
      setConfig({
        ...config,
        include_patterns: [],
        exclude_patterns: [
          '.*/admin.*',
          '.*\\.pdf$',
          '.*\\.jpg$',
          '.*\\.png$',
          '.*\\.css$',
          '.*\\.js$',
        ]
      });
    }
  };
  
  // Handle next step
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1)
  }
  
  // Handle back step
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1)
  }
  
  // Handle submit
  const handleSubmit = async () => {
    if (!domain) {
      setError('Please enter a domain URL')
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      const response = await api.crawls.create({
        domain: domain,
        config: config
      })
      setSuccess(true)
      
      // Redirect to crawl details page after 2 seconds
      setTimeout(() => {
        navigate(`/crawls/${response.crawl_id}`)
      }, 2000)
      
    } catch (error) {
      console.error('Failed to start crawl', error)
      setError(error.response?.data?.detail || 'Failed to start crawl')
    } finally {
      setLoading(false)
    }
  }
  
  // Steps
  const steps = [
    {
      label: 'Enter Domain',
      description: 'Enter the domain URL you want to crawl',
      content: (
        <Box sx={{ mt: 2 }}>
          <TextField
            label="Domain URL"
            fullWidth
            variant="outlined"
            placeholder="example.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LanguageIcon />
                </InputAdornment>
              ),
            }}
            helperText="Enter a website domain without http:// or https://"
            required
          />
        </Box>
      ),
    },
    {
      label: 'Crawl Settings',
      description: 'Configure basic crawl settings',
      content: (
        <Box sx={{ mt: 2 }}>
          {/* 🎯 NEW: Optimization notice */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>✨ Optimized for fast, focused crawling!</strong> 
              <br/>Pre-configured to crawl /product and /blog paths while avoiding slow pages like /contact.
              This prevents timeouts and triggers RAG automation faster.
            </Typography>
          </Alert>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Crawl Depth</Typography>
              <Slider
                value={config.max_depth}
                onChange={handleSliderChange('max_depth')}
                step={1}
                marks
                min={1}
                max={10}
                valueLabelDisplay="auto"
                aria-labelledby="crawl-depth-slider"
              />
              <Typography variant="caption" color="textSecondary">
                Maximum depth of pages to crawl (1-10)
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Max Pages</Typography>
              <TextField
                type="number"
                value={config.max_pages}
                onChange={handleChange('max_pages')}
                inputProps={{ min: 1 }}
                fullWidth
                helperText="Maximum number of pages to crawl (optimized for focused content)"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Request Delay (seconds)
                <Tooltip title="Increased to 2 seconds to avoid being blocked by websites">
                  <InfoIcon sx={{ ml: 1, fontSize: 16, color: 'text.secondary' }} />
                </Tooltip>
              </Typography>
              <Slider
                value={config.delay}
                onChange={handleSliderChange('delay')}
                step={0.1}
                min={0.1}
                max={5}
                valueLabelDisplay="auto"
                aria-labelledby="delay-slider"
              />
              <Typography variant="caption" color="textSecondary">
                Delay between requests in seconds (0.1-5)
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Request Timeout (seconds)
                <Tooltip title="Reduced to 15 seconds to skip slow pages faster">
                  <InfoIcon sx={{ ml: 1, fontSize: 16, color: 'text.secondary' }} />
                </Tooltip>
              </Typography>
              <TextField
                type="number"
                value={config.timeout}
                onChange={handleChange('timeout')}
                inputProps={{ min: 1 }}
                fullWidth
                helperText="Request timeout in seconds (optimized to skip slow pages)"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.respect_robots_txt}
                      onChange={handleChange('respect_robots_txt')}
                    />
                  }
                  label="Respect robots.txt"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.follow_external_links}
                      onChange={handleChange('follow_external_links')}
                    />
                  }
                  label="Follow external links"
                />
              </FormGroup>
            </Grid>
          </Grid>
        </Box>
      ),
    },
    {
      label: 'Advanced Settings',
      description: 'Configure advanced crawl settings',
      content: (
        <Box sx={{ mt: 2 }}>
          {/* 🎯 NEW: Quick preset buttons */}
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom variant="h6">Quick Presets</Typography>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => applyPreset('product-blog')}
                sx={{ mb: 1 }}
              >
                Product & Blog Focus
              </Button>
              <Button 
                variant="outlined" 
                color="secondary"
                onClick={() => applyPreset('full-site')}
                sx={{ mb: 1 }}
              >
                Full Site Crawl
              </Button>
            </Stack>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography gutterBottom>
                User Agent
                <Tooltip title="Now uses realistic browser signature instead of crawler identifier">
                  <InfoIcon sx={{ ml: 1, fontSize: 16, color: 'text.secondary' }} />
                </Tooltip>
              </Typography>
              <TextField
                fullWidth
                value={config.user_agent}
                onChange={handleChange('user_agent')}
                helperText="User agent string for the crawler (optimized to avoid blocking)"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography gutterBottom>
                Include Patterns
                <Tooltip title="Pre-configured to focus on /product and /blog paths">
                  <InfoIcon sx={{ ml: 1, fontSize: 16, color: 'text.secondary' }} />
                </Tooltip>
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TextField
                  fullWidth
                  placeholder="e.g. /blog/ or \.html$"
                  value={includePattern}
                  onChange={(e) => setIncludePattern(e.target.value)}
                  helperText="URL patterns to include (regular expressions)"
                />
                <Button
                  variant="contained"
                  onClick={addIncludePattern}
                  disabled={!includePattern}
                  sx={{ ml: 2, height: 56 }}
                >
                  Add
                </Button>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                {config.include_patterns.map((pattern) => (
                  <Chip
                    key={pattern}
                    label={pattern}
                    onDelete={() => removeIncludePattern(pattern)}
                    color="primary"
                    variant="outlined"
                    sx={{ m: 0.5 }}
                  />
                ))}
              </Stack>
            </Grid>
            
            <Grid item xs={12}>
              <Typography gutterBottom>
                Exclude Patterns
                <Tooltip title="Pre-configured to skip slow pages like /contact, /admin, etc.">
                  <InfoIcon sx={{ ml: 1, fontSize: 16, color: 'text.secondary' }} />
                </Tooltip>
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TextField
                  fullWidth
                  placeholder="e.g. /admin/ or \.pdf$"
                  value={excludePattern}
                  onChange={(e) => setExcludePattern(e.target.value)}
                  helperText="URL patterns to exclude (regular expressions)"
                />
                <Button
                  variant="contained"
                  onClick={addExcludePattern}
                  disabled={!excludePattern}
                  sx={{ ml: 2, height: 56 }}
                >
                  Add
                </Button>
              </Box>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {config.exclude_patterns.map((pattern) => (
                  <Chip
                    key={pattern}
                    label={pattern}
                    onDelete={() => removeExcludePattern(pattern)}
                    color="secondary"
                    variant="outlined"
                    sx={{ m: 0.5 }}
                  />
                ))}
              </Stack>
            </Grid>
          </Grid>
        </Box>
      ),
    },
  ]
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Start New Crawl
        {/* 🎯 NEW: Optimization indicator */}
        <Chip 
          label="✨ Optimized" 
          color="success" 
          size="small" 
          sx={{ ml: 2, verticalAlign: 'middle' }}
        />
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {success ? (
        <Alert severity="success" sx={{ mb: 3 }}>
          Crawl started successfully! Redirecting to crawl details...
        </Alert>
      ) : (
        <Card>
          <CardContent>
            <Stepper activeStep={activeStep} orientation="vertical">
              {steps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel>
                    <Typography variant="h6">{step.label}</Typography>
                  </StepLabel>
                  <StepContent>
                    <Typography color="textSecondary" gutterBottom>
                      {step.description}
                    </Typography>
                    {step.content}
                    <Box sx={{ mb: 2, mt: 3 }}>
                      <div>
                        <Button
                          variant="contained"
                          onClick={
                            index === steps.length - 1 ? handleSubmit : handleNext
                          }
                          sx={{ mt: 1, mr: 1 }}
                          disabled={loading || (index === 0 && !domain)}
                        >
                          {index === steps.length - 1 ? 'Start Optimized Crawl' : 'Continue'}
                        </Button>
                        <Button
                          disabled={index === 0 || loading}
                          onClick={handleBack}
                          sx={{ mt: 1, mr: 1 }}
                        >
                          Back
                        </Button>
                      </div>
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
            
            {activeStep === steps.length && (
              <Paper square elevation={0} sx={{ p: 3 }}>
                <Typography>All steps completed - you&apos;re finished</Typography>
                <Button onClick={handleSubmit} sx={{ mt: 1, mr: 1 }}>
                  Start Optimized Crawl
                </Button>
              </Paper>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  )
}

export default NewCrawl