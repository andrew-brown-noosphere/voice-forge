  // Form data with OPTIMIZED DEFAULTS
  const [domain, setDomain] = useState('')
  const [config, setConfig] = useState({
    max_depth: 3,
    max_pages: 20,  // 🎯 Reduced for focused crawling
    respect_robots_txt: true,
    delay: 2.0,     // 🎯 Increased to 2 seconds to avoid blocking
    timeout: 15,    // 🎯 Reduced from 30 to 15 seconds
    follow_external_links: false,
    exclude_patterns: [
      '.*/contact.*',     // 🎯 Skip contact pages (slow)
      '.*/login.*',       // 🎯 Skip login pages
      '.*/register.*',    // 🎯 Skip registration
      '.*/checkout.*',    // 🎯 Skip checkout flows
      '.*/cart.*',        // 🎯 Skip shopping cart
      '.*/admin.*',       // 🎯 Skip admin areas
      '.*\\.pdf$',        // 🎯 Skip PDF files
      '.*\\.jpg$',        // 🎯 Skip images
      '.*\\.png$',
      '.*\\.css$',        // 🎯 Skip stylesheets
      '.*\\.js$',         // 🎯 Skip JavaScript files
    ],
    include_patterns: [
      '.*/product/?$',    // 🎯 Include /product page
      '.*/product/.*',    // 🎯 Include /product/* subpages
      '.*/blog/?$',       // 🎯 Include /blog page
      '.*/blog/.*',       // 🎯 Include /blog/* subpages
    ],
    // 🎯 FIXED: Realistic browser User-Agent instead of crawler signature
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  })