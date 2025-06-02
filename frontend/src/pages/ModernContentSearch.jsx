import React, { useState, useEffect } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  MenuItem,
  CircularProgress,
  Pagination,
  Avatar,
  alpha,
  useTheme,
  Fade,
  Zoom,
  Stack
} from '@mui/material'
import {
  Search as SearchIcon,
  Article as ArticleIcon,
  Language as LanguageIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Visibility as VisibilityIcon,
  Category as CategoryIcon
} from '@mui/icons-material'
import { format } from 'date-fns'

// API service
import apiService from '../services/api'

// Modern components
import {
  ModernCard,
  ModernTextField,
  ModernSelect,
  ModernButton,
  ModernSectionHeader
} from '../components/ModernFormComponents'

// Search Result Card Component
const SearchResultCard = ({ content, index }) => {
  const theme = useTheme()
  
  return (
    <Zoom in={true} timeout={300 + index * 100}>
      <ModernCard
        component={RouterLink}
        to={`/content/${content.content_id}`}
        sx={{
          display: 'block',
          textDecoration: 'none',
          color: 'inherit',
          mb: 3,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            width: '4px',
            height: '100%',
            background: `linear-gradient(180deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            opacity: 0,
            transition: 'opacity 0.3s ease'
          },
          '&:hover::before': {
            opacity: 1
          }
        }}
      >
        <Box sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flex: 1 }}>
              <Avatar
                sx={{
                  bgcolor: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 100%)`,
                  color: theme.palette.primary.main,
                  width: 56,
                  height: 56,
                  border: `2px solid ${alpha(theme.palette.primary.main, 0.2)}`
                }}
              >
                <ArticleIcon sx={{ fontSize: 28 }} />
              </Avatar>
              
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 700,
                    mb: 1,
                    color: theme.palette.text.primary,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {content.metadata.title || 'Untitled Content'}
                </Typography>
                
                <Stack direction="row" spacing={1.5} sx={{ flexWrap: 'wrap', gap: 1 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      px: 2,
                      py: 0.5,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`
                    }}
                  >
                    <LanguageIcon sx={{ fontSize: 16, color: theme.palette.primary.main }} />
                    <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
                      {content.domain}
                    </Typography>
                  </Box>
                  
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      px: 2,
                      py: 0.5,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.secondary.main, 0.2)}`
                    }}
                  >
                    <CategoryIcon sx={{ fontSize: 16, color: theme.palette.secondary.main }} />
                    <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.secondary.main }}>
                      {content.metadata.content_type}
                    </Typography>
                  </Box>
                </Stack>
              </Box>
            </Box>
            
            {content.relevance_score !== null && (
              <Box sx={{ textAlign: 'center', minWidth: 100, ml: 2 }}>
                <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Relevance
                </Typography>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontWeight: 800,
                    background: content.relevance_score > 0.7 
                      ? `linear-gradient(45deg, ${theme.palette.success.main}, ${theme.palette.success.light})`
                      : content.relevance_score > 0.4 
                        ? `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`
                        : `linear-gradient(45deg, ${theme.palette.text.secondary}, ${alpha(theme.palette.text.secondary, 0.7)})`,
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}
                >
                  {Math.round(content.relevance_score * 100)}%
                </Typography>
              </Box>
            )}
          </Box>
          
          <Typography
            variant="body1"
            color="textSecondary"
            sx={{
              mb: 3,
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              lineHeight: 1.7,
              fontSize: '1rem'
            }}
          >
            {content.text.substring(0, 300)}...
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Stack direction="row" spacing={3}>
              {content.metadata.publication_date && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ScheduleIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                  <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 500 }}>
                    {format(new Date(content.metadata.publication_date), 'MMM d, yyyy')}
                  </Typography>
                </Box>
              )}
              
              {content.metadata.author && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PersonIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                  <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 500 }}>
                    {content.metadata.author}
                  </Typography>
                </Box>
              )}
            </Stack>
            
            <ModernButton
              size="small"
              variant="outlined"
              startIcon={<VisibilityIcon />}
              sx={{ minWidth: 120 }}
            >
              View Details
            </ModernButton>
          </Box>
        </Box>
      </ModernCard>
    </Zoom>
  )
}

const ModernContentSearch = () => {
  const theme = useTheme()
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
        searchQuery || "",
        domain || null,
        contentType || null,
        limit,
        (page - 1) * limit
      )
      setResults(searchResults)
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
      {/* Header */}
      <ModernSectionHeader
        icon={SearchIcon}
        title="Content Search"
        subtitle="Search through your crawled content with powerful filters"
        color="primary"
      />
      
      {/* Search Panel */}
      <ModernCard sx={{ mb: 4 }}>
        <Box sx={{ p: 4 }}>
          <ModernSectionHeader
            icon={SearchIcon}
            title="Search & Filter"
            color="primary"
          />
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <ModernTextField
                fullWidth
                label="Search Content"
                placeholder="Enter keywords, topics, or phrases..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={SearchIcon}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch()
                  }
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <ModernSelect
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                label="Domain Filter"
                icon={LanguageIcon}
              >
                <MenuItem value="">
                  <em>All Domains</em>
                </MenuItem>
                {domains.map((domainItem) => (
                  <MenuItem key={domainItem} value={domainItem}>
                    {domainItem}
                  </MenuItem>
                ))}
              </ModernSelect>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <ModernSelect
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
                label="Content Type"
                icon={CategoryIcon}
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
              </ModernSelect>
            </Grid>
            
            <Grid item xs={12}>
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <ModernButton
                  variant="outlined"
                  onClick={handleClearSearch}
                  disabled={loading}
                >
                  Clear Filters
                </ModernButton>
                <ModernButton
                  variant="contained"
                  onClick={handleSearch}
                  disabled={loading}
                  gradient={true}
                  glow={true}
                >
                  {loading ? 'Searching...' : 'Search Content'}
                </ModernButton>
              </Stack>
            </Grid>
          </Grid>
        </Box>
      </ModernCard>
      
      {/* Results Section */}
      <ModernCard>
        <Box sx={{ p: 4 }}>
          <ModernSectionHeader
            icon={TrendingUpIcon}
            title="Search Results"
            subtitle={results.length > 0 ? `${results.length} items found` : 'Ready to search'}
            color="success"
            action={
              <Stack direction="row" spacing={1}>
                {domain && (
                  <Box
                    sx={{
                      px: 2,
                      py: 0.5,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
                      Domain: {domain}
                    </Typography>
                  </Box>
                )}
                {contentType && (
                  <Box
                    sx={{
                      px: 2,
                      py: 0.5,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.secondary.main, 0.3)}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.secondary.main }}>
                      Type: {contentType}
                    </Typography>
                  </Box>
                )}
              </Stack>
            }
          />
          
          {loading ? (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              py: 12,
              gap: 3
            }}>
              <CircularProgress size={60} thickness={4} />
              <Typography variant="h6" color="textSecondary" sx={{ fontWeight: 600 }}>
                Searching through your content...
              </Typography>
            </Box>
          ) : results.length > 0 ? (
            <Fade in={true} timeout={600}>
              <Box>
                {results.map((content, index) => (
                  <SearchResultCard 
                    key={content.content_id} 
                    content={content} 
                    index={index}
                  />
                ))}
                
                {totalPages > 1 && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
                    <Pagination
                      count={totalPages}
                      page={page}
                      onChange={handlePageChange}
                      color="primary"
                      size="large"
                      sx={{
                        '& .MuiPaginationItem-root': {
                          borderRadius: 3,
                          fontWeight: 600,
                          background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
                          backdropFilter: 'blur(10px)',
                          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
                          '&:hover': {
                            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`
                          },
                          '&.Mui-selected': {
                            background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                            color: '#fff'
                          }
                        }
                      }}
                    />
                  </Box>
                )}
              </Box>
            </Fade>
          ) : (
            <Box sx={{ 
              textAlign: 'center', 
              py: 12,
              background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.5)} 0%, ${alpha(theme.palette.background.paper, 0.3)} 100%)`,
              borderRadius: 4,
              border: `2px dashed ${alpha(theme.palette.divider, 0.2)}`
            }}>
              <SearchIcon sx={{ fontSize: 100, color: alpha(theme.palette.text.secondary, 0.3), mb: 3 }} />
              <Typography variant="h5" color="textSecondary" sx={{ mb: 2, fontWeight: 600 }}>
                {searchQuery ? 'No results found' : 'Ready to search'}
              </Typography>
              <Typography variant="body1" color="textSecondary">
                {searchQuery
                  ? 'Try adjusting your search terms or filters'
                  : 'Enter keywords above or click Search to see all content'}
              </Typography>
            </Box>
          )}
        </Box>
      </ModernCard>
    </Box>
  )
}

export default ModernContentSearch