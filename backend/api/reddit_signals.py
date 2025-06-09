"""
Reddit Signal Discovery API
Integrates Reddit Scanner functionality into VoiceForge for signal-based content generation
"""

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from auth.clerk_auth import get_current_user_with_org, get_org_id_from_user, AuthUser
from api.dependencies import get_db, get_rag_service
from processor.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reddit-signals", tags=["reddit-signals"])


# Pydantic models for request/response
class RedditDiscoveryRequest(BaseModel):
    """Request model for Reddit signal discovery"""
    subreddits: List[str] = Field(..., description="List of subreddits to scan")
    keywords: List[str] = Field(default=[], description="Keywords to search for")
    time_filter: str = Field(default="week", description="Time filter: day, week, month, year, all")
    max_posts_per_subreddit: int = Field(default=50, description="Maximum posts per subreddit")
    relevance_threshold: float = Field(default=0.6, description="Minimum relevance score (0-1)")


class RedditSignal(BaseModel):
    """Reddit signal response model"""
    signal_id: str
    thread_id: str
    subreddit: str
    title: str
    content: str
    url: str
    author: str
    score: int
    num_comments: int
    created_at: datetime
    relevance_score: float
    signal_type: str
    engagement_potential: float
    top_comments: List[str] = []


class RedditDiscoveryResponse(BaseModel):
    """Response model for Reddit discovery"""
    discovery_id: str
    signals_found: int
    subreddits_scanned: List[str]
    signals: List[RedditSignal]
    scan_timestamp: datetime
    status: str


class ContentGenerationRequest(BaseModel):
    """Request for generating content from Reddit signal"""
    signal_id: str
    platform: str = Field(default="reddit", description="Target platform for response")
    tone: str = Field(default="professional", description="Tone for generated content")
    response_type: str = Field(default="comment_reply", description="Type of response")
    include_context: bool = Field(default=True, description="Include signal context in generation")


class GeneratedSignalResponse(BaseModel):
    """Response model for generated content from signal"""
    signal_id: str
    generated_content: str
    response_type: str
    platform: str
    tone: str
    confidence_score: float
    source_signal: RedditSignal
    metadata: Dict[str, Any]


class RedditSignalService:
    """Service for Reddit signal discovery and processing"""
    
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def discover_reddit_signals(
        self, 
        request: RedditDiscoveryRequest, 
        org_id: str
    ) -> RedditDiscoveryResponse:
        """
        Discover signals from Reddit using public JSON API (fallback to PRAW later)
        """
        try:
            import requests
            from urllib.parse import quote
            
            signals = []
            
            for subreddit in request.subreddits:
                try:
                    # Use public Reddit JSON API for now
                    for keyword in request.keywords:
                        # Use general Reddit search instead of subreddit-specific
                        url = "https://www.reddit.com/search.json"
                        params = {
                            'q': f"{keyword} subreddit:{subreddit}",
                            't': request.time_filter,
                            'sort': 'relevance',
                            'limit': min(request.max_posts_per_subreddit, 25)
                        }
                        
                        headers = {
                            'User-Agent': 'VoiceForge Signal Discovery Bot v1.0'
                        }
                        
                        self.logger.info(f"Searching Reddit for '{keyword}' in r/{subreddit}")
                        response = requests.get(url, params=params, headers=headers)
                        
                        if response.status_code == 200:
                            data = response.json()
                            posts = data.get('data', {}).get('children', [])
                            
                            self.logger.info(f"Found {len(posts)} posts for '{keyword}' in r/{subreddit}")
                            
                            for post_data in posts:
                                post = post_data.get('data', {})
                                
                                # Only include posts from the target subreddit
                                if post.get('subreddit', '').lower() == subreddit.lower():
                                    # Calculate relevance score
                                    relevance_score = self._calculate_relevance_score_public(post, request.keywords)
                                    
                                    if relevance_score >= request.relevance_threshold:
                                        signal = RedditSignal(
                                            signal_id=f"reddit_{post['id']}_{org_id}",
                                            thread_id=post['id'],
                                            subreddit=post['subreddit'],
                                            title=post['title'],
                                            content=post.get('selftext', ''),
                                            url=f"https://www.reddit.com{post['permalink']}",
                                            author=str(post.get('author', 'unknown')),
                                            score=int(post.get('score', 0)),
                                            num_comments=int(post.get('num_comments', 0)),
                                            created_at=datetime.fromtimestamp(post['created_utc']),
                                            relevance_score=relevance_score,
                                            signal_type=self._classify_signal_type_public(post),
                                            engagement_potential=self._calculate_engagement_potential_public(post),
                                            top_comments=[]
                                        )
                                        signals.append(signal)
                        else:
                            self.logger.warning(f"Reddit search failed: HTTP {response.status_code}")
                            
                except Exception as e:
                    self.logger.error(f"Error collecting from r/{subreddit}: {str(e)}")
                    continue
            
            # Sort by relevance and engagement potential
            signals.sort(key=lambda x: x.relevance_score * x.engagement_potential, reverse=True)
            
            # Store signals in database for later use
            self._store_signals(signals, org_id)
            
            return RedditDiscoveryResponse(
                discovery_id=str(uuid.uuid4()),
                signals_found=len(signals),
                subreddits_scanned=request.subreddits,
                signals=signals,
                scan_timestamp=datetime.utcnow(),
                status="completed"
            )
            
        except Exception as e:
            self.logger.error(f"Error discovering Reddit signals: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to discover Reddit signals: {str(e)}"
            )
    
    def generate_response_for_signal(
        self, 
        request: ContentGenerationRequest, 
        org_id: str,
        rag_service: RAGService
    ) -> GeneratedSignalResponse:
        """
        Generate a response for a discovered Reddit signal using VoiceForge RAG
        """
        try:
            # Retrieve the signal from storage
            signal = self._get_signal(request.signal_id, org_id)
            if not signal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Signal {request.signal_id} not found"
                )
            
            # Build context for RAG generation
            signal_context = f"""
            Reddit Signal Context:
            Subreddit: r/{signal.subreddit}
            Title: {signal.title}
            Content: {signal.content}
            Author: {signal.author}
            Engagement: {signal.score} upvotes, {signal.num_comments} comments
            
            Top Comments:
            {chr(10).join(['- ' + comment for comment in signal.top_comments])}
            
            Signal Type: {signal.signal_type}
            """
            
            # Create enhanced query for RAG system
            if request.include_context:
                rag_query = f"{signal.title}\n\n{signal.content}\n\nContext: This is a {signal.signal_type} from r/{signal.subreddit}. Generate a helpful response that addresses the original post."
            else:
                rag_query = f"{signal.title}\n{signal.content}"
            
            # Use VoiceForge RAG system to generate response
            from processor.rag import RAGSystem
            rag_system = RAGSystem(self.db)
            
            rag_response = rag_system.process_and_generate(
                query=rag_query,
                platform=request.platform,
                tone=request.tone,
                org_id=org_id
            )
            
            # Calculate confidence score based on RAG confidence and signal relevance
            confidence_score = (
                rag_response.get('metadata', {}).get('confidence', 0.8) * 0.7 +
                signal.relevance_score * 0.3
            )
            
            # Create enhanced response
            generated_response = GeneratedSignalResponse(
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
                    'signal_engagement': {
                        'score': signal.score,
                        'comments': signal.num_comments,
                        'engagement_potential': signal.engagement_potential
                    }
                }
            )
            
            # Store the generated response
            self._store_generated_response(generated_response, org_id)
            
            return generated_response
            
        except Exception as e:
            self.logger.error(f"Error generating response for signal: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate response: {str(e)}"
            )
    
    def _calculate_relevance_score_public(self, post: dict, keywords: List[str]) -> float:
        """Calculate relevance score for a Reddit post from public API"""
        score = 0.0
        
        # Base score from engagement metrics
        upvote_score = min(post.get('score', 0) / 100, 1.0)  # Normalize to 0-1
        comment_score = min(post.get('num_comments', 0) / 50, 1.0)  # Normalize to 0-1
        engagement_score = (upvote_score + comment_score) / 2
        
        # Keyword relevance score
        keyword_score = 0.0
        if keywords:
            title_text = str(post.get('title', '')).lower()
            content_text = str(post.get('selftext', '')).lower()
            combined_text = f"{title_text} {content_text}"
            
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            keyword_score = min(keyword_matches / len(keywords), 1.0)
        else:
            keyword_score = 1.0  # No keywords specified, so everything is relevant
        
        # Time recency score (newer posts get higher scores)
        try:
            post_age_hours = (datetime.utcnow() - datetime.fromtimestamp(post.get('created_utc', 0))).total_seconds() / 3600
            recency_score = max(0, 1 - (post_age_hours / (7 * 24)))  # Decay over a week
        except:
            recency_score = 0.5
        
        # Weighted combination
        score = (
            engagement_score * 0.4 +
            keyword_score * 0.4 +
            recency_score * 0.2
        )
        
        return min(max(score, 0.0), 1.0)
    
    def _classify_signal_type_public(self, post: dict) -> str:
        """Classify the type of Reddit signal from public API data"""
        title = str(post.get('title', '')).lower()
        content = str(post.get('selftext', '')).lower()
        combined = f"{title} {content}"
        
        # Simple rule-based classification
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
    
    def _calculate_engagement_potential_public(self, post: dict) -> float:
        """Calculate potential for engagement based on Reddit metrics from public API"""
        # Factors: score, comments, time since posted
        score_factor = min(post.get('score', 0) / 50, 1.0)  # Normalize
        comment_factor = min(post.get('num_comments', 0) / 25, 1.0)  # Normalize
        
        # Time factor - newer posts have higher potential
        try:
            hours_old = (datetime.utcnow() - datetime.fromtimestamp(post.get('created_utc', 0))).total_seconds() / 3600
            time_factor = max(0, 1 - (hours_old / 48))  # Decay over 48 hours
        except:
            time_factor = 0.5
        
        return (score_factor + comment_factor + time_factor) / 3
    
    def _store_signals(self, signals: List[RedditSignal], org_id: str):
        """Store discovered signals in database"""
        try:
            for signal in signals:
                # Convert to database format and store
                signal_data = {
                    'signal_id': signal.signal_id,
                    'org_id': org_id,
                    'platform': 'reddit',
                    'thread_id': signal.thread_id,
                    'subreddit': signal.subreddit,
                    'title': signal.title,
                    'content': signal.content,
                    'url': signal.url,
                    'author': signal.author,
                    'score': signal.score,
                    'num_comments': signal.num_comments,
                    'created_at': signal.created_at,
                    'relevance_score': signal.relevance_score,
                    'signal_type': signal.signal_type,
                    'engagement_potential': signal.engagement_potential,
                    'top_comments': signal.top_comments,
                    'discovered_at': datetime.utcnow()
                }
                
                # Store in database (implement based on your schema)
                self.db.store_reddit_signal(signal_data)
                
        except Exception as e:
            self.logger.warning(f"Failed to store signals: {str(e)}")
    
    def _get_signal(self, signal_id: str, org_id: str) -> Optional[RedditSignal]:
        """Retrieve a signal from storage"""
        try:
            signal_data = self.db.get_reddit_signal(signal_id, org_id)
            if signal_data:
                return RedditSignal(**signal_data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve signal: {str(e)}")
            return None
    
    def _store_generated_response(self, response: GeneratedSignalResponse, org_id: str):
        """Store generated response for analytics"""
        try:
            response_data = {
                'signal_id': response.signal_id,
                'org_id': org_id,
                'generated_content': response.generated_content,
                'response_type': response.response_type,
                'platform': response.platform,
                'tone': response.tone,
                'confidence_score': response.confidence_score,
                'metadata': response.metadata,
                'generated_at': datetime.utcnow()
            }
            
            # Store in database
            self.db.store_signal_response(response_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to store generated response: {str(e)}")


# API endpoints
@router.post("/discover", response_model=RedditDiscoveryResponse)
async def discover_reddit_signals(
    request: RedditDiscoveryRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Discover relevant signals from Reddit
    
    This endpoint scans specified subreddits for relevant content that could
    be turned into marketing opportunities or content ideas.
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        service = RedditSignalService(db)
        result = service.discover_reddit_signals(request, org_id)
        
        logger.info(f"Discovered {result.signals_found} Reddit signals for org {org_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to discover Reddit signals: {str(e)}")
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
    Generate a response for a discovered Reddit signal
    
    Uses VoiceForge's RAG system to generate contextually appropriate
    responses to Reddit signals based on your organization's content.
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        service = RedditSignalService(db)
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


@router.get("/signals", response_model=List[RedditSignal])
async def list_signals(
    limit: int = 20,
    offset: int = 0,
    signal_type: Optional[str] = None,
    subreddit: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    List discovered Reddit signals with filtering
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Get signals from database with filters
        signals_data = db.list_reddit_signals(
            org_id=org_id,
            limit=limit,
            offset=offset,
            signal_type=signal_type,
            subreddit=subreddit
        )
        
        signals = [RedditSignal(**data) for data in signals_data]
        return signals
        
    except Exception as e:
        logger.error(f"Failed to list signals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list signals: {str(e)}"
        )


@router.get("/signals/{signal_id}", response_model=RedditSignal)
async def get_signal(
    signal_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Get a specific Reddit signal by ID
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        service = RedditSignalService(db)
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


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reddit-signals",
        "timestamp": datetime.utcnow().isoformat()
    }
