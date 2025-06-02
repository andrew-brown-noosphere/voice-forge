import React, { useState, useEffect } from 'react'
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton, 
  Avatar,
  alpha,
  useTheme,
  Fade,
  Breadcrumbs,
  Link
} from '@mui/material'
import { 
  Menu as MenuIcon,
  Notifications,
  Settings,
  Search,
  ChevronRight
} from '@mui/icons-material'
import { useLocation } from 'react-router-dom'

const ModernAppLayout = ({ 
  children, 
  sidebarOpen, 
  toggleSidebar, 
  title,
  breadcrumbs = []
}) => {
  const theme = useTheme()

  return (
    <Box sx={{ 
      flexGrow: 1,
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      minHeight: '100vh',
      p: 3,
      width: '100%'
    }}>
      {children}
    </Box>
  )
}

export default ModernAppLayout