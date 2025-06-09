import React from 'react'
import { Typography, Box, Alert } from '@mui/material'

export default function TestComponent() {
  return (
    <Box>
      <Alert severity="success" sx={{ mb: 2 }}>
        🎯 THIS IS A TEST - If you see this, hot reload is working!
      </Alert>
      <Typography variant="h4">
        TEST COMPONENT LOADED SUCCESSFULLY
      </Typography>
    </Box>
  )
}
