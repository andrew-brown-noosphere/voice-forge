import React, { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import LanguageIcon from '@mui/icons-material/Language'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { format } from 'date-fns'

// API service
import apiService from '../services/api'

// Chart components
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend)

const Dashboard = () => {
  const [crawls, setCrawls] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalCrawls: 0,
    totalPages: 0,
    totalContent: 0,
    activeCrawls: 0,
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const crawlsData = await apiService.listCrawls(5, 0)
        setCrawls(crawlsData)
        
        // Calculate stats
        const activeCrawls = crawlsData.filter(
          (crawl) => crawl.state === 'running' || crawl.state === 'pending'
        ).length
        
        const totalPages = crawlsData.reduce(
          (total, crawl) => total + crawl.progress.pages_crawled,
          0
        )
        
        const totalContent = crawlsData.reduce(
          (total, crawl) => total + crawl.progress.content_extracted,
          0
        )
        
        setStats({
          totalCrawls: crawlsData.length,
          totalPages,
          totalContent,
          activeCrawls,
        })
        
        setLoading(false)
      } catch (error) {
        console.error('Failed to fetch dashboard data', error)
        setLoading(false)
      }
    }

    fetchData()
    
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchData, 5000)
    
    return () => clearInterval(interval)
  }, [])

  // Prepare chart data
  const chartData = {
    labels: ['Completed', 'Running', 'Failed', 'Cancelled'],
    datasets: [
      {
        data: [
          crawls.filter((crawl) => crawl.state === 'completed').length,
          crawls.filter((crawl) => crawl.state === 'running').length,
          crawls.filter((crawl) => crawl.state === 'failed').length,
          crawls.filter((crawl) => crawl.state === 'cancelled').length,
        ],
        backgroundColor: ['#4caf50', '#2196f3', '#f44336', '#ff9800'],
        hoverBackgroundColor: ['#388e3c', '#1976d2', '#d32f2f', '#f57c00'],
      },
    ],
  }

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Button
          component={RouterLink}
          to="/crawls/new"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
        >
          New Crawl
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Total Crawls
            </Typography>
            <Typography variant="h3">{stats.totalCrawls}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Active Crawls
            </Typography>
            <Typography variant="h3">{stats.activeCrawls}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Pages Crawled
            </Typography>
            <Typography variant="h3">{stats.totalPages}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Content Extracted
            </Typography>
            <Typography variant="h3">{stats.totalContent}</Typography>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Crawls */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader title="Recent Crawls" />
            <Divider />
            <CardContent sx={{ p: 0 }}>
              {loading ? (
                <LinearProgress />
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Domain</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Progress</TableCell>
                        <TableCell>Start Time</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {crawls.map((crawl) => (
                        <TableRow key={crawl.crawl_id}>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <LanguageIcon fontSize="small" sx={{ mr: 1 }} />
                              {crawl.domain}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={crawl.state.charAt(0).toUpperCase() + crawl.state.slice(1)}
                              color={getStatusColor(crawl.state)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {crawl.state === 'running' ? (
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Box sx={{ width: '100%', mr: 1 }}>
                                  <LinearProgress
                                    variant="determinate"
                                    value={Math.min(
                                      (crawl.progress.pages_crawled / Math.max(1, crawl.progress.pages_discovered)) * 100,
                                      100
                                    )}
                                  />
                                </Box>
                                <Box sx={{ minWidth: 35 }}>
                                  <Typography variant="body2" color="text.secondary">
                                    {`${crawl.progress.pages_crawled}/${crawl.progress.pages_discovered}`}
                                  </Typography>
                                </Box>
                              </Box>
                            ) : (
                              `${crawl.progress.pages_crawled} pages`
                            )}
                          </TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <ScheduleIcon fontSize="small" sx={{ mr: 1 }} />
                              {crawl.start_time
                                ? format(new Date(crawl.start_time), 'MMM d, yyyy HH:mm')
                                : 'N/A'}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Button
                              component={RouterLink}
                              to={`/crawls/${crawl.crawl_id}`}
                              size="small"
                            >
                              Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Crawl Status Chart */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardHeader title="Crawl Status" />
            <Divider />
            <CardContent>
              <Box sx={{ height: 250, position: 'relative' }}>
                {loading ? (
                  <LinearProgress />
                ) : (
                  <Doughnut data={chartData} options={chartOptions} />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
