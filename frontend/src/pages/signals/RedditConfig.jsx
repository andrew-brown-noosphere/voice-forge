import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../../hooks/useApi';
import { 
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  TextField,
  Container,
  Avatar,
  Stack,
  Alert,
  Paper,
  Tabs,
  Tab,
  IconButton,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Save as SaveIcon,
  Cable as TestConnectionIcon,
  Person as PersonIcon,
  Monitor as MonitorIcon,
  Help as HelpIcon,
  Launch as LaunchIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

// Styled components for modern look
const GradientBackground = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  background: 'linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%)',
  padding: theme.spacing(3),
}));

const HeaderCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
  color: 'white',
  borderRadius: 24,
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  marginBottom: theme.spacing(4),
}));

const PlatformIcon = styled(Avatar)(({ theme }) => ({
  width: 80,
  height: 80,
  borderRadius: 24,
  background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
  fontSize: '2.5rem',
  boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '1rem',
  minHeight: 60,
  '&.Mui-selected': {
    color: '#e53e3e',
  },
}));

const GuideStep = styled(Paper)(({ theme, stepcolor }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  border: `1px solid ${stepcolor}20`,
  backgroundColor: `${stepcolor}08`,
  transition: 'transform 0.2s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
  },
}));

function TabPanel({ children, value, index, ...other }) {
  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`config-tabpanel-${index}`}
      aria-labelledby={`config-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </Box>
  );
}

const RedditConfig = () => {
  const navigate = useNavigate();
  const api = useApi();
  
  const [config, setConfig] = useState({
    username: '',
    password: '',
    subreddits: '',
    keywords: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('not_connected');
  const [saveStatus, setSaveStatus] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await api.platforms.getStatus('reddit');
        setConnectionStatus(response.connection_status || 'not_connected');
      } catch (error) {
        console.error('Failed to fetch Reddit status:', error);
      }
    };
    
    fetchStatus();
  }, []);

  const handleInputChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
    setSaveStatus(null);
  };

  const handleSave = async () => {
    setLoading(true);
    setSaveStatus(null);
    
    try {
      const backendConfig = {
        username: config.username,
        password: config.password,
        additional_config: {
          subreddits: config.subreddits.split(',').map(s => s.trim()).filter(s => s),
          keywords: config.keywords.split(',').map(k => k.trim()).filter(k => k)
        }
      };

      const response = await api.platforms.configure('reddit', backendConfig);
      
      setSaveStatus({ 
        type: 'success', 
        message: response.message || 'Reddit account connected successfully! 🎉' 
      });
      setConnectionStatus('pending');
    } catch (error) {
      setSaveStatus({ 
        type: 'error', 
        message: `Failed to connect Reddit account: ${error.message}` 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setSaveStatus(null);
    
    try {
      const response = await api.platforms.testConnection('reddit');
      
      if (response.test_status === 'success') {
        setConnectionStatus('connected');
        setSaveStatus({ 
          type: 'success', 
          message: 'Reddit connection test successful! ✅ Your account is working properly.' 
        });
      } else {
        setConnectionStatus('error');
        setSaveStatus({ 
          type: 'error', 
          message: `Connection test failed: ${response.error_details || 'Invalid credentials or account issue'}` 
        });
      }
    } catch (error) {
      setConnectionStatus('error');
      setSaveStatus({ 
        type: 'error', 
        message: `Connection test failed: ${error.message}` 
      });
    } finally {
      setTesting(false);
    }
  };

  const getStatusChip = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Chip label="✅ Connected" color="success" />;
      case 'error':
        return <Chip label="❌ Connection Error" color="error" />;
      case 'pending':
        return <Chip label="⏳ Ready to Test" color="warning" />;
      default:
        return <Chip label="⭕ Not Connected" color="default" />;
    }
  };

  const isFormValid = config.username && config.password;

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
                    🔴
                  </PlatformIcon>
                  <Box>
                    <Typography variant="h3" fontWeight="bold" gutterBottom>
                      Reddit Account Setup
                    </Typography>
                    <Typography variant="h6" sx={{ opacity: 0.9 }}>
                      Connect your Reddit account to monitor subreddits and engage with discussions
                    </Typography>
                  </Box>
                </Box>
                
                <Box textAlign="right">
                  {getStatusChip()}
                </Box>
              </Box>
            </CardContent>
          </HeaderCard>

          {/* Info Alert */}
          <Alert 
            severity="info" 
            sx={{ borderRadius: 3 }}
            icon={<SecurityIcon />}
          >
            <Typography variant="body2">
              <strong>Secure Multi-Tenant Setup:</strong> VoiceForge is already registered as a Reddit application. 
              Simply provide your Reddit account credentials below to start monitoring and posting on your behalf.
            </Typography>
          </Alert>

          {/* Main Configuration Card */}
          <Card sx={{ borderRadius: 4, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            {/* Tab Navigation */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs 
                value={activeTab} 
                onChange={(e, newValue) => setActiveTab(newValue)}
                variant="fullWidth"
              >
                <StyledTab icon={<PersonIcon />} label="Account Connection" />
                <StyledTab icon={<MonitorIcon />} label="Monitoring Setup" />
                <StyledTab icon={<HelpIcon />} label="How It Works" />
              </Tabs>
            </Box>

            <CardContent sx={{ p: 4 }}>
              {/* Account Connection Tab */}
              <TabPanel value={activeTab} index={0}>
                <Stack spacing={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" gutterBottom>
                      Connect Your Reddit Account
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Provide your Reddit login credentials to enable monitoring and posting
                    </Typography>
                  </Box>

                  <Paper sx={{ p: 4, backgroundColor: 'primary.50', borderRadius: 3, border: 1, borderColor: 'primary.200' }}>
                    <Box display="flex" gap={2} mb={2}>
                      <CheckCircleIcon color="primary" />
                      <Typography variant="h6" fontWeight="bold" color="primary.main">
                        VoiceForge Reddit App is Pre-Configured
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="primary.dark">
                      Our Reddit application is already registered and approved. You don't need to create any apps or get API keys - 
                      just connect your personal Reddit account below.
                    </Typography>
                  </Paper>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Reddit Username *"
                        value={config.username}
                        onChange={(e) => handleInputChange('username', e.target.value)}
                        placeholder="Your Reddit username"
                        variant="outlined"
                        helperText="Enter your Reddit username (without u/ prefix)"
                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Reddit Password *"
                        type={showPassword ? 'text' : 'password'}
                        value={config.password}
                        onChange={(e) => handleInputChange('password', e.target.value)}
                        placeholder="Your Reddit password"
                        variant="outlined"
                        helperText="Your account password (stored securely)"
                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowPassword(!showPassword)}
                                edge="end"
                              >
                                {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                  </Grid>

                  <Paper sx={{ p: 3, backgroundColor: 'warning.50', borderRadius: 3, border: 1, borderColor: 'warning.200' }}>
                    <Box display="flex" gap={2}>
                      <SecurityIcon color="warning" />
                      <Box>
                        <Typography variant="h6" fontWeight="bold" color="warning.main" gutterBottom>
                          Security & Privacy
                        </Typography>
                        <Stack spacing={1}>
                          <Typography variant="body2" color="warning.dark">
                            • Your credentials are encrypted and stored securely
                          </Typography>
                          <Typography variant="body2" color="warning.dark">
                            • VoiceForge will only access public content and post on your behalf when you explicitly request it
                          </Typography>
                          <Typography variant="body2" color="warning.dark">
                            • You can disconnect your account anytime from this page
                          </Typography>
                          <Typography variant="body2" color="warning.dark">
                            • We recommend using a dedicated Reddit account for business monitoring
                          </Typography>
                        </Stack>
                      </Box>
                    </Box>
                  </Paper>
                </Stack>
              </TabPanel>

              {/* Monitoring Setup Tab */}
              <TabPanel value={activeTab} index={1}>
                <Stack spacing={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" gutterBottom>
                      Configure Monitoring
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Set up which subreddits and topics you want to monitor
                    </Typography>
                  </Box>

                  <TextField
                    fullWidth
                    label="Subreddits to Monitor"
                    multiline
                    rows={4}
                    value={config.subreddits}
                    onChange={(e) => handleInputChange('subreddits', e.target.value)}
                    placeholder="startups, SaaS, webdev, programming, javascript"
                    variant="outlined"
                    helperText="Enter subreddit names separated by commas (without r/ prefix)"
                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                  />

                  <TextField
                    fullWidth
                    label="Keywords to Track (Optional)"
                    multiline
                    rows={4}
                    value={config.keywords}
                    onChange={(e) => handleInputChange('keywords', e.target.value)}
                    placeholder="API, integration, automation, feedback, feature request"
                    variant="outlined"
                    helperText="Specific keywords to monitor within the subreddits (comma-separated). Leave empty to monitor all content."
                    sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
                  />

                  <Paper sx={{ p: 3, backgroundColor: 'success.50', borderRadius: 3, border: 1, borderColor: 'success.200' }}>
                    <Typography variant="h6" fontWeight="bold" color="success.main" gutterBottom>
                      📊 What VoiceForge Will Monitor
                    </Typography>
                    <Stack spacing={1}>
                      <Typography variant="body2" color="success.dark">
                        <strong>Subreddits:</strong> {config.subreddits || 'None configured yet'}
                      </Typography>
                      <Typography variant="body2" color="success.dark">
                        <strong>Keywords:</strong> {config.keywords || 'All content (no keyword filtering)'}
                      </Typography>
                      <Typography variant="body2" color="success.dark">
                        <strong>Content Types:</strong> Posts, comments, and discussions
                      </Typography>
                      <Typography variant="body2" color="success.dark">
                        <strong>Analysis:</strong> Sentiment, engagement potential, and relevance scoring
                      </Typography>
                    </Stack>
                  </Paper>
                </Stack>
              </TabPanel>

              {/* How It Works Tab */}
              <TabPanel value={activeTab} index={2}>
                <Stack spacing={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" gutterBottom>
                      How VoiceForge Reddit Integration Works
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Understanding our secure, multi-tenant Reddit monitoring system
                    </Typography>
                  </Box>

                  <Stack spacing={3}>
                    <GuideStep stepcolor="#f56565">
                      <Box display="flex" gap={2}>
                        <Avatar sx={{ bgcolor: '#f56565', color: 'white', fontWeight: 'bold' }}>
                          1
                        </Avatar>
                        <Box flex={1}>
                          <Typography variant="h6" fontWeight="bold" gutterBottom>
                            Pre-Configured Reddit App
                          </Typography>
                          <Typography variant="body2">
                            VoiceForge is already registered as a Reddit application with all necessary permissions. 
                            You don't need to create any apps or manage API keys - we handle all the technical setup.
                          </Typography>
                        </Box>
                      </Box>
                    </GuideStep>

                    <GuideStep stepcolor="#4299e1">
                      <Box display="flex" gap={2}>
                        <Avatar sx={{ bgcolor: '#4299e1', color: 'white', fontWeight: 'bold' }}>
                          2
                        </Avatar>
                        <Box flex={1}>
                          <Typography variant="h6" fontWeight="bold" gutterBottom>
                            Your Account, Your Control
                          </Typography>
                          <Typography variant="body2">
                            You provide your Reddit account credentials, which allows VoiceForge to monitor and post 
                            on your behalf. All activity appears as coming from your account, giving you full ownership and control.
                          </Typography>
                        </Box>
                      </Box>
                    </GuideStep>

                    <GuideStep stepcolor="#48bb78">
                      <Box display="flex" gap={2}>
                        <Avatar sx={{ bgcolor: '#48bb78', color: 'white', fontWeight: 'bold' }}>
                          3
                        </Avatar>
                        <Box flex={1}>
                          <Typography variant="h6" fontWeight="bold" gutterBottom>
                            Intelligent Monitoring
                          </Typography>
                          <Typography variant="body2">
                            VoiceForge continuously monitors your specified subreddits for relevant discussions, 
                            analyzes sentiment and engagement potential, and surfaces the most important signals for your business.
                          </Typography>
                        </Box>
                      </Box>
                    </GuideStep>

                    <GuideStep stepcolor="#ed8936">
                      <Box display="flex" gap={2}>
                        <Avatar sx={{ bgcolor: '#ed8936', color: 'white', fontWeight: 'bold' }}>
                          4
                        </Avatar>
                        <Box flex={1}>
                          <Typography variant="h6" fontWeight="bold" gutterBottom>
                            AI-Powered Responses
                          </Typography>
                          <Typography variant="body2">
                            When you choose to engage, VoiceForge can generate contextually appropriate responses 
                            that you can review and post. All posts are made from your account with your approval.
                          </Typography>
                        </Box>
                      </Box>
                    </GuideStep>
                  </Stack>

                  <Paper sx={{ p: 3, backgroundColor: 'info.50', borderRadius: 3, border: 1, borderColor: 'info.200' }}>
                    <Box display="flex" gap={2}>
                      <SecurityIcon color="info" />
                      <Box>
                        <Typography variant="h6" fontWeight="bold" color="info.main" gutterBottom>
                          Multi-Tenant Security
                        </Typography>
                        <Stack spacing={1}>
                          <Typography variant="body2" color="info.dark">
                            • Each company's data is completely isolated and secure
                          </Typography>
                          <Typography variant="body2" color="info.dark">
                            • Your Reddit credentials are encrypted using industry-standard security
                          </Typography>
                          <Typography variant="body2" color="info.dark">
                            • VoiceForge operates under strict data protection and privacy policies
                          </Typography>
                          <Typography variant="body2" color="info.dark">
                            • You maintain full control over your Reddit account and can disconnect anytime
                          </Typography>
                        </Stack>
                      </Box>
                    </Box>
                  </Paper>
                </Stack>
              </TabPanel>
            </CardContent>
          </Card>

          {/* Status Messages */}
          {saveStatus && (
            <Alert 
              severity={saveStatus.type === 'error' ? 'error' : 'success'}
              sx={{ borderRadius: 3 }}
            >
              {saveStatus.message}
            </Alert>
          )}

          {/* Action Buttons */}
          <Paper sx={{ p: 3, borderRadius: 4, boxShadow: '0 4px 16px rgba(0,0,0,0.1)' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Button 
                variant="outlined"
                onClick={() => navigate('/settings/signals')}
                sx={{ textTransform: 'none', borderRadius: 3, px: 4, py: 1.5 }}
              >
                Cancel
              </Button>
              
              <Stack direction="row" spacing={2}>
                <Button 
                  variant="outlined"
                  startIcon={testing ? <CircularProgress size={16} /> : <TestConnectionIcon />}
                  onClick={handleTest}
                  disabled={testing || !isFormValid}
                  sx={{ 
                    textTransform: 'none', 
                    borderRadius: 3, 
                    px: 4, 
                    py: 1.5,
                    minWidth: 160
                  }}
                >
                  {testing ? 'Testing...' : 'Test Connection'}
                </Button>
                
                <Button 
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
                  onClick={handleSave}
                  disabled={loading || !isFormValid}
                  sx={{ 
                    background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
                    textTransform: 'none', 
                    borderRadius: 3, 
                    px: 4, 
                    py: 1.5,
                    minWidth: 160,
                    boxShadow: '0 4px 16px rgba(245, 101, 101, 0.3)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)',
                      boxShadow: '0 6px 20px rgba(245, 101, 101, 0.4)',
                    }
                  }}
                >
                  {loading ? 'Connecting...' : 'Connect Account'}
                </Button>
              </Stack>
            </Box>
          </Paper>
        </Stack>
      </Container>
    </GradientBackground>
  );
};

export default RedditConfig;