import React, { useState } from 'react'
import {
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Box,
  Typography,
  Avatar,
  IconButton,
  InputAdornment,
  Alert,
  Paper,
  alpha,
  useTheme,
  Fade,
  Zoom
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Clear as ClearIcon,
  Add as AddIcon
} from '@mui/icons-material'

// Enhanced Glassmorphism Card
export const ModernCard = ({ 
  children, 
  hover = true, 
  gradient,
  sx = {}, 
  ...props 
}) => {
  const theme = useTheme()
  
  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.95)} 0%, ${alpha(theme.palette.background.paper, 0.8)} 100%)`,
        backdropFilter: 'blur(8px)',
        border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
        borderRadius: 4,
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          opacity: 0,
          transition: 'opacity 0.3s ease'
        },
        ...(hover && {
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: `0 12px 40px ${alpha(theme.palette.primary.main, 0.12)}`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.25)}`,
            '&::before': {
              opacity: 1
            }
          }
        }),
        ...sx
      }}
      {...props}
    >
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        {children}
      </Box>
    </Card>
  )
}

// Modern Text Field
export const ModernTextField = ({ 
  icon: Icon,
  type = 'text',
  sx = {},
  ...props 
}) => {
  const theme = useTheme()
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  
  return (
    <TextField
      type={isPassword && showPassword ? 'text' : type}
      InputProps={{
        startAdornment: Icon && (
          <InputAdornment position="start">
            <Icon sx={{ color: theme.palette.primary.main, fontSize: 20 }} />
          </InputAdornment>
        ),
        endAdornment: isPassword && (
          <InputAdornment position="end">
            <IconButton
              onClick={() => setShowPassword(!showPassword)}
              edge="end"
              sx={{ color: theme.palette.text.secondary }}
            >
              {showPassword ? <VisibilityOff /> : <Visibility />}
            </IconButton>
          </InputAdornment>
        ),
        ...props.InputProps
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: 3,
          background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
          backdropFilter: 'blur(4px)',
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.9)} 0%, ${alpha(theme.palette.background.paper, 0.7)} 100%)`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
            boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.1)}`
          },
          '&.Mui-focused': {
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.95)} 0%, ${alpha(theme.palette.background.paper, 0.8)} 100%)`,
            border: `1px solid ${theme.palette.primary.main}`,
            boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
          },
          '& fieldset': {
            border: 'none'
          }
        },
        '& .MuiInputLabel-root': {
          color: theme.palette.text.secondary,
          fontWeight: 500,
          '&.Mui-focused': {
            color: theme.palette.primary.main
          }
        },
        ...sx
      }}
      {...props}
    />
  )
}

// Modern Select Field
export const ModernSelect = ({ 
  label,
  value,
  onChange,
  options = [],
  icon: Icon,
  size = 'medium',
  sx = {},
  ...props 
}) => {
  const theme = useTheme()
  
  return (
    <FormControl fullWidth size={size} sx={sx}>
      <InputLabel sx={{ color: theme.palette.text.secondary, fontWeight: 500 }}>
        {label}
      </InputLabel>
      <Select
        value={value}
        onChange={onChange}
        label={label}
        startAdornment={Icon && (
          <InputAdornment position="start">
            <Icon sx={{ color: theme.palette.primary.main, fontSize: 20, ml: 1 }} />
          </InputAdornment>
        )}
        sx={{
          borderRadius: 3,
          background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
          backdropFilter: 'blur(4px)',
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.9)} 0%, ${alpha(theme.palette.background.paper, 0.7)} 100%)`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
            boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.1)}`
          },
          '&.Mui-focused': {
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.95)} 0%, ${alpha(theme.palette.background.paper, 0.8)} 100%)`,
            border: `1px solid ${theme.palette.primary.main}`,
            boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`
          },
          '& fieldset': {
            border: 'none'
          }
        }}
        {...props}
      >
        {options.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}

// Modern Button
export const ModernButton = ({ 
  variant = 'contained',
  color = 'primary',
  size = 'medium',
  gradient = true,
  glow = true,
  icon: Icon,
  sx = {},
  children,
  ...props 
}) => {
  const theme = useTheme()
  
  const getButtonStyles = () => {
    if (variant === 'contained') {
      return {
        background: gradient 
          ? `linear-gradient(45deg, ${theme.palette[color].main}, ${theme.palette[color === 'primary' ? 'secondary' : 'primary'].main})`
          : theme.palette[color].main,
        color: '#fff',
        boxShadow: glow ? `0 4px 20px ${alpha(theme.palette[color].main, 0.3)}` : 'none',
        '&:hover': {
          background: gradient
            ? `linear-gradient(45deg, ${theme.palette[color].dark}, ${theme.palette[color === 'primary' ? 'secondary' : 'primary'].dark})`
            : theme.palette[color].dark,
          boxShadow: glow ? `0 6px 25px ${alpha(theme.palette[color].main, 0.4)}` : 'none',
          transform: 'translateY(-2px)'
        }
      }
    } else if (variant === 'outlined') {
      return {
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
        backdropFilter: 'blur(4px)',
        border: `1px solid ${alpha(theme.palette[color].main, 0.3)}`,
        color: theme.palette[color].main,
        '&:hover': {
          background: `linear-gradient(135deg, ${alpha(theme.palette[color].main, 0.1)} 0%, ${alpha(theme.palette[color].main, 0.05)} 100%)`,
          border: `1px solid ${theme.palette[color].main}`,
          transform: 'translateY(-1px)'
        }
      }
    }
    return {}
  }
  
  return (
    <Button
      variant={variant}
      size={size}
      startIcon={Icon && <Icon />}
      sx={{
        borderRadius: 3,
        px: size === 'large' ? 4 : size === 'small' ? 2 : 3,
        py: size === 'large' ? 1.5 : size === 'small' ? 0.75 : 1.25,
        fontWeight: 600,
        textTransform: 'none',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        ...getButtonStyles(),
        ...sx
      }}
      {...props}
    >
      {children}
    </Button>
  )
}

// Modern Switch
export const ModernSwitch = ({ label, description, sx = {}, ...props }) => {
  const theme = useTheme()
  
  return (
    <Box sx={sx}>
      <FormControlLabel
        control={
          <Switch
            sx={{
              '& .MuiSwitch-switchBase': {
                '&.Mui-checked': {
                  '& + .MuiSwitch-track': {
                    background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    opacity: 1
                  }
                }
              },
              '& .MuiSwitch-track': {
                borderRadius: 13,
                background: alpha(theme.palette.text.secondary, 0.2),
                transition: 'all 0.3s ease'
              },
              '& .MuiSwitch-thumb': {
                boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, 0.2)}`
              }
            }}
            {...props}
          />
        }
        label={
          <Box>
            <Typography sx={{ fontWeight: 500 }}>{label}</Typography>
            {description && (
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                {description}
              </Typography>
            )}
          </Box>
        }
      />
    </Box>
  )
}

// Modern Chip Input
export const ModernChipInput = ({ 
  label,
  placeholder,
  chips = [],
  onAdd,
  onDelete,
  icon: Icon,
  color = 'primary',
  sx = {}
}) => {
  const [inputValue, setInputValue] = useState('')
  const theme = useTheme()
  
  const handleAdd = () => {
    if (inputValue.trim() && !chips.includes(inputValue.trim())) {
      onAdd(inputValue.trim())
      setInputValue('')
    }
  }
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAdd()
    }
  }
  
  return (
    <Box sx={sx}>
      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
        {label}
      </Typography>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <ModernTextField
          fullWidth
          placeholder={placeholder}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          icon={Icon}
          size="small"
        />
        <ModernButton
          variant="contained"
          size="small"
          onClick={handleAdd}
          disabled={!inputValue.trim()}
          sx={{ minWidth: 80 }}
        >
          <AddIcon sx={{ fontSize: 18 }} />
        </ModernButton>
      </Box>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {chips.map((chip, index) => (
          <Zoom in={true} key={chip} timeout={300 + index * 50}>
            <Chip
              label={chip}
              onDelete={() => onDelete(chip)}
              color={color}
              variant="outlined"
              size="small"
              sx={{
                borderRadius: 2,
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                background: `linear-gradient(135deg, ${alpha(theme.palette[color].main, 0.1)} 0%, ${alpha(theme.palette[color].main, 0.05)} 100%)`,
                backdropFilter: 'blur(4px)',
                border: `1px solid ${alpha(theme.palette[color].main, 0.3)}`,
                '&:hover': {
                  background: `linear-gradient(135deg, ${alpha(theme.palette[color].main, 0.15)} 0%, ${alpha(theme.palette[color].main, 0.08)} 100%)`
                }
              }}
            />
          </Zoom>
        ))}
      </Box>
    </Box>
  )
}

// Modern Alert
export const ModernAlert = ({ 
  severity = 'info',
  title,
  description,
  onClose,
  sx = {},
  ...props 
}) => {
  const theme = useTheme()
  
  return (
    <Fade in={true}>
      <Alert
        severity={severity}
        onClose={onClose}
        sx={{
          borderRadius: 3,
          background: `linear-gradient(135deg, ${alpha(theme.palette[severity].main, 0.1)} 0%, ${alpha(theme.palette[severity].main, 0.05)} 100%)`,
          backdropFilter: 'blur(8px)',
          border: `1px solid ${alpha(theme.palette[severity].main, 0.3)}`,
          boxShadow: `0 4px 20px ${alpha(theme.palette[severity].main, 0.1)}`,
          '& .MuiAlert-icon': {
            fontSize: 24
          },
          '& .MuiAlert-message': {
            fontWeight: 500
          },
          ...sx
        }}
        {...props}
      >
        {title && (
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
            {title}
          </Typography>
        )}
        {description && (
          <Typography variant="body2">
            {description}
          </Typography>
        )}
      </Alert>
    </Fade>
  )
}

// Modern Section Header
export const ModernSectionHeader = ({ 
  icon: Icon,
  title,
  subtitle,
  action,
  color = 'primary'
}) => {
  const theme = useTheme()
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {Icon && (
          <Avatar
            sx={{
              bgcolor: alpha(theme.palette[color].main, 0.1),
              color: theme.palette[color].main,
              width: 48,
              height: 48
            }}
          >
            <Icon sx={{ fontSize: 24 }} />
          </Avatar>
        )}
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="textSecondary">
              {subtitle}
            </Typography>
          )}
        </Box>
      </Box>
      {action && action}
    </Box>
  )
}

export default {
  ModernCard,
  ModernTextField,
  ModernSelect,
  ModernButton,
  ModernSwitch,
  ModernChipInput,
  ModernAlert,
  ModernSectionHeader
}