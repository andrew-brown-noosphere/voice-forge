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
  Snackbar
} from '@mui/material'
import SaveIcon from '@mui/icons-material/Save'
import SettingsIcon from '@mui/icons-material/Settings'

const Settings = () => {
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

  const handleChange = (field) => (event) => {
    setSettings({
      ...settings,
      [field]: field === 'respectRobotsTxt' || field === 'enableVectorSearch'
        ? event.target.checked
        : event.target.value,
    })
  }

  const handleSliderChange = (field) => (event, value) => {
    setSettings({
      ...settings,
      [field]: value,
    })
  }

  const handleSave = () => {
    // In a real app, this would save to localStorage or API
    console.log('Saving settings:', settings)
    setSuccess(true)
  }

  const handleCloseSnackbar = () => {
    setSuccess(false)
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <SettingsIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            Crawler Settings
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Max Concurrent Crawls</Typography>
              <Slider
                value={settings.maxConcurrentCrawls}
                onChange={handleSliderChange('maxConcurrentCrawls')}
                step={1}
                marks
                min={1}
                max={10}
                valueLabelDisplay="auto"
              />
              <Typography variant="caption" color="textSecondary">
                Maximum number of crawl jobs to run simultaneously
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Default Request Delay (seconds)</Typography>
              <Slider
                value={settings.defaultDelay}
                onChange={handleSliderChange('defaultDelay')}
                step={0.1}
                min={0.1}
                max={5}
                valueLabelDisplay="auto"
              />
              <Typography variant="caption" color="textSecondary">
                Default delay between requests in seconds
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Default Timeout (seconds)</Typography>
              <TextField
                type="number"
                fullWidth
                value={settings.defaultTimeout}
                onChange={handleChange('defaultTimeout')}
                inputProps={{ min: 1 }}
                helperText="Default request timeout in seconds"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Default Max Depth</Typography>
              <TextField
                type="number"
                fullWidth
                value={settings.defaultMaxDepth}
                onChange={handleChange('defaultMaxDepth')}
                inputProps={{ min: 1, max: 10 }}
                helperText="Default maximum crawl depth"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Default Max Pages</Typography>
              <TextField
                type="number"
                fullWidth
                value={settings.defaultMaxPages}
                onChange={handleChange('defaultMaxPages')}
                inputProps={{ min: 1 }}
                helperText="Default maximum pages to crawl (0 for unlimited)"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.respectRobotsTxt}
                    onChange={handleChange('respectRobotsTxt')}
                  />
                }
                label="Respect robots.txt by default"
              />
            </Grid>

            <Grid item xs={12}>
              <Typography gutterBottom>User Agent</Typography>
              <TextField
                fullWidth
                value={settings.userAgent}
                onChange={handleChange('userAgent')}
                helperText="Default user agent string for the crawler"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <SettingsIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            System Settings
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableVectorSearch}
                    onChange={handleChange('enableVectorSearch')}
                  />
                }
                label="Enable vector search"
              />
              <Typography variant="caption" display="block" color="textSecondary">
                Use vector embeddings for semantic search (requires pgvector extension)
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="theme-select-label">Theme</InputLabel>
                <Select
                  labelId="theme-select-label"
                  value={settings.theme}
                  label="Theme"
                  onChange={handleChange('theme')}
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="system">System</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Typography gutterBottom>API Base URL</Typography>
              <TextField
                fullWidth
                value={settings.apiBaseUrl}
                onChange={handleChange('apiBaseUrl')}
                helperText="Base URL for the backend API"
              />
            </Grid>

            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 3 }}>
                Some settings may require a restart of the application to take effect.
              </Alert>

              <Button
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={handleSave}
              >
                Save Settings
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message="Settings saved successfully"
      />
    </Box>
  )
}

export default Settings
