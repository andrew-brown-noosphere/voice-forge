import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  alpha,
  useTheme,
  LinearProgress,
  Grid
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  Refresh,
  CheckCircle,
  Error,
  Warning,
  Info
} from '@mui/icons-material'

// Floating Action Button Component
export const FloatingActionButton = ({ icon: Icon, onClick, color = 'primary', tooltip, ...props }) => {
  const theme = useTheme()
  
  return (
    <Tooltip title={tooltip}>
      <IconButton
        onClick={onClick}
        sx={{
          position: 'fixed',
          bottom: 32,
          right: 32,
          width: 64,
          height: 64,
          background: `linear-gradient(135deg, ${theme.palette[color].main}, ${theme.palette[color].dark})`,
          color: 'white',
          boxShadow: `0 8px 32px ${alpha(theme.palette[color].main, 0.4)}`,
          backdropFilter: 'blur(20px)',
          border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
          zIndex: 1000,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'scale(1.1) translateY(-4px)',
            boxShadow: `0 12px 40px ${alpha(theme.palette[color].main, 0.6)}`,
            background: `linear-gradient(135deg, ${theme.palette[color].dark}, ${theme.palette[color].main})`
          },
          '&:active': {
            transform: 'scale(0.95)'
          }
        }}
        {...props}
      >
        <Icon sx={{ fontSize: 28 }} />
      </IconButton>
    </Tooltip>
  )
}

// Notification Toast Component
export const NotificationToast = ({ 
  message, 
  type = 'info', 
  onClose, 
  autoHide = true, 
  duration = 4000 
}) => {
  const theme = useTheme()
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    if (autoHide) {
      const timer = setTimeout(() => {
        setVisible(false)
        setTimeout(onClose, 300) // Wait for animation to complete
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [autoHide, duration, onClose])

  const getConfig = () => {
    switch (type) {
      case 'success':
        return { icon: CheckCircle, color: theme.palette.success.main }
      case 'error':
        return { icon: Error, color: theme.palette.error.main }
      case 'warning':
        return { icon: Warning, color: theme.palette.warning.main }
      default:
        return { icon: Info, color: theme.palette.info.main }
    }
  }

  const { icon: Icon, color } = getConfig()

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 24,
        right: 24,
        zIndex: 2000,
        transform: visible ? 'translateX(0)' : 'translateX(400px)',
        opacity: visible ? 1 : 0,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
      }}
    >
      <Card
        sx={{
          minWidth: 300,
          background: alpha(theme.palette.background.paper, 0.95),
          backdropFilter: 'blur(20px)',
          border: `1px solid ${alpha(color, 0.3)}`,
          borderLeft: `4px solid ${color}`,
          boxShadow: `0 8px 32px ${alpha(color, 0.2)}`
        }}
      >
        <CardContent sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
          <Avatar sx={{ bgcolor: alpha(color, 0.2), mr: 2, width: 40, height: 40 }}>
            <Icon sx={{ color, fontSize: 20 }} />
          </Avatar>
          <Typography variant="body1" sx={{ flexGrow: 1, fontWeight: 500 }}>
            {message}
          </Typography>
          <IconButton size="small" onClick={() => { setVisible(false); setTimeout(onClose, 300) }}>
            <MoreVert sx={{ fontSize: 16 }} />
          </IconButton>
        </CardContent>
      </Card>
    </Box>
  )
}

// Metric Card Component with Enhanced Animations
export const MetricCard = ({ 
  title, 
  value, 
  change, 
  changeType = 'positive',
  icon: Icon,
  color = 'primary',
  loading = false
}) => {
  const theme = useTheme()
  const [animatedValue, setAnimatedValue] = useState(0)
  const [isHovered, setIsHovered] = useState(false)

  useEffect(() => {
    if (!loading) {
      const timer = setTimeout(() => {
        let start = 0
        const end = parseInt(value)
        const duration = 2000
        const increment = end / (duration / 50)
        
        const counter = setInterval(() => {
          start += increment
          if (start >= end) {
            setAnimatedValue(end)
            clearInterval(counter)
          } else {
            setAnimatedValue(Math.floor(start))
          }
        }, 50)
        
        return () => clearInterval(counter)
      }, 300)
      return () => clearTimeout(timer)
    }
  }, [value, loading])

  return (
    <Card
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        background: `linear-gradient(135deg, ${alpha(theme.palette[color].main, 0.1)} 0%, ${alpha(theme.palette[color].main, 0.05)} 100%)`,
        backdropFilter: 'blur(20px)',
        border: `1px solid ${alpha(theme.palette[color].main, 0.2)}`,
        borderRadius: 3,
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: `linear-gradient(90deg, ${theme.palette[color].main}, ${theme.palette[color].light})`,
          opacity: isHovered ? 1 : 0,
          transition: 'opacity 0.3s ease'
        },
        '&:hover': {
          transform: 'translateY(-8px) scale(1.02)',
          boxShadow: `0 20px 40px ${alpha(theme.palette[color].main, 0.25)}`,
          border: `1px solid ${alpha(theme.palette[color].main, 0.4)}`
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Avatar
            sx={{
              bgcolor: `${color}.main`,
              width: 56,
              height: 56,
              transition: 'all 0.3s ease',
              transform: isHovered ? 'scale(1.1) rotate(5deg)' : 'scale(1)',
              boxShadow: isHovered ? `0 8px 25px ${alpha(theme.palette[color].main, 0.4)}` : 'none'
            }}
          >
            <Icon sx={{ fontSize: 28 }} />
          </Avatar>
          
          {change && (
            <Chip
              icon={changeType === 'positive' ? <TrendingUp sx={{ fontSize: 14 }} /> : <TrendingDown sx={{ fontSize: 14 }} />}
              label={`${change}%`}
              size="small"
              color={changeType === 'positive' ? 'success' : 'error'}
              sx={{ 
                fontWeight: 600,
                animation: isHovered ? 'pulse 2s infinite' : 'none',
                '@keyframes pulse': {
                  '0%': { transform: 'scale(1)' },
                  '50%': { transform: 'scale(1.05)' },
                  '100%': { transform: 'scale(1)' }
                }
              }}
            />
          )}
        </Box>
        
        <Typography variant="body2" color="textSecondary" sx={{ mb: 1, fontWeight: 500 }}>
          {title}
        </Typography>
        
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 700,
            color: `${color}.main`,
            transition: 'all 0.3s ease'
          }}
        >
          {loading ? (
            <LinearProgress sx={{ width: '100%', height: 8, borderRadius: 4 }} />
          ) : (
            animatedValue.toLocaleString()
          )}
        </Typography>
      </CardContent>
    </Card>
  )
}

// Status Indicator Component
export const StatusIndicator = ({ status, label, size = 'medium' }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'online':
      case 'active':
      case 'healthy':
        return { color: '#4caf50', pulse: true }
      case 'warning':
      case 'degraded':
        return { color: '#ff9800', pulse: false }
      case 'error':
      case 'offline':
      case 'failed':
        return { color: '#f44336', pulse: false }
      default:
        return { color: '#757575', pulse: false }
    }
  }

  const { color, pulse } = getStatusConfig()
  const dotSize = size === 'small' ? 8 : size === 'large' ? 16 : 12

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Box
        sx={{
          width: dotSize,
          height: dotSize,
          borderRadius: '50%',
          backgroundColor: color,
          boxShadow: `0 0 0 ${dotSize / 4}px ${alpha(color, 0.3)}`,
          animation: pulse ? 'statusPulse 2s infinite' : 'none',
          '@keyframes statusPulse': {
            '0%': {
              boxShadow: `0 0 0 0 ${alpha(color, 0.7)}`
            },
            '70%': {
              boxShadow: `0 0 0 ${dotSize}px ${alpha(color, 0)}`
            },
            '100%': {
              boxShadow: `0 0 0 0 ${alpha(color, 0)}`
            }
          }
        }}
      />
      {label && (
        <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
          {label}
        </Typography>
      )}
    </Box>
  )
}

// Loading Skeleton Component
export const LoadingSkeleton = ({ variant = 'rectangular', width, height, animation = 'wave' }) => {
  const theme = useTheme()
  
  return (
    <Box
      sx={{
        width: width || '100%',
        height: height || (variant === 'circular' ? 40 : 20),
        borderRadius: variant === 'circular' ? '50%' : variant === 'rounded' ? 2 : 1,
        background: `linear-gradient(90deg, ${alpha(theme.palette.grey[300], 0.3)} 25%, ${alpha(theme.palette.grey[100], 0.5)} 50%, ${alpha(theme.palette.grey[300], 0.3)} 75%)`,
        backgroundSize: '200% 100%',
        animation: animation === 'wave' ? 'skeletonWave 1.5s infinite' : animation === 'pulse' ? 'skeletonPulse 1.5s infinite' : 'none',
        '@keyframes skeletonWave': {
          '0%': {
            backgroundPosition: '200% 0'
          },
          '100%': {
            backgroundPosition: '-200% 0'
          }
        },
        '@keyframes skeletonPulse': {
          '0%': {
            opacity: 1
          },
          '50%': {
            opacity: 0.4
          },
          '100%': {
            opacity: 1
          }
        }
      }}
    />
  )
}

// Quick Stats Grid Component
export const QuickStatsGrid = ({ stats = [] }) => {
  return (
    <Grid container spacing={3}>
      {stats.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Box
            sx={{
              animation: `slideInUp 0.6s ease-out ${index * 0.1}s both`,
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
            <MetricCard {...stat} />
          </Box>
        </Grid>
      ))}
    </Grid>
  )
}

export default {
  FloatingActionButton,
  NotificationToast,
  MetricCard,
  StatusIndicator,
  LoadingSkeleton,
  QuickStatsGrid
}