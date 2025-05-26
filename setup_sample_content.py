#!/usr/bin/env python3
"""
Quick Setup for VoiceForge RAG Testing
Adds sample content if database is empty
"""

import os
import sys
from datetime import datetime

# Load environment
def load_env_file():
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Add backend to path
backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
sys.path.append(backend_path)

def add_sample_content():
    """Add sample content for testing"""
    print("📝 Adding sample content for RAG testing...")
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from database.db import Database
        from processor.rag import RAGSystem
        import uuid
        
        session = get_db_session()
        db = Database(session)
        
        # Check if we already have content
        content_count = session.query(Content).count()
        if content_count > 0:
            print(f"✅ Database already has {content_count} content items")
            session.close()
            return True
        
        # Sample content about AI and technology
        sample_contents = [
            {
                "title": "What is Artificial Intelligence?",
                "content": """Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation. Modern AI includes machine learning, deep learning, and neural networks that enable computers to improve their performance on specific tasks through experience.""",
                "url": "https://example.com/ai-intro",
                "domain": "https://example.com",
                "content_type": "article"
            },
            {
                "title": "Machine Learning Fundamentals",
                "content": """Machine Learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. ML algorithms build mathematical models based on training data to make predictions or decisions. Common types include supervised learning (learning with labeled examples), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error with rewards).""",
                "url": "https://example.com/ml-basics",
                "domain": "https://example.com",
                "content_type": "article"
            },
            {
                "title": "Natural Language Processing",
                "content": """Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret, and manipulate human language. NLP combines computational linguistics with statistical, machine learning, and deep learning models. Applications include chatbots, language translation, sentiment analysis, text summarization, and speech recognition. Modern NLP uses transformer models like GPT and BERT for advanced language understanding.""",
                "url": "https://example.com/nlp-guide",
                "domain": "https://example.com",
                "content_type": "guide"
            },
            {
                "title": "Deep Learning and Neural Networks",
                "content": """Deep Learning is a subset of machine learning that uses neural networks with multiple layers (hence 'deep') to analyze and learn from data. These artificial neural networks are inspired by the human brain's structure and function. Deep learning excels at tasks like image recognition, natural language processing, and game playing. Popular frameworks include TensorFlow, PyTorch, and Keras, which make building deep learning models more accessible.""",
                "url": "https://example.com/deep-learning",
                "domain": "https://example.com", 
                "content_type": "article"
            },
            {
                "title": "AI Ethics and Future Impact",
                "content": """As artificial intelligence becomes more prevalent, ethical considerations become crucial. Key concerns include bias in AI systems, job displacement, privacy protection, and ensuring AI benefits all of humanity. Responsible AI development requires transparency, fairness, accountability, and human oversight. The future of AI includes potential breakthroughs in healthcare, climate change solutions, education, and scientific research, but requires careful consideration of societal impacts.""",
                "url": "https://example.com/ai-ethics",
                "domain": "https://example.com",
                "content_type": "article"
            }
        ]
        
        # Add content to database
        content_ids = []
        for content_data in sample_contents:
            content_id = str(uuid.uuid4())
            
            # Create content record
            content = Content(
                id=content_id,
                url=content_data["url"],
                title=content_data["title"],
                text=content_data["content"],  # Use 'text' field, not 'content'
                content_type=content_data["content_type"],
                domain=content_data["domain"],
                crawl_id="sample-crawl-" + str(uuid.uuid4())[:8],
                extracted_at=datetime.utcnow()
            )
            
            session.add(content)
            content_ids.append(content_id)
        
        session.commit()
        print(f"✅ Added {len(sample_contents)} content items")
        
        # Process content for RAG
        print("🔄 Processing content for RAG...")
        rag_system = RAGSystem(db)
        
        for content_id in content_ids:
            success = rag_system.process_content_for_rag(content_id)
            if success:
                print(f"   ✅ Processed content {content_id[:8]}...")
            else:
                print(f"   ❌ Failed to process content {content_id[:8]}...")
        
        session.close()
        
        print("🎉 Sample content setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to add sample content: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 VoiceForge RAG Quick Setup")
    print("=" * 30)
    
    success = add_sample_content()
    
    if success:
        print("\n✅ Setup complete! Your RAG system is ready for testing.")
        print("\n🧪 Next steps:")
        print("   1. Run: python test_integration.py")
        print("   2. Start the application: ./start_voiceforge.sh")
        print("   3. Test content generation in the frontend")
    else:
        print("\n❌ Setup failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
