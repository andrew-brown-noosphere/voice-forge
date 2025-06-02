import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Tooltip,
  Paper,
  alpha,
  useTheme
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Launch as LaunchIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Analytics as AnalyticsIcon,
  Storage as StorageIcon,
  Assessment as AssessmentIcon,
  CloudSync as CloudSyncIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ArrowUpward,
  ArrowDownward,
  MoreVert
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'

// Animated Counter Component
const AnimatedCounter = ({ value, duration = 2000, prefix = '', suffix = '' }) => {
  const [count, setCount] = useState(0)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
    let start = 0
    const end = parseInt(value)
    if (start === end) return

    const timer = setInterval(() => {
      start += Math.ceil(end / (duration / 50))
      if (start >= end) {
        setCount(end)
        clearInterval(timer)
      } else {
        setCount(start)
      }
    }, 50)

    return () => clearInterval(timer)
  }, [value, duration])

  return (
    <Typography
      variant="h3"
      component="div"
      sx={{
        fontWeight: 700,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 1s ease-out'
      }}
    >
      {prefix}{count.toLocaleString()}{suffix}
    </Typography>
  )
}

// Glassmorphism Card Component
const GlassCard = ({ children, gradient, hover = true, sx = {}, ...props }) => {
  const theme = useTheme()
  
  return (
    <Card
      sx={{
        background: gradient || `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)} 0%, ${alpha(theme.palette.secondary.main, 0.08)} 100%)`,
        backdropFilter: 'blur(20px)',
        border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
        borderRadius: 3,
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          opacity: 0,
          transition: 'opacity 0.3s ease'
        },
        ...(hover && {
          '&:hover': {
            transform: 'translateY(-12px) scale(1.02)',
            boxShadow: `0 25px 50px ${alpha(theme.palette.primary.main, 0.3)}`,
            '&::before': {
              opacity: 1
            }
          }
        }),
        ...sx
      }}
      {...props}
    >
      {children}
    </Card>
  )
}

// Enhanced Metric Widget Component
const MetricWidget = ({ 
  icon: Icon, 
  title, 
  value, 
  change, 
  changeType = 'positive',
  color = 'primary',
  trend = [],
  suffix = '',
  prefix = '' 
}) => {
  const theme = useTheme()
  const [isHovered, setIsHovered] = useState(false)
  
  const gradients = {
    primary: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.25)} 0%, ${alpha(theme.palette.primary.dark, 0.12)} 100%)`,
    success: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.25)} 0%, ${alpha(theme.palette.success.dark, 0.12)} 100%)`,
    warning: `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.25)} 0%, ${alpha(theme.palette.warning.dark, 0.12)} 100%)`,
    error: `linear-gradient(135deg, ${alpha(theme.palette.error.main, 0.25)} 0%, ${alpha(theme.palette.error.dark, 0.12)} 100%)`,
    info: `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.25)} 0%, ${alpha(theme.palette.info.dark, 0.12)} 100%)`
  }

  return (
    <GlassCard 
      gradient={gradients[color]}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Avatar
            sx={{
              bgcolor: `${color}.main`,
              width: 70,
              height: 70,
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              transform: isHovered ? 'scale(1.15) rotate(8deg)' : 'scale(1)',
              boxShadow: isHovered ? `0 12px 30px ${alpha(theme.palette[color].main, 0.5)}` : `0 4px 15px ${alpha(theme.palette[color].main, 0.3)}`
            }}
          >
            <Icon sx={{ fontSize: 32 }} />
          </Avatar>
          
          <Box sx={{ textAlign: 'right' }}>
            {change && (
              <Chip
                icon={changeType === 'positive' ? <ArrowUpward sx={{ fontSize: 16 }} /> : <ArrowDownward sx={{ fontSize: 16 }} />}
                label={`${change}%`}
                size="small"
                color={changeType === 'positive' ? 'success' : 'error'}
                sx={{ 
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  animation: isHovered ? 'pulse 2s infinite' : 'none',
                  '@keyframes pulse': {
                    '0%': { transform: 'scale(1)' },
                    '50%': { transform: 'scale(1.08)' },
                    '100%': { transform: 'scale(1)' }
                  }
                }}
              />
            )}
          </Box>
        </Box>
        
        <Typography variant="body1" color="textSecondary" sx={{ mb: 2, fontWeight: 600, fontSize: '1.1rem' }}>
          {title}
        </Typography>
        
        <AnimatedCounter 
          value={value} 
          prefix={prefix} 
          suffix={suffix}
        />
        
        {/* Enhanced Mini trend visualization */}
        {trend.length > 0 && (
          <Box sx={{ mt: 3, height: 50, position: 'relative', overflow: 'hidden' }}>
            <svg width="100%" height="50" style={{ position: 'absolute' }}>
              <defs>
                <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor={theme.palette[color].main} stopOpacity="0.4" />
                  <stop offset="100%" stopColor={theme.palette[color].main} stopOpacity="0" />
                </linearGradient>
              </defs>
              
              {/* Area fill */}
              <path
                d={`M 0,50 ${trend.map((point, index) => 
                  `L ${(index / (trend.length - 1)) * 100}%,${50 - (point / 100) * 40}`
                ).join(' ')} L 100%,50 Z`}
                fill={`url(#gradient-${color})`}
                opacity={isHovered ? 0.8 : 0.6}
                style={{ transition: 'opacity 0.3s ease' }}
              />
              
              {/* Line */}
              <polyline
                fill="none"
                stroke={theme.palette[color].main}
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={trend.map((point, index) => 
                  `${(index / (trend.length - 1)) * 100}%,${50 - (point / 100) * 40}`
                ).join(' ')}
                style={{
                  filter: `drop-shadow(0 2px 6px ${alpha(theme.palette[color].main, 0.3)})`,
                  transition: 'all 0.3s ease'
                }}
              />
              
              {/* Data points */}
              {trend.map((point, index) => (
                <circle
                  key={index}
                  cx={`${(index / (trend.length - 1)) * 100}%`}
                  cy={`${50 - (point / 100) * 40}`}
                  r={isHovered ? "4" : "2"}
                  fill={theme.palette[color].main}
                  style={{
                    transition: 'all 0.3s ease',
                    filter: `drop-shadow(0 2px 4px ${alpha(theme.palette[color].main, 0.4)})`
                  }}
                />
              ))}
            </svg>
          </Box>
        )}
      </CardContent>
    </GlassCard>
  )
}

// Enhanced Progress Ring Component
const ProgressRing = ({ value, size = 140, strokeWidth = 10, color = 'primary' }) => {
  const theme = useTheme()
  const [animatedValue, setAnimatedValue] = useState(0)
  
  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 300)
    return () => clearTimeout(timer)
  }, [value])
  
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (animatedValue / 100) * circumference
  
  return (
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <svg width={size} height={size}>
        <defs>
          <linearGradient id={`progress-gradient-${color}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={theme.palette[color].main} />
            <stop offset="100%" stopColor={theme.palette[color].light} />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={alpha(theme.palette[color].main, 0.15)}
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={`url(#progress-gradient-${color})`}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          filter="url(#glow)"
          style={{
            transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        />
      </svg>
      
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column'
        }}
      >
        <Typography variant="h3" sx={{ fontWeight: 800, color: `${color}.main` }}>
          {Math.round(animatedValue)}%
        </Typography>
      </Box>
    </Box>
  )
}

// Enhanced Activity Feed Component
const ActivityFeed = ({ activities = [] }) => {
  const theme = useTheme()
  
  const defaultActivities = [
    { id: 1, type: 'crawl', message: 'New crawl started for example.com', time: '2 minutes ago', status: 'running' },
    { id: 2, type: 'content', message: '150 new content items processed', time: '5 minutes ago', status: 'completed' },
    { id: 3, type: 'analysis', message: 'Analytics report generated', time: '10 minutes ago', status: 'completed' },
    { id: 4, type: 'crawl', message: 'Crawl completed for blog.example.com', time: '15 minutes ago', status: 'completed' },
    { id: 5, type: 'ai', message: 'AI embeddings generated for 200 items', time: '20 minutes ago', status: 'completed' }
  ]

  const activityData = activities.length > 0 ? activities : defaultActivities
  
  const getActivityIcon = (type, status) => {
    if (status === 'running') return <PlayIcon sx={{ color: 'primary.main' }} />
    if (status === 'completed') return <StorageIcon sx={{ color: 'success.main' }} />
    if (type === 'ai') return <AnalyticsIcon sx={{ color: 'info.main' }} />
    return <AssessmentIcon sx={{ color: 'info.main' }} />
  }

  return (
    <GlassCard>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
            🔥 Live Activity
          </Typography>
          <IconButton size="small" sx={{ color: 'text.secondary' }}>
            <MoreVert />
          </IconButton>
        </Box>
        
        <Box sx={{ maxHeight: 350, overflowY: 'auto', pr: 1 }}>
          {activityData.map((activity, index) => (
            <Box
              key={activity.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                mb: 2.5,
                p: 2.5,
                borderRadius: 3,
                background: alpha(theme.palette.background.paper, 0.6),
                backdropFilter: 'blur(10px)',
                border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                animation: `slideInUp 0.6s ease-out ${index * 0.1}s both`,
                '&:hover': {
                  background: alpha(theme.palette.primary.main, 0.08),
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                  transform: 'translateX(12px) scale(1.02)',
                  boxShadow: `0 8px 25px ${alpha(theme.palette.primary.main, 0.15)}`
                },
                '@keyframes slideInUp': {
                  from: {
                    opacity: 0,
                    transform: 'translateY(30px)'
                  },
                  to: {
                    opacity: 1,
                    transform: 'translateY(0)'
                  }
                }
              }}
            >
              <Avatar
                sx={{
                  width: 40,
                  height: 40,
                  bgcolor: 'transparent',
                  mr: 2.5
                }}
              >
                {getActivityIcon(activity.type, activity.status)}
              </Avatar>
              
              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                  {activity.message}
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.85rem' }}>
                  {activity.time}
                </Typography>
              </Box>
              
              <Chip
                label={activity.status}
                size="small"
                color={activity.status === 'completed' ? 'success' : 'primary'}
                variant="outlined"
                sx={{ fontWeight: 600 }}
              />
            </Box>
          ))}
        </Box>
      </CardContent>
    </GlassCard>
  )
}

// Enhanced Status Grid Component
const StatusGrid = ({ statuses = {} }) => {
  const theme = useTheme()
  
  const defaultStatuses = {
    'Server Status': { value: 'Online', color: 'success', icon: CloudSyncIcon },
    'API Health': { value: 'Healthy', color: 'success', icon: AssessmentIcon },
    'Queue Status': { value: '3 Active', color: 'primary', icon: SpeedIcon },
    'AI Processing': { value: '87%', color: 'warning', icon: AnalyticsIcon }
  }

  const statusData = Object.keys(statuses).length > 0 ? statuses : defaultStatuses

  return (
    <GlassCard>
      <CardContent sx={{ p: 4 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, mb: 4, display: 'flex', alignItems: 'center', gap: 1 }}>
          ⚡ System Status
        </Typography>
        
        <Grid container spacing={2.5}>
          {Object.entries(statusData).map(([key, status], index) => {
            const Icon = status.icon
            return (
              <Grid item xs={6} key={key}>
                <Paper
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    background: alpha(
                      status.color === 'success' ? theme.palette.success.main :
                      status.color === 'warning' ? theme.palette.warning.main :
                      status.color === 'error' ? theme.palette.error.main :
                      theme.palette.primary.main, 0.12
                    ),
                    border: `1px solid ${alpha(
                      status.color === 'success' ? theme.palette.success.main :
                      status.color === 'warning' ? theme.palette.warning.main :
                      status.color === 'error' ? theme.palette.error.main :
                      theme.palette.primary.main, 0.3
                    )}`,
                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                    animation: `zoomIn 0.6s ease-out ${index * 0.15}s both`,
                    '&:hover': {
                      transform: 'scale(1.08) translateY(-4px)',
                      background: alpha(
                        status.color === 'success' ? theme.palette.success.main :
                        status.color === 'warning' ? theme.palette.warning.main :
                        status.color === 'error' ? theme.palette.error.main :
                        theme.palette.primary.main, 0.20
                      ),
                      boxShadow: `0 12px 30px ${alpha(
                        status.color === 'success' ? theme.palette.success.main :
                        status.color === 'warning' ? theme.palette.warning.main :
                        status.color === 'error' ? theme.palette.error.main :
                        theme.palette.primary.main, 0.25
                      )}`
                    },
                    '@keyframes zoomIn': {
                      from: {
                        opacity: 0,
                        transform: 'scale(0.8)'
                      },
                      to: {
                        opacity: 1,
                        transform: 'scale(1)'
                      }
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                    <Icon sx={{ 
                      fontSize: 20, 
                      mr: 1, 
                      color: `${status.color}.main`,
                      filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
                    }} />
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                      {key}
                    </Typography>
                  </Box>
                  <Typography variant="body1" sx={{ fontWeight: 700, fontSize: '1.1rem' }}>
                    {status.value}
                  </Typography>
                </Paper>
              </Grid>
            )
          })}
        </Grid>
      </CardContent>
    </GlassCard>
  )
}

// Main Enhanced Dashboard Component
const ModernDashboard = ({ onRefresh }) => {
  const navigate = useNavigate()
  const api = useApi()
  const theme = useTheme()
  
  // State management
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [stats, setStats] = useState({
    totalCrawls: 12847,
    activeCrawls: 8456,
    completedCrawls: 234567,
    totalDomains: 1247
  })

  // Sample data - replace with your actual API calls
  const metrics = [
    {
      icon: StorageIcon,
      title: 'Pages Analyzed',
      value: stats.totalCrawls,
      change: 15.3,
      changeType: 'positive',
      color: 'primary',
      trend: [20, 45, 35, 60, 45, 80, 65, 75]
    },
    {
      icon: AnalyticsIcon,
      title: 'Content Items',
      value: stats.activeCrawls,
      change: 8.7,
      changeType: 'positive',
      color: 'success',
      trend: [30, 25, 45, 55, 60, 45, 70, 85]
    },
    {
      icon: CloudSyncIcon,
      title: 'Text Chunks',
      value: stats.completedCrawls,
      change: 12.4,
      changeType: 'positive',
      color: 'info',
      trend: [40, 35, 55, 45, 65, 70, 60, 90]
    },
    {
      icon: AssessmentIcon,
      title: 'Dataset Size',
      value: stats.totalDomains,
      suffix: 'MB',
      change: 5.2,
      changeType: 'positive',
      color: 'warning',
      trend: [25, 40, 30, 50, 45, 60, 55, 70]
    }
  ]

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      // Add your actual data loading logic here
      if (onRefresh) {
        await onRefresh()
      }
      setTimeout(() => setRefreshing(false), 2000)
    } catch (err) {
      console.error('Refresh failed:', err)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    // Load initial data
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '60vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <CircularProgress size={60} thickness={4} />
        <Typography sx={{ ml: 3, color: 'white', fontSize: '1.2rem' }}>Loading modern dashboard...</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      p: 4
    }}>
      {/* Enhanced Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6 }}>
        <Box>
          <Typography 
            variant="h2" 
            sx={{ 
              fontWeight: 800, 
              background: 'linear-gradient(45deg, #fff, #f0f0f0)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1,
              fontSize: { xs: '2.5rem', md: '3.5rem' }
            }}
          >
            🚀 VoiceForge Analytics
          </Typography>
          <Typography variant="h5" sx={{ color: alpha('#fff', 0.85), fontWeight: 500 }}>
            Real-time insights into your content pipeline
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/crawls/new')}
            sx={{
              background: 'linear-gradient(45deg, #FF6B6B, #4ECDC4)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: 3,
              px: 4,
              py: 1.5,
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(45deg, #FF5252, #26C6DA)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(255,107,107,0.4)'
              }
            }}
          >
            Analyze Web Content
          </Button>
          
          <IconButton
            onClick={handleRefresh}
            sx={{
              background: alpha('#fff', 0.15),
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: '#fff',
              borderRadius: 3,
              width: 56,
              height: 56,
              '&:hover': {
                background: alpha('#fff', 0.25),
                transform: 'rotate(180deg) scale(1.1)'
              },
              transition: 'all 0.4s ease'
            }}
          >
            <RefreshIcon sx={{ 
              animation: refreshing ? 'spin 2s linear infinite' : 'none',
              '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' }
              }
            }} />
          </IconButton>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 4, 
            borderRadius: 3,
            backdropFilter: 'blur(20px)',
            background: alpha(theme.palette.error.main, 0.1),
            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`
          }} 
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {/* Enhanced Metrics Grid */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <Box
              sx={{
                animation: `slideInUp 0.8s ease-out ${index * 0.2}s both`,
                '@keyframes slideInUp': {
                  from: {
                    opacity: 0,
                    transform: 'translateY(50px)'
                  },
                  to: {
                    opacity: 1,
                    transform: 'translateY(0)'
                  }
                }
              }}
            >
              <MetricWidget {...metric} />
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* Secondary Enhanced Widgets */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ p: 5, textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 4, color: 'white' }}>
                🎯 AI Processing
              </Typography>
              <ProgressRing value={87} color="primary" />
              <Typography variant="body1" sx={{ mt: 3, color: alpha('#fff', 0.8), fontWeight: 500 }}>
                87% of content ready for AI processing
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ p: 5, textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 4, color: 'white' }}>
                🚀 Embedding Coverage
              </Typography>
              <ProgressRing value={73} color="success" />
              <Typography variant="body1" sx={{ mt: 3, color: alpha('#fff', 0.8), fontWeight: 500 }}>
                73% of content has embeddings generated
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <StatusGrid />
        </Grid>
      </Grid>

      {/* Bottom Enhanced Section */}
      <Grid container spacing={4}>
        <Grid item xs={12} lg={8}>
          <GlassCard>
            <CardContent sx={{ p: 5 }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 4, color: 'white' }}>
                📊 Performance Metrics (Last 7 Days)
              </Typography>
              <Box sx={{ 
                height: 300, 
                background: alpha('#fff', 0.08), 
                borderRadius: 3, 
                border: `1px solid ${alpha('#fff', 0.1)}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                backdropFilter: 'blur(10px)'
              }}>
                <TrendingUpIcon sx={{ fontSize: 80, color: alpha('#fff', 0.4), mb: 2 }} />
                <Typography variant="h6" sx={{ color: alpha('#fff', 0.7), textAlign: 'center' }}>
                  Interactive chart placeholder<br/>
                  Integrate with Recharts or Chart.js
                </Typography>
              </Box>
            </CardContent>
          </GlassCard>
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <ActivityFeed />
        </Grid>
      </Grid>
    </Box>
  )
}

export default ModernDashboard