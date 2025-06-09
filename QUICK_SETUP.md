# 🚀 Quick Setup Instructions

## Database Setup (with correct database name)

Run this single command to set up everything:

```bash
chmod +x setup_platform_config.sh
./setup_platform_config.sh
```

## Or manually:

### 1. Database Migration
```bash
cd backend
psql -d voice_forge -f database/migrations/add_platform_configurations.sql
```

### 2. Test Backend
```bash
python test_platform_endpoints.py
```

### 3. Start Services
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 4. View the Magic
Navigate to: `http://localhost:3000/settings/signals`

## 🎨 What You'll See

- **Beautiful gradient backgrounds** for each platform
- **Interactive hover animations** on platform cards
- **Real-time status indicators** with color-coded badges
- **Professional tabbed interface** for Reddit configuration
- **Smooth loading states** and form validation
- **Modern coming soon pages** for other platforms

Your UI transformation is complete! From ugly tables to premium SaaS interface! ✨