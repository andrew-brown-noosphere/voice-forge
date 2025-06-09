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
import TrendingUpIcon from '@mui/icons-material/TrendingUp'

const drawerWidth = 240

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
    ]
  },
  {
    section: 'Content Generation',
    items: [
      { text: 'Content Generator', icon: <AutoAwesomeIcon />, path: '/generator' },
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

const AppSidebar = ({ open, toggleDrawer }) => {
  const location = useLocation()

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerWidth,
          boxSizing: 'border-box',
          ...(open === false && {
            width: '64px',
            overflowX: 'hidden',
          }),
          transition: (theme) =>
            theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        {menuItems.map((section) => (
          <React.Fragment key={section.section}>
            {open && (
              <ListSubheader sx={{ bgcolor: 'transparent' }}>
                {section.section}
              </ListSubheader>
            )}
            <List>
              {section.items.map((item) => (
                <ListItem key={item.text} disablePadding>
                  <ListItemButton
                    component={RouterLink}
                    to={item.path}
                    selected={location.pathname === item.path}
                    sx={{ px: 2.5 }}
                  >
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText 
                      primary={item.text} 
                      sx={{ 
                        opacity: open ? 1 : 0,
                        display: open ? 'block' : 'none',
                      }} 
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
            <Divider sx={{ my: 1 }} />
          </React.Fragment>
        ))}
      </Box>

      {open && (
        <Paper 
          elevation={0}
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            p: 2,
            borderTop: '1px solid',
            borderColor: 'divider',
            textAlign: 'center',
            display: open ? 'block' : 'none',
          }}
        >
          <img 
            src="/logo.svg" 
            alt="VoiceForge Logo" 
            style={{ height: '24px', opacity: 0.7 }} 
          />
        </Paper>
      )}
    </Drawer>
  )
}

export default AppSidebar
