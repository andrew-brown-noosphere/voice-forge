import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  useTheme,
  alpha,
  Fade,
  Stack,
  IconButton,
  Tooltip,
  CircularProgress,
  InputAdornment,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Launch as LaunchIcon,
  Delete as DeleteIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  MoreVert as MoreVertIcon,
  Language as LanguageIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material'

// Modern components
import {
  ModernCard,
  ModernTextField,
  ModernSelect,
  ModernButton,
  ModernAlert,
  ModernSectionHeader
} from '../components/ModernFormComponents'

// API service
import { useApi } from '../hooks/useApi'

const ModernCrawlList = () => {
  const navigate = useNavigate()
  const theme = useTheme()
  const api = useApi()
  
  // State management
  const [crawls, setCrawls] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('newest')
  const [anchorEl, setAnchorEl] = useState(null)
  const [selectedCrawl, setSelectedCrawl] = useState(null)
  
  // Load crawls
  const loadCrawls = async () => {
    try {
      setLoading(true)
      setError('')
      
      const crawlsData = await api.crawls.list()
      setCrawls(crawlsData)
      
    } catch (err) {
      console.error('Failed to load crawls:', err)
      setError(`Failed to load crawls: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadCrawls()
  }, [])
  
  // Handle crawl actions
  const handleDeleteCrawl = async (crawlId) => {
    try {
      console.log('🗑️ Deleting crawl:', crawlId)
      
      // Show loading state for the specific crawl
      setCrawls(prevCrawls => 
        prevCrawls.map(crawl => 
          crawl.id === crawlId || crawl.crawl_id === crawlId 
            ? { ...crawl, deleting: true }
            : crawl
        )
      )
      
      await api.crawls.delete(crawlId)
      console.log('✅ Delete API call completed')
      
      // Immediately remove from local state
      setCrawls(prevCrawls => 
        prevCrawls.filter(crawl => 
          crawl.id !== crawlId && crawl.crawl_id !== crawlId
        )
      )
      
      console.log('🔄 Refreshing crawl list...')
      // Also refresh from server to be sure
      await loadCrawls()
      
    } catch (err) {
      console.error('❌ Failed to delete crawl:', err)
      setError(`Failed to delete crawl: ${err.message}`)
      
      // Remove loading state on error
      setCrawls(prevCrawls => 
        prevCrawls.map(crawl => 
          crawl.id === crawlId || crawl.crawl_id === crawlId 
            ? { ...crawl, deleting: false }
            : crawl
        )
      )
    }
  }
  
  const handleMenuOpen = (event, crawl) => {
    setAnchorEl(event.currentTarget)
    setSelectedCrawl(crawl)
  }
  
  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedCrawl(null)
  }
  
  // Get status properties
  const getStatusProps = (status) => {
    switch (status) {
      case 'completed':
        return { color: 'success', icon: CheckCircleIcon, label: 'Completed' }
      case 'running':
        return { color: 'primary', icon: PlayIcon, label: 'Running' }
      case 'processing':
        return { color: 'info', icon: AccessTimeIcon, label: 'Processing' }
      case 'pending':
        return { color: 'warning', icon: ScheduleIcon, label: 'Pending' }
      case 'failed':
        return { color: 'error', icon: ErrorIcon, label: 'Failed' }
      case 'cancelled':
        return { color: 'error', icon: PauseIcon, label: 'Cancelled' }
      default:
        return { color: 'default', icon: ScheduleIcon, label: status }
    }
  }
  
  // Filter and sort crawls
  const filteredCrawls = crawls
    .filter(crawl => {
      const matchesSearch = crawl.domain.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' || crawl.state === statusFilter
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.start_time) - new Date(a.start_time)
        case 'oldest':
          return new Date(a.start_time) - new Date(b.start_time)
        case 'domain':
          return a.domain.localeCompare(b.domain)
        case 'status':
          return a.state.localeCompare(b.state)
        default:
          return 0
      }
    })
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }
  
  // Calculate progress
  const calculateProgress = (crawl) => {
    if (!crawl.progress) return 0
    const { pages_crawled, pages_discovered } = crawl.progress
    return Math.min((pages_crawled / Math.max(pages_discovered, 1)) * 100, 100)
  }
  
  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          component="h1" 
          sx={{ 
            fontWeight: 800,
            background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1
          }}
        >
          🕸️ Content Analysis
        </Typography>
        <Typography variant="h6" color="textSecondary" sx={{ fontWeight: 400, mb: 3 }}>
          Monitor and manage your website content analysis sessions
        </Typography>
        
        {/* Action Bar */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', flex: 1 }}>
            <ModernTextField
              placeholder="Search crawls..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              icon={SearchIcon}
              size="small"
              sx={{ minWidth: 250 }}
            />
            
            <ModernSelect
              label="Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'running', label: 'Running' },
                { value: 'completed', label: 'Completed' },
                { value: 'pending', label: 'Pending' },
                { value: 'failed', label: 'Failed' }
              ]}
              size="small"
              sx={{ minWidth: 130 }}
            />
            
            <ModernSelect
              label="Sort By"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              options={[
                { value: 'newest', label: 'Newest First' },
                { value: 'oldest', label: 'Oldest First' },
                { value: 'domain', label: 'Domain A-Z' },
                { value: 'status', label: 'Status' }
              ]}
              size="small"
              sx={{ minWidth: 130 }}
            />
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <ModernButton
              variant="outlined"
              icon={RefreshIcon}
              onClick={loadCrawls}
              disabled={loading}
            >
              Refresh
            </ModernButton>
            
            <ModernButton
              variant="contained"
              icon={AddIcon}
              onClick={() => navigate('/crawls/new')}
              gradient={true}
              glow={true}
            >
              New Crawl
            </ModernButton>
          </Box>
        </Box>
      </Box>
      
      {/* Error Alert */}
      {error && (
        <Fade in={!!error}>
          <Box sx={{ mb: 3 }}>
            <ModernAlert
              severity="error"
              title="Error"
              description={error}
              onClose={() => setError('')}
            />
          </Box>
        </Fade>
      )}
      
      {/* Stats Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <ModernCard sx={{ textAlign: 'center', p: 3 }} hover={false}>
            <Avatar sx={{ 
              width: 56, 
              height: 56, 
              bgcolor: alpha(theme.palette.primary.main, 0.1), 
              color: theme.palette.primary.main,
              mx: 'auto',
              mb: 2
            }}>
              <LanguageIcon />
            </Avatar>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              {crawls.length}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Analysis Sessions
            </Typography>
          </ModernCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <ModernCard sx={{ textAlign: 'center', p: 3 }} hover={false}>
            <Avatar sx={{ 
              width: 56, 
              height: 56, 
              bgcolor: alpha(theme.palette.success.main, 0.1), 
              color: theme.palette.success.main,
              mx: 'auto',
              mb: 2
            }}>
              <CheckCircleIcon />
            </Avatar>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              {crawls.filter(c => c.state === 'completed').length}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Completed
            </Typography>
          </ModernCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <ModernCard sx={{ textAlign: 'center', p: 3 }} hover={false}>
            <Avatar sx={{ 
              width: 56, 
              height: 56, 
              bgcolor: alpha(theme.palette.warning.main, 0.1), 
              color: theme.palette.warning.main,
              mx: 'auto',
              mb: 2
            }}>
              <PlayIcon />
            </Avatar>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              {crawls.filter(c => ['running', 'processing'].includes(c.state)).length}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Active
            </Typography>
          </ModernCard>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <ModernCard sx={{ textAlign: 'center', p: 3 }} hover={false}>
            <Avatar sx={{ 
              width: 56, 
              height: 56, 
              bgcolor: alpha(theme.palette.error.main, 0.1), 
              color: theme.palette.error.main,
              mx: 'auto',
              mb: 2
            }}>
              <ErrorIcon />
            </Avatar>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              {crawls.filter(c => c.state === 'failed').length}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Failed
            </Typography>
          </ModernCard>
        </Grid>
      </Grid>
      
      {/* Crawls List */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress size={40} />
          <Typography sx={{ ml: 2 }}>Loading crawls...</Typography>
        </Box>
      ) : filteredCrawls.length === 0 ? (
        <ModernCard sx={{ textAlign: 'center', p: 6 }} hover={false}>
          <Avatar sx={{ 
            width: 80, 
            height: 80, 
            bgcolor: alpha(theme.palette.text.secondary, 0.1), 
            color: theme.palette.text.secondary,
            mx: 'auto',
            mb: 3
          }}>
            <LanguageIcon sx={{ fontSize: 40 }} />
          </Avatar>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
            {searchTerm || statusFilter !== 'all' ? 'No analysis sessions match your filters' : 'No analysis sessions found'}
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search criteria or filters' 
              : 'Start your first content analysis to see it appear here'}
          </Typography>
          <ModernButton
            variant="contained"
            icon={AddIcon}
            onClick={() => navigate('/crawls/new')}
            gradient={true}
            glow={true}
          >
            Start New Analysis
          </ModernButton>
        </ModernCard>
      ) : (
        <Grid container spacing={3}>
          {filteredCrawls.map((crawl) => {
            const statusProps = getStatusProps(crawl.state)
            const StatusIcon = statusProps.icon
            const progress = calculateProgress(crawl)
            
            return (
              <Grid item xs={12} md={6} lg={4} key={crawl.crawl_id}>
                <ModernCard sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1, p: 3 }}>
                    {/* Header */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1, minWidth: 0 }}>
                        <Avatar sx={{ 
                          bgcolor: alpha(theme.palette[statusProps.color].main, 0.1), 
                          color: theme.palette[statusProps.color].main 
                        }}>
                          <StatusIcon />
                        </Avatar>
                        <Box sx={{ minWidth: 0, flex: 1 }}>
                          <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }} noWrap>
                            {crawl.domain}
                          </Typography>
                          <Chip 
                            label={statusProps.label} 
                            color={statusProps.color} 
                            size="small"
                            sx={{ fontWeight: 600 }}
                          />
                        </Box>
                      </Box>
                      
                      <IconButton 
                        size="small" 
                        onClick={(e) => handleMenuOpen(e, crawl)}
                        sx={{ ml: 1 }}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </Box>
                    
                    {/* Progress */}
                    {crawl.progress && (
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" color="textSecondary">
                            Progress
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {Math.round(progress)}%
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={progress} 
                          sx={{ 
                            height: 8, 
                            borderRadius: 4,
                            backgroundColor: alpha(theme.palette.primary.main, 0.1),
                            '& .MuiLinearProgress-bar': {
                              borderRadius: 4,
                              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
                            }
                          }}
                        />
                        <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                          {crawl.progress.pages_crawled} of {crawl.progress.pages_discovered} pages
                        </Typography>
                      </Box>
                    )}
                    
                    {/* Details */}
                    <Stack spacing={1}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ScheduleIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                        <Typography variant="body2" color="textSecondary">
                          Started: {formatDate(crawl.start_time)}
                        </Typography>
                      </Box>
                      
                      {crawl.end_time && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CheckCircleIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                          <Typography variant="body2" color="textSecondary">
                            Completed: {formatDate(crawl.end_time)}
                          </Typography>
                        </Box>
                      )}
                    </Stack>
                    
                    {/* Actions */}
                    <Box sx={{ display: 'flex', gap: 1, mt: 3 }}>
                      <ModernButton
                        variant="outlined"
                        size="small"
                        onClick={() => navigate(`/crawls/${crawl.crawl_id}`)}
                        sx={{ flex: 1 }}
                      >
                        View Details
                      </ModernButton>
                      <Tooltip title="View Crawled Content">
                        <IconButton 
                          size="small"
                          onClick={() => navigate(`/content?crawl_id=${crawl.crawl_id}`)}
                          sx={{ 
                            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                            color: theme.palette.primary.main,
                            '&:hover': {
                              backgroundColor: alpha(theme.palette.primary.main, 0.1)
                            }
                          }}
                        >
                          <LaunchIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </CardContent>
                </ModernCard>
              </Grid>
            )
          })}
        </Grid>
      )}
      
      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => {
          navigate(`/crawls/${selectedCrawl?.crawl_id}`)
          handleMenuClose()
        }}>
          <ListItemIcon>
            <LaunchIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => {
          navigate(`/content?crawl_id=${selectedCrawl?.crawl_id}`)
          handleMenuClose()
        }}>
          <ListItemIcon>
            <SearchIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Content</ListItemText>
        </MenuItem>
        
        <MenuItem 
          onClick={() => {
            if (selectedCrawl) {
              console.log('🗑️ Menu delete clicked for crawl:', selectedCrawl.id || selectedCrawl.crawl_id)
              handleDeleteCrawl(selectedCrawl.id || selectedCrawl.crawl_id)
            }
            handleMenuClose()
          }}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete Crawl</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  )
}

export default ModernCrawlList