import React from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Typography,
  Button,
  Container,
  Paper,
  Grid
} from '@mui/material'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import HomeIcon from '@mui/icons-material/Home'

const NotFound = () => {
  return (
    <Container maxWidth="md">
      <Paper
        elevation={3}
        sx={{
          py: 6,
          px: 4,
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 100, color: 'text.secondary', mb: 2 }} />
        
        <Typography variant="h3" component="h1" gutterBottom>
          404 - Page Not Found
        </Typography>
        
        <Typography variant="body1" paragraph color="text.secondary">
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        
        <Grid container spacing={2} justifyContent="center" sx={{ mt: 3 }}>
          <Grid item>
            <Button
              component={RouterLink}
              to="/"
              variant="contained"
              color="primary"
              startIcon={<HomeIcon />}
            >
              Back to Dashboard
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  )
}

export default NotFound
