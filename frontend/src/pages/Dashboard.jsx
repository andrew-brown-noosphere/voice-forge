import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import AnalyticsDashboard from '../components/AnalyticsDashboard'
import ModernDashboard from '../components/ModernDashboard'

const Dashboard = () => {
  const navigate = useNavigate()
  const api = useApi()
  
  // State management
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAnalytics, setShowAnalytics] = useState(false)

  // Load dashboard data (simplified for modern dashboard)
  const loadDashboardData = async () => {
    // ModernDashboard will handle its own data loading
    // This is just a placeholder for the refresh functionality
    try {
      setLoading(true)
      setError(null)
      // The actual data loading will be handled by ModernDashboard
    } catch (err) {
      console.error('Dashboard refresh error:', err)
      if (!err.message.includes('no organization')) {
        setError(`Failed to refresh dashboard: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  // Load data on component mount
  useEffect(() => {
    // ModernDashboard handles its own data loading
    // Just initialize the state
    setLoading(false)
  }, [])


  if (loading) {
    return (
      <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading dashboard...</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<AnalyticsIcon />}
            onClick={() => setShowAnalytics(!showAnalytics)}
          >
            {showAnalytics ? 'Hide Analytics' : 'Show Analytics'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDashboardData}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/crawls/new')}
          >
            Analyze Web Content
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Analytics Dashboard */}
      {showAnalytics && (
        <Box sx={{ mb: 4 }}>
          <AnalyticsDashboard key="analytics-dashboard" />
        </Box>
      )}

      {/* Modern Dashboard View - Now Default */}
      <ModernDashboard onRefresh={loadDashboardData} />
    </Box>
  )
}

export default Dashboard