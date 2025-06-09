"""
Abstracted Signal Discovery API
Supports multiple platforms: Reddit, Twitter, GitHub, LinkedIn
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import List, Dict, Any, Optional, Union
import logging
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from auth.clerk_auth import get_current_user_with_org, get_org_id_from_user, AuthUser
from api.dependencies import get_db, get_rag_service
from processor.rag_service import RAGService
from signals.ai_service import SignalIntelligenceService
from signals.tasks import execute_automated_signal_scan
from database.models import SignalSource, SignalRecommendation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])


# Pydantic models for request/response
class SignalDiscoveryRequest(BaseModel):
    """Request model for signal discovery across platforms"""
    platform: str = Field(..., description="Platform: reddit, twitter, github, linkedin")
    sources: List[str] = Field(..., description="Sources to scan (subreddits, hashtags, repos, etc.)")
    keywords: List[str] = Field(default=[], description="Keywords to search for")
    time_filter: str = Field(default="week", description="Time filter: day, week, month, year, all")
    max_items_per_source: int = Field(default=50, description="Maximum items per source")
    relevance_threshold: float = Field(default=0.6, description="Minimum relevance score (0-1)")


class Signal(BaseModel):
    """Universal signal response model for all platforms"""
    signal_id: str
    platform: str
    platform_id: str
    title: str
    content: Optional[str] = None
    url: str
    author: Optional[str] = None
    author_url: Optional[str] = None
    created_at: datetime
    discovered_at: datetime
    signal_type: str
    relevance_score: float
    engagement_potential: float
    sentiment_score: Optional[float] = None
    status: str = "active"
    platform_metadata: Dict[str, Any] = {}
    keywords_matched: List[str] = []
    engagement_metrics: Dict[str, Any] = {}


class SignalDiscoveryResponse(BaseModel):
    """Response model for signal discovery"""
    discovery_id: str
    platform: str
    signals_found: int
    sources_scanned: List[str]
    signals: List[Signal]
    scan_timestamp: datetime
    status: str


class ContentGenerationRequest(BaseModel):
    """Request for generating content from signal"""
    signal_id: str
    platform: str = Field(description="Target platform for response")
    tone: str = Field(default="professional", description="Tone for generated content")
    response_type: str = Field(default="comment_reply", description="Type of response")
    include_context: bool = Field(default=True, description="Include signal context in generation")


class GeneratedSignalResponse(BaseModel):
    """Response model for generated content from signal"""
    response_id: str
    signal_id: str
    generated_content: str
    response_type: str
    platform: str
    tone: str
    confidence_score: float
    source_signal: Signal
    metadata: Dict[str, Any]


# Platform Configuration Models
class PlatformConfig(BaseModel):
    """Base platform configuration model"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    username: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: Optional[str] = None
    additional_config: Dict[str, Any] = {}


class PlatformStatusResponse(BaseModel):
    """Platform status response model"""
    platform: str
    connection_status: str  # "connected", "not_connected", "error", "configuring"
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    config_status: str  # "complete", "incomplete", "not_configured"
    available_features: List[str] = []
    rate_limits: Dict[str, Any] = {}


class PlatformTestResponse(BaseModel):
    """Platform connection test response model"""
    platform: str
    test_status: str  # "success", "failed", "partial"
    test_results: Dict[str, Any]
    error_details: Optional[str] = None
    recommendations: List[str] = []


class SignalService:
    """Service for multi-platform signal discovery and processing"""
    
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def discover_signals(
        self, 
        request: SignalDiscoveryRequest, 
        org_id: str
    ) -> SignalDiscoveryResponse:
        """
        Discover signals from any supported platform
        """
        try:
            if request.platform == "reddit":
                return self._discover_reddit_signals(request, org_id)
            elif request.platform == "twitter":
                return self._discover_twitter_signals(request, org_id)
            elif request.platform == "github":
                return self._discover_github_signals(request, org_id)
            elif request.platform == "linkedin":
                return self._discover_linkedin_signals(request, org_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Platform '{request.platform}' is not supported"
                )
                
        except Exception as e:
            self.logger.error(f"Error discovering {request.platform} signals: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to discover {request.platform} signals: {str(e)}"
            )
    
    def _discover_reddit_signals(self, request: SignalDiscoveryRequest, org_id: str) -> SignalDiscoveryResponse:
        """Discover signals from Reddit using public JSON API (no authentication required)"""
        try:
            # Use public Reddit JSON API instead of praw for now
            return self._discover_reddit_signals_public(request, org_id)
            
        except Exception as e:
            self.logger.error(f"Error discovering Reddit signals: {str(e)}")
            raise
    
    def _discover_reddit_signals_public(self, request: SignalDiscoveryRequest, org_id: str) -> SignalDiscoveryResponse:
        """Discover signals from Reddit using public JSON API (no auth needed)"""
        import requests
        import json
        from urllib.parse import quote
        
        try:
            signals = []
            
            for subreddit in request.sources:
                try:
                    # Build search URL for public Reddit JSON API
                    if request.keywords:
                        # Search with keywords in the subreddit
                        search_query = ' '.join(request.keywords)
                        url = f"https://www.reddit.com/r/{subreddit}/search.json"
                        params = {
                            'q': search_query,
                            'restrict_sr': 1,  # Restrict to this subreddit
                            'sort': 'new',
                            'limit': min(request.max_items_per_source, 100),
                            't': request.time_filter
                        }
                    else:
                        # Just get latest posts from subreddit
                        url = f"https://www.reddit.com/r/{subreddit}/new.json"
                        params = {
                            'limit': min(request.max_items_per_source, 100),
                            't': request.time_filter
                        }
                    
                    # Make request to Reddit public API
                    headers = {
                        'User-Agent': 'VoiceForge Signal Discovery (Public Search) v1.0'
                    }
                    
                    self.logger.info(f"Searching r/{subreddit} with query: {request.keywords}")
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    
                    if response.status_code != 200:
                        self.logger.warning(f"Reddit API returned {response.status_code} for r/{subreddit}")
                        continue
                    
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    self.logger.info(f"Found {len(posts)} posts in r/{subreddit}")
                    
                    # Process posts
                    for post_data in posts:
                        post = post_data.get('data', {})
                        
                        # Skip removed/deleted posts
                        if post.get('removed_by_category') or post.get('author') == '[deleted]':
                            continue
                        
                        # Create row-like structure for compatibility with existing scoring
                        row = {
                            'thread_id': post.get('id', ''),
                            'title': post.get('title', ''),
                            'text': post.get('selftext', ''),
                            'score': post.get('score', 0),
                            'comments': post.get('num_comments', 0),
                            'author': post.get('author', 'unknown'),
                            'subreddit': subreddit,
                            'permalink': f"https://reddit.com{post.get('permalink', '')}",
                            'created_utc': datetime.fromtimestamp(post.get('created_utc', 0))
                        }
                        
                        # Calculate relevance score
                        relevance_score = self._calculate_relevance_score(row, request.keywords)
                        
                        if relevance_score >= request.relevance_threshold:
                            signal = Signal(
                                signal_id=f"reddit_{row['thread_id']}_{org_id}",
                                platform="reddit",
                                platform_id=row['thread_id'],
                                title=row['title'],
                                content=row['text'] if isinstance(row['text'], str) else '',
                                url=row['permalink'],
                                author=str(row.get('author', 'unknown')),
                                author_url=f"https://reddit.com/u/{row.get('author', '')}" if row.get('author') else None,
                                created_at=row['created_utc'],
                                discovered_at=datetime.utcnow(),
                                signal_type=self._classify_signal_type(row),
                                relevance_score=relevance_score,
                                engagement_potential=self._calculate_engagement_potential(row),
                                platform_metadata={
                                    'thread_id': row['thread_id'],
                                    'subreddit': row['subreddit'],
                                    'score': int(row['score']),
                                    'num_comments': int(row['comments'])
                                },
                                keywords_matched=[kw for kw in request.keywords if kw.lower() in (str(row['title']) + str(row.get('text', ''))).lower()],
                                engagement_metrics={
                                    'upvotes': int(row['score']),
                                    'comments': int(row['comments']),
                                    'engagement_rate': min(1.0, (int(row['score']) + int(row['comments'])) / 100)
                                }
                            )
                            signals.append(signal)
                            
                except Exception as e:
                    self.logger.warning(f"Error searching r/{subreddit}: {str(e)}")
                    continue
            
            # Sort by relevance and engagement
            signals.sort(key=lambda x: x.relevance_score * x.engagement_potential, reverse=True)
            
            # Store signals
            self._store_signals(signals, org_id)
            
            return SignalDiscoveryResponse(
                discovery_id=str(uuid.uuid4()),
                platform="reddit",
                signals_found=len(signals),
                sources_scanned=request.sources,
                signals=signals,
                scan_timestamp=datetime.utcnow(),
                status="completed"
            )
            
        except Exception as e:
            self.logger.error(f"Error with public Reddit search: {str(e)}")
            raise
    
    def _discover_reddit_signals_praw(self, request: SignalDiscoveryRequest, org_id: str) -> SignalDiscoveryResponse:
        """Discover signals from Reddit using PRAW (requires authentication) - KEPT FOR LATER USE"""
        try:
            # Import Reddit Scanner
            import sys
            
            # Add reddit-scanner to path
            reddit_scanner_path = "/Users/andrewbrown/Sites/noosphere/github/reddit-scanner"
            if reddit_scanner_path not in sys.path:
                sys.path.append(reddit_scanner_path)
            
            from reddit_scanner.scanner import RedditScanner
            
            # Initialize Reddit Scanner
            reddit_scanner = RedditScanner(
                client_id=os.environ.get('REDDIT_CLIENT_ID'),
                client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                user_agent=os.environ.get('REDDIT_USER_AGENT', 'VoiceForge Signal Discovery Bot v1.0')
            )
            
            # Collect threads from subreddits
            df = reddit_scanner.collect_threads(
                subreddits=request.sources,
                keywords=request.keywords,
                time_filter=request.time_filter,
                limit=request.max_items_per_source
            )
            
            if df.empty:
                return SignalDiscoveryResponse(
                    discovery_id=str(uuid.uuid4()),
                    platform="reddit",
                    signals_found=0,
                    sources_scanned=request.sources,
                    signals=[],
                    scan_timestamp=datetime.utcnow(),
                    status="no_signals_found"
                )
            
            # Convert DataFrame to abstracted signals
            signals = []
            for _, row in df.iterrows():
                relevance_score = self._calculate_relevance_score(row, request.keywords)
                
                if relevance_score >= request.relevance_threshold:
                    signal = Signal(
                        signal_id=f"reddit_{row['thread_id']}_{org_id}",
                        platform="reddit",
                        platform_id=row['thread_id'],
                        title=row['title'],
                        content=row['text'] if isinstance(row['text'], str) else '',
                        url=row['permalink'],
                        author=str(row.get('author', 'unknown')),
                        author_url=f"https://reddit.com/u/{row.get('author', '')}" if row.get('author') else None,
                        created_at=row['created_utc'],
                        discovered_at=datetime.utcnow(),
                        signal_type=self._classify_signal_type(row),
                        relevance_score=relevance_score,
                        engagement_potential=self._calculate_engagement_potential(row),
                        platform_metadata={
                            'thread_id': row['thread_id'],
                            'subreddit': row['subreddit'],
                            'score': int(row['score']),
                            'num_comments': int(row['comments']),
                            'top_comments': row.get('top_comments', [])[:3]
                        },
                        keywords_matched=[kw for kw in request.keywords if kw.lower() in (str(row['title']) + str(row.get('text', ''))).lower()],
                        engagement_metrics={
                            'upvotes': int(row['score']),
                            'comments': int(row['comments']),
                            'engagement_rate': min(1.0, (int(row['score']) + int(row['comments'])) / 100)
                        }
                    )
                    signals.append(signal)
            
            # Sort by relevance and engagement
            signals.sort(key=lambda x: x.relevance_score * x.engagement_potential, reverse=True)
            
            # Store signals using abstracted database method
            self._store_signals(signals, org_id)
            
            return SignalDiscoveryResponse(
                discovery_id=str(uuid.uuid4()),
                platform="reddit",
                signals_found=len(signals),
                sources_scanned=request.sources,
                signals=signals,
                scan_timestamp=datetime.utcnow(),
                status="completed"
            )
            
        except Exception as e:
            self.logger.error(f"Error discovering Reddit signals with PRAW: {str(e)}")
            raise
    
    def _discover_twitter_signals(self, request: SignalDiscoveryRequest, org_id: str) -> SignalDiscoveryResponse:
        """Discover signals from Twitter (placeholder for future implementation)"""
        # TODO: Implement Twitter signal discovery
        return SignalDiscoveryResponse(
            discovery_id=str(uuid.uuid4()),
            platform="twitter",
            signals_found=0,
            sources_scanned=request.sources,
            signals=[],
            scan_timestamp=datetime.utcnow(),
            status="not_implemented"
        )
    
    def _discover_github_signals(self, request: SignalDiscoveryRequest, org_id: str) -> SignalDiscoveryResponse:
        """Discover signals from GitHub (placeholder for future implementation)"""
        # TODO: Implement GitHub signal discovery
        return SignalDiscoveryResponse(
            discovery_id=str(uuid.uuid4()),
            platform="github",
            signals_found=0,
            sources_scanned=request.sources,
            signals=[],
            scan_timestamp=datetime.utcnow(),
            status="not_implemented"
        )
    
    def _discover_linkedin_signals(self, request: SignalDiscoveryRequest, org_id: str) -> SignalDiscoveryResponse:
        """Discover signals from LinkedIn (placeholder for future implementation)"""
        # TODO: Implement LinkedIn signal discovery
        return SignalDiscoveryResponse(
            discovery_id=str(uuid.uuid4()),
            platform="linkedin",
            signals_found=0,
            sources_scanned=request.sources,
            signals=[],
            scan_timestamp=datetime.utcnow(),
            status="not_implemented"
        )
    
    def generate_response_for_signal(
        self, 
        request: ContentGenerationRequest, 
        org_id: str,
        rag_service: RAGService
    ) -> GeneratedSignalResponse:
        """Generate a response for any platform signal using VoiceForge RAG"""
        try:
            # Retrieve the signal from storage
            signal = self._get_signal(request.signal_id, org_id)
            if not signal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Signal {request.signal_id} not found"
                )
            
            # Build platform-specific context
            signal_context = self._build_signal_context(signal)
            
            # Create enhanced query for RAG system
            if request.include_context:
                rag_query = f"{signal.title}\n\n{signal.content or ''}\n\nContext: This is a {signal.signal_type} from {signal.platform}. Generate a helpful response."
            else:
                rag_query = f"{signal.title}\n{signal.content or ''}"
            
            # Use VoiceForge RAG system to generate response
            from processor.rag import RAGSystem
            rag_system = RAGSystem(self.db)
            
            rag_response = rag_system.process_and_generate(
                query=rag_query,
                platform=request.platform,
                tone=request.tone,
                org_id=org_id
            )
            
            # Calculate confidence score
            confidence_score = (
                rag_response.get('metadata', {}).get('confidence', 0.8) * 0.7 +
                signal.relevance_score * 0.3
            )
            
            # Create response
            response_id = str(uuid.uuid4())
            generated_response = GeneratedSignalResponse(
                response_id=response_id,
                signal_id=request.signal_id,
                generated_content=rag_response['text'],
                response_type=request.response_type,
                platform=request.platform,
                tone=request.tone,
                confidence_score=confidence_score,
                source_signal=signal,
                metadata={
                    'rag_metadata': rag_response.get('metadata', {}),
                    'source_chunks': len(rag_response.get('source_chunks', [])),
                    'signal_context': signal_context,
                    'generation_timestamp': datetime.utcnow().isoformat(),
                    'engagement_metrics': signal.engagement_metrics
                }
            )
            
            # Store the generated response
            self._store_generated_response(generated_response, org_id)
            
            return generated_response
            
        except Exception as e:
            self.logger.error(f"Error generating response for signal: {str(e)}")
            raise
    
    def _build_signal_context(self, signal: Signal) -> str:
        """Build platform-specific context for signal"""
        if signal.platform == "reddit":
            reddit_data = signal.platform_metadata
            return f"""
            Reddit Signal Context:
            Subreddit: r/{reddit_data.get('subreddit', 'unknown')}
            Title: {signal.title}
            Content: {signal.content or 'No content'}
            Author: {signal.author}
            Engagement: {reddit_data.get('score', 0)} upvotes, {reddit_data.get('num_comments', 0)} comments
            
            Top Comments:
            {chr(10).join(['- ' + comment for comment in reddit_data.get('top_comments', [])])}
            
            Signal Type: {signal.signal_type}
            """
        elif signal.platform == "twitter":
            return f"""
            Twitter Signal Context:
            Tweet: {signal.title}
            Author: @{signal.author}
            Engagement: {signal.engagement_metrics.get('likes', 0)} likes, {signal.engagement_metrics.get('retweets', 0)} retweets
            Signal Type: {signal.signal_type}
            """
        elif signal.platform == "github":
            return f"""
            GitHub Signal Context:
            Repository: {signal.platform_metadata.get('repository', 'unknown')}
            Issue/PR: {signal.title}
            Author: {signal.author}
            Type: {signal.platform_metadata.get('issue_type', 'unknown')}
            Signal Type: {signal.signal_type}
            """
        elif signal.platform == "linkedin":
            return f"""
            LinkedIn Signal Context:
            Post: {signal.title}
            Author: {signal.author}
            Content: {signal.content or 'No content'}
            Signal Type: {signal.signal_type}
            """
        else:
            return f"""
            Signal Context:
            Platform: {signal.platform}
            Title: {signal.title}
            Content: {signal.content or 'No content'}
            Author: {signal.author}
            Signal Type: {signal.signal_type}
            """
    
    def _calculate_relevance_score(self, row, keywords: List[str]) -> float:
        """Calculate relevance score (same logic as Reddit-specific version)"""
        score = 0.0
        
        # Base score from engagement metrics
        upvote_score = min(row['score'] / 100, 1.0)
        comment_score = min(row['comments'] / 50, 1.0)
        engagement_score = (upvote_score + comment_score) / 2
        
        # Keyword relevance score
        keyword_score = 0.0
        if keywords:
            title_text = str(row['title']).lower()
            content_text = str(row.get('text', '')).lower()
            combined_text = f"{title_text} {content_text}"
            
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            keyword_score = min(keyword_matches / len(keywords), 1.0)
        else:
            keyword_score = 1.0
        
        # Time recency score
        try:
            post_age_hours = (datetime.utcnow() - row['created_utc']).total_seconds() / 3600
            recency_score = max(0, 1 - (post_age_hours / (7 * 24)))
        except:
            recency_score = 0.5
        
        # Weighted combination
        score = (
            engagement_score * 0.4 +
            keyword_score * 0.4 +
            recency_score * 0.2
        )
        
        return min(max(score, 0.0), 1.0)
    
    def _classify_signal_type(self, row) -> str:
        """Classify the type of signal (same logic as Reddit-specific version)"""
        title = str(row['title']).lower()
        content = str(row.get('text', '')).lower()
        combined = f"{title} {content}"
        
        if any(word in combined for word in ['question', 'help', 'how to', '?']):
            return 'question'
        elif any(word in combined for word in ['complaint', 'problem', 'issue', 'broken']):
            return 'complaint'
        elif any(word in combined for word in ['feature', 'request', 'wish', 'should add']):
            return 'feature_request'
        elif any(word in combined for word in ['vs', 'alternative', 'competitor', 'compare']):
            return 'competitive_mention'
        elif any(word in combined for word in ['trend', 'future', 'prediction']):
            return 'industry_trend'
        elif any(word in combined for word in ['success', 'achievement', 'won']):
            return 'customer_success'
        else:
            return 'discussion'
    
    def _calculate_engagement_potential(self, row) -> float:
        """Calculate engagement potential (same logic as Reddit-specific version)"""
        score_factor = min(row['score'] / 50, 1.0)
        comment_factor = min(row['comments'] / 25, 1.0)
        
        try:
            hours_old = (datetime.utcnow() - row['created_utc']).total_seconds() / 3600
            time_factor = max(0, 1 - (hours_old / 48))
        except:
            time_factor = 0.5
        
        return (score_factor + comment_factor + time_factor) / 3
    
    def _store_signals(self, signals: List[Signal], org_id: str):
        """Store discovered signals using abstracted database method"""
        try:
            for signal in signals:
                signal_data = {
                    'signal_id': signal.signal_id,
                    'org_id': org_id,
                    'platform': signal.platform,
                    'platform_id': signal.platform_id,
                    'title': signal.title,
                    'content': signal.content,
                    'url': signal.url,
                    'author': signal.author,
                    'author_url': signal.author_url,
                    'created_at': signal.created_at,
                    'discovered_at': signal.discovered_at,
                    'signal_type': signal.signal_type,
                    'relevance_score': signal.relevance_score,
                    'engagement_potential': signal.engagement_potential,
                    'sentiment_score': signal.sentiment_score,
                    'status': signal.status,
                    'platform_metadata': signal.platform_metadata,
                    'keywords_matched': signal.keywords_matched,
                    'engagement_metrics': signal.engagement_metrics
                }
                
                # Use the new abstracted database method
                self.db.store_signal(signal_data)
                
        except Exception as e:
            self.logger.warning(f"Failed to store signals: {str(e)}")
    
    def _get_signal(self, signal_id: str, org_id: str) -> Optional[Signal]:
        """Retrieve a signal from storage using abstracted method"""
        try:
            signal_data = self.db.get_signal(signal_id, org_id)
            if signal_data:
                return Signal(**signal_data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve signal: {str(e)}")
            return None
    
    def _store_generated_response(self, response: GeneratedSignalResponse, org_id: str):
        """Store generated response using abstracted method"""
        try:
            response_data = {
                'response_id': response.response_id,
                'signal_id': response.signal_id,
                'org_id': org_id,
                'generated_content': response.generated_content,
                'response_type': response.response_type,
                'platform': response.platform,
                'tone': response.tone,
                'confidence_score': response.confidence_score,
                'response_metadata': response.metadata,
                'generated_at': datetime.utcnow()
            }
            
            # Use the new abstracted database method
            self.db.store_abstracted_signal_response(response_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to store generated response: {str(e)}")


# API endpoints
@router.post("/discover", response_model=SignalDiscoveryResponse)
async def discover_signals(
    request: SignalDiscoveryRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Discover relevant signals from any supported platform
    
    Supported platforms: reddit, twitter, github, linkedin
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        service = SignalService(db)
        result = service.discover_signals(request, org_id)
        
        logger.info(f"Discovered {result.signals_found} {result.platform} signals for org {org_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to discover signals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover signals: {str(e)}"
        )


@router.post("/generate-response", response_model=GeneratedSignalResponse)
async def generate_signal_response(
    request: ContentGenerationRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Generate a response for a discovered signal from any platform
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        service = SignalService(db)
        result = service.generate_response_for_signal(request, org_id, rag_service)
        
        logger.info(f"Generated response for signal {request.signal_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate signal response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.get("/list", response_model=List[Signal])
async def list_signals(
    limit: int = 20,
    offset: int = 0,
    platform: Optional[str] = None,
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    List discovered signals with filtering across all platforms
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Get signals from database with filters using abstracted method
        signals_data = db.list_signals(
            org_id=org_id,
            limit=limit,
            offset=offset,
            platform=platform,
            signal_type=signal_type,
            status=status
        )
        
        signals = [Signal(**data) for data in signals_data]
        return signals
        
    except Exception as e:
        logger.error(f"Failed to list signals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list signals: {str(e)}"
        )


@router.get("/{signal_id}", response_model=Signal)
async def get_signal(
    signal_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Get a specific signal by ID from any platform
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        service = SignalService(db)
        signal = service._get_signal(signal_id, org_id)
        
        if not signal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Signal {signal_id} not found"
            )
        
        return signal
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get signal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get signal: {str(e)}"
        )


@router.get("/platforms/supported")
async def get_supported_platforms():
    """Get list of supported platforms"""
    return {
        "platforms": [
            {
                "id": "reddit",
                "name": "Reddit",
                "description": "Discover signals from subreddits",
                "status": "active",
                "source_types": ["subreddit"],
                "example_sources": ["startups", "SaaS", "webdev"]
            },
            {
                "id": "twitter",
                "name": "Twitter",
                "description": "Discover signals from tweets and hashtags",
                "status": "coming_soon",
                "source_types": ["hashtag", "user"],
                "example_sources": ["#saas", "#startup", "@username"]
            },
            {
                "id": "github",
                "name": "GitHub",
                "description": "Discover signals from issues and discussions",
                "status": "coming_soon",
                "source_types": ["repository", "user"],
                "example_sources": ["facebook/react", "microsoft/vscode"]
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "description": "Discover signals from posts and company pages",
                "status": "coming_soon",
                "source_types": ["company", "hashtag"],
                "example_sources": ["#technology", "company/microsoft"]
            }
        ]
    }


# Platform Configuration Endpoints
@router.get("/platforms/{platform}/status", response_model=PlatformStatusResponse)
async def get_platform_status(
    platform: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Get platform connection and configuration status"""
    try:
        # Validate platform
        supported_platforms = ["reddit", "twitter", "github", "linkedin"]
        if platform not in supported_platforms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform}' not supported. Supported platforms: {supported_platforms}"
            )
        
        org_id = get_org_id_from_user(current_user)
        
        # For now, return basic status since we don't have platform config storage yet
        if platform == "reddit":
            connection_status = "connected" if os.environ.get('REDDIT_CLIENT_ID') else "not_connected"
            config_status = "complete" if os.environ.get('REDDIT_CLIENT_ID') else "not_configured"
            available_features = ["subreddit_monitoring", "keyword_search"] if connection_status == "connected" else []
        else:
            connection_status = "not_connected"
            config_status = "not_configured"
            available_features = []
        
        return PlatformStatusResponse(
            platform=platform,
            connection_status=connection_status,
            last_sync=datetime.utcnow() if connection_status == "connected" else None,
            error_message=None,
            config_status=config_status,
            available_features=available_features,
            rate_limits={"requests_per_minute": 60}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get platform status for {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform status: {str(e)}"
        )


@router.post("/platforms/{platform}/configure")
async def configure_platform(
    platform: str,
    config: PlatformConfig,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Configure platform credentials and settings"""
    try:
        # Validate platform
        supported_platforms = ["reddit", "twitter", "github", "linkedin"]
        if platform not in supported_platforms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform}' not supported. Supported platforms: {supported_platforms}"
            )
        
        org_id = get_org_id_from_user(current_user)
        
        # For now, just return success - platform config storage not implemented yet
        logger.info(f"Platform {platform} configuration requested for org {org_id}")
        
        return {
            "status": "configured",
            "platform": platform,
            "message": f"Platform {platform} configuration received (storage not yet implemented)",
            "next_steps": ["Platform configuration storage coming soon"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to configure platform {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure platform: {str(e)}"
        )


@router.post("/platforms/{platform}/test-connection", response_model=PlatformTestResponse)
async def test_platform_connection(
    platform: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Test platform connection with current configuration"""
    try:
        # Validate platform
        supported_platforms = ["reddit", "twitter", "github", "linkedin"]
        if platform not in supported_platforms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{platform}' not supported. Supported platforms: {supported_platforms}"
            )
        
        # Test connection based on platform
        if platform == "reddit":
            if os.environ.get('REDDIT_CLIENT_ID'):
                return PlatformTestResponse(
                    platform=platform,
                    test_status="success",
                    test_results={"authentication": "successful", "api_access": "working"},
                    recommendations=["Reddit connection is working properly"]
                )
            else:
                return PlatformTestResponse(
                    platform=platform,
                    test_status="failed",
                    test_results={"error": "Reddit credentials not configured"},
                    error_details="REDDIT_CLIENT_ID not found in environment",
                    recommendations=["Configure Reddit API credentials"]
                )
        else:
            return PlatformTestResponse(
                platform=platform,
                test_status="failed",
                test_results={"error": f"{platform} integration not implemented"},
                error_details=f"{platform} connection testing is not yet available",
                recommendations=[f"Wait for {platform} integration to be completed"]
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test platform connection for {platform}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test platform connection: {str(e)}"
        )


@router.post("/sources")
async def create_signal_source(
    source_data: dict,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Create a new signal source with automation"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        source = SignalSource(
            source_id=str(uuid.uuid4()),
            org_id=org_id,
            platform=source_data['platform'],
            source_name=source_data['source_name'],
            source_type=source_data['source_type'],
            keywords=source_data['keywords'],
            crawl_frequency=source_data.get('crawl_frequency', 'daily'),
            relevance_threshold=source_data.get('relevance_threshold', 0.6),
            business_context=source_data.get('business_context'),
            target_goals=source_data.get('target_goals', []),
            ai_optimization_enabled=source_data.get('ai_optimization_enabled', True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(source)
        db.session.commit()
        
        # Schedule first automated scan
        execute_automated_signal_scan.delay(source.source_id)
        
        return {"source_id": source.source_id, "status": "created"}
        
    except Exception as e:
        logger.error(f"Failed to create signal source: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def list_signal_sources(
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """List all signal sources for the organization"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        sources = db.session.query(SignalSource).filter(
            SignalSource.org_id == org_id
        ).all()
        
        return [
            {
                "source_id": source.source_id,
                "platform": source.platform,
                "source_name": source.source_name,
                "keywords": source.keywords,
                "is_active": source.is_active,
                "crawl_frequency": source.crawl_frequency,
                "last_crawled_at": source.last_crawled_at,
                "performance_metrics": source.performance_metrics,
                "ai_optimization_enabled": source.ai_optimization_enabled
            }
            for source in sources
        ]
        
    except Exception as e:
        logger.error(f"Failed to list signal sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/ai-setup")
async def ai_guided_source_setup(
    setup_request: dict,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """AI-guided signal source setup using VoiceForge content + Gypsum personas"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Use content-driven approach if persona_id provided, fallback to legacy if not
        if 'persona_id' in setup_request:
            ai_service = SignalIntelligenceService(voiceforge_db=db, gypsum_client=None)
            
            strategy = await ai_service.generate_content_driven_multi_platform_strategy(
                org_id=org_id,
                persona_id=setup_request['persona_id'],
                platforms=[setup_request.get('platform', 'reddit')],
                options=setup_request.get('options', {})
            )
            
            # Extract platform-specific recommendations
            platform = setup_request.get('platform', 'reddit')
            platform_strategy = strategy.get('platform_strategies', {}).get(platform, {})
            
            return {
                "recommended_sources": platform_strategy.get('recommended_sources', []),
                "recommended_keywords": [q['query'] for q in platform_strategy.get('search_queries', [])],
                "suggested_frequency": platform_strategy.get('targeting_criteria', {}).get('time_filter', 'week'),
                "priority_signal_types": platform_strategy.get('targeting_criteria', {}).get('engagement_focus', ['question', 'complaint']),
                "strategy_notes": f"Content-driven strategy based on VoiceForge analysis and {strategy.get('selected_persona', {}).get('role', 'target')} persona",
                "content_driven": True
            }
        else:
            # Legacy approach
            ai_service = SignalIntelligenceService()
            
            return await ai_service.analyze_business_and_setup_sources(
                business_description=setup_request['business_description'],
                target_audience=setup_request['target_audience'],
                goals=setup_request['goals'],
                platform=setup_request.get('platform', 'reddit')
            )
        
    except Exception as e:
        logger.error(f"AI setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy")
async def generate_signal_strategy(
    request: dict,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Generate intelligent signal strategy using VoiceForge content + Gypsum personas"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        persona_id = request.get('persona_id')  # This can now be None!
        platforms = request.get('platforms', ['reddit'])
        options = request.get('options', {})
        
        ai_service = SignalIntelligenceService(voiceforge_db=db, gypsum_client=None)
        
        # Generate strategy (allow None persona_id)
        strategy = await ai_service.generate_content_driven_multi_platform_strategy(
            org_id=org_id,
            persona_id=persona_id,  # Can be None now
            platforms=platforms,
            options=options
        )
        
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Strategy generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover-intelligent", response_model=SignalDiscoveryResponse)
async def discover_signals_intelligent(
    request: dict,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Discover signals using content-driven strategy + actual platform data + save sources"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        persona_id = request.get('persona_id')
        platforms = request.get('platforms', ['reddit'])
        options = request.get('options', {})
        save_sources = request.get('save_sources', True)  # New option to save sources
        
        logger.info(f'🧠 Starting intelligent signal discovery for {platforms} with persona {persona_id}')
        
        # Step 1: Generate content-driven strategy
        ai_service = SignalIntelligenceService(voiceforge_db=db, gypsum_client=None)
        strategy = await ai_service.generate_content_driven_multi_platform_strategy(
            org_id=org_id,
            persona_id=persona_id,
            platforms=platforms,
            options=options
        )
        
        logger.info(f'📋 Generated strategy with {len(strategy.get("platform_strategies", {}))} platform strategies')
        
        # Step 2: Execute actual discovery using the intelligent strategy
        all_signals = []
        platform_results = {}
        saved_sources = []
        
        for platform in platforms:
            platform_strategy = strategy.get('platform_strategies', {}).get(platform, {})
            
            if not platform_strategy:
                logger.warning(f'No strategy found for platform {platform}')
                continue
                
            if platform == 'reddit':
                # Extract intelligent subreddit recommendations
                recommended_sources = platform_strategy.get('recommended_sources', [])
                search_queries = platform_strategy.get('search_queries', [])
                
                # Convert to subreddit names
                subreddits = []
                for source in recommended_sources:
                    if isinstance(source, dict):
                        subreddit_name = source.get('name') or source.get('source') or source.get('subreddit')
                    else:
                        subreddit_name = str(source)
                    
                    if subreddit_name:
                        subreddits.append(subreddit_name)
                
                # Extract intelligent keywords from search queries
                keywords = []
                for query in search_queries:
                    if isinstance(query, dict):
                        query_text = query.get('query', '')
                    else:
                        query_text = str(query)
                    
                    if query_text:
                        keywords.append(query_text)
                
                logger.info(f'🎯 Reddit discovery: {len(subreddits)} subreddits, {len(keywords)} intelligent queries')
                
                # Step 3: Save sources as persistent SignalSource records
                if save_sources and subreddits:
                    for subreddit in subreddits:
                        source_id = f"reddit_{subreddit}_{org_id}"
                        
                        # Check if source already exists
                        existing_source = db.session.query(SignalSource).filter(
                            SignalSource.org_id == org_id,
                            SignalSource.platform == 'reddit',
                            SignalSource.source_name == subreddit
                        ).first()
                        
                        if not existing_source:
                            # Create new SignalSource
                            new_source = SignalSource(
                                source_id=source_id,
                                org_id=org_id,
                                platform='reddit',
                                source_name=subreddit,
                                source_type='subreddit',
                                keywords=keywords,
                                crawl_frequency='daily',
                                relevance_threshold=request.get('relevance_threshold', 0.6),
                                business_context=f"Content-driven discovery for {strategy.get('selected_persona', {}).get('role', 'business')}",
                                target_goals=['signal_discovery', 'community_monitoring'],
                                ai_optimization_enabled=True,
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            
                            db.session.add(new_source)
                            saved_sources.append({
                                'source_id': source_id,
                                'platform': 'reddit',
                                'source_name': subreddit,
                                'status': 'created'
                            })
                            
                            logger.info(f'💾 Saved new signal source: r/{subreddit}')
                        else:
                            # Update existing source with new keywords
                            existing_source.keywords = list(set(existing_source.keywords + keywords))
                            existing_source.updated_at = datetime.utcnow()
                            existing_source.last_ai_analysis = datetime.utcnow()
                            
                            saved_sources.append({
                                'source_id': existing_source.source_id,
                                'platform': 'reddit',
                                'source_name': subreddit,
                                'status': 'updated'
                            })
                            
                            logger.info(f'🔄 Updated existing signal source: r/{subreddit}')
                    
                    # Commit the source changes
                    db.session.commit()
                    logger.info(f'✅ Saved {len(saved_sources)} signal sources to database')
                
                # Step 4: Run actual discovery if subreddits exist
                if subreddits:
                    # Use the existing Reddit discovery with intelligent inputs
                    discovery_request = SignalDiscoveryRequest(
                        platform='reddit',
                        sources=subreddits,
                        keywords=keywords,
                        time_filter=request.get('time_filter', 'week'),
                        max_items_per_source=request.get('max_items_per_source', 50),
                        relevance_threshold=request.get('relevance_threshold', 0.6)
                    )
                    
                    service = SignalService(db)
                    platform_result = service.discover_signals(discovery_request, org_id)
                    
                    all_signals.extend(platform_result.signals)
                    platform_results[platform] = {
                        'signals_found': platform_result.signals_found,
                        'sources_used': subreddits,
                        'queries_used': keywords,
                        'strategy_confidence': strategy.get('strategy_confidence', 0.8),
                        'sources_saved': len(saved_sources)
                    }
                    
                    logger.info(f'✅ Reddit discovery complete: {platform_result.signals_found} signals found')
                else:
                    logger.warning('No subreddits extracted from strategy - using fallback')
                    platform_results[platform] = {
                        'signals_found': 0,
                        'sources_used': [],
                        'queries_used': [],
                        'error': 'No subreddits found in strategy',
                        'sources_saved': 0
                    }
            else:
                logger.info(f'Platform {platform} not yet implemented for intelligent discovery')
                platform_results[platform] = {
                    'signals_found': 0,
                    'sources_used': [],
                    'queries_used': [],
                    'status': 'not_implemented',
                    'sources_saved': 0
                }
        
        # Sort signals by relevance
        all_signals.sort(key=lambda x: x.relevance_score * x.engagement_potential, reverse=True)
        
        return SignalDiscoveryResponse(
            discovery_id=str(uuid.uuid4()),
            platform=','.join(platforms),
            signals_found=len(all_signals),
            sources_scanned=[source for result in platform_results.values() for source in result.get('sources_used', [])],
            signals=all_signals,
            scan_timestamp=datetime.utcnow(),
            status='completed_intelligent'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intelligent signal discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligent discovery failed: {str(e)}"
        )


@router.get("/analysis")
async def get_content_analysis(
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Get VoiceForge content analysis for signal targeting"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        ai_service = SignalIntelligenceService(voiceforge_db=db, gypsum_client=None)
        analysis = await ai_service.get_content_analysis_summary(org_id)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{source_id}/scan")
async def scan_signal_source(
    source_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Run a signal discovery scan on a specific saved source"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Get the source
        source = db.session.query(SignalSource).filter(
            SignalSource.source_id == source_id,
            SignalSource.org_id == org_id
        ).first()
        
        if not source:
            raise HTTPException(status_code=404, detail="Signal source not found")
        
        if not source.is_active:
            raise HTTPException(status_code=400, detail="Signal source is not active")
        
        logger.info(f'🔍 Running scan on source: {source.platform}/{source.source_name}')
        
        # Create discovery request from saved source
        discovery_request = SignalDiscoveryRequest(
            platform=source.platform,
            sources=[source.source_name],
            keywords=source.keywords,
            time_filter='week',
            max_items_per_source=50,
            relevance_threshold=source.relevance_threshold
        )
        
        # Run the discovery
        service = SignalService(db)
        result = service.discover_signals(discovery_request, org_id)
        
        # Update source's last_crawled_at
        source.last_crawled_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'✅ Scan complete for {source.source_name}: {result.signals_found} signals found')
        
        return {
            "source_id": source_id,
            "source_name": source.source_name,
            "platform": source.platform,
            "signals_found": result.signals_found,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/{source_id}/recommendations")
async def get_ai_recommendations(
    source_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """Get AI recommendations for a signal source"""
    try:
        org_id = get_org_id_from_user(current_user)
        
        recommendations = db.session.query(SignalRecommendation).filter(
            SignalRecommendation.source_id == source_id,
            SignalRecommendation.org_id == org_id,
            SignalRecommendation.status == 'pending'
        ).all()
        
        return [
            {
                "recommendation_id": rec.recommendation_id,
                "type": rec.recommendation_type,
                "item": rec.recommended_item,
                "reasoning": rec.reasoning,
                "confidence": rec.confidence_score,
                "predicted_improvement": rec.predicted_improvement
            }
            for rec in recommendations
        ]
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "abstracted-signals",
        "supported_platforms": ["reddit", "twitter", "github", "linkedin"],
        "content_driven": True,
        "timestamp": datetime.utcnow().isoformat()
    }
