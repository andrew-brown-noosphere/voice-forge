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
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import LanguageIcon from '@mui/icons-material/Language'
import SearchIcon from '@mui/icons-material/Search'
import SettingsIcon from '@mui/icons-material/Settings'
import ArticleIcon from '@mui/icons-material/Article'

const drawerWidth = 240

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Recent Crawls', icon: <LanguageIcon />, path: '/dashboard' },
  { text: 'Content Search', icon: <SearchIcon />, path: '/content' },
  { text: 'Content Library', icon: <ArticleIcon />, path: '/content' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
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
        <List>
          {menuItems.map((item, index) => (
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
