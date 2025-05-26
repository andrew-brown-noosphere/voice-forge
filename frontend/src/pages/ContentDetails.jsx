import React, { useState, useEffect } from 'react'
import { useParams, Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Paper,
  Link,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Alert,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import DescriptionIcon from '@mui/icons-material/Description'
import CodeIcon from '@mui/icons-material/Code'
import InfoIcon from '@mui/icons-material/Info'
import ViewStreamIcon from '@mui/icons-material/ViewStream'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import { format } from 'date-fns'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

// API service
import apiService from '../services/api'

// TabPanel component
function TabPanel(props) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`content-tabpanel-${index}`}
      aria-labelledby={`content-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

const ContentDetails = () => {
  const { id } = useParams()
  const [content, setContent] = useState(null)
  const [chunks, setChunks] = useState([])
  const [loading, setLoading] = useState(true)
  const [chunksLoading, setChunksLoading] = useState(false)
  const [processingChunks, setProcessingChunks] = useState(false)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const contentData = await apiService.getContent(id)
        setContent(contentData)
        setLoading(false)
        
        // Try to fetch chunks if content exists
        fetchChunks()
      } catch (error) {
        console.error('Failed to fetch content', error)
        setError('Failed to fetch content')
        setLoading(false)
      }
    }
    
    const fetchChunks = async () => {
      try {
        setChunksLoading(true)
        const chunksData = await apiService.getContentChunks(id)
        setChunks(chunksData)
        setChunksLoading(false)
      } catch (error) {
        console.error('Failed to fetch chunks', error)
        // Don't set error for chunks - they might not exist yet
        setChunksLoading(false)
      }
    }

    fetchContent()
  }, [id])

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue)
  }
  
  const handleProcessContent = async () => {
    try {
      setProcessingChunks(true)
      await apiService.processContentForRag(id)
      // Add a delay to allow processing to start
      setTimeout(async () => {
        try {
          const chunksData = await apiService.getContentChunks(id)
          setChunks(chunksData)
        } catch (error) {
          console.error('Failed to fetch chunks after processing', error)
        } finally {
          setProcessingChunks(false)
        }
      }, 2000)
    } catch (error) {
      console.error('Failed to process content', error)
      setProcessingChunks(false)
    }
  }

  const handleGenerateContent = () => {
    // Navigate to content generator with pre-filled values
    if (content) {
      const url = `/generator?content_id=${content.content_id}&domain=${content.domain}`
      window.location.href = url
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

  if (!content) {
    return (
      <Alert severity="warning" sx={{ mb: 3 }}>
        Content not found
      </Alert>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Button
          component={RouterLink}
          to="/content"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          Back to Search
        </Button>
        
        <Box>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateContent}
            startIcon={<AutoAwesomeIcon />}
            sx={{ mr: 2 }}
          >
            Generate Content
          </Button>
          
          <Button
            variant="outlined"
            href={content.url}
            target="_blank"
            rel="noopener noreferrer"
            endIcon={<OpenInNewIcon />}
          >
            View Original
          </Button>
        </Box>
      </Box>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom>
            {content.metadata.title || 'Untitled Content'}
          </Typography>
          
          <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip 
              label={content.domain} 
              color="primary" 
              size="small" 
            />
            <Chip 
              label={content.metadata.content_type} 
              size="small" 
            />
            {content.metadata.language && (
              <Chip 
                label={`Language: ${content.metadata.language}`} 
                size="small" 
              />
            )}
          </Box>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" component="div" color="textSecondary">
              <Grid container spacing={2}>
                {content.metadata.author && (
                  <Grid item>
                    <strong>Author:</strong> {content.metadata.author}
                  </Grid>
                )}
                
                {content.metadata.publication_date && (
                  <Grid item>
                    <strong>Published:</strong>{' '}
                    {format(new Date(content.metadata.publication_date), 'MMM d, yyyy')}
                  </Grid>
                )}
                
                <Grid item>
                  <strong>Extracted:</strong>{' '}
                  {format(new Date(content.extracted_at), 'MMM d, yyyy HH:mm')}
                </Grid>
              </Grid>
            </Typography>
          </Box>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" component="div">
              <strong>URL:</strong>{' '}
              <Link href={content.url} target="_blank" rel="noopener noreferrer">
                {content.url}
              </Link>
            </Typography>
          </Box>
          
          {content.metadata.categories && content.metadata.categories.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="div">
                <strong>Categories:</strong>{' '}
                {content.metadata.categories.map((category) => (
                  <Chip 
                    key={category} 
                    label={category} 
                    size="small" 
                    sx={{ mr: 0.5, mb: 0.5 }} 
                  />
                ))}
              </Typography>
            </Box>
          )}
          
          {content.metadata.tags && content.metadata.tags.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="div">
                <strong>Tags:</strong>{' '}
                {content.metadata.tags.map((tag) => (
                  <Chip 
                    key={tag} 
                    label={tag} 
                    size="small" 
                    sx={{ mr: 0.5, mb: 0.5 }} 
                  />
                ))}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
      
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="content tabs">
            <Tab icon={<DescriptionIcon />} iconPosition="start" label="Content" />
            <Tab icon={<ViewStreamIcon />} iconPosition="start" label="Chunks" />
            <Tab icon={<CodeIcon />} iconPosition="start" label="HTML" />
            <Tab icon={<InfoIcon />} iconPosition="start" label="Metadata" />
          </Tabs>
        </Box>
        
        {/* Content Tab */}
        <TabPanel value={tabValue} index={0}>
          <Paper elevation={0} sx={{ p: 2, whiteSpace: 'pre-line' }}>
            {content.text.split('\n').map((paragraph, index) => (
              paragraph ? (
                <Typography key={index} paragraph>
                  {paragraph}
                </Typography>
              ) : <br key={index} />
            ))}
          </Paper>
        </TabPanel>
        
        {/* Chunks Tab */}
        <TabPanel value={tabValue} index={1}>
          {chunksLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : chunks.length > 0 ? (
            <>
              <Typography variant="h6" gutterBottom>
                Content Chunks ({chunks.length})
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                This content has been processed into chunks for retrieval-augmented generation (RAG).
                Each chunk is indexed independently for more precise retrieval.
              </Typography>
              
              {chunks.map((chunk, index) => (
                <Accordion key={chunk.id} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" justifyContent="space-between" width="100%" alignItems="center">
                      <Typography variant="subtitle1">
                        Chunk {index + 1}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" sx={{ mr: 2 }}>
                        {`Characters ${chunk.start_char}-${chunk.end_char}`}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Paper elevation={0} variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                      <Typography variant="body1">
                        {chunk.text}
                      </Typography>
                    </Paper>
                    
                    {chunk.metadata && (
                      <Box mt={2}>
                        <Typography variant="subtitle2" gutterBottom>
                          Chunk Metadata:
                        </Typography>
                        <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                          <Table size="small">
                            <TableBody>
                              {Object.entries(chunk.metadata).map(([key, value]) => (
                                <TableRow key={key}>
                                  <TableCell component="th" scope="row" width="30%">
                                    <strong>{key}</strong>
                                  </TableCell>
                                  <TableCell>
                                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Box>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))}
            </>
          ) : (
            <Box textAlign="center" p={3}>
              <Typography variant="h6" gutterBottom>
                Content not yet processed for RAG
              </Typography>
              <Typography paragraph color="textSecondary">
                This content hasn't been processed into chunks for retrieval-augmented generation.
                Processing will split the content into semantic chunks and generate embeddings.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={handleProcessContent}
                disabled={processingChunks}
                startIcon={processingChunks ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
              >
                {processingChunks ? 'Processing...' : 'Process for RAG'}
              </Button>
              
              {processingChunks && (
                <Box sx={{ width: '100%', mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                    Processing content into chunks. This may take a moment...
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </TabPanel>
        
        {/* HTML Tab */}
        <TabPanel value={tabValue} index={2}>
          {content.html ? (
            <SyntaxHighlighter language="html" style={atomDark} wrapLines showLineNumbers>
              {content.html}
            </SyntaxHighlighter>
          ) : (
            <Alert severity="info">HTML content not available</Alert>
          )}
        </TabPanel>
        
        {/* Metadata Tab */}
        <TabPanel value={tabValue} index={3}>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableBody>
                <TableRow>
                  <TableCell component="th" scope="row" width="30%">
                    <strong>Content ID</strong>
                  </TableCell>
                  <TableCell>{content.content_id}</TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Crawl ID</strong>
                  </TableCell>
                  <TableCell>
                    <Link component={RouterLink} to={`/crawls/${content.crawl_id}`}>
                      {content.crawl_id}
                    </Link>
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Domain</strong>
                  </TableCell>
                  <TableCell>{content.domain}</TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Content Type</strong>
                  </TableCell>
                  <TableCell>{content.metadata.content_type}</TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Language</strong>
                  </TableCell>
                  <TableCell>{content.metadata.language || 'Not detected'}</TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Author</strong>
                  </TableCell>
                  <TableCell>{content.metadata.author || 'Not available'}</TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Publication Date</strong>
                  </TableCell>
                  <TableCell>
                    {content.metadata.publication_date
                      ? format(new Date(content.metadata.publication_date), 'MMM d, yyyy')
                      : 'Not available'}
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Last Modified</strong>
                  </TableCell>
                  <TableCell>
                    {content.metadata.last_modified
                      ? format(new Date(content.metadata.last_modified), 'MMM d, yyyy')
                      : 'Not available'}
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Extracted</strong>
                  </TableCell>
                  <TableCell>
                    {format(new Date(content.extracted_at), 'MMM d, yyyy HH:mm:ss')}
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Categories</strong>
                  </TableCell>
                  <TableCell>
                    {content.metadata.categories && content.metadata.categories.length > 0
                      ? content.metadata.categories.join(', ')
                      : 'None'}
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>Tags</strong>
                  </TableCell>
                  <TableCell>
                    {content.metadata.tags && content.metadata.tags.length > 0
                      ? content.metadata.tags.join(', ')
                      : 'None'}
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell component="th" scope="row">
                    <strong>RAG Status</strong>
                  </TableCell>
                  <TableCell>
                    {chunks.length > 0 
                      ? `Processed (${chunks.length} chunks)` 
                      : 'Not processed for RAG'}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Card>
    </Box>
  )
}

export default ContentDetails
