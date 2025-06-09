import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { 
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  CircularProgress,
  Paper,
  Container,
  Avatar,
  Stack,
  Alert
} from '@mui/material';
import { styled } from '@mui/material/styles';

// Styled components for modern look
const GradientBackground = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  padding: theme.spacing(3),
}));

const StatsCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  borderRadius: 16,
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 40px rgba(0,0,0,0.15)',
  },
}));

const PlatformCard = styled(Card)(({ theme }) => ({
  borderRadius: 24,
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 16px 48px rgba(0,0,0,0.15)',
  },
}));

const PlatformIcon = styled(Avatar)(({ theme, platformcolor }) => ({
  width: 64,
  height: 64,
  borderRadius: 16,
  background: platformcolor,
  fontSize: '2rem',
  boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
}));

const GradientText = styled(Typography)(({ theme }) => ({
  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  fontWeight: 'bold',
}));

const SignalSettings = () => {
  const navigate = useNavigate();
  const api = useApi();
  const [platformStatuses, setPlatformStatuses] = useState({});
  const [loading, setLoading] = useState(true);

  const platforms = [
    { 
      id: 'reddit', 
      name: 'Reddit', 
      icon: '🔴', 
      description: 'Monitor subreddits and discussions for community insights',
      configPath: '/settings/signals/reddit',
      color: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
      features: ['Subreddit monitoring', 'Comment analysis', 'Trend detection']
    },
    { 
      id: 'twitter', 
      name: 'Twitter', 
      icon: '🐦', 
      description: 'Track mentions, hashtags, and social conversations',
      configPath: '/settings/signals/twitter',
      color: 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
      features: ['Hashtag tracking', 'Mention monitoring', 'Sentiment analysis']
    },
    { 
      id: 'github', 
      name: 'GitHub', 
      icon: '⭐', 
      description: 'Monitor repository issues and development discussions',
      configPath: '/settings/signals/github',
      color: 'linear-gradient(135deg, #636e72 0%, #2d3436 100%)',
      features: ['Issue tracking', 'PR monitoring', 'Release updates']
    },
    { 
      id: 'linkedin', 
      name: 'LinkedIn', 
      icon: '💼', 
      description: 'Track professional discussions and industry insights',
      configPath: '/settings/signals/linkedin',
      color: 'linear-gradient(135deg, #0984e3 0%, #74b9ff 100%)',
      features: ['Company tracking', 'Industry posts', 'Professional insights']
    }
  ];

  useEffect(() => {
    const fetchPlatformStatuses = async () => {
      setLoading(true);
      const statuses = {};
      
      for (const platform of platforms) {
        try {
          const response = await api.platforms.getStatus(platform.id);
          statuses[platform.id] = response;
        } catch (error) {
          console.error(`Failed to fetch status for ${platform.name}:`, error);
          statuses[platform.id] = { 
            connection_status: 'error',
            config_status: 'error',
            error_message: error.message
          };
        }
      }
      
      setPlatformStatuses(statuses);
      setLoading(false);
    };

    fetchPlatformStatuses();
  }, []);

  const getStatusInfo = (platform) => {
    const status = platformStatuses[platform.id];
    const connectionStatus = status?.connection_status || 'not_connected';
    const configStatus = status?.config_status || 'not_configured';
    
    if (connectionStatus === 'connected') {
      return {
        badge: 'Connected',
        color: 'success',
        icon: '✅',
        actionText: 'Manage',
        actionColor: 'success'
      };
    } else if (connectionStatus === 'error') {
      return {
        badge: 'Error',
        color: 'error',
        icon: '❌',
        actionText: 'Fix Issues',
        actionColor: 'error'
      };
    } else if (configStatus === 'incomplete') {
      return {
        badge: 'Incomplete',
        color: 'warning',
        icon: '⚠️',
        actionText: 'Complete Setup',
        actionColor: 'warning'
      };
    } else {
      return {
        badge: 'Not Connected',
        color: 'default',
        icon: '⭕',
        actionText: 'Setup',
        actionColor: 'primary'
      };
    }
  };

  const handleTestConnection = async (platformId) => {
    try {
      const response = await api.platforms.testConnection(platformId);
      console.log(`Connection test result for ${platformId}:`, response);
      
      const statusResponse = await api.platforms.getStatus(platformId);
      setPlatformStatuses(prev => ({
        ...prev,
        [platformId]: statusResponse
      }));
    } catch (error) {
      console.error(`Connection test failed for ${platformId}:`, error);
    }
  };

  const connectedCount = Object.values(platformStatuses).filter(
    status => status?.connection_status === 'connected'
  ).length;

  const errorCount = Object.values(platformStatuses).filter(
    status => status?.connection_status === 'error'
  ).length;

  const notConnectedCount = Object.values(platformStatuses).filter(
    status => !status || status?.connection_status === 'not_connected'
  ).length;

  if (loading) {
    return (
      <GradientBackground>
        <Container maxWidth="lg">
          <Box 
            display="flex" 
            flexDirection="column" 
            alignItems="center" 
            justifyContent="center" 
            minHeight="60vh"
          >
            <CircularProgress size={60} thickness={4} />
            <Typography variant="h6" sx={{ mt: 3, color: 'text.secondary' }}>
              Loading platform configurations...
            </Typography>
          </Box>
        </Container>
      </GradientBackground>
    );
  }

  return (
    <GradientBackground>
      <Container maxWidth="lg">
        <Stack spacing={6}>
          {/* Header */}
          <Box textAlign="center">
            <Avatar
              sx={{
                width: 80,
                height: 80,
                mx: 'auto',
                mb: 3,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                fontSize: '2.5rem'
              }}
            >
              ⚡
            </Avatar>
            <GradientText variant="h2" component="h1" gutterBottom>
              Signal Sources
            </GradientText>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
              Configure and manage your data sources for intelligent signal monitoring and analysis
            </Typography>
          </Box>

          {/* Quick Stats */}
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard>
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                  <Typography variant="h3" component="div" fontWeight="bold">
                    {connectedCount}
                  </Typography>
                  <Typography variant="body2">Connected</Typography>
                  <Box sx={{ mt: 2 }}>
                    <Avatar sx={{ mx: 'auto', backgroundColor: 'rgba(255,255,255,0.2)' }}>
                      ✅
                    </Avatar>
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard sx={{ background: 'linear-gradient(135deg, #fd79a8 0%, #e84393 100%)' }}>
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                  <Typography variant="h3" component="div" fontWeight="bold">
                    {errorCount}
                  </Typography>
                  <Typography variant="body2">Errors</Typography>
                  <Box sx={{ mt: 2 }}>
                    <Avatar sx={{ mx: 'auto', backgroundColor: 'rgba(255,255,255,0.2)' }}>
                      ❌
                    </Avatar>
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard sx={{ background: 'linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)' }}>
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                  <Typography variant="h3" component="div" fontWeight="bold">
                    {notConnectedCount}
                  </Typography>
                  <Typography variant="body2">Not Connected</Typography>
                  <Box sx={{ mt: 2 }}>
                    <Avatar sx={{ mx: 'auto', backgroundColor: 'rgba(255,255,255,0.2)' }}>
                      ⭕
                    </Avatar>
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <StatsCard sx={{ background: 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)' }}>
                <CardContent sx={{ textAlign: 'center', py: 3 }}>
                  <Typography variant="h3" component="div" fontWeight="bold">
                    {platforms.length}
                  </Typography>
                  <Typography variant="body2">Total Platforms</Typography>
                  <Box sx={{ mt: 2 }}>
                    <Avatar sx={{ mx: 'auto', backgroundColor: 'rgba(255,255,255,0.2)' }}>
                      🔗
                    </Avatar>
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
          </Grid>

          {/* Platform Grid */}
          <Grid container spacing={4}>
            {platforms.map((platform) => {
              const statusInfo = getStatusInfo(platform);
              return (
                <Grid item xs={12} md={6} key={platform.id}>
                  <PlatformCard>
                    <CardContent sx={{ p: 4 }}>
                      {/* Platform Header */}
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
                        <Box display="flex" alignItems="center" gap={2}>
                          <PlatformIcon platformcolor={platform.color}>
                            {platform.icon}
                          </PlatformIcon>
                          <Box>
                            <Typography variant="h5" fontWeight="bold" gutterBottom>
                              {platform.name}
                            </Typography>
                            <Chip
                              label={statusInfo.badge}
                              color={statusInfo.color}
                              size="small"
                              icon={<span>{statusInfo.icon}</span>}
                            />
                          </Box>
                        </Box>
                        
                        <Button
                          variant="contained"
                          color={statusInfo.actionColor}
                          onClick={() => navigate(platform.configPath)}
                          sx={{ 
                            borderRadius: 3,
                            textTransform: 'none',
                            fontWeight: 'bold',
                            px: 3
                          }}
                        >
                          {statusInfo.actionText}
                        </Button>
                      </Box>

                      {/* Platform Description */}
                      <Typography 
                        variant="body1" 
                        color="text.secondary" 
                        sx={{ mb: 3, lineHeight: 1.6 }}
                      >
                        {platform.description}
                      </Typography>

                      {/* Features */}
                      <Box>
                        <Typography 
                          variant="caption" 
                          color="text.secondary" 
                          sx={{ 
                            textTransform: 'uppercase', 
                            fontWeight: 'bold',
                            letterSpacing: 1
                          }}
                        >
                          Key Features
                        </Typography>
                        <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 1 }}>
                          {platform.features.map((feature, index) => (
                            <Chip
                              key={index}
                              label={feature}
                              variant="outlined"
                              size="small"
                              sx={{ borderRadius: 2 }}
                            />
                          ))}
                        </Stack>
                      </Box>

                      {/* Connection Test Button */}
                      {platformStatuses[platform.id]?.connection_status === 'connected' && (
                        <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
                          <Button
                            variant="outlined"
                            fullWidth
                            onClick={() => handleTestConnection(platform.id)}
                            sx={{ borderRadius: 3, textTransform: 'none' }}
                          >
                            🔍 Test Connection
                          </Button>
                        </Box>
                      )}

                      {/* Error Message */}
                      {platformStatuses[platform.id]?.error_message && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                          <strong>Error:</strong> {platformStatuses[platform.id].error_message}
                        </Alert>
                      )}
                    </CardContent>
                  </PlatformCard>
                </Grid>
              );
            })}
          </Grid>

          {/* Getting Started Guide */}
          <Paper sx={{ p: 6, borderRadius: 6, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            <Box textAlign="center" mb={4}>
              <Avatar
                sx={{
                  width: 60,
                  height: 60,
                  mx: 'auto',
                  mb: 2,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  fontSize: '1.5rem'
                }}
              >
                🚀
              </Avatar>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Getting Started
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Follow these simple steps to connect your first platform
              </Typography>
            </Box>
            
            <Grid container spacing={4}>
              {[
                { number: '1', title: 'Choose Platform', desc: 'Select the platform you want to monitor and click the setup button' },
                { number: '2', title: 'Configure API', desc: 'Follow the platform-specific guide to obtain and enter your API credentials' },
                { number: '3', title: 'Start Monitoring', desc: 'Test your connection and begin collecting valuable signals from your sources' }
              ].map((step, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Box textAlign="center">
                    <Avatar
                      sx={{
                        width: 64,
                        height: 64,
                        mx: 'auto',
                        mb: 2,
                        background: `linear-gradient(135deg, ${['#667eea', '#764ba2', '#74b9ff'][index]} 0%, ${['#764ba2', '#667eea', '#0984e3'][index]} 100%)`,
                        fontSize: '1.5rem',
                        fontWeight: 'bold'
                      }}
                    >
                      {step.number}
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {step.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {step.desc}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Stack>
      </Container>
    </GradientBackground>
  );
};

export default SignalSettings;