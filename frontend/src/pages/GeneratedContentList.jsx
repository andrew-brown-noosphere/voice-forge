import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Menu,
  MenuItem,
  Tabs,
  Tab,
  Pagination,
  Alert,
  ButtonGroup,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import InfoIcon from '@mui/icons-material/Info';
import ShareIcon from '@mui/icons-material/Share';
import EditIcon from '@mui/icons-material/Edit';
import TwitterIcon from '@mui/icons-material/Twitter';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import InstagramIcon from '@mui/icons-material/Instagram';
import EmailIcon from '@mui/icons-material/Email';
import ForumIcon from '@mui/icons-material/Forum';
import WebIcon from '@mui/icons-material/Web';
import MessageIcon from '@mui/icons-material/Message';

// This is a mock implementation since we don't have the actual API yet
// In a real app, this would be fetched from the server
const mockGeneratedContent = [
  {
    id: '1',
    text: "✨ Introducing our new AI-powered analytics dashboard! It provides real-time insights, customizable reports, and predictive analytics to help you make data-driven decisions faster. Learn more at our website. #analytics #datascience",
    platform: 'twitter',
    tone: 'enthusiastic',
    generated_at: '2025-05-18T08:30:00Z',
    query: 'Write a tweet about our new analytics dashboard',
    source_chunks: [
      { 
        chunk_id: 'c1', 
        text: 'Our new analytics dashboard provides real-time insights and customizable reports.',
        similarity: 0.89,
        content_id: 'd1'
      },
      { 
        chunk_id: 'c2', 
        text: 'The AI-powered analytics solution helps users make data-driven decisions faster.',
        similarity: 0.82,
        content_id: 'd2'
      },
    ]
  },
  {
    id: '2',
    text: "Company Update: Q2 Financial Results\n\nWe're pleased to announce that our Q2 financial results exceeded expectations, with a 28% year-over-year revenue growth and significant expansion in international markets. This success stems from our strategic investments in product development and customer experience improvements.\n\nLearn more about how we're innovating in this space. #financialresults #growth",
    platform: 'linkedin',
    tone: 'professional',
    generated_at: '2025-05-17T14:45:00Z',
    query: 'Write a LinkedIn post about our Q2 financial results',
    source_chunks: [
      { 
        chunk_id: 'c3', 
        text: 'Q2 financial results exceeded expectations with 28% YoY revenue growth.',
        similarity: 0.95,
        content_id: 'd3'
      },
      { 
        chunk_id: 'c4', 
        text: 'Significant expansion in international markets due to strategic investments.',
        similarity: 0.87,
        content_id: 'd3'
      },
    ]
  },
  {
    id: '3',
    text: "Subject: Exciting New Features Coming Next Month - Early Access Available\n\nHello,\n\nWe hope this email finds you well. Here's the latest on our upcoming features:\n\n- Advanced data visualization options\n- Streamlined workflow automation\n- Enhanced collaboration tools\n- Improved mobile experience\n\nWant to learn more? Join our webinar next Tuesday at 2 PM EST or reply to this email for early access.\n\nBest regards,\nThe Team",
    platform: 'email',
    tone: 'friendly',
    generated_at: '2025-05-16T11:20:00Z',
    query: 'Write an email about upcoming features with early access',
    source_chunks: [
      { 
        chunk_id: 'c5', 
        text: 'New features coming next month include advanced data visualization and streamlined workflow automation.',
        similarity: 0.91,
        content_id: 'd4'
      },
      { 
        chunk_id: 'c6', 
        text: 'Early access is available by joining the webinar or replying to the email.',
        similarity: 0.85,
        content_id: 'd4'
      },
    ]
  },
  {
    id: '4',
    text: "✨ New sustainable packaging line ✨\n\nWe're so excited to share our new eco-friendly packaging made from 100% recycled materials! Not only is it better for the environment, but it looks amazing too. Swipe to see all the color options!\n\n.\n.\n.\n#sustainability #ecofriendly #recycled #newproduct",
    platform: 'instagram',
    tone: 'casual',
    generated_at: '2025-05-15T09:10:00Z',
    query: 'Instagram post about our new sustainable packaging',
    source_chunks: [
      { 
        chunk_id: 'c7', 
        text: 'New eco-friendly packaging line made from 100% recycled materials.',
        similarity: 0.93,
        content_id: 'd5'
      },
      { 
        chunk_id: 'c8', 
        text: 'The sustainable packaging comes in multiple color options.',
        similarity: 0.79,
        content_id: 'd5'
      },
    ]
  },
  {
    id: '5',
    text: "Hi there,\n\nThank you for reaching out about the export functionality issue. I understand how important this is for your workflow.\n\nI've checked your account and can confirm that this is a known issue affecting a small number of users. Our engineering team is working on a fix that will be deployed within the next 24 hours.\n\nIn the meantime, you can use the workaround of saving your report as a PDF and then converting it using our online tool at tools.ourcompany.com/converter.\n\nPlease let me know if you have any other questions. We're here to help!\n\nBest regards,\nCustomer Support Team",
    platform: 'customer_support',
    tone: 'helpful',
    generated_at: '2025-05-14T16:35:00Z',
    query: 'Response to customer having issues with export functionality',
    source_chunks: [
      { 
        chunk_id: 'c9', 
        text: 'Export functionality issue is affecting a small number of users and will be fixed within 24 hours.',
        similarity: 0.96,
        content_id: 'd6'
      },
      { 
        chunk_id: 'c10', 
        text: 'Workaround: save as PDF and convert using the online tool at tools.ourcompany.com/converter.',
        similarity: 0.88,
        content_id: 'd6'
      },
    ]
  },
];

// Platform icons mapping
const platformIcons = {
  twitter: <TwitterIcon />,
  linkedin: <LinkedInIcon />,
  instagram: <InstagramIcon />,
  facebook: <MessageIcon />,
  email: <EmailIcon />,
  blog: <ForumIcon />,
  website: <WebIcon />,
  customer_support: <MessageIcon />,
};

// Platform color mapping
const platformColors = {
  twitter: '#1DA1F2',
  linkedin: '#0A66C2',
  facebook: '#1877F2',
  instagram: '#E4405F',
  email: '#D44638',
  blog: '#FF5722',
  website: '#2196F3',
  customer_support: '#4CAF50',
};

const GeneratedContentList = () => {
  const [generatedContent, setGeneratedContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [selectedContent, setSelectedContent] = useState(null);
  const [showSourcesDialog, setShowSourcesDialog] = useState(false);
  const [page, setPage] = useState(1);
  const [anchorEl, setAnchorEl] = useState(null);
  const [activeItemId, setActiveItemId] = useState(null);
  
  const rowsPerPage = 6;

  // Simulate fetching data from API
  useEffect(() => {
    const fetchGeneratedContent = async () => {
      try {
        setLoading(true);
        // In a real app, this would be an API call
        setTimeout(() => {
          setGeneratedContent(mockGeneratedContent);
          setLoading(false);
        }, 1000);
      } catch (err) {
        console.error('Error fetching generated content:', err);
        setError('Failed to load generated content. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchGeneratedContent();
  }, []);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleOpenMenu = (event, id) => {
    setAnchorEl(event.currentTarget);
    setActiveItemId(id);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setActiveItemId(null);
  };

  const handleCopyContent = (text) => {
    navigator.clipboard.writeText(text);
    handleCloseMenu();
    // Could add a success toast here
  };

  const handleViewSources = (content) => {
    setSelectedContent(content);
    setShowSourcesDialog(true);
    handleCloseMenu();
  };

  const handleDelete = (id) => {
    // In a real app, this would be an API call
    setGeneratedContent(generatedContent.filter(item => item.id !== id));
    handleCloseMenu();
  };

  // Filter content by platform and search query
  const filteredContent = generatedContent.filter((content) => {
    const matchesPlatform = platformFilter === 'all' || content.platform === platformFilter;
    const matchesSearch = !searchQuery || 
      content.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      content.query.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesPlatform && matchesSearch;
  });

  // Paginate content
  const paginatedContent = filteredContent.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Generated Content
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Search generated content"
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Tabs
              value={platformFilter}
              onChange={(e, newValue) => setPlatformFilter(newValue)}
              variant="scrollable"
              scrollButtons="auto"
              aria-label="platform filter tabs"
            >
              <Tab label="All" value="all" />
              <Tab 
                label="Twitter" 
                value="twitter" 
                icon={<TwitterIcon />} 
                iconPosition="start"
              />
              <Tab 
                label="LinkedIn" 
                value="linkedin" 
                icon={<LinkedInIcon />} 
                iconPosition="start"
              />
              <Tab 
                label="Email" 
                value="email" 
                icon={<EmailIcon />} 
                iconPosition="start"
              />
            </Tabs>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : filteredContent.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No content found
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            {searchQuery || platformFilter !== 'all'
              ? 'Try adjusting your filters or search query.'
              : 'Generate new content using the Content Generator.'}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            href="/generator"
          >
            Generate New Content
          </Button>
        </Paper>
      ) : (
        <>
          <Grid container spacing={3}>
            {paginatedContent.map((content) => (
              <Grid item xs={12} md={6} key={content.id}>
                <Card sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  borderLeft: `4px solid ${platformColors[content.platform] || '#ccc'}`,
                }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                      <Box display="flex" alignItems="center">
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {platformIcons[content.platform] || <WebIcon />}
                        </ListItemIcon>
                        <Chip 
                          label={content.platform}
                          size="small"
                        />
                        <Chip 
                          label={content.tone}
                          size="small"
                          color="secondary"
                          variant="outlined"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                      <Typography variant="caption" color="textSecondary">
                        {formatDate(content.generated_at)}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Query: "{content.query}"
                    </Typography>
                    
                    <Divider sx={{ my: 1 }} />
                    
                    <Typography variant="body1" component="div" sx={{
                      whiteSpace: 'pre-wrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      maxHeight: '120px',
                    }}>
                      {content.text}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'space-between' }}>
                    <ButtonGroup size="small" variant="outlined">
                      <Button
                        onClick={() => handleCopyContent(content.text)}
                        startIcon={<ContentCopyIcon />}
                      >
                        Copy
                      </Button>
                      <Button
                        onClick={() => handleViewSources(content)}
                        startIcon={<InfoIcon />}
                      >
                        Sources
                      </Button>
                    </ButtonGroup>
                    
                    <IconButton
                      aria-label="more actions"
                      onClick={(e) => handleOpenMenu(e, content.id)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          <Box display="flex" justifyContent="center" mt={4}>
            <Pagination
              count={Math.ceil(filteredContent.length / rowsPerPage)}
              page={page}
              onChange={handleChangePage}
              color="primary"
            />
          </Box>
        </>
      )}

      {/* Context menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
      >
        <MenuItem onClick={() => {
          const content = generatedContent.find(c => c.id === activeItemId);
          if (content) handleCopyContent(content.text);
        }}>
          <ListItemIcon>
            <ContentCopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Copy to Clipboard</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          const content = generatedContent.find(c => c.id === activeItemId);
          if (content) handleViewSources(content);
        }}>
          <ListItemIcon>
            <InfoIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Sources</ListItemText>
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <ShareIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Share</ListItemText>
        </MenuItem>
        <MenuItem>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit & Regenerate</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => handleDelete(activeItemId)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Sources Dialog */}
      <Dialog
        open={showSourcesDialog}
        onClose={() => setShowSourcesDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Source Content</DialogTitle>
        <DialogContent>
          {selectedContent && (
            <>
              <Typography variant="subtitle2" gutterBottom>
                Original Query: "{selectedContent.query}"
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom>
                Generated Content:
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
                <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
                  {selectedContent.text}
                </Typography>
              </Paper>
              
              <Typography variant="h6" gutterBottom>
                Source References:
              </Typography>
              <List>
                {selectedContent.source_chunks.map((chunk, index) => (
                  <ListItem key={index} divider={index < selectedContent.source_chunks.length - 1}>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="subtitle2">
                            Source {index + 1}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            Relevance: {(chunk.similarity * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {chunk.text}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSourcesDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default GeneratedContentList;
