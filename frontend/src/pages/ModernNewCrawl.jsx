import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  FormGroup,
  Alert,
  InputAdornment,
  Chip,
  Stack,
  Avatar,
  LinearProgress,
  alpha,
  useTheme,
  Fade,
  Zoom,
  CircularProgress
} from '@mui/material'
import {
  Language as LanguageIcon,
  Tune as TuneIcon,
  FilterList as FilterListIcon,
  Code as CodeIcon,
  Rocket as RocketIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material'

// Modern components
import {
  ModernCard,
  ModernTextField,
  ModernSelect,
  ModernButton,
  ModernSwitch,
  ModernChipInput,
  ModernAlert,
  ModernSectionHeader
} from '../components/ModernFormComponents'

// API service
import { useApi } from '../hooks/useApi'

// Step Icon Component
const StepIcon = ({ icon: Icon, active, completed }) => {
  const theme = useTheme()
  
  return (
    <Avatar
      sx={{
        width: 56,
        height: 56,
        bgcolor: completed 
          ? theme.palette.success.main 
          : active 
            ? `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
            : alpha(theme.palette.text.secondary, 0.1),
        color: completed || active ? '#fff' : theme.palette.text.secondary,
        transition: 'all 0.3s ease',
        boxShadow: active ? `0 4px 15px ${alpha(theme.palette.primary.main, 0.2)}` : 'none'
      }}
    >
      {completed ? <CheckCircleIcon /> : <Icon />}
    </Avatar>
  )
}

const ModernNewCrawl = () => {
  const navigate = useNavigate()
  const theme = useTheme()
  const [activeStep, setActiveStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  
  const api = useApi()
  
  // Form data
  const [domain, setDomain] = useState('')
  const [config, setConfig] = useState({
    max_depth: 3,
    max_pages: null,  // 🔧 FIX: Set to null for unlimited pages by default
    respect_robots_txt: true,
    delay: 2.0,
    timeout: 30,    // 🔧 FIX: Increased timeout for complex sites
    follow_external_links: false,
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
    ],
    include_patterns: [],  // 🔧 FIX: Start with no include patterns - let user add them if needed
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  })
  
  const [excludePattern, setExcludePattern] = useState('')
  const [includePattern, setIncludePattern] = useState('')
  
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
  
  const handleSliderChange = (field) => (event, value) => {
    setConfig({
      ...config,
      [field]: value,
    })
  }
  
  const addExcludePattern = () => {
    if (excludePattern && !config.exclude_patterns.includes(excludePattern)) {
      setConfig({
        ...config,
        exclude_patterns: [...config.exclude_patterns, excludePattern],
      })
      setExcludePattern('')
    }
  }
  
  const removeExcludePattern = (pattern) => {
    setConfig({
      ...config,
      exclude_patterns: config.exclude_patterns.filter((p) => p !== pattern),
    })
  }
  
  const addIncludePattern = () => {
    if (includePattern && !config.include_patterns.includes(includePattern)) {
      setConfig({
        ...config,
        include_patterns: [...config.include_patterns, includePattern],
      })
      setIncludePattern('')
    }
  }
  
  const removeIncludePattern = (pattern) => {
    setConfig({
      ...config,
      include_patterns: config.include_patterns.filter((p) => p !== pattern),
    })
  }
  
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1)
  }
  
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1)
  }
  
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
  
  const steps = [
    {
      label: 'Website Setup',
      description: 'Enter the website you want to analyze for AI content generation',
      icon: LanguageIcon,
      content: (
        <ModernCard sx={{ mt: 3 }} hover={false}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
                <LanguageIcon />
              </Avatar>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Target Website
              </Typography>
            </Box>
            
            <TextField
              label="Website Domain"
              fullWidth
              variant="outlined"
              placeholder="example.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LanguageIcon sx={{ color: theme.palette.primary.main }} />
                  </InputAdornment>
                ),
              }}
              helperText="Enter a website domain without http:// or https://"
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  background: alpha(theme.palette.background.paper, 0.5),
                  backdropFilter: 'blur(10px)',
                  fontSize: '1.1rem',
                  '&:hover': {
                    background: alpha(theme.palette.background.paper, 0.7)
                  },
                  '&.Mui-focused': {
                    background: alpha(theme.palette.background.paper, 0.9)
                  }
                }
              }}
            />
            
            <Box sx={{ mt: 3, p: 3, borderRadius: 3, background: alpha(theme.palette.info.main, 0.05), border: `1px solid ${alpha(theme.palette.info.main, 0.2)}` }}>
              <Typography variant="body2" color="info.main" sx={{ fontWeight: 600, mb: 1 }}>
                💡 Tips for better crawling:
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Use clean domain names (e.g., "example.com" not "www.example.com/page")
                <br />
                • Ensure the website is publicly accessible
                <br />
                • Check if the site allows crawling in robots.txt
              </Typography>
            </Box>
          </CardContent>
        </ModernCard>
      ),
    },
    {
      label: 'Analysis Configuration',
      description: 'Configure basic content analysis parameters',
      icon: TuneIcon,
      content: (
        <ModernCard sx={{ mt: 3 }} hover={false}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
              <Avatar sx={{ bgcolor: alpha(theme.palette.secondary.main, 0.1), color: theme.palette.secondary.main }}>
                <TuneIcon />
              </Avatar>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Analysis Parameters
              </Typography>
            </Box>
            
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.primary.main, 0.05) }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
                    Content Depth
                  </Typography>
                  <Slider
                    value={config.max_depth}
                    onChange={handleSliderChange('max_depth')}
                    step={1}
                    marks
                    min={1}
                    max={10}
                    valueLabelDisplay="auto"
                    sx={{
                      color: theme.palette.primary.main,
                      '& .MuiSlider-thumb': {
                        boxShadow: `0 0 0 8px ${alpha(theme.palette.primary.main, 0.16)}`,
                      }
                    }}
                  />
                  <Typography variant="caption" color="textSecondary">
                    How deep to analyze content structure (Current: {config.max_depth} levels)
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.secondary.main, 0.05) }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.secondary.main }}>
                    Maximum Pages
                  </Typography>
                  <TextField
                    type="number"
                    value={config.max_pages || ''}
                    onChange={(e) => {
                      const value = e.target.value;
                      setConfig({
                        ...config,
                        max_pages: value === '' ? null : parseInt(value, 10)
                      });
                    }}
                    placeholder="Unlimited"
                    inputProps={{ min: 1, max: 1000 }}
                    fullWidth
                    sx={{ mt: 1 }}
                  />
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                    {config.max_pages ? `Limit to ${config.max_pages} pages` : 'No limit - crawl entire site (recommended)'}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.warning.main, 0.05) }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.warning.main }}>
                    Request Delay (seconds)
                  </Typography>
                  <Slider
                    value={config.delay}
                    onChange={handleSliderChange('delay')}
                    step={0.1}
                    min={0.1}
                    max={5}
                    valueLabelDisplay="auto"
                    sx={{
                      color: theme.palette.warning.main,
                      '& .MuiSlider-thumb': {
                        boxShadow: `0 0 0 8px ${alpha(theme.palette.warning.main, 0.16)}`,
                      }
                    }}
                  />
                  <Typography variant="caption" color="textSecondary">
                    Delay between requests (Current: {config.delay}s)
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.error.main, 0.05) }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.error.main }}>
                    Request Timeout
                  </Typography>
                  <TextField
                    type="number"
                    value={config.timeout}
                    onChange={handleChange('timeout')}
                    inputProps={{ min: 5, max: 60 }}
                    fullWidth
                    sx={{ mt: 1 }}
                    InputProps={{
                      endAdornment: <InputAdornment position="end">seconds</InputAdornment>
                    }}
                  />
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                    How long to wait for each page
                  </Typography>
                </Box>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 4, p: 3, borderRadius: 3, background: alpha(theme.palette.success.main, 0.05), border: `1px solid ${alpha(theme.palette.success.main, 0.2)}` }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: theme.palette.success.main, mb: 2 }}>
                🛡️ Crawler Behavior
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.respect_robots_txt}
                      onChange={handleChange('respect_robots_txt')}
                      color="success"
                    />
                  }
                  label="Respect robots.txt (recommended)"
                  sx={{ mb: 1 }}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.follow_external_links}
                      onChange={handleChange('follow_external_links')}
                      color="warning"
                    />
                  }
                  label="Follow external links (may slow crawling)"
                />
              </FormGroup>
            </Box>
          </CardContent>
        </ModernCard>
      ),
    },
    {
      label: 'Advanced Filters',
      description: 'Configure URL patterns and advanced settings',
      icon: FilterListIcon,
      content: (
        <ModernCard sx={{ mt: 3 }} hover={false}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
              <Avatar sx={{ bgcolor: alpha(theme.palette.info.main, 0.1), color: theme.palette.info.main }}>
                <FilterListIcon />
              </Avatar>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                URL Patterns & Filters
              </Typography>
            </Box>
            
            <Grid container spacing={4}>
              <Grid item xs={12}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.background.paper, 0.5), border: `1px solid ${alpha(theme.palette.divider, 0.2)}` }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CodeIcon sx={{ fontSize: 20 }} />
                    User Agent String
                  </Typography>
                  <TextField
                    fullWidth
                    value={config.user_agent}
                    onChange={handleChange('user_agent')}
                    helperText="Browser identification string sent with requests"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        fontFamily: 'monospace',
                        fontSize: '0.9rem'
                      }
                    }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.error.main, 0.05), border: `1px solid ${alpha(theme.palette.error.main, 0.2)}` }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.error.main }}>
                    🚫 Exclude Patterns
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TextField
                      fullWidth
                      placeholder="e.g. /admin/ or \.pdf$"
                      value={excludePattern}
                      onChange={(e) => setExcludePattern(e.target.value)}
                      helperText="URL patterns to skip"
                      size="small"
                    />
                    <Button
                      variant="contained"
                      onClick={addExcludePattern}
                      disabled={!excludePattern}
                      sx={{ ml: 2, minWidth: 80, bgcolor: theme.palette.error.main }}
                    >
                      Add
                    </Button>
                  </Box>
                  <Box sx={{ maxHeight: 150, overflowY: 'auto' }}>
                    <Stack spacing={1} flexWrap="wrap">
                      {config.exclude_patterns.map((pattern) => (
                        <Chip
                          key={pattern}
                          label={pattern}
                          onDelete={() => removeExcludePattern(pattern)}
                          color="error"
                          variant="outlined"
                          size="small"
                          sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                        />
                      ))}
                    </Stack>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 3, borderRadius: 3, background: alpha(theme.palette.success.main, 0.05), border: `1px solid ${alpha(theme.palette.success.main, 0.2)}` }}>
                  <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.success.main }}>
                    ✅ Include Patterns
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TextField
                      fullWidth
                      placeholder="e.g. /blog/ or \.html$"
                      value={includePattern}
                      onChange={(e) => setIncludePattern(e.target.value)}
                      helperText="URL patterns to prioritize"
                      size="small"
                    />
                    <Button
                      variant="contained"
                      onClick={addIncludePattern}
                      disabled={!includePattern}
                      sx={{ ml: 2, minWidth: 80, bgcolor: theme.palette.success.main }}
                    >
                      Add
                    </Button>
                  </Box>
                  <Box sx={{ maxHeight: 150, overflowY: 'auto' }}>
                    <Stack spacing={1} flexWrap="wrap">
                      {config.include_patterns.map((pattern) => (
                        <Chip
                          key={pattern}
                          label={pattern}
                          onDelete={() => removeIncludePattern(pattern)}
                          color="success"
                          variant="outlined"
                          size="small"
                          sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                        />
                      ))}
                    </Stack>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </ModernCard>
      ),
    },
  ]
  
  const getStepProgress = () => {
    return ((activeStep + 1) / steps.length) * 100
  }
  
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
          🚀 Start New Crawl
        </Typography>
        <Typography variant="h6" color="textSecondary" sx={{ fontWeight: 400, mb: 3 }}>
          Configure and launch a new website content analysis session
        </Typography>
        
        {/* Progress Bar */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 600 }}>
              Step {activeStep + 1} of {steps.length}: {steps[activeStep].label}
            </Typography>
            <Typography variant="body2" color="primary" sx={{ fontWeight: 600 }}>
              {Math.round(getStepProgress())}% Complete
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={getStepProgress()}
            sx={{ 
              height: 8, 
              borderRadius: 4,
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              '& .MuiLinearProgress-bar': {
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                borderRadius: 4
              }
            }}
          />
        </Box>
      </Box>
      
      {error && (
        <Fade in={!!error}>
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              borderRadius: 3,
              backdropFilter: 'blur(20px)',
              background: alpha(theme.palette.error.main, 0.1),
              border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`
            }}
          >
            {error}
          </Alert>
        </Fade>
      )}
      
      {success ? (
        <ModernCard sx={{ textAlign: 'center', p: 6 }} hover={false}>
          <Avatar
            sx={{
              width: 80,
              height: 80,
              bgcolor: theme.palette.success.main,
              margin: '0 auto 24px auto',
              animation: 'pulse 2s infinite'
            }}
          >
            <RocketIcon sx={{ fontSize: 40 }} />
          </Avatar>
          <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.success.main, mb: 2 }}>
            🎉 Crawl Started Successfully!
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Your crawl is now running. Redirecting to crawl details...
          </Typography>
          <LinearProgress sx={{ mt: 3, borderRadius: 2, height: 6 }} />
        </ModernCard>
      ) : (
        <ModernCard hover={false}>
          <CardContent sx={{ p: 0 }}>
            {/* Step Navigation */}
            <Box sx={{ p: 4, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
              <Grid container spacing={2}>
                {steps.map((step, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 2,
                        borderRadius: 3,
                        background: index === activeStep 
                          ? alpha(theme.palette.primary.main, 0.1)
                          : index < activeStep
                            ? alpha(theme.palette.success.main, 0.05)
                            : 'transparent',
                        border: `1px solid ${index === activeStep 
                          ? alpha(theme.palette.primary.main, 0.3)
                          : index < activeStep
                            ? alpha(theme.palette.success.main, 0.2)
                            : alpha(theme.palette.divider, 0.1)}`
                      }}
                    >
                      <StepIcon 
                        icon={step.icon} 
                        active={index === activeStep} 
                        completed={index < activeStep}
                      />
                      <Box>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {step.label}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {step.description}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Box>
            
            {/* Step Content */}
            <Box sx={{ p: 4 }}>
              <Fade in={true} key={activeStep}>
                <Box>
                  {steps[activeStep].content}
                </Box>
              </Fade>
              
              {/* Navigation Buttons */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                <Button
                  disabled={activeStep === 0 || loading}
                  onClick={handleBack}
                  variant="outlined"
                  sx={{
                    borderRadius: 3,
                    px: 4,
                    py: 1.5,
                    borderColor: alpha(theme.palette.text.secondary, 0.3),
                    color: theme.palette.text.secondary
                  }}
                >
                  Back
                </Button>
                
                <Button
                  variant="contained"
                  onClick={activeStep === steps.length - 1 ? handleSubmit : handleNext}
                  disabled={loading || (activeStep === 0 && !domain)}
                  startIcon={loading ? null : activeStep === steps.length - 1 ? <RocketIcon /> : <ArrowForwardIcon />}
                  sx={{
                    borderRadius: 3,
                    px: 4,
                    py: 1.5,
                    background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.3)}`,
                    '&:hover': {
                      background: `linear-gradient(45deg, ${theme.palette.primary.dark}, ${theme.palette.secondary.dark})`,
                      boxShadow: `0 6px 25px ${alpha(theme.palette.primary.main, 0.4)}`,
                      transform: 'translateY(-2px)'
                    },
                    '&:disabled': {
                      background: alpha(theme.palette.text.secondary, 0.3)
                    }
                  }}
                >
                  {loading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={20} color="inherit" />
                      Starting Crawl...
                    </Box>
                  ) : activeStep === steps.length - 1 ? (
                    'Launch Crawl'
                  ) : (
                    'Continue'
                  )}
                </Button>
              </Box>
            </Box>
          </CardContent>
        </ModernCard>
      )}
    </Box>
  )
}

export default ModernNewCrawl