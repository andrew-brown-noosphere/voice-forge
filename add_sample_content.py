#!/usr/bin/env python3
"""
Quick setup script to add sample content for testing.
"""

import sys
import os
import uuid
from datetime import datetime

# Add backend to path
backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
sys.path.append(backend_path)

# Load environment
env_path = os.path.join(backend_path, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def add_sample_content():
    """Add sample content for testing content generation."""
    print("🧪 ADDING SAMPLE CONTENT FOR TESTING")
    print("=" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Crawl, Content, ContentChunk
        import json
        
        session = get_db_session()
        
        # Sample content
        sample_content = [
            {
                "title": "Content Generation Best Practices",
                "domain": "example.com",
                "url": "https://example.com/content-generation",
                "content_type": "blog_post",
                "text": """Content generation is the process of creating written material using various techniques and tools. 
                Modern content generation often involves AI and machine learning to produce high-quality, relevant content at scale.
                
                Key principles include understanding your audience, maintaining consistency in tone and style, and ensuring accuracy.
                Content should be engaging, informative, and provide value to readers. Whether for marketing, education, or entertainment,
                effective content generation requires careful planning and execution.
                
                Tools and technologies have evolved significantly, allowing creators to produce content more efficiently while maintaining quality.
                The integration of AI assists in research, drafting, and optimization processes."""
            },
            {
                "title": "RAG Systems and Information Retrieval",
                "domain": "example.com", 
                "url": "https://example.com/rag-systems",
                "content_type": "article",
                "text": """Retrieval-Augmented Generation (RAG) systems combine the power of information retrieval with text generation.
                These systems first search through a knowledge base to find relevant information, then use that context to generate responses.
                
                RAG is particularly useful for creating content that needs to be factual and grounded in specific knowledge.
                By retrieving relevant documents or chunks of text, the system can produce more accurate and contextually appropriate content.
                
                The process typically involves three steps: retrieving relevant information, ranking the results by relevance,
                and then generating content that incorporates the most useful retrieved information. This approach helps ensure
                that generated content is both informative and accurate."""
            },
            {
                "title": "Digital Marketing and Communication",
                "domain": "marketing-example.com",
                "url": "https://marketing-example.com/digital-strategies", 
                "content_type": "guide",
                "text": """Digital marketing encompasses various strategies for reaching audiences through online channels.
                Content marketing, social media engagement, and email campaigns are fundamental components of modern marketing.
                
                Effective communication requires understanding your target audience and crafting messages that resonate with their needs.
                The tone and style should align with your brand identity while remaining accessible to your intended readers.
                
                Personalization and relevance are crucial factors in successful digital marketing campaigns.
                Data-driven insights help optimize content for better engagement and conversion rates.
                The integration of technology allows for more sophisticated targeting and measurement of campaign effectiveness."""
            }
        ]
        
        # Create a sample crawl
        crawl_id = str(uuid.uuid4())
        org_id = "test-org-001"  # Sample org ID
        
        crawl = Crawl(
            id=crawl_id,
            org_id=org_id,
            domain="example.com",
            state="completed",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            config={"max_pages": 10, "max_depth": 2, "delay": 1},
            pages_crawled=len(sample_content),
            pages_discovered=len(sample_content),
            content_extracted=len(sample_content)
        )
        session.add(crawl)
        
        print(f"📊 Creating sample crawl: {crawl_id}")
        
        # Add sample content
        content_objects = []
        for i, content_data in enumerate(sample_content):
            content_id = str(uuid.uuid4())
            
            content_obj = Content(
                id=content_id,
                org_id=org_id,
                url=content_data["url"],
                domain=content_data["domain"],
                crawl_id=crawl_id,
                extracted_at=datetime.utcnow(),
                text=content_data["text"],
                title=content_data["title"],
                content_type=content_data["content_type"],
                is_processed=False
            )
            
            session.add(content_obj)
            content_objects.append(content_obj)
            print(f"   📄 Added: {content_data['title']}")
        
        # Commit to database
        session.commit()
        
        print(f"\n✅ Added {len(sample_content)} sample content items!")
        print(f"🎯 Now run: python3 process_simple.py")
        print(f"📊 Then test: python3 debug_focused_content_generation.py")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample content: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_sample_content()
    if success:
        print("\n🚀 Sample content added successfully!")
        print("Next steps:")
        print("1. python3 process_simple.py")
        print("2. python3 debug_focused_content_generation.py")
    else:
        print("\n❌ Failed to add sample content")
