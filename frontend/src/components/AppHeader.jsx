import React from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Avatar,
  Box,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import AddIcon from '@mui/icons-material/Add'

const AppHeader = ({ open, toggleDrawer }) => {
  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        transition: (theme) =>
          theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={toggleDrawer}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <Typography
          component={RouterLink}
          to="/"
          variant="h6"
          color="inherit"
          noWrap
          sx={{ flexGrow: 1, textDecoration: 'none' }}
        >
          VoiceForge
        </Typography>

        <Button
          component={RouterLink}
          to="/crawls/new"
          variant="contained"
          color="secondary"
          startIcon={<AddIcon />}
          sx={{ mr: 2 }}
        >
          New Crawl
        </Button>

        <Box sx={{ flexGrow: 0 }}>
          <Avatar
            alt="User"
            src="/user-avatar.png"
            sx={{ width: 32, height: 32 }}
          />
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default AppHeader
