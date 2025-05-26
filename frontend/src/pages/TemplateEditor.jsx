import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AddIcon from '@mui/icons-material/Add';
import PreviewIcon from '@mui/icons-material/Preview';
import SaveIcon from '@mui/icons-material/Save';
import apiService from '../services/api';

// Platform and tone options (same as in other components)
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

// Common placeholder examples
const commonPlaceholders = [
  { name: 'topic', description: 'The main topic or subject' },
  { name: 'content', description: 'The main content body' },
  { name: 'key_points', description: 'Key points or bullet points' },
  { name: 'company_name', description: 'Your company name' },
  { name: 'user_name', description: 'User or customer name' },
  { name: 'platform', description: 'Platform name (e.g., Twitter)' },
]

const TemplateEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = !!id;
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    template_text: '',
    platform: '',
    tone: '',
    purpose: '',
    parameters: [],
  });
  
  const [loading, setLoading] = useState(isEditing);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showParameterDialog, setShowParameterDialog] = useState(false);
  const [newParameter, setNewParameter] = useState({
    name: '',
    description: '',
    default_value: '',
  });

  // Fetch template if editing
  useEffect(() => {
    const fetchTemplate = async () => {
      if (!isEditing) return;
      
      try {
        setLoading(true);
        const data = await apiService.getTemplate(id);
        setFormData({
          name: data.name,
          description: data.description || '',
          template_text: data.template_text,
          platform: data.platform,
          tone: data.tone,
          purpose: data.purpose,
          parameters: data.parameters || [],
        });
      } catch (err) {
        console.error('Error fetching template:', err);
        setError('Failed to load template. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchTemplate();
  }, [id, isEditing]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleParameterDialogOpen = () => {
    setShowParameterDialog(true);
    setNewParameter({
      name: '',
      description: '',
      default_value: '',
    });
  };

  const handleAddParameter = () => {
    // Validate parameter
    if (!newParameter.name) return;
    
    // Add parameter to form data
    setFormData(prev => ({
      ...prev,
      parameters: [...prev.parameters, newParameter],
    }));
    
    // Close dialog
    setShowParameterDialog(false);
  };

  const handleRemoveParameter = (index) => {
    setFormData(prev => ({
      ...prev,
      parameters: prev.parameters.filter((_, i) => i !== index),
    }));
  };

  const handleAddCommonPlaceholder = (placeholder) => {
    const placeholderText = `{{${placeholder.name}}}`;
    
    // Insert at cursor position or append to end
    const textArea = document.getElementById('template-text');
    if (textArea) {
      const start = textArea.selectionStart;
      const end = textArea.selectionEnd;
      const text = formData.template_text;
      const newText = text.substring(0, start) + placeholderText + text.substring(end);
      
      setFormData(prev => ({
        ...prev,
        template_text: newText,
      }));
      
      // Set cursor position after inserted placeholder
      setTimeout(() => {
        textArea.focus();
        textArea.setSelectionRange(start + placeholderText.length, start + placeholderText.length);
      }, 10);
    } else {
      // Fallback if element not found
      setFormData(prev => ({
        ...prev,
        template_text: prev.template_text + placeholderText,
      }));
    }
  };

  const handleSave = async () => {
    // Validate form
    if (!formData.name || !formData.template_text || !formData.platform || !formData.tone || !formData.purpose) {
      setError('Please fill in all required fields');
      return;
    }
    
    try {
      setSaving(true);
      setError(null);
      
      // Create or update template
      const templateData = {
        ...formData,
        id: isEditing ? id : undefined,
      };
      
      await apiService.createTemplate(templateData);
      
      // Navigate back to templates list
      navigate('/templates');
    } catch (err) {
      console.error('Error saving template:', err);
      setError('Failed to save template. Please try again later.');
    } finally {
      setSaving(false);
    }
  };

  const renderPreview = () => {
    // Generate preview by replacing placeholders with their default values
    let previewText = formData.template_text;
    
    formData.parameters.forEach(param => {
      const placeholder = `{{${param.name}}}`;
      const value = param.default_value || `[${param.name}]`;
      previewText = previewText.replace(new RegExp(placeholder, 'g'), value);
    });
    
    // Replace any remaining placeholders
    previewText = previewText.replace(/{{(\w+)}}/g, '[$1]');
    
    return previewText;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/templates')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          {isEditing ? 'Edit Template' : 'New Template'}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Template Details
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  label="Template Name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  fullWidth
                  required
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  fullWidth
                  multiline
                  rows={2}
                />
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth required>
                  <InputLabel id="platform-label">Platform</InputLabel>
                  <Select
                    labelId="platform-label"
                    name="platform"
                    value={formData.platform}
                    label="Platform"
                    onChange={handleChange}
                  >
                    {platforms.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth required>
                  <InputLabel id="tone-label">Tone</InputLabel>
                  <Select
                    labelId="tone-label"
                    name="tone"
                    value={formData.tone}
                    label="Tone"
                    onChange={handleChange}
                  >
                    {tones.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth required>
                  <InputLabel id="purpose-label">Purpose</InputLabel>
                  <Select
                    labelId="purpose-label"
                    name="purpose"
                    value={formData.purpose}
                    label="Purpose"
                    onChange={handleChange}
                  >
                    {purposes.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  id="template-text"
                  label="Template Text"
                  name="template_text"
                  value={formData.template_text}
                  onChange={handleChange}
                  fullWidth
                  multiline
                  rows={8}
                  required
                  placeholder="Write your template here. Use {{placeholder}} syntax for dynamic content."
                  helperText="Use {{placeholder}} syntax for dynamic content. E.g., 'Hello {{user_name}}!'"
                />
              </Grid>
            </Grid>
          </Paper>
          
          <Box display="flex" justifyContent="space-between">
            <Button
              variant="outlined"
              startIcon={<PreviewIcon />}
              onClick={() => setShowPreview(true)}
              disabled={!formData.template_text}
            >
              Preview
            </Button>
            
            <Button
              variant="contained"
              color="primary"
              startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
              onClick={handleSave}
              disabled={saving}
            >
              Save Template
            </Button>
          </Box>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Template Parameters
              </Typography>
              <Button
                startIcon={<AddIcon />}
                size="small"
                onClick={handleParameterDialogOpen}
              >
                Add
              </Button>
            </Box>
            
            {formData.parameters.length === 0 ? (
              <Typography color="textSecondary" variant="body2" sx={{ py: 2 }}>
                No parameters defined. Add parameters to make your template dynamic.
              </Typography>
            ) : (
              <List dense>
                {formData.parameters.map((param, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => handleRemoveParameter(index)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center">
                          <Chip
                            label={`{{${param.name}}}`}
                            size="small"
                            color="primary"
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="body2">{param.description}</Typography>
                        </Box>
                      }
                      secondary={param.default_value ? `Default: ${param.default_value}` : null}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
          
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Common Placeholders
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Click to insert at cursor position:
            </Typography>
            
            <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
              {commonPlaceholders.map((placeholder) => (
                <Chip
                  key={placeholder.name}
                  label={`{{${placeholder.name}}}`}
                  onClick={() => handleAddCommonPlaceholder(placeholder)}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body2" color="textSecondary">
              Template variables use the syntax: <code>&#123;&#123;variable_name&#125;&#125;</code>
            </Typography>
          </Paper>
        </Grid>
      </Grid>
      
      {/* Parameter Dialog */}
      <Dialog open={showParameterDialog} onClose={() => setShowParameterDialog(false)}>
        <DialogTitle>Add Parameter</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ pt: 1 }}>
            <Grid item xs={12}>
              <TextField
                label="Parameter Name"
                value={newParameter.name}
                onChange={(e) => setNewParameter(prev => ({ ...prev, name: e.target.value }))}
                fullWidth
                required
                helperText="Used in template as {{parameter_name}}"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={newParameter.description}
                onChange={(e) => setNewParameter(prev => ({ ...prev, description: e.target.value }))}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Default Value"
                value={newParameter.default_value}
                onChange={(e) => setNewParameter(prev => ({ ...prev, default_value: e.target.value }))}
                fullWidth
                helperText="Used in preview and as fallback"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowParameterDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddParameter}
            variant="contained" 
            disabled={!newParameter.name}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Preview Dialog */}
      <Dialog 
        open={showPreview} 
        onClose={() => setShowPreview(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Template Preview
          {formData.platform && (
            <Chip 
              label={platforms.find(p => p.value === formData.platform)?.label || formData.platform}
              size="small"
              color="primary"
              sx={{ ml: 1 }}
            />
          )}
          {formData.tone && (
            <Chip 
              label={tones.find(t => t.value === formData.tone)?.label || formData.tone}
              size="small"
              color="secondary"
              sx={{ ml: 1 }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="body1" component="pre" sx={{ 
                whiteSpace: 'pre-wrap',
                fontSize: '1rem',
                fontFamily: 'inherit',
                p: 1,
              }}>
                {renderPreview()}
              </Typography>
            </CardContent>
          </Card>
          
          <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
            Note: Placeholders are shown with default values or as [placeholder_name].
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TemplateEditor;
