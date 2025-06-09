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
  Paper,
  Divider
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
  background: 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)',
  padding: theme.spacing(3),
}));

const HeaderCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%)',
  color: 'white',
  borderRadius: 24,
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  marginBottom: theme.spacing(4),
}));

const PlatformIcon = styled(Avatar)(({ theme }) => ({
  width: 80,
  height: 80,
  borderRadius: 24,
  background: 'linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%)',
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

const TwitterConfig = () => {
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
                    🐦
                  </PlatformIcon>
                  <Box>
                    <Typography variant="h3" fontWeight="bold" gutterBottom>
                      Twitter Configuration
                    </Typography>
                    <Typography variant="h6" sx={{ opacity: 0.9 }}>
                      Monitor tweets, hashtags, and social conversations (Coming Soon)
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
                    backgroundColor: 'primary.50',
                    fontSize: '3rem'
                  }}
                >
                  🚧
                </Avatar>
                
                <Box>
                  <Typography variant="h3" fontWeight="bold" gutterBottom>
                    Twitter Integration Coming Soon
                  </Typography>
                  <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600 }}>
                    We're working hard to bring you comprehensive Twitter monitoring capabilities
                  </Typography>
                </Box>

                {/* Features Preview */}
                <Paper sx={{ p: 4, backgroundColor: 'primary.50', borderRadius: 4, width: '100%', maxWidth: 800 }}>
                  <Typography variant="h5" fontWeight="bold" color="primary.main" gutterBottom sx={{ mb: 3 }}>
                    🔮 Planned Features
                  </Typography>
                  <Grid container spacing={2}>
                    {[
                      { icon: '📊', text: 'Tweet Monitoring' },
                      { icon: '#️⃣', text: 'Hashtag Tracking' },
                      { icon: '@', text: 'Mention Alerts' },
                      { icon: '😊', text: 'Sentiment Analysis' },
                      { icon: '🔄', text: 'Real-time Updates' },
                      { icon: '📈', text: 'Trend Detection' }
                    ].map((feature, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <FeatureCard>
                          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32, fontSize: '1rem' }}>
                            {feature.icon}
                          </Avatar>
                          <Typography fontWeight="medium">{feature.text}</Typography>
                        </FeatureCard>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>

                {/* Timeline */}
                <Paper sx={{ p: 4, backgroundColor: 'grey.50', borderRadius: 4, width: '100%', maxWidth: 600 }}>
                  <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ mb: 3 }}>
                    📅 Development Timeline
                  </Typography>
                  <Stack spacing={2} sx={{ textAlign: 'left' }}>
                    <TimelineItem status="complete">
                      <Typography>Backend API architecture - <strong>Complete</strong></Typography>
                    </TimelineItem>
                    <TimelineItem status="progress">
                      <Typography>Twitter API integration - <strong>In Progress</strong></Typography>
                    </TimelineItem>
                    <TimelineItem status="planned">
                      <Typography>Frontend configuration UI - <strong>Planned</strong></Typography>
                    </TimelineItem>
                    <TimelineItem status="planned">
                      <Typography>Testing and optimization - <strong>Planned</strong></Typography>
                    </TimelineItem>
                  </Stack>
                </Paper>

                {/* CTA */}
                <Box>
                  <Typography variant="body1" color="text.secondary" gutterBottom>
                    Want to be notified when Twitter integration is ready?
                  </Typography>
                  <Button 
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/settings/signals')}
                    sx={{ 
                      background: 'linear-gradient(135deg, #1da1f2 0%, #0d8bd9 100%)',
                      borderRadius: 3,
                      px: 4,
                      py: 1.5,
                      textTransform: 'none',
                      fontWeight: 'bold',
                      boxShadow: '0 4px 16px rgba(29, 161, 242, 0.3)'
                    }}
                  >
                    Explore Other Platforms
                  </Button>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          {/* What You Can Do Now */}
          <Card sx={{ borderRadius: 6, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            <CardContent sx={{ p: 6 }}>
              <Box textAlign="center" mb={4}>
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  What You Can Do Right Now
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  While we work on Twitter integration, check out these available options
                </Typography>
              </Box>
              
              <Grid container spacing={4} justifyContent="center">
                <Grid item xs={12} md={4}>
                  <Card 
                    sx={{ 
                      p: 3, 
                      textAlign: 'center', 
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      borderRadius: 4,
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                      }
                    }}
                    onClick={() => navigate('/settings/signals/reddit')}
                  >
                    <Avatar sx={{ 
                      width: 60, 
                      height: 60, 
                      mx: 'auto', 
                      mb: 2,
                      background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)'
                    }}>
                      🔴
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      Reddit
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Monitor subreddits and discussions
                    </Typography>
                    <Chip label="Available Now" color="success" size="small" />
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card 
                    sx={{ 
                      p: 3, 
                      textAlign: 'center', 
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      borderRadius: 4,
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                      }
                    }}
                    onClick={() => navigate('/settings/signals/github')}
                  >
                    <Avatar sx={{ 
                      width: 60, 
                      height: 60, 
                      mx: 'auto', 
                      mb: 2,
                      background: 'linear-gradient(135deg, #636e72 0%, #2d3436 100%)'
                    }}>
                      ⭐
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      GitHub
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Track repository activity
                    </Typography>
                    <Chip label="Coming Soon" color="warning" size="small" />
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card 
                    sx={{ 
                      p: 3, 
                      textAlign: 'center', 
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      borderRadius: 4,
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                      }
                    }}
                    onClick={() => navigate('/settings/signals/linkedin')}
                  >
                    <Avatar sx={{ 
                      width: 60, 
                      height: 60, 
                      mx: 'auto', 
                      mb: 2,
                      background: 'linear-gradient(135deg, #0984e3 0%, #74b9ff 100%)'
                    }}>
                      💼
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      LinkedIn
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Professional insights
                    </Typography>
                    <Chip label="Coming Soon" color="warning" size="small" />
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </GradientBackground>
  );
};

export default TwitterConfig;