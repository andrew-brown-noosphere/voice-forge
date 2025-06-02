import React, { createContext, useContext, useState } from 'react'

// Create context for modern UI state
const ModernUIContext = createContext()

// Hook to use modern UI context
export const useModernUI = () => {
  const context = useContext(ModernUIContext)
  if (!context) {
    throw new Error('useModernUI must be used within a ModernUIProvider')
  }
  return context
}

// Provider component
export const ModernUIProvider = ({ children }) => {
  const [modernUI, setModernUI] = useState(true) // Default to modern UI
  
  const toggleModernUI = () => {
    setModernUI(prev => !prev)
  }
  
  return (
    <ModernUIContext.Provider value={{ modernUI, setModernUI, toggleModernUI }}>
      {children}
    </ModernUIContext.Provider>
  )
}

// Page wrapper component that switches between classic and modern versions
export const PageWrapper = ({ classicComponent: ClassicComponent, modernComponent: ModernComponent, ...props }) => {
  const { modernUI } = useModernUI()
  
  return modernUI && ModernComponent ? (
    <ModernComponent {...props} />
  ) : (
    <ClassicComponent {...props} />
  )
}

export default {
  ModernUIProvider,
  useModernUI,
  PageWrapper
}