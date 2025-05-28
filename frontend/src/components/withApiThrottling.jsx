import React, { useState, useEffect, useRef } from 'react'
import { Box, Alert, IconButton } from '@mui/material'
import { Refresh as RefreshIcon } from '@mui/icons-material'

/**
 * Higher-order component that prevents excessive API calls and provides error boundaries
 */
const withApiThrottling = (WrappedComponent, throttleMs = 1000) => {
  return function ThrottledComponent(props) {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const lastCallTime = useRef(0)
    const componentMounted = useRef(true)

    useEffect(() => {
      componentMounted.current = true
      return () => {
        componentMounted.current = false
      }
    }, [])

    const throttledApiCall = async (apiFunction, ...args) => {
      const now = Date.now()
      
      // Throttle API calls
      if (now - lastCallTime.current < throttleMs) {
        console.log(`API call throttled, waiting ${throttleMs - (now - lastCallTime.current)}ms`)
        return
      }

      if (isLoading) {
        console.log('API call already in progress, skipping')
        return
      }

      try {
        setIsLoading(true)
        setError(null)
        lastCallTime.current = now

        if (componentMounted.current) {
          const result = await apiFunction(...args)
          return result
        }
      } catch (err) {
        if (componentMounted.current) {
          // Only show error if it's not an organization/auth error
          if (!err.message?.includes('organization') && !err.message?.includes('401')) {
            setError(err.message)
          }
        }
        throw err
      } finally {
        if (componentMounted.current) {
          setIsLoading(false)
        }
      }
    }

    const clearError = () => setError(null)

    return (
      <Box>
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            action={
              <IconButton color="inherit" size="small" onClick={clearError}>
                <RefreshIcon />
              </IconButton>
            }
          >
            {error}
          </Alert>
        )}
        <WrappedComponent 
          {...props} 
          throttledApiCall={throttledApiCall}
          isApiLoading={isLoading}
        />
      </Box>
    )
  }
}

export default withApiThrottling