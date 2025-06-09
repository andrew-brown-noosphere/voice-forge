import React from 'react'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import {
  Box,
  Drawer,
  Toolbar,
  List,
  Divider,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  ListSubheader,
  Typography,
  alpha,
  useTheme
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import LanguageIcon from '@mui/icons-material/Language'
import SearchIcon from '@mui/icons-material/Search'
import SettingsIcon from '@mui/icons-material/Settings'
import ArticleIcon from '@mui/icons-material/Article'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import FormatQuoteIcon from '@mui/icons-material/FormatQuote'
import DesignServicesIcon from '@mui/icons-material/DesignServices'
import LayersIcon from '@mui/icons-material/Layers'
import PersonIcon from '@mui/icons-material/Person'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import SourceIcon from '@mui/icons-material/Source'
import ScannerIcon from '@mui/icons-material/Scanner'

const drawerWidth = 260

const menuItems = [
  { 
    section: 'General',
    items: [
      { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
      { text: 'Content Search', icon: <SearchIcon />, path: '/content' },
    ]
  },
  {
    section: 'Content Analysis',
    items: [
      { text: 'Recent Analysis', icon: <LanguageIcon />, path: '/crawls' },
      { text: 'New Analysis', icon: <LayersIcon />, path: '/crawls/new' },
    ]
  },
  {
    section: 'Signal Discovery',
    items: [
      { text: 'Social Signals', icon: <TrendingUpIcon />, path: '/signals' },
      { text: 'Signal Sources', icon: <SourceIcon />, path: '/signals/sources' },
      { text: 'Discovery Scan', icon: <ScannerIcon />, path: '/signals/scan' },
    ]
  },
  {
    section: 'Content Generation',
    items: [
      { text: 'Content Generator', icon: <AutoAwesomeIcon />, path: '/generator' },
      { text: 'Persona-Aware Generator', icon: <PersonIcon />, path: '/enhanced-generator' },
      { text: 'Templates', icon: <DesignServicesIcon />, path: '/templates' },
      { text: 'Generated Content', icon: <FormatQuoteIcon />, path: '/generated' },
    ]
  },
  {
    section: 'Settings',
    items: [
      { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
    ]
  }
]

const ModernSidebar = ({ open, toggleDrawer }) => {
  const location = useLocation()
  const theme = useTheme()

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? drawerWidth : 80,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: open ? drawerWidth : 80,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: 'none',
          borderRight: `1px solid ${alpha('#fff', 0.1)}`,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          overflowX: 'hidden',
          overflowY: 'auto'
        },
      }}
    >
      <Toolbar />
      
      {/* Brand Section */}
      <Box sx={{ 
        p: 3, 
        textAlign: 'center',
        display: open ? 'block' : 'none'
      }}>
        <Typography 
          variant="h5" 
          sx={{ 
            fontWeight: 800,
            color: '#fff',
            mb: 1,
            background: 'linear-gradient(45deg, #fff, #f0f0f0)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          🚀 VoiceForge
        </Typography>
        <Typography variant="caption" sx={{ color: alpha('#fff', 0.7) }}>
          AI Content Platform
        </Typography>
      </Box>

      <Box sx={{ flex: 1, px: 1 }}>
        {menuItems.map((section, sectionIndex) => (
          <React.Fragment key={section.section}>
            {open && (
              <ListSubheader 
                sx={{ 
                  bgcolor: 'transparent',
                  color: alpha('#fff', 0.8),
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  px: 2,
                  py: 1,
                  mt: sectionIndex > 0 ? 2 : 1
                }}
              >
                {section.section}
              </ListSubheader>
            )}
            <List dense sx={{ py: 0.5 }}>
              {section.items.map((item) => {
                const isSelected = location.pathname === item.path
                return (
                  <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={RouterLink}
                      to={item.path}
                      selected={isSelected}
                      sx={{ 
                        mx: 1,
                        borderRadius: 3,
                        minHeight: 48,
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        color: alpha('#fff', 0.8),
                        position: 'relative',
                        overflow: 'hidden',
                        '&::before': isSelected ? {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          background: 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%)',
                          borderRadius: 3,
                          backdropFilter: 'blur(10px)'
                        } : {},
                        '&:hover': {
                          background: alpha('#fff', 0.1),
                          transform: 'translateX(4px)',
                          color: '#fff',
                          '& .MuiListItemIcon-root': {
                            transform: 'scale(1.1)',
                            color: '#fff'
                          }
                        },
                        '&.Mui-selected': {
                          background: alpha('#fff', 0.15),
                          color: '#fff',
                          boxShadow: `0 4px 20px ${alpha('#000', 0.1)}`,
                          '&::after': {
                            content: '""',
                            position: 'absolute',
                            left: 0,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            width: '4px',
                            height: '20px',
                            background: 'linear-gradient(180deg, #fff 0%, rgba(255,255,255,0.8) 100%)',
                            borderRadius: '0 2px 2px 0'
                          },
                          '&:hover': {
                            background: alpha('#fff', 0.2)
                          }
                        }
                      }}
                    >
                      <ListItemIcon 
                        sx={{ 
                          color: isSelected ? '#fff' : alpha('#fff', 0.8),
                          minWidth: 40,
                          transition: 'all 0.3s ease',
                          zIndex: 1
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={item.text}
                        primaryTypographyProps={{
                          fontWeight: isSelected ? 600 : 500,
                          fontSize: '0.9rem'
                        }}
                        sx={{ 
                          opacity: open ? 1 : 0,
                          transition: 'opacity 0.3s ease',
                          zIndex: 1
                        }} 
                      />
                    </ListItemButton>
                  </ListItem>
                )
              })}
            </List>
          </React.Fragment>
        ))}
      </Box>

      {/* Footer */}
      {open && (
        <Box
          sx={{
            p: 3,
            borderTop: `1px solid ${alpha('#fff', 0.1)}`,
            background: alpha('#000', 0.1),
            backdropFilter: 'blur(10px)'
          }}
        >
          <Box sx={{ textAlign: 'center' }}>
            <Typography 
              variant="caption" 
              sx={{ 
                color: alpha('#fff', 0.6),
                display: 'block',
                mb: 1
              }}
            >
              Powered by AI
            </Typography>
            <Box
              sx={{
                width: 40,
                height: 2,
                background: 'linear-gradient(90deg, transparent, #fff, transparent)',
                margin: '0 auto',
                borderRadius: 1,
                opacity: 0.3
              }}
            />
          </Box>
        </Box>
      )}
    </Drawer>
  )
}

export default ModernSidebar