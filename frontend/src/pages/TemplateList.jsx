import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
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
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Alert,
  Pagination,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import SearchIcon from '@mui/icons-material/Search';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import apiService from '../services/api';

// Platform and tone options (same as in ContentGenerator)
const platforms = [
  { value: 'twitter', label: 'Twitter' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'email', label: 'Email' },
  { value: 'blog', label: 'Blog Post' },
  { value: 'website', label: 'Website' },
  { value: 'customer_support', label: 'Customer Support' },
]

const tones = [
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'informative', label: 'Informative' },
  { value: 'persuasive', label: 'Persuasive' },
  { value: 'authoritative', label: 'Authoritative' },
]

// Common purposes
const purposes = [
  { value: 'promotion', label: 'Promotion' },
  { value: 'announcement', label: 'Announcement' },
  { value: 'engagement', label: 'Engagement' },
  { value: 'support', label: 'Support' },
  { value: 'newsletter', label: 'Newsletter' },
]

const TemplateList = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState('');
  const [toneFilter, setToneFilter] = useState('');
  const [purposeFilter, setPurposeFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const rowsPerPage = 6;

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const data = await apiService.searchTemplates(
        platformFilter || undefined,
        toneFilter || undefined,
        purposeFilter || undefined,
        rowsPerPage,
        (page - 1) * rowsPerPage
      );
      setTemplates(data);
      // Assuming we'd have pagination info from the server in a real app
      setTotalPages(Math.ceil(data.length / rowsPerPage) || 1);
      setError(null);
    } catch (err) {
      console.error('Error fetching templates:', err);
      setError('Failed to load templates. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, [page, platformFilter, toneFilter, purposeFilter]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleCopyTemplate = (templateText) => {
    navigator.clipboard.writeText(templateText);
    // Could add a success toast here
  };

  // Filter templates by search query (client-side filtering)
  const filteredTemplates = templates.filter((template) => {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    return (
      template.name.toLowerCase().includes(query) ||
      template.description?.toLowerCase().includes(query) ||
      template.template_text.toLowerCase().includes(query)
    );
  });

  const getPlatformLabel = (value) => {
    const platform = platforms.find(p => p.value === value);
    return platform ? platform.label : value;
  };
  
  const getToneLabel = (value) => {
    const tone = tones.find(t => t.value === value);
    return tone ? tone.label : value;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Marketing Templates
        </Typography>
        <Button
          component={RouterLink}
          to="/templates/new"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
        >
          New Template
        </Button>
      </Box>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search templates"
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
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel id="platform-filter-label">Platform</InputLabel>
              <Select
                labelId="platform-filter-label"
                value={platformFilter}
                label="Platform"
                onChange={(e) => setPlatformFilter(e.target.value)}
              >
                <MenuItem value="">All Platforms</MenuItem>
                {platforms.map((platform) => (
                  <MenuItem key={platform.value} value={platform.value}>
                    {platform.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel id="tone-filter-label">Tone</InputLabel>
              <Select
                labelId="tone-filter-label"
                value={toneFilter}
                label="Tone"
                onChange={(e) => setToneFilter(e.target.value)}
              >
                <MenuItem value="">All Tones</MenuItem>
                {tones.map((tone) => (
                  <MenuItem key={tone.value} value={tone.value}>
                    {tone.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel id="purpose-filter-label">Purpose</InputLabel>
              <Select
                labelId="purpose-filter-label"
                value={purposeFilter}
                label="Purpose"
                onChange={(e) => setPurposeFilter(e.target.value)}
              >
                <MenuItem value="">All Purposes</MenuItem>
                {purposes.map((purpose) => (
                  <MenuItem key={purpose.value} value={purpose.value}>
                    {purpose.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
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
      ) : filteredTemplates.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No templates found
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            Try adjusting your filters or create a new template.
          </Typography>
          <Button
            component={RouterLink}
            to="/templates/new"
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
          >
            Create Template
          </Button>
        </Paper>
      ) : (
        <>
          <Grid container spacing={3}>
            {filteredTemplates.map((template) => (
              <Grid item xs={12} md={6} lg={4} key={template.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                      <Typography variant="h6" component="h2" noWrap sx={{ maxWidth: '70%' }}>
                        {template.name}
                      </Typography>
                      <Chip 
                        label={getPlatformLabel(template.platform)}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                    
                    <Box display="flex" mb={2} gap={1} flexWrap="wrap">
                      <Chip 
                        label={getToneLabel(template.tone)}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                      <Chip 
                        label={template.purpose}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                    
                    {template.description && (
                      <Typography variant="body2" color="textSecondary" paragraph>
                        {template.description}
                      </Typography>
                    )}
                    
                    <Divider sx={{ my: 1 }} />
                    
                    <Typography variant="body2" sx={{
                      whiteSpace: 'pre-wrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                    }}>
                      {template.template_text}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<EditIcon />}
                      component={RouterLink}
                      to={`/templates/${template.id}`}
                    >
                      Edit
                    </Button>
                    <Button
                      size="small"
                      startIcon={<ContentCopyIcon />}
                      onClick={() => handleCopyTemplate(template.template_text)}
                    >
                      Copy
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          <Box display="flex" justifyContent="center" mt={4}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={handleChangePage}
              color="primary"
            />
          </Box>
        </>
      )}
    </Container>
  );
};

export default TemplateList;
