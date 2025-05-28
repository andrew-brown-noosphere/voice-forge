import React from 'react'
import { Box, Typography, Alert } from '@mui/material'

const CrawlList = () => {
  console.log('CrawlList component rendered - NO API CALLS')
  
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Crawl List - DISABLED FOR DEBUGGING
      </Typography>
      
      <Alert severity="warning" sx={{ mb: 3 }}>
        All API calls have been completely removed from this component.
        If you're still seeing requests to /crawl, they're coming from somewhere else.
      </Alert>
      
      <Typography variant="body1">
        This CrawlList component is now completely inert - it makes zero API calls.
        Check your backend logs to see if the requests stop.
      </Typography>
    </Box>
  )
}

export default CrawlList
