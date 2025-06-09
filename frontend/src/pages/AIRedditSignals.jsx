import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useUser, useOrganization } from '@clerk/clerk-react'
import { useApi } from '../hooks/useApi'
import { gypsumClient } from '../services/gypsum'

// Import the subreddit discovery component
import RedditSubredditDiscovery from '../components/RedditSubredditDiscovery'

const AIRedditSignals = () => {
  const navigate = useNavigate()
  const { user } = useUser()
  const { organization } = useOrganization()
  const api = useApi()
  
  const [currentStep, setCurrentStep] = useState(0)
  const [gypsumConnected, setGypsumConnected] = useState(false)
  const [gypsumPersonas, setGypsumPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Demo user ID for Gypsum - use the hardcoded demo ID that Gypsum recognizes
  const gypsumUserId = '123e4567-e89b-12d3-a456-426614174000' // Demo user with personas

  const steps = [
    'Connect to Gypsum',
    'Select Persona',
    'Discover Subreddits',
    'Setup Monitoring'
  ]

  useEffect(() => {
    const initializeGypsum = async () => {
      try {
        setLoading(true)
        console.log('🔌 Connecting to Gypsum for Reddit signals...')
        console.log('🎯 Using demo user ID:', gypsumUserId)
        
        const validation = await gypsumClient.validateConnection(gypsumUserId)
        console.log('📋 Validation result:', validation)
        
        if (validation.connected && validation.userAccess) {
          setGypsumConnected(true)
          
          // Fetch context data
          const context = await gypsumClient.fetchAllContext(gypsumUserId)
          const personas = context.personas?.personas || []
          
          setGypsumPersonas(personas)
          
          if (personas.length > 0) {
            setSelectedPersona(personas[0].id)
            setCurrentStep(1) // Move to persona selection
          }
          
          console.log(`📊 Loaded ${personas.length} personas for Reddit analysis`)
        } else {
          setError(`Could not access Gypsum data. ${validation.error || 'Please ensure Gypsum API is running and configured.'}`)
        }
      } catch (err) {
        console.error('Failed to connect to Gypsum:', err)
        setError(`Failed to connect to Gypsum: ${err.message}`)
      } finally {
        setLoading(false)
      }
    }

    initializeGypsum()
  }, [gypsumUserId])

  const handlePersonaSelect = (personaId) => {
    setSelectedPersona(personaId)
    setCurrentStep(2) // Move to subreddit discovery
  }

  const handleSubredditsSelected = (selectedSubreddits) => {
    console.log('Selected subreddits for monitoring:', selectedSubreddits)
    setCurrentStep(3) // Move to monitoring setup
    // TODO: Setup monitoring configuration
  }

  const selectedPersonaData = gypsumPersonas.find(p => p.id === selectedPersona)

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="60vh">
          <CircularProgress size={60} thickness={4} />
          <Typography variant="h6" sx={{ mt: 3, color: 'text.secondary' }}>
            Connecting to Gypsum Product Compass...
          </Typography>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        AI-Powered Reddit Signal Discovery
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Use AI to discover relevant Reddit discussions based on your Gypsum personas and start monitoring for business signals.
      </Typography>

      {/* Progress Stepper */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Step Content */}
      {currentStep === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            🔌 Connecting to Gypsum
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Establishing connection to Gypsum Product Compass to access your personas...
          </Typography>
        </Paper>
      )}

      {currentStep === 1 && gypsumConnected && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            👥 Select Target Persona
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Choose which persona you'd like to discover Reddit signals for:
          </Typography>
          
          <Grid container spacing={3}>
            {gypsumPersonas.map((persona) => (
              <Grid item xs={12} md={6} key={persona.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    border: selectedPersona === persona.id ? 2 : 1,
                    borderColor: selectedPersona === persona.id ? 'primary.main' : 'grey.300',
                    '&:hover': { boxShadow: 3 }
                  }}
                  onClick={() => handlePersonaSelect(persona.id)}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {persona.role} ({persona.seniority_level})
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {persona.industry} • {persona.company_size}
                    </Typography>
                    <Typography variant="body2">
                      {persona.pain_points?.slice(0, 2).join(', ')}
                      {persona.pain_points?.length > 2 && '...'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {selectedPersona && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Button 
                variant="contained" 
                size="large"
                onClick={() => setCurrentStep(2)}
                sx={{ px: 4 }}
              >
                Discover Subreddits for {selectedPersonaData?.role}
              </Button>
            </Box>
          )}
        </Paper>
      )}

      {currentStep === 2 && selectedPersona && (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Selected Persona:</strong> {selectedPersonaData?.role} ({selectedPersonaData?.seniority_level}) 
              in {selectedPersonaData?.industry}
            </Typography>
          </Alert>
          
          {/* This will render the subreddit discovery component */}
          <RedditSubredditDiscovery 
            persona={selectedPersonaData}
            onSubredditsSelected={handleSubredditsSelected}
          />
        </Box>
      )}

      {currentStep === 3 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            🎯 Monitoring Setup Complete
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Your Reddit signal monitoring has been configured and will begin scanning shortly.
          </Typography>
          
          <Grid container spacing={2} justifyContent="center">
            <Grid item>
              <Button 
                variant="contained" 
                onClick={() => navigate('/reddit-signals')}
              >
                View Reddit Signals
              </Button>
            </Grid>
            <Grid item>
              <Button 
                variant="outlined" 
                onClick={() => navigate('/settings/signals')}
              >
                Signal Settings
              </Button>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* What Happens Next */}
      {gypsumConnected && (
        <Paper sx={{ p: 4, mt: 4, backgroundColor: 'primary.50' }}>
          <Typography variant="h6" color="primary.main" gutterBottom>
            🚀 What Happens Next
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2">
                <strong>AI Search Generation:</strong> System generates intelligent search queries based on your persona's pain points and goals
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2">
                <strong>Automated Scanning:</strong> Reddit monitoring runs every 6 hours to discover new relevant discussions
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2">
                <strong>Signal Processing:</strong> Results are analyzed, scored, and filtered to show only high-value opportunities
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  )
}

export default AIRedditSignals