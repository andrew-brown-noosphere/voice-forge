import React, { useState, useEffect } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  IconButton,
  LinearProgress,
  TablePagination,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import VisibilityIcon from '@mui/icons-material/Visibility'
import CancelIcon from '@mui/icons-material/Cancel'
import apiService from '../services/api'

const statusColors = {
  pending: 'warning',
  running: 'info',
  completed: 'success',
  failed: 'error',
  cancelled: 'default',
}

const CrawlList = () => {
  const [crawls, setCrawls] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  const fetchCrawls = async () => {
    try {
      setLoading(true)
      const data = await apiService.listCrawls(rowsPerPage, page * rowsPerPage)
      setCrawls(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching crawls:', err)
      setError('Failed to load crawls. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCrawls()
    
    // Poll for updates every 5 seconds if there are active crawls
    const hasActiveCrawls = crawls.some(
      (crawl) => crawl.state === 'pending' || crawl.state === 'running'
    )
    
    let interval
    if (hasActiveCrawls) {
      interval = setInterval(fetchCrawls, 5000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [page, rowsPerPage])

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleCancelCrawl = async (crawlId) => {
    try {
      await apiService.cancelCrawl(crawlId)
      fetchCrawls()
    } catch (err) {
      console.error('Error cancelling crawl:', err)
      setError('Failed to cancel crawl. Please try again later.')
    }
  }

  const handleDeleteAllCrawls = async () => {
    if (window.confirm('Are you sure you want to delete ALL crawls and content? This action cannot be undone.')) {
      try {
        await apiService.deleteAllCrawls()
        fetchCrawls()
        setError(null)
      } catch (err) {
        console.error('Error deleting all crawls:', err)
        setError('Failed to delete all crawls. Please try again later.')
      }
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Recent Crawls
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            color="error"
            onClick={handleDeleteAllCrawls}
            disabled={loading || crawls.length === 0}
          >
            Delete All Crawls
          </Button>
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
      </Box>

      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'error.light' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        {loading && <LinearProgress />}
        
        <TableContainer sx={{ maxHeight: 'calc(100vh - 250px)' }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Domain</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Start Time</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {crawls.length === 0 && !loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No crawls found. Start a new crawl to begin collecting content.
                  </TableCell>
                </TableRow>
              ) : (
                crawls.map((crawl) => {
                  const duration = crawl.end_time
                    ? new Date(crawl.end_time) - new Date(crawl.start_time)
                    : crawl.start_time
                    ? new Date() - new Date(crawl.start_time)
                    : 0
                  
                  const formatDuration = (ms) => {
                    if (!ms) return 'N/A'
                    const seconds = Math.floor(ms / 1000)
                    const minutes = Math.floor(seconds / 60)
                    const hours = Math.floor(minutes / 60)
                    return `${hours > 0 ? hours + 'h ' : ''}${minutes % 60}m ${seconds % 60}s`
                  }
                  
                  return (
                    <TableRow key={crawl.crawl_id}>
                      <TableCell>{crawl.domain}</TableCell>
                      <TableCell>
                        <Chip
                          label={crawl.state}
                          color={statusColors[crawl.state] || 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={
                              crawl.state === 'completed'
                                ? 100
                                : crawl.progress.pages_crawled /
                                  (crawl.progress.pages_discovered || 1) * 100
                            }
                            sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                          />
                          <Typography variant="caption">
                            {`${crawl.progress.pages_crawled}/${crawl.progress.pages_discovered || '?'} pages`}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{formatDate(crawl.start_time)}</TableCell>
                      <TableCell>{formatDuration(duration)}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                          <IconButton
                            component={RouterLink}
                            to={`/crawls/${crawl.crawl_id}`}
                            color="info"
                            size="small"
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                          
                          {(crawl.state === 'pending' || crawl.state === 'running') && (
                            <IconButton
                              color="error"
                              size="small"
                              onClick={() => handleCancelCrawl(crawl.crawl_id)}
                            >
                              <CancelIcon fontSize="small" />
                            </IconButton>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={-1} // Unknown total count
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Container>
  )
}

export default CrawlList
