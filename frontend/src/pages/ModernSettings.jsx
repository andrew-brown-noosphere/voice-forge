import React, { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
  Grid,
  FormControl,
  FormControlLabel,
  Switch,
  TextField,
  Button,
  Slider,
  Select,
  MenuItem,
  InputLabel,
  Alert,
  Snackbar,
  Avatar,
  useTheme,
  alpha,
  Fade,
  Stack,
  IconButton
} from '@mui/material'
import {
  Save as SaveIcon,
  Settings as SettingsIcon,
  Tune as TuneIcon,
  Computer as ComputerIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Web as WebIcon,
  Palette as PaletteIcon,
  Api as ApiIcon,
  RestoreOutlined as RestoreIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material'

// Modern components
import {
  ModernCard,
  ModernTextField,
  ModernSelect,
  ModernButton,
  ModernSwitch,
  ModernAlert,
  ModernSectionHeader
} from '../components/ModernFormComponents'
import { useNavigate } from 'react-router-dom'

const ModernSettings = () => {
  const theme = useTheme()
  const navigate = useNavigate()
  const [settings, setSettings] = useState({
    maxConcurrentCrawls: 4,
    defaultDelay: 1.0,
    defaultTimeout: 30,
    defaultMaxDepth: 3,
    defaultMaxPages: 100,
    respectRobotsTxt: true,
    userAgent: 'VoiceForge Crawler (+https://voiceforge.example.com)',
    enableVectorSearch: true,
    theme: 'light',
    apiBaseUrl: 'http://localhost:8000',
  })
  
  const [success, setSuccess] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  
  const handleChange = (field) => (event) => {
    const newValue = field === 'respectRobotsTxt' || field === 'enableVectorSearch'
      ? event.target.checked
      : event.target.value
      
    setSettings({
      ...settings,
      [field]: newValue,
    })
    setHasChanges(true)
  }
  
  const handleSliderChange = (field) => (event, value) => {
    setSettings({
      ...settings,
      [field]: value,
    })
    setHasChanges(true)
  }
  
  const handleSave = () => {
    // In a real app, this would save to localStorage or API
    console.log('Saving settings:', settings)
    setSuccess(true)
    setHasChanges(false)
  }
  
  const handleReset = () => {
    setSettings({
      maxConcurrentCrawls: 4,
      defaultDelay: 1.0,
      defaultTimeout: 30,
      defaultMaxDepth: 3,
      defaultMaxPages: 100,
      respectRobotsTxt: true,
      userAgent: 'VoiceForge Crawler (+https://voiceforge.example.com)',
      enableVectorSearch: true,
      theme: 'light',
      apiBaseUrl: 'http://localhost:8000',
    })
    setHasChanges(false)
  }
  
  const handleCloseSnackbar = () => {
    setSuccess(false)
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
          ⚙️ Settings
        </Typography>
        <Typography variant="h6" color="textSecondary" sx={{ fontWeight: 400, mb: 3 }}>
          Configure your VoiceForge crawler settings and preferences
        </Typography>
        
        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <ModernButton
            variant="contained"
            icon={SaveIcon}
            onClick={handleSave}
            disabled={!hasChanges}
            gradient={true}
            glow={hasChanges}
          >
            Save Changes
          </ModernButton>
          <ModernButton
            variant="outlined"
            icon={RestoreIcon}
            onClick={handleReset}
            disabled={!hasChanges}
          >
            Reset to Defaults
          </ModernButton>
        </Box>
      </Box>
      
      {/* Crawler Settings */}
      <ModernCard sx={{ mb: 4 }} hover={false}>
        <CardContent sx={{ p: 4 }}>
          <ModernSectionHeader
            icon={TuneIcon}
            title="Crawler Configuration"
            description="Configure default crawling behavior and performance settings"
          />
          
          <Grid container spacing={4} sx={{ mt: 1 }}>
            {/* Performance Settings */}
            <Grid item xs={12}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.primary.main, 0.05),
                border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
                    <SpeedIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Performance Settings
                  </Typography>
                </Box>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
                      Max Concurrent Crawls
                    </Typography>
                    <Slider
                      value={settings.maxConcurrentCrawls}
                      onChange={handleSliderChange('maxConcurrentCrawls')}
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
                      Maximum number of crawl jobs to run simultaneously (Current: {settings.maxConcurrentCrawls})
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Typography gutterBottom sx={{ fontWeight: 600, color: theme.palette.warning.main }}>
                      Request Delay (seconds)
                    </Typography>
                    <Slider
                      value={settings.defaultDelay}
                      onChange={handleSliderChange('defaultDelay')}
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
                      Default delay between requests (Current: {settings.defaultDelay}s)
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <ModernTextField
                      label="Default Timeout (seconds)"
                      type="number"
                      value={settings.defaultTimeout}
                      onChange={handleChange('defaultTimeout')}
                      inputProps={{ min: 1 }}
                      helperText="Request timeout in seconds"
                      icon={SpeedIcon}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <ModernTextField
                      label="Default Max Depth"
                      type="number"
                      value={settings.defaultMaxDepth}
                      onChange={handleChange('defaultMaxDepth')}
                      inputProps={{ min: 1, max: 10 }}
                      helperText="Maximum crawl depth"
                      icon={WebIcon}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <ModernTextField
                      label="Default Max Pages"
                      type="number"
                      value={settings.defaultMaxPages}
                      onChange={handleChange('defaultMaxPages')}
                      inputProps={{ min: 1 }}
                      helperText="Maximum pages to crawl"
                      icon={WebIcon}
                    />
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            {/* Behavior Settings */}
            <Grid item xs={12}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.success.main, 0.05),
                border: `1px solid ${alpha(theme.palette.success.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), color: theme.palette.success.main }}>
                    <SecurityIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Crawler Behavior
                  </Typography>
                </Box>
                
                <Stack spacing={2}>
                  <ModernSwitch
                    checked={settings.respectRobotsTxt}
                    onChange={handleChange('respectRobotsTxt')}
                    label="Respect robots.txt by default"
                    description="Follow robots.txt rules when crawling websites (recommended)"
                  />
                  
                  <ModernSwitch
                    checked={settings.enableVectorSearch}
                    onChange={handleChange('enableVectorSearch')}
                    label="Enable vector search"
                    description="Use vector embeddings for semantic search (requires pgvector extension)"
                  />
                </Stack>
              </Box>
            </Grid>
            
            {/* User Agent */}
            <Grid item xs={12}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.info.main, 0.05),
                border: `1px solid ${alpha(theme.palette.info.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.info.main, 0.1), color: theme.palette.info.main }}>
                    <WebIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    User Agent Configuration
                  </Typography>
                </Box>
                
                <ModernTextField
                  label="User Agent String"
                  value={settings.userAgent}
                  onChange={handleChange('userAgent')}
                  helperText="Browser identification string sent with requests"
                  multiline
                  rows={2}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontFamily: 'monospace',
                      fontSize: '0.9rem'
                    }
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </ModernCard>
      
      {/* Signal Discovery Settings */}
      <ModernCard sx={{ mb: 4 }} hover={false}>
        <CardContent sx={{ p: 4 }}>
          <ModernSectionHeader
            icon={TrendingUpIcon}
            title="Signal Discovery Settings"
            description="Configure automated signal discovery from Reddit, Twitter, GitHub, and LinkedIn"
          />
          
          <Box sx={{ 
            p: 3, 
            borderRadius: 3, 
            background: alpha(theme.palette.primary.main, 0.05),
            border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
            mt: 2
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <Avatar sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), color: theme.palette.primary.main }}>
                <TrendingUpIcon />
              </Avatar>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                AI-Powered Signal Monitoring
              </Typography>
            </Box>
            
            <ModernButton
              variant="contained"
              icon={TrendingUpIcon}
              onClick={() => navigate('/settings/signals')}
              gradient={true}
              sx={{ mb: 2 }}
              fullWidth
            >
              Manage Signal Sources & Automation
            </ModernButton>
            
            <Typography variant="body2" color="textSecondary">
              Set up automated monitoring for Reddit discussions, Twitter mentions, GitHub issues, and LinkedIn posts. 
              Use AI to discover the best sources and keywords for your business.
            </Typography>
          </Box>
        </CardContent>
      </ModernCard>
      
      {/* System Settings */}
      <ModernCard hover={false}>
        <CardContent sx={{ p: 4 }}>
          <ModernSectionHeader
            icon={ComputerIcon}
            title="System Configuration"
            description="Application-wide settings and preferences"
          />
          
          <Grid container spacing={4} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.secondary.main, 0.05),
                border: `1px solid ${alpha(theme.palette.secondary.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.secondary.main, 0.1), color: theme.palette.secondary.main }}>
                    <PaletteIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Appearance
                  </Typography>
                </Box>
                
                <ModernSelect
                  label="Theme"
                  value={settings.theme}
                  onChange={handleChange('theme')}
                  options={[
                    { value: 'light', label: '☀️ Light Mode' },
                    { value: 'dark', label: '🌙 Dark Mode' },
                    { value: 'system', label: '💻 System Default' }
                  ]}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                p: 3, 
                borderRadius: 3, 
                background: alpha(theme.palette.error.main, 0.05),
                border: `1px solid ${alpha(theme.palette.error.main, 0.1)}`
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar sx={{ bgcolor: alpha(theme.palette.error.main, 0.1), color: theme.palette.error.main }}>
                    <ApiIcon />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    API Configuration
                  </Typography>
                </Box>
                
                <ModernTextField
                  label="API Base URL"
                  value={settings.apiBaseUrl}
                  onChange={handleChange('apiBaseUrl')}
                  helperText="Base URL for the backend API"
                  icon={ApiIcon}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <ModernAlert
                severity="info"
                title="Settings Notice"
                description="Some settings may require a restart of the application to take effect. Your changes will be saved automatically."
              />
            </Grid>
          </Grid>
        </CardContent>
      </ModernCard>
      
      {/* Success Snackbar */}
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity="success" 
          sx={{ 
            width: '100%',
            borderRadius: 3,
            backdropFilter: 'blur(20px)',
            background: alpha(theme.palette.success.main, 0.9),
            color: 'white'
          }}
        >
          ✅ Settings saved successfully!
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default ModernSettings