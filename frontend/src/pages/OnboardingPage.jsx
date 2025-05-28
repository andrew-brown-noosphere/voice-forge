import React from 'react'
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  Alert,
  Container,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stepper,
  Step,
  StepLabel
} from '@mui/material'
import { 
  Business as BusinessIcon, 
  Add as AddIcon,
  CheckCircle as CheckIcon,
  Search as SearchIcon,
  Create as CreateIcon,
  People as PeopleIcon
} from '@mui/icons-material'
import { CreateOrganization } from '@clerk/clerk-react'

const OnboardingPage = () => {
  const [showCreateOrg, setShowCreateOrg] = React.useState(false)

  const steps = [
    'Create Organization',
    'Start First Crawl', 
    'Generate Content'
  ]

  const features = [
    {
      icon: <SearchIcon color="primary" />,
      title: 'Web Crawling',
      description: 'Crawl websites to extract content and build your knowledge base'
    },
    {
      icon: <CreateIcon color="primary" />,
      title: 'Content Generation',
      description: 'Use AI to generate content based on your crawled data'
    },
    {
      icon: <PeopleIcon color="primary" />,
      title: 'Team Collaboration',
      description: 'Work together with your team in a shared organization'
    }
  ]

  if (showCreateOrg) {
    return (
      <Container maxWidth="md">
        <Box sx={{ 
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4
        }}>
          <Card sx={{ width: '100%', maxWidth: 600 }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h5" gutterBottom>
                Create Your Organization
              </Typography>
              
              <Typography variant="body1" color="textSecondary" paragraph>
                This will be your workspace for managing crawls and generating content.
              </Typography>

              <Box sx={{ mt: 3 }}>
                <CreateOrganization 
                  afterCreateOrganizationUrl="/dashboard"
                  appearance={{
                    elements: {
                      card: {
                        boxShadow: 'none',
                        border: 'none'
                      }
                    }
                  }}
                />
              </Box>

              <Button
                variant="text"
                onClick={() => setShowCreateOrg(false)}
                sx={{ mt: 2 }}
              >
                ← Back
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <BusinessIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h3" gutterBottom>
            Welcome to VoiceForge
          </Typography>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Your AI-powered content generation platform
          </Typography>
        </Box>

        {/* Alert */}
        <Alert severity="info" sx={{ mb: 4 }}>
          <Typography variant="body2">
            <strong>Organization Required:</strong> VoiceForge uses organizations to manage your crawls and content. 
            You'll need to create an organization to get started.
          </Typography>
        </Alert>

        {/* Setup Steps */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom sx={{ textAlign: 'center' }}>
              Get Started in 3 Steps
            </Typography>
            
            <Stepper activeStep={0} alternativeLabel sx={{ mt: 3, mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            <Box sx={{ textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                onClick={() => setShowCreateOrg(true)}
              >
                Create Your Organization
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Features */}
        <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
          What You Can Do with VoiceForge
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3, mb: 4 }}>
          {features.map((feature, index) => (
            <Card key={index}>
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* What happens next */}
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h6" gutterBottom>
              What happens after you create an organization?
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Access the full dashboard"
                  secondary="View analytics, manage crawls, and generate content"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Start your first web crawl"
                  secondary="Crawl any website to build your knowledge base"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Generate AI content"
                  secondary="Create content using your crawled data and AI templates"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckIcon color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Invite team members"
                  secondary="Collaborate with others in your organization"
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}

export default OnboardingPage