import React, { useEffect, useState } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
  Grid,
  Chip,
  LinearProgress,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import CancelIcon from '@mui/icons-material/Cancel'
import LanguageIcon from '@mui/icons-material/Language'
import ScheduleIcon from '@mui/icons-material/Schedule'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import { format } from 'date-fns'

// API service
import apiService from '../services/api'

const CrawlDetails = () => {
  const { id } = useParams()
  const [crawlStatus, setCrawlStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [confirmCancel, setConfirmCancel] = useState(false)
  const [latestContent, setLatestContent] = useState([])
  
  useEffect(() => {
    fetchCrawlStatus()
    
    // Poll for updates if crawl is running
    const interval = setInterval(() => {
      if (crawlStatus && (crawlStatus.state === 'running' || crawlStatus.state === 'pending')) {
        fetchCrawlStatus()
      }
    }, 3000)
    
    return () => clearInterval(interval)
  }, [id, crawlStatus?.state])
  
  const fetchCrawlStatus = async () => {
    try {
      const status = await apiService.getCrawlStatus(id)
      setCrawlStatus(status)
      
      // Fetch latest content if crawl is running or completed
      if (status.state === 'running' || status.state === 'completed') {
        fetchLatestContent()
      }
      
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch crawl status', error)
      setError('Failed to fetch crawl status')
      setLoading(false)
    }
  }
  
  const fetchLatestContent = async () => {
    try {
      const content = await apiService.searchContent('', crawlStatus?.domain, null, 5, 0)
      setLatestContent(content)
    } catch (error) {
      console.error('Failed to fetch latest content', error)
    }
  }
  
  const handleCancelCrawl = async () => {
    try {
      await apiService.cancelCrawl(id)
      setConfirmCancel(false)
      fetchCrawlStatus()
    } catch (error) {
      console.error('Failed to cancel crawl', error)
      setError('Failed to cancel crawl')
    }
  }
  
  // Get status chip color
  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'primary'
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      case 'cancelled':
        return 'warning'
      default:
        return 'default'
    }
  }
  
  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <CircularProgress size={20} />
      case 'completed':
        return <CheckCircleIcon color="success" />
      case 'failed':
        return <ErrorIcon color="error" />
      case 'cancelled':
        return <CancelIcon color="warning" />
      default:
        return null
    }
  }
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    )
  }
  
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    )
  }
  
  if (!crawlStatus) {
    return (
      <Alert severity="warning" sx={{ mb: 3 }}>
        Crawl not found
      </Alert>
    )
  }
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Crawl Details
        </Typography>
        
        {crawlStatus.state === 'running' && (
          <Button
            variant="outlined"
            color="error"
            startIcon={<CancelIcon />}
            onClick={() => setConfirmCancel(true)}
          >
            Cancel Crawl
          </Button>
        )}
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <LanguageIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                Domain: {crawlStatus.domain}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Status
                  </Typography>
                  <Box display="flex" alignItems="center" mt={0.5}>
                    {getStatusIcon(crawlStatus.state)}
                    <Chip
                      label={
                        crawlStatus.state.charAt(0).toUpperCase() +
                        crawlStatus.state.slice(1)
                      }
                      color={getStatusColor(crawlStatus.state)}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Started
                  </Typography>
                  <Typography variant="body1">
                    {crawlStatus.start_time
                      ? format(new Date(crawlStatus.start_time), 'MMM d, yyyy HH:mm')
                      : 'N/A'}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Max Depth
                  </Typography>
                  <Typography variant="body1">
                    {crawlStatus.config.max_depth}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Current Depth
                  </Typography>
                  <Typography variant="body1">
                    {crawlStatus.progress.current_depth}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Max Pages
                  </Typography>
                  <Typography variant="body1">
                    {crawlStatus.config.max_pages || 'Unlimited'}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Request Delay
                  </Typography>
                  <Typography variant="body1">
                    {crawlStatus.config.delay} seconds
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    User Agent
                  </Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                    {crawlStatus.config.user_agent}
                  </Typography>
                </Grid>
                
                {crawlStatus.error && (
                  <Grid item xs={12}>
                    <Alert severity="error">
                      <Typography variant="body2">Error:</Typography>
                      {crawlStatus.error}
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
          
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Advanced Settings
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>URL Patterns</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Include Patterns:
                  </Typography>
                  {crawlStatus.config.include_patterns &&
                  crawlStatus.config.include_patterns.length > 0 ? (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      {crawlStatus.config.include_patterns.map((pattern) => (
                        <Chip key={pattern} label={pattern} size="small" />
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" gutterBottom>
                      No include patterns
                    </Typography>
                  )}
                  
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Exclude Patterns:
                  </Typography>
                  {crawlStatus.config.exclude_patterns &&
                  crawlStatus.config.exclude_patterns.length > 0 ? (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {crawlStatus.config.exclude_patterns.map((pattern) => (
                        <Chip key={pattern} label={pattern} size="small" />
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2">No exclude patterns</Typography>
                  )}
                </AccordionDetails>
              </Accordion>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Crawl Options</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Respect robots.txt
                      </Typography>
                      <Typography variant="body1">
                        {crawlStatus.config.respect_robots_txt ? 'Yes' : 'No'}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Follow External Links
                      </Typography>
                      <Typography variant="body1">
                        {crawlStatus.config.follow_external_links ? 'Yes' : 'No'}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        Request Timeout
                      </Typography>
                      <Typography variant="body1">
                        {crawlStatus.config.timeout} seconds
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Progress
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Pages Crawled
                  </Typography>
                  <Typography variant="h4">
                    {crawlStatus.progress.pages_crawled}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Pages Discovered
                  </Typography>
                  <Typography variant="h4">
                    {crawlStatus.progress.pages_discovered}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Pages Failed
                  </Typography>
                  <Typography variant="h4" color="error">
                    {crawlStatus.progress.pages_failed}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Content Extracted
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {crawlStatus.progress.content_extracted}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Crawl Progress
                  </Typography>
                  {crawlStatus.state === 'running' ? (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(
                            (crawlStatus.progress.pages_crawled /
                              Math.max(1, crawlStatus.progress.pages_discovered)) *
                              100,
                            100
                          )}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="textSecondary">
                          {`${Math.round(
                            (crawlStatus.progress.pages_crawled /
                              Math.max(1, crawlStatus.progress.pages_discovered)) *
                              100
                          )}%`}
                        </Typography>
                      </Box>
                    </Box>
                  ) : (
                    <LinearProgress
                      variant="determinate"
                      value={100}
                      color={
                        crawlStatus.state === 'completed'
                          ? 'success'
                          : crawlStatus.state === 'failed'
                          ? 'error'
                          : 'warning'
                      }
                    />
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
          
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Latest Content
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              {latestContent.length > 0 ? (
                <List>
                  {latestContent.map((content) => (
                    <ListItem
                      key={content.content_id}
                      button
                      component={RouterLink}
                      to={`/content/${content.content_id}`}
                      divider
                    >
                      <ListItemText
                        primary={content.metadata.title || content.url}
                        secondary={
                          <>
                            <Typography
                              variant="body2"
                              color="textSecondary"
                              component="span"
                            >
                              Type: {content.metadata.content_type}
                            </Typography>
                            <br />
                            <Typography
                              variant="body2"
                              color="textSecondary"
                              component="span"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                              }}
                            >
                              {content.text.substring(0, 150)}...
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body1" color="textSecondary" align="center">
                  No content extracted yet
                </Typography>
              )}
              
              {latestContent.length > 0 && (
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Button
                    component={RouterLink}
                    to="/content"
                    variant="outlined"
                    color="primary"
                  >
                    View All Content
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Cancel Confirmation Dialog */}
      <Dialog
        open={confirmCancel}
        onClose={() => setConfirmCancel(false)}
        aria-labelledby="cancel-dialog-title"
        aria-describedby="cancel-dialog-description"
      >
        <DialogTitle id="cancel-dialog-title">Cancel Crawl?</DialogTitle>
        <DialogContent>
          <DialogContentText id="cancel-dialog-description">
            Are you sure you want to cancel this crawl? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmCancel(false)}>No, Continue</Button>
          <Button onClick={handleCancelCrawl} color="error" autoFocus>
            Yes, Cancel Crawl
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default CrawlDetails
