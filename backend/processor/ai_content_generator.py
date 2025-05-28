"""
AI-Powered Content Generator for VoiceForge RAG System
Uses OpenAI GPT to generate intelligent, contextual content
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """
    AI-powered content generator using OpenAI GPT for intelligent content creation
    """
    
    def __init__(self):
        """Initialize the AI content generator"""
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return
        
        try:
            # Initialize OpenAI client
            openai.api_key = api_key
            self.client = openai
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
    
    def _get_platform_constraints(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific constraints and guidelines"""
        constraints = {
            'twitter': {
                'max_length': 280,
                'style': 'concise, engaging, hashtag-friendly',
                'format': 'Keep it short and punchy. Use relevant hashtags.'
            },
            'linkedin': {
                'max_length': 3000,
                'style': 'professional, thought-leadership',
                'format': 'Professional tone with clear structure. Can include insights and calls to action.'
            },
            'facebook': {
                'max_length': 2000,
                'style': 'conversational, community-focused',
                'format': 'Engaging and conversational. Encourage interaction.'
            },
            'instagram': {
                'max_length': 2200,
                'style': 'visual-focused, story-driven',
                'format': 'Visual storytelling approach. Include relevant hashtags.'
            },
            'email': {
                'max_length': 5000,
                'style': 'direct, actionable',
                'format': 'Clear subject line equivalent. Professional structure with clear call to action.'
            },
            'blog': {
                'max_length': 10000,
                'style': 'informative, detailed',
                'format': 'Comprehensive content with clear structure, headings, and detailed explanations.'
            },
            'website': {
                'max_length': 3000,
                'style': 'clear, informative',
                'format': 'Clear, scannable content optimized for web reading.'
            },
            'customer_support': {
                'max_length': 1000,
                'style': 'helpful, empathetic',
                'format': 'Helpful and solution-focused. Address concerns directly.'
            }
        }
        
        return constraints.get(platform, {
            'max_length': 2000,
            'style': 'clear, informative',
            'format': 'Clear and well-structured content.'
        })
    
    def _build_prompt(
        self, 
        query: str, 
        platform: str, 
        tone: str, 
        chunks: List[Dict[str, Any]]
    ) -> str:
        """Build a comprehensive prompt for the AI"""
        
        # Get platform constraints
        constraints = self._get_platform_constraints(platform)
        
        # Extract relevant content from chunks
        context_content = []
        for i, chunk in enumerate(chunks[:5], 1):  # Use top 5 chunks
            similarity = chunk.get('similarity', 0)
            text = chunk.get('text', '')[:500]  # Limit chunk length
            context_content.append(f"Source {i} (relevance: {similarity:.2f}):\n{text}")
        
        context = "\n\n".join(context_content)
        
        # Build the prompt
        prompt = f"""You are a world-class content creator and copywriter specializing in {platform} content. You create engaging, persuasive content that drives action.

USER REQUEST: "{query}"

PLATFORM: {platform}
TONE: {tone}
MAX LENGTH: {constraints['max_length']} characters
STYLE: {constraints['style']}
FORMAT GUIDELINES: {constraints['format']}

COMPANY INFORMATION (use as primary source):
{context}

WRITING INSTRUCTIONS:
1. Write compelling, high-quality {platform} content that directly addresses the user's request
2. Use the company information as your primary source - be accurate and factual
3. Write in a {tone} tone that's perfect for {platform}
4. Stay within {constraints['max_length']} characters
5. Make it engaging, clear, and actionable
6. Use strong, active verbs and compelling language
7. Include a clear value proposition or benefit
8. For Twitter: Use 1-2 strategic hashtags and make it shareable
9. For LinkedIn: Be thought-provoking and professional
10. For Blog: Use clear structure with compelling hooks
11. Focus on benefits to the reader, not just features
12. Make every word count - be concise but impactful

Write exceptional {platform} content now:"""
        
        return prompt
    
    def generate_content(
        self,
        query: str,
        platform: str,
        tone: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered content using OpenAI GPT
        
        Args:
            query: User's content request
            platform: Target platform (twitter, linkedin, etc.)
            tone: Desired tone (professional, casual, etc.)
            chunks: Retrieved relevant content chunks
            
        Returns:
            Generated content with metadata
        """
        
        if not self.client:
            logger.error("OpenAI client not available")
            return {
                "text": "AI content generation is not available. Please check your OpenAI API configuration.",
                "source_chunks": [],
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "error": "openai_not_configured"
                }
            }
        
        if not chunks:
            return {
                "text": f"I couldn't find relevant information to create content about '{query}'. Please try a different topic or ensure your content has been processed.",
                "source_chunks": [],
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "error": "no_source_content"
                }
            }
        
        try:
            # Build the prompt
            prompt = self._build_prompt(query, platform, tone, chunks)
            
            logger.info(f"Generating AI content for query: {query}")
            logger.info(f"Using {len(chunks)} source chunks")
            
            # Call OpenAI API with optimized settings for better writing
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Better quality than gpt-3.5-turbo
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are an expert copywriter and content strategist who creates exceptional {platform} content. Your writing is engaging, persuasive, and drives action. You excel at turning technical information into compelling narratives that resonate with audiences."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,  # More space for quality content
                temperature=0.8,  # More creativity for engaging content
                top_p=0.9,
                presence_penalty=0.1,  # Encourage diverse language
                frequency_penalty=0.1   # Reduce repetition
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            # Get platform constraints for validation
            constraints = self._get_platform_constraints(platform)
            
            # Check length and provide feedback
            if len(generated_text) > constraints['max_length']:
                logger.info(f"Content generated for {platform}: {len(generated_text)} chars (exceeds {constraints['max_length']} limit by {len(generated_text) - constraints['max_length']} chars - consider editing)")
            else:
                logger.info(f"Content generated for {platform}: {len(generated_text)} chars (within {constraints['max_length']} limit)")
            
            # Prepare source chunks for response
            source_chunks = [
                {
                    "chunk_id": chunk["id"],
                    "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                    "similarity": chunk.get("similarity", 0.0),
                    "content_id": chunk.get("content_id")
                }
                for chunk in chunks
            ]
            
            result = {
                "text": generated_text,
                "source_chunks": source_chunks,
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "character_count": len(generated_text),
                    "character_limit": constraints['max_length'],
                    "model_used": "gpt-4o-mini",
                    "chunks_used": len(chunks)
                }
            }
            
            logger.info(f"Successfully generated {len(generated_text)} character content for {platform}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate AI content: {str(e)}")
            return {
                "text": f"Sorry, I encountered an error while generating content: {str(e)}",
                "source_chunks": [],
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "error": str(e)
                }
            }
