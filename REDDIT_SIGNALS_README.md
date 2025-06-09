"""
Reddit Signal Discovery Integration - README
============================================

This integration adds Reddit signal discovery capabilities to VoiceForge, allowing you to:

1. Discover relevant discussions and opportunities on Reddit
2. Generate AI-powered responses using your organization's content
3. Track engagement and effectiveness of your Reddit interactions

## What's New

### API Endpoints Added:
- `POST /reddit-signals/discover` - Discover signals from specified subreddits
- `POST /reddit-signals/generate-response` - Generate responses using VoiceForge RAG
- `GET /reddit-signals/signals` - List discovered signals with filtering
- `GET /reddit-signals/signals/{signal_id}` - Get specific signal details
- `GET /reddit-signals/health` - Service health check

### Database Tables Added:
- `reddit_signals` - Stores discovered Reddit signals
- `signal_responses` - Stores generated responses and tracking

## Setup Instructions

### 1. Install Dependencies
```bash
pip install praw pandas nltk scikit-learn
```

### 2. Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Create a new application (script type)
3. Get your client ID and secret
4. Add to your `backend/.env` file:

```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=VoiceForge Signal Discovery Bot v1.0
```

### 3. Database Migration
```bash
cd backend
python -m alembic upgrade head
```

### 4. Start the Server
```bash
cd backend
python -m uvicorn api.main:app --reload
```

## Usage Examples

### Discover Reddit Signals
```bash
curl -X POST "http://localhost:8000/reddit-signals/discover" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["startups", "SaaS", "webdev"],
    "keywords": ["api", "integration", "automation"],
    "time_filter": "week",
    "max_posts_per_subreddit": 50,
    "relevance_threshold": 0.7
  }'
```

### Generate Response to Signal
```bash
curl -X POST "http://localhost:8000/reddit-signals/generate-response" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "signal_id": "reddit_abc123_org456",
    "platform": "reddit",
    "tone": "helpful",
    "response_type": "comment_reply",
    "include_context": true
  }'
```

### List Discovered Signals
```bash
curl -X GET "http://localhost:8000/reddit-signals/signals?limit=20&signal_type=question" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## How It Works

### Signal Discovery Flow:
1. **Scan Subreddits**: Uses Reddit API to scan specified subreddits
2. **Filter by Keywords**: Matches posts against your specified keywords
3. **Relevance Scoring**: Calculates relevance based on keywords, engagement, and recency
4. **Classification**: Categorizes signals (question, complaint, feature_request, etc.)
5. **Storage**: Stores signals in database for response generation

### Response Generation Flow:
1. **Retrieve Signal**: Gets the stored Reddit signal and context
2. **Build Context**: Creates enhanced context including thread comments
3. **RAG Query**: Uses VoiceForge's RAG system with signal context
4. **AI Generation**: Generates contextually appropriate response
5. **Validation**: Scores confidence and validates response quality
6. **Storage**: Stores response for analytics and tracking

### Signal Types Detected:
- `question` - Help requests and how-to questions
- `complaint` - Problems or issues mentioned
- `feature_request` - Requests for new features
- `competitive_mention` - Mentions of competitors
- `industry_trend` - Discussion of industry trends
- `customer_success` - Success stories and achievements
- `discussion` - General discussions (default)

## Key Features

### Multi-Tenant Support
- All signals are isolated by organization ID
- Secure access control through existing auth system

### Relevance Scoring
- Keyword matching (40%)
- Engagement metrics (40%) 
- Recency factor (20%)

### Engagement Potential
- Considers upvotes, comments, and timing
- Helps prioritize which signals to respond to

### VoiceForge Integration
- Uses existing RAG system for content generation
- Leverages your crawled content for contextual responses
- Maintains brand consistency through existing tone/platform settings

## Database Schema

### reddit_signals table:
- `signal_id` - Unique identifier
- `org_id` - Organization for multi-tenancy
- `thread_id` - Reddit thread ID
- `subreddit` - Source subreddit
- `title` - Post title
- `content` - Post content
- `url` - Reddit permalink
- `author` - Post author
- `score` - Reddit upvotes
- `num_comments` - Comment count
- `created_at` - When post was created
- `relevance_score` - Calculated relevance (0-1)
- `signal_type` - Classified type
- `engagement_potential` - Engagement score (0-1)
- `top_comments` - Top 3 comments
- `discovered_at` - When signal was discovered
- `status` - Signal status
- `metadata` - Additional data

### signal_responses table:
- `response_id` - Unique identifier
- `signal_id` - Links to reddit_signals
- `org_id` - Organization ID
- `generated_content` - AI-generated response
- `response_type` - Type of response
- `platform` - Target platform
- `tone` - Response tone
- `confidence_score` - AI confidence (0-1)
- `metadata` - Generation metadata
- `generated_at` - When response was generated
- `status` - Response status
- `published_at` - When response was published (if applicable)
- `engagement_metrics` - Performance tracking

## Next Steps

This is the foundation for the full Arctura vision. Future enhancements:

1. **Twitter/LinkedIn Integration** - Expand to other platforms
2. **Gypsum Integration** - Connect with messaging framework system
3. **Campaign Orchestration** - Automated campaign planning
4. **Revenue Attribution** - Track signal-to-revenue conversion
5. **Advanced Analytics** - Performance dashboards and insights

## Troubleshooting

### Common Issues:

1. **Reddit API Errors**: Check your credentials and rate limits
2. **Database Errors**: Ensure migrations are run
3. **Import Errors**: Make sure reddit-scanner path is accessible
4. **NLTK Errors**: Run `python -c "import nltk; nltk.download('punkt')"`

### Debug Mode:
Set logging to DEBUG in your backend configuration to see detailed signal processing logs.

## Contributing

This integration follows VoiceForge's existing patterns:
- Multi-tenant database design
- Clerk authentication
- Error handling with safe execution
- Background task processing
- RESTful API design

Feel free to extend the signal classification, add new platforms, or enhance the scoring algorithms!
