import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  Container,
  Avatar,
  Stack,
  Paper
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  ArrowBack as ArrowBackIcon,
  Construction as ConstructionIcon,
  Launch as LaunchIcon
} from '@mui/icons-material';

// Styled components for modern look
const GradientBackground = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
  padding: theme.spacing(3),
}));

const HeaderCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #495057 0%, #343a40 100%)',
  color: 'white',
  borderRadius: 24,
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  marginBottom: theme.spacing(4),
}));

const PlatformIcon = styled(Avatar)(({ theme }) => ({
  width: 80,
  height: 80,
  borderRadius: 24,
  background: 'linear-gradient(135deg, #495057 0%, #343a40 100%)',
  fontSize: '2.5rem',
  boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
}));

const FeatureCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: 12,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  transition: 'transform 0.2s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
  },
}));

const TimelineItem = styled(Box)(({ theme, status }) => {
  const colors = {
    complete: '#48bb78',
    progress: '#ed8936',
    planned: '#a0aec0'
  };
  
  return {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
    '&::before': {
      content: '""',
      width: 12,
      height: 12,
      borderRadius: '50%',
      backgroundColor: colors[status],
      flexShrink: 0,
    }
  };
});

const GitHubConfig = () => {
  const navigate = useNavigate();

  return (
    <GradientBackground>
      <Container maxWidth="lg">
        <Stack spacing={4}>
          {/* Back Button */}
          <Button 
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/settings/signals')}
            sx={{ 
              alignSelf: 'flex-start',
              color: 'text.secondary',
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            Back to Signal Sources
          </Button>

          {/* Header */}
          <HeaderCard>
            <CardContent sx={{ p: 4 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center" gap={3}>
                  <PlatformIcon>
                    ⭐
                  </PlatformIcon>
                  <Box>
                    <Typography variant="h3" fontWeight="bold" gutterBottom>
                      GitHub Configuration
                    </Typography>
                    <Typography variant="h6" sx={{ opacity: 0.9 }}>
                      Monitor repositories, issues, and development discussions (Coming Soon)
                    </Typography>
                  </Box>
                </Box>
                
                <Chip 
                  label="🚧 Coming Soon" 
                  sx={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    color: 'white',
                    fontWeight: 'bold'
                  }} 
                />
              </Box>
            </CardContent>
          </HeaderCard>

          {/* Coming Soon Main Card */}
          <Card sx={{ borderRadius: 6, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            <CardContent sx={{ p: 6 }}>
              <Stack spacing={6} alignItems="center" textAlign="center">
                <Avatar 
                  sx={{ 
                    width: 120, 
                    height: 120, 
                    backgroundColor: 'grey.100',
                    fontSize: '3rem'
                  }}
                >
                  🚧
                </Avatar>
                
                <Box>
                  <Typography variant="h3" fontWeight="bold" gutterBottom>
                    GitHub Integration Coming Soon
                  </Typography>
                  <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600 }}>
                    We're building comprehensive GitHub monitoring to track development activity and community discussions
                  </Typography>
                </Box>

                {/* Features Preview */}
                <Paper sx={{ p: 4, backgroundColor: 'grey.50', borderRadius: 4, width: '100%', maxWidth: 800 }}>
                  <Typography variant="h5" fontWeight="bold" color="text.primary" gutterBottom sx={{ mb: 3 }}>
                    🔮 Planned Features
                  </Typography>
                  <Grid container spacing={2}>
                    {[
                      { icon: '🐛', text: 'Issue Tracking' },
                      { icon: '🔄', text: 'Pull Request Monitoring' },
                      { icon: '💬', text: 'Discussion Alerts' },
                      { icon: '🏷️', text: 'Release Tracking' },
                      { icon: '📊', text: 'Repository Analytics' },
                      { icon: '🌟', text: 'Star & Fork Alerts' }
                    ].map((feature, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <FeatureCard>
                          <Avatar sx={{ bgcolor: 'grey.700', width: 32, height: 32, fontSize: '1rem' }}>
                            {feature.icon}
                          </Avatar>
                          <Typography fontWeight="medium">{feature.text}</Typography>
                        </FeatureCard>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>

                {/* Timeline */}
                <Paper sx={{ p: 4, backgroundColor: 'primary.50', borderRadius: 4, width: '100%', maxWidth: 600 }}>
                  <Typography variant="h5" fontWeight="bold" color="primary.main" gutterBottom sx={{ mb: 3 }}>
                    📅 Development Timeline
                  </Typography>
                  <Stack spacing={2} sx={{ textAlign: 'left' }}>
                    <TimelineItem status="complete">
                      <Typography>Backend API framework - <strong>Complete</strong></Typography>
                    </TimelineItem>
                    <TimelineItem status="progress">
                      <Typography>GitHub API integration - <strong>Next Up</strong></Typography>
                    </TimelineItem>
                    <TimelineItem status="planned">
                      <Typography>Authentication setup - <strong>Planned</strong></Typography>
                    </TimelineItem>
                    <TimelineItem status="planned">
                      <Typography>Frontend interface - <strong>Planned</strong></Typography>
                    </TimelineItem>
                  </Stack>
                </Paper>
              </Stack>
            </CardContent>
          </Card>

          {/* Available Now */}
          <Card sx={{ borderRadius: 6, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            <CardContent sx={{ p: 6 }}>
              <Box textAlign="center" mb={4}>
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  Available Platform
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Start monitoring signals right now with our Reddit integration
                </Typography>
              </Box>
              
              <Box maxWidth={400} mx="auto">
                <Card 
                  sx={{ 
                    p: 4, 
                    textAlign: 'center', 
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    borderRadius: 4,
                    border: 2,
                    borderColor: 'orange.200',
                    backgroundColor: 'orange.50',
                    '&:hover': {
                      borderColor: 'orange.300',
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                    }
                  }}
                  onClick={() => navigate('/settings/signals/reddit')}
                >
                  <Avatar sx={{ 
                    width: 80, 
                    height: 80, 
                    mx: 'auto', 
                    mb: 3,
                    borderRadius: 4,
                    background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
                    fontSize: '2rem'
                  }}>
                    🔴
                  </Avatar>
                  
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    Reddit Integration
                  </Typography>
                  
                  <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    Monitor subreddits, discussions, and community insights
                  </Typography>
                  
                  <Chip 
                    label="✅ Available Now" 
                    color="success" 
                    sx={{ mb: 3, fontWeight: 'bold' }}
                  />
                  
                  <Button 
                    variant="contained"
                    size="large"
                    sx={{ 
                      background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
                      borderRadius: 3,
                      px: 4,
                      py: 1.5,
                      textTransform: 'none',
                      fontWeight: 'bold',
                      boxShadow: '0 4px 16px rgba(245, 101, 101, 0.3)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)',
                      }
                    }}
                  >
                    Configure Reddit
                  </Button>
                </Card>
              </Box>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </GradientBackground>
  );
};

export default GitHubConfig;