import React, { useState, useEffect } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  Pagination,
  CircularProgress,
  InputAdornment,
  IconButton,
  Stack
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import ClearIcon from '@mui/icons-material/Clear'
import FilterListIcon from '@mui/icons-material/FilterList'
import { format } from 'date-fns'

// API service
import apiService from '../services/api'

const ContentSearch = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [domain, setDomain] = useState('')
  const [contentType, setContentType] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [domains, setDomains] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const limit = 10

  useEffect(() => {
    // Fetch available domains for filtering
    const fetchDomains = async () => {
      try {
        const domainsData = await apiService.listDomains()
        setDomains(domainsData)
      } catch (error) {
        console.error('Failed to fetch domains', error)
      }
    }

    fetchDomains()
  }, [])

  const handleSearch = async () => {
    setLoading(true)
    try {
      const searchResults = await apiService.searchContent(
        searchQuery,
        domain || null,
        contentType || null,
        limit,
        (page - 1) * limit
      )
      setResults(searchResults)
      // In a real implementation, the API would return total count for pagination
      setTotalPages(Math.ceil(searchResults.length / limit) || 1)
      setLoading(false)
    } catch (error) {
      console.error('Search failed', error)
      setResults([])
      setLoading(false)
    }
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setDomain('')
    setContentType('')
    setResults([])
    setPage(1)
  }

  const handlePageChange = (event, value) => {
    setPage(value)
    handleSearch()
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Content Search
      </Typography>
      
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Search Content"
                variant="outlined"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter search query..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: searchQuery && (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setSearchQuery('')} edge="end">
                        <ClearIcon />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch()
                  }
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="domain-select-label">Domain</InputLabel>
                <Select
                  labelId="domain-select-label"
                  id="domain-select"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  label="Domain"
                >
                  <MenuItem value="">
                    <em>All Domains</em>
                  </MenuItem>
                  {domains.map((domain) => (
                    <MenuItem key={domain} value={domain}>
                      {domain}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="content-type-select-label">Content Type</InputLabel>
                <Select
                  labelId="content-type-select-label"
                  id="content-type-select"
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  label="Content Type"
                >
                  <MenuItem value="">
                    <em>All Types</em>
                  </MenuItem>
                  <MenuItem value="blog_post">Blog Post</MenuItem>
                  <MenuItem value="product_description">Product Description</MenuItem>
                  <MenuItem value="about_page">About Page</MenuItem>
                  <MenuItem value="landing_page">Landing Page</MenuItem>
                  <MenuItem value="article">Article</MenuItem>
                  <MenuItem value="news">News</MenuItem>
                  <MenuItem value="press_release">Press Release</MenuItem>
                  <MenuItem value="documentation">Documentation</MenuItem>
                  <MenuItem value="faq">FAQ</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <Button
                  variant="outlined"
                  onClick={handleClearSearch}
                  startIcon={<ClearIcon />}
                >
                  Clear
                </Button>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  disabled={loading}
                  startIcon={<SearchIcon />}
                >
                  Search
                </Button>
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Search Results
              {results.length > 0 && ` (${results.length})`}
            </Typography>
            {domain && (
              <Chip
                label={`Domain: ${domain}`}
                onDelete={() => setDomain('')}
                size="small"
              />
            )}
            {contentType && (
              <Chip
                label={`Type: ${contentType}`}
                onDelete={() => setContentType('')}
                size="small"
              />
            )}
          </Box>
          
          <Divider />
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : results.length > 0 ? (
            <List sx={{ width: '100%' }}>
              {results.map((content) => (
                <ListItem
                  key={content.content_id}
                  alignItems="flex-start"
                  component={RouterLink}
                  to={`/content/${content.content_id}`}
                  sx={{
                    textDecoration: 'none',
                    color: 'inherit',
                    borderRadius: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                  divider
                >
                  <ListItemText
                    primary={
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="subtitle1" component="span" fontWeight="medium">
                          {content.metadata.title || 'Untitled Content'}
                        </Typography>
                        {content.relevance_score !== null && (
                          <Chip
                            label={`Relevance: ${Math.round(content.relevance_score * 100)}%`}
                            size="small"
                            color={
                              content.relevance_score > 0.7
                                ? 'success'
                                : content.relevance_score > 0.4
                                ? 'primary'
                                : 'default'
                            }
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography
                          component="span"
                          variant="body2"
                          color="textPrimary"
                          sx={{
                            display: 'inline',
                            fontWeight: 'bold',
                          }}
                        >
                          {content.domain}
                        </Typography>
                        {' — '}
                        <Typography
                          component="span"
                          variant="body2"
                          color="textSecondary"
                        >
                          {content.metadata.content_type}
                        </Typography>
                        <Typography
                          component="p"
                          variant="body2"
                          color="textSecondary"
                          sx={{
                            mt: 1,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {content.text.substring(0, 200)}...
                        </Typography>
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            mt: 1,
                          }}
                        >
                          <Typography variant="caption" color="textSecondary">
                            {content.metadata.publication_date
                              ? `Published: ${format(
                                  new Date(content.metadata.publication_date),
                                  'MMM d, yyyy'
                                )}`
                              : `Extracted: ${format(
                                  new Date(content.extracted_at),
                                  'MMM d, yyyy'
                                )}`}
                          </Typography>
                          {content.metadata.author && (
                            <Typography variant="caption" color="textSecondary">
                              Author: {content.metadata.author}
                            </Typography>
                          )}
                        </Box>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body1" color="textSecondary" sx={{ py: 4, textAlign: 'center' }}>
              {searchQuery
                ? 'No results found for your search criteria'
                : 'Enter a search query to find content'}
            </Typography>
          )}
          
          {results.length > 0 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default ContentSearch
