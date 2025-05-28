import React from 'react'
import { useOrganization, useUser } from '@clerk/clerk-react'
import { 
  Box, 
  Typography, 
  CircularProgress
} from '@mui/material'
import OnboardingPage from '../pages/OnboardingPage'

/**
 * OrganizationGate - Ensures user has organization access before showing main app
 * 
 * This component acts as a gate that:
 * 1. Checks if user has an active organization
 * 2. If not, shows organization creation flow
 * 3. Only renders children when user has org access
 */
const OrganizationGate = ({ children }) => {
  const { organization, isLoaded: orgLoaded } = useOrganization()
  const { user, isLoaded: userLoaded } = useUser()

  // Show loading while Clerk loads organization data
  if (!orgLoaded || !userLoaded) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        flexDirection: 'column',
        gap: 2
      }}>
        <CircularProgress />
        <Typography color="textSecondary">
          Loading organization...
        </Typography>
      </Box>
    )
  }

  // If user has an organization, render the main app
  if (organization) {
    return children
  }

  // If no organization, show the onboarding page
  return <OnboardingPage />
}

export default OrganizationGate