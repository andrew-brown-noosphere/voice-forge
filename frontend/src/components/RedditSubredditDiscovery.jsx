import React, { useState, useEffect } from 'react';
import { 
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  Container,
  Alert,
  Paper,
  Checkbox,
  CircularProgress,
  Divider,
  Stack
} from '@mui/material';
import { 
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

const RedditSubredditDiscovery = ({ persona, onSubredditsSelected }) => {
  const [loading, setLoading] = useState(false);
  const [suggestedSubreddits, setSuggestedSubreddits] = useState([]);
  const [selectedSubreddits, setSelectedSubreddits] = useState(new Set());
  const [discoveryComplete, setDiscoveryComplete] = useState(false);

  // Generate subreddit suggestions based on persona
  const generateSubredditSuggestions = async () => {
    setLoading(true);
    
    console.log('🤖 Starting AI-powered analysis...');
    console.log('📊 Analyzing VoiceForge content repository...');
    
    // Simulate content analysis of VoiceForge vectorized data
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    console.log('🎯 Mapping content to persona pain points...');
    
    // Simulate AI matching VoiceForge content to persona needs
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log('🔍 Generating targeted subreddit recommendations...');
    
    // Enhanced suggestions based on VoiceForge content + persona analysis
    const suggestions = [
      {
        name: 'ProductManagement',
        members: '124k',
        description: 'Product Managers discussing integration challenges and workflow optimization',
        relevanceScore: 95,
        reasons: [
          'Your content shows API integration focus - PMs discuss integration challenges here',
          'Workflow automation features match PM pain points about efficiency',
          'Direct role match with decision-making authority'
        ],
        category: 'Role-based',
        activityLevel: 'High',
        estimatedSignals: 18,
        keyTopics: ['API Integration', 'Workflow Automation', 'Product Strategy'],
        lastActive: '2 hours ago',
        contentMatch: 'High - API integration content aligns with PM discussions'
      },
      {
        name: 'SaaS',
        members: '89k',
        description: 'SaaS builders discussing integration tools and automation platforms',
        relevanceScore: 92,
        reasons: [
          'Your automation platform content matches SaaS scaling discussions',
          'Integration management features address common SaaS pain points',
          'Industry alignment with your target market'
        ],
        category: 'Industry',
        activityLevel: 'High',
        estimatedSignals: 15,
        keyTopics: ['SaaS Tools', 'Integration Platforms', 'Automation'],
        lastActive: '1 hour ago',
        contentMatch: 'Very High - Direct SaaS automation platform match'
      },
      {
        name: 'webdev',
        members: '890k',
        description: 'Developers seeking API integration solutions and workflow tools',
        relevanceScore: 88,
        reasons: [
          'Your API connectivity content matches developer integration needs',
          'Technical documentation aligns with developer problem-solving discussions',
          'Large community with frequent integration questions'
        ],
        category: 'Technology',
        activityLevel: 'Very High',
        estimatedSignals: 22,
        keyTopics: ['API Design', 'Integration Solutions', 'Development Tools'],
        lastActive: '15 minutes ago',
        contentMatch: 'High - API/integration content matches dev discussions'
      },
      {
        name: 'startups',
        members: '1.2M',
        description: 'Startup teams discussing automation tools and operational efficiency',
        relevanceScore: 85,
        reasons: [
          'Your workflow optimization content addresses startup efficiency needs',
          'Cost-effective automation matches startup budget constraints',
          'Scaling solutions align with startup growth challenges'
        ],
        category: 'Company Size',
        activityLevel: 'Very High',
        estimatedSignals: 20,
        keyTopics: ['Startup Tools', 'Operational Efficiency', 'Growth'],
        lastActive: '30 minutes ago',
        contentMatch: 'Medium-High - Efficiency/automation content matches startup needs'
      },
      {
        name: 'entrepreneur',
        members: '756k',
        description: 'Entrepreneurs seeking business automation and integration solutions',
        relevanceScore: 78,
        reasons: [
          'Business automation content matches entrepreneur efficiency goals',
          'Integration solutions address multi-tool management pain points',
          'ROI-focused messaging aligns with business owner priorities'
        ],
        category: 'Business',
        activityLevel: 'High',
        estimatedSignals: 12,
        keyTopics: ['Business Automation', 'Tool Integration', 'Efficiency'],
        lastActive: '1 hour ago',
        contentMatch: 'Medium - Business automation focus matches entrepreneur needs'
      },
      {
        name: 'nocode',
        members: '45k',
        description: 'No-code enthusiasts discussing integration and automation platforms',
        relevanceScore: 82,
        reasons: [
          'Your platform simplification content matches no-code philosophy',
          'Visual workflow tools align with no-code user preferences',
          'Integration without coding appeals to this community'
        ],
        category: 'Technology',
        activityLevel: 'Medium',
        estimatedSignals: 8,
        keyTopics: ['No-Code Tools', 'Visual Workflows', 'Integrations'],
        lastActive: '3 hours ago',
        contentMatch: 'High - Simplified integration approach matches no-code needs'
      }
    ];

    setSuggestedSubreddits(suggestions);
    setLoading(false);
    setDiscoveryComplete(true);
  };

  const toggleSubreddit = (subredditName) => {
    const newSelected = new Set(selectedSubreddits);
    if (newSelected.has(subredditName)) {
      newSelected.delete(subredditName);
    } else {
      newSelected.add(subredditName);
    }
    setSelectedSubreddits(newSelected);
  };

  const getActivityColor = (level) => {
    switch (level) {
      case 'Very High': return 'success';
      case 'High': return 'primary';
      case 'Medium': return 'warning';
      default: return 'default';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Role-based': return '#e53e3e';
      case 'Industry': return '#3182ce';
      case 'Technology': return '#38a169';
      case 'Company Size': return '#d69e2e';
      case 'Business': return '#9f7aea';
      default: return '#718096';
    }
  };

  const handleProceedToMonitoring = () => {
    const selectedData = Array.from(selectedSubreddits).map(name => 
      suggestedSubreddits.find(s => s.name === name)
    );
    onSubredditsSelected?.(selectedData);
  };

  return (
    <Container maxWidth="lg">
      <Stack spacing={4}>
        {/* Persona Summary */}
        {persona && (
          <Paper sx={{ p: 3, backgroundColor: 'primary.50', borderRadius: 2 }}>
            <Typography variant="h6" fontWeight="bold" color="primary.main" gutterBottom>
              👥 Target Persona Analysis
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2">
                  <strong>Role:</strong> {persona.role} ({persona.seniority_level})
                </Typography>
                <Typography variant="body2">
                  <strong>Industry:</strong> {persona.industry}
                </Typography>
                <Typography variant="body2">
                  <strong>Company Size:</strong> {persona.company_size}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" gutterBottom>
                  <strong>Pain Points:</strong>
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={0.5}>
                  {persona.pain_points?.map((point, index) => (
                    <Chip key={index} label={point} size="small" color="warning" />
                  )) || []}
                </Box>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Discovery Action */}
        {!discoveryComplete && (
          <Box textAlign="center">
            <Button
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <TrendingUpIcon />}
              onClick={generateSubredditSuggestions}
              disabled={loading}
              sx={{
                borderRadius: 3,
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                textTransform: 'none',
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Analyzing Persona...' : 'Discover Relevant Subreddits'}
            </Button>
          </Box>
        )}

        {/* Discovery Results */}
        {discoveryComplete && (
          <>
            <Alert severity="success" sx={{ borderRadius: 2 }}>
              <Typography variant="body1">
                <strong>Discovery Complete!</strong> Found {suggestedSubreddits.length} relevant subreddits based on your persona analysis.
                Select the ones you'd like to monitor for signals.
              </Typography>
            </Alert>

            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h5" fontWeight="bold">
                Suggested Subreddits ({selectedSubreddits.size} selected)
              </Typography>
              <Button
                variant="contained"
                startIcon={<ScheduleIcon />}
                onClick={handleProceedToMonitoring}
                disabled={selectedSubreddits.size === 0}
                sx={{
                  borderRadius: 3,
                  textTransform: 'none',
                  fontWeight: 'bold'
                }}
              >
                Setup Monitoring ({selectedSubreddits.size})
              </Button>
            </Box>

            <Grid container spacing={3}>
              {suggestedSubreddits.map((subreddit) => (
                <Grid item xs={12} md={6} key={subreddit.name}>
                  <Card 
                    sx={{
                      borderRadius: 4,
                      transition: 'all 0.3s ease',
                      cursor: 'pointer',
                      border: selectedSubreddits.has(subreddit.name) ? 2 : 1,
                      borderColor: selectedSubreddits.has(subreddit.name) ? 'primary.main' : 'grey.300',
                      backgroundColor: selectedSubreddits.has(subreddit.name) ? 'primary.50' : 'white',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 4,
                      },
                    }}
                    onClick={() => toggleSubreddit(subreddit.name)}
                  >
                    <CardContent sx={{ p: 3 }}>
                      {/* Header */}
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Box
                            sx={{
                              width: 40,
                              height: 40,
                              borderRadius: 2,
                              background: getCategoryColor(subreddit.category),
                              color: 'white',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '1rem',
                              fontWeight: 'bold'
                            }}
                          >
                            r/
                          </Box>
                          <Box>
                            <Typography variant="h6" fontWeight="bold">
                              r/{subreddit.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {subreddit.members} members
                            </Typography>
                          </Box>
                        </Box>
                        
                        <Box textAlign="right">
                          <Checkbox
                            checked={selectedSubreddits.has(subreddit.name)}
                            onChange={() => toggleSubreddit(subreddit.name)}
                            color="primary"
                          />
                          <Chip 
                            label={`${subreddit.relevanceScore}%`}
                            color="primary"
                            size="small"
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      </Box>

                      {/* Description */}
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {subreddit.description}
                      </Typography>

                      {/* Stats */}
                      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                        <Chip 
                          label={subreddit.category} 
                          size="small"
                          sx={{ backgroundColor: getCategoryColor(subreddit.category), color: 'white' }}
                        />
                        <Chip 
                          label={`${subreddit.activityLevel} Activity`}
                          color={getActivityColor(subreddit.activityLevel)}
                          size="small"
                        />
                        <Chip 
                          label={`~${subreddit.estimatedSignals} signals/week`}
                          color="info"
                          size="small"
                        />
                      </Stack>

                      {/* Key Topics */}
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        Key Topics:
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5} sx={{ mb: 2 }}>
                        {subreddit.keyTopics.map((topic, index) => (
                          <Chip 
                            key={index} 
                            label={topic} 
                            size="small" 
                            variant="outlined"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                          />
                        ))}
                      </Box>

                      {/* Reasons */}
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        Why this subreddit:
                      </Typography>
                      <Stack spacing={0.5}>
                        {subreddit.reasons.map((reason, index) => (
                          <Typography key={index} variant="caption" color="success.main">
                            • {reason}
                          </Typography>
                        ))}
                      </Stack>

                      <Divider sx={{ my: 2 }} />

                      {/* Footer */}
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="caption" color="text.secondary">
                          Last active: {subreddit.lastActive}
                        </Typography>
                        <Typography variant="caption" color="primary.main" fontWeight="bold">
                          {subreddit.relevanceScore}% match
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {/* Next Steps Preview */}
            {selectedSubreddits.size > 0 && (
              <Paper sx={{ p: 4, backgroundColor: 'success.50', borderRadius: 4 }}>
                <Typography variant="h6" fontWeight="bold" color="success.main" gutterBottom>
                  <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Next Steps Preview
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2">
                      <strong>Search Generation:</strong> AI will create intelligent search queries based on your persona's pain points and goals
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2">
                      <strong>Automated Monitoring:</strong> System will scan selected subreddits every 6 hours for new relevant discussions
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2">
                      <strong>Signal Processing:</strong> Results will be scored and filtered to show only the most relevant opportunities
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            )}
          </>
        )}
      </Stack>
    </Container>
  );
};

export default RedditSubredditDiscovery;