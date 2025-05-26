#!/usr/bin/env python3
"""
Add Sample Content for RAG Testing
Adds sample content to test the RAG system functionality
"""

import os
import sys
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sample_content():
    """Add sample content for RAG testing"""
    session = get_db_session()
    
    sample_contents = [
        {
            'title': 'Introduction to Artificial Intelligence',
            'url': 'https://example.com/ai-intro',
            'content': '''
            Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.

            The ideal characteristic of artificial intelligence is its ability to rationalize and take actions that have the best chance of achieving a specific goal. A subset of artificial intelligence is machine learning, which refers to the concept that computer programs can automatically learn from and adapt to new data without being assisted by humans.

            AI applications include expert systems, natural language processing, speech recognition and machine vision. Modern AI techniques include deep learning, neural networks, and natural language processing which enable computers to understand, interpret and generate human language.

            The field of AI research was born at a Dartmouth College workshop in 1956. AI has experienced several waves of optimism, followed by disappointment and the loss of funding, followed by new approaches, success and renewed funding.
            ''',
            'content_type': 'article'
        },
        {
            'title': 'Web Development Best Practices',
            'url': 'https://example.com/web-dev-practices',
            'content': '''
            Web development best practices are essential for creating robust, scalable, and maintainable web applications. Here are key principles every developer should follow:

            1. Semantic HTML: Use HTML elements according to their intended purpose. This improves accessibility and SEO.

            2. Responsive Design: Ensure your website works well on all devices and screen sizes using CSS media queries and flexible layouts.

            3. Performance Optimization: Minimize HTTP requests, optimize images, use CDNs, and implement caching strategies to improve load times.

            4. Security: Always validate and sanitize user input, use HTTPS, implement proper authentication and authorization, and keep dependencies updated.

            5. Accessibility: Follow WCAG guidelines to make your site usable by people with disabilities. Use proper heading structure, alt text for images, and keyboard navigation.

            6. Code Organization: Use consistent naming conventions, modular code structure, and version control systems like Git.

            7. Testing: Implement unit tests, integration tests, and end-to-end tests to ensure code quality and catch bugs early.

            8. Browser Compatibility: Test your application across different browsers and implement progressive enhancement.
            ''',
            'content_type': 'article'
        },
        {
            'title': 'Database Optimization Techniques',
            'url': 'https://example.com/database-optimization',
            'content': '''
            Database optimization is crucial for maintaining high-performance applications. Here are key techniques to optimize database performance:

            1. Indexing: Create appropriate indexes on frequently queried columns. However, avoid over-indexing as it can slow down write operations.

            2. Query Optimization: Write efficient SQL queries, avoid SELECT *, use appropriate JOIN types, and leverage query execution plans.

            3. Normalization vs Denormalization: Apply proper normalization to reduce redundancy, but consider denormalization for read-heavy workloads.

            4. Connection Pooling: Use connection pools to manage database connections efficiently and reduce connection overhead.

            5. Caching: Implement caching strategies at different levels - query result caching, object caching, and distributed caching.

            6. Partitioning: Divide large tables into smaller, more manageable pieces based on specific criteria like date ranges or geographic regions.

            7. Regular Maintenance: Perform regular database maintenance tasks like updating statistics, rebuilding indexes, and cleaning up unused data.

            8. Monitoring: Continuously monitor database performance using tools to identify bottlenecks and optimize accordingly.

            For PostgreSQL specifically, consider using pgvector for efficient vector similarity searches and enable query parallelization for complex analytical queries.
            ''',
            'content_type': 'article'
        },
        {
            'title': 'Cloud Computing Fundamentals',
            'url': 'https://example.com/cloud-computing',
            'content': '''
            Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the Internet to offer faster innovation, flexible resources, and economies of scale.

            Key characteristics of cloud computing include:

            1. On-demand self-service: Users can provision computing capabilities automatically without requiring human interaction with service providers.

            2. Broad network access: Services are available over the network and accessed through standard mechanisms.

            3. Resource pooling: Computing resources are pooled to serve multiple consumers using a multi-tenant model.

            4. Rapid elasticity: Capabilities can be elastically provisioned and released to scale rapidly with demand.

            5. Measured service: Cloud systems automatically control and optimize resource use by leveraging metering capabilities.

            Service Models:
            - Infrastructure as a Service (IaaS): Provides virtualized computing resources over the internet
            - Platform as a Service (PaaS): Provides a platform allowing customers to develop, run, and manage applications
            - Software as a Service (SaaS): Delivers software applications over the internet on a subscription basis

            Major cloud providers include Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), and IBM Cloud.
            ''',
            'content_type': 'article'
        },
        {
            'title': 'React Development Guide',
            'url': 'https://example.com/react-guide',
            'content': '''
            React is a popular JavaScript library for building user interfaces, particularly single-page applications. Here's a comprehensive guide to React development:

            Core Concepts:

            1. Components: React applications are built using components, which are reusable pieces of UI. Components can be functional or class-based.

            2. JSX: JavaScript XML allows you to write HTML-like syntax in JavaScript, making component development more intuitive.

            3. Props: Properties are used to pass data from parent to child components, enabling component reusability.

            4. State: State management allows components to maintain and update their internal data.

            5. Hooks: Introduced in React 16.8, hooks allow you to use state and lifecycle features in functional components.

            Best Practices:
            - Use functional components with hooks over class components
            - Implement proper key props for list items
            - Use React.memo for performance optimization
            - Follow the single responsibility principle for components
            - Implement proper error boundaries
            - Use TypeScript for better type safety

            Popular React ecosystem tools include Redux for state management, React Router for navigation, and Next.js for server-side rendering.

            Testing React applications can be done using Jest and React Testing Library for unit and integration tests.
            ''',
            'content_type': 'article'
        }
    ]
    
    try:
        added_count = 0
        for content_data in sample_contents:
            # Check if content already exists
            existing = session.query(Content).filter(Content.url == content_data['url']).first()
            if existing:
                logger.info(f"Content already exists: {content_data['title']}")
                continue
            
            # Create new content
            content = Content(
                title=content_data['title'],
                url=content_data['url'],
                content=content_data['content'].strip(),
                content_type=content_data['content_type'],
                domain=content_data['url'].split('/')[2],
                created_at=datetime.utcnow(),
                processed=False  # Will be processed by the RAG system
            )
            
            session.add(content)
            added_count += 1
            logger.info(f"Added content: {content_data['title']}")
        
        session.commit()
        logger.info(f"✅ Successfully added {added_count} sample content items")
        
        if added_count > 0:
            logger.info("\n📋 Next Steps:")
            logger.info("   1. Process content: python scripts/process_content_for_rag.py")
            logger.info("   2. Optimize vector DB: python scripts/optimize_vector_db.py")
            logger.info("   3. Test RAG pipeline: python scripts/test_full_rag_pipeline.py")
        
        return added_count
        
    except Exception as e:
        logger.error(f"Error adding sample content: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def main():
    """Main function"""
    logger.info("🚀 Adding Sample Content for RAG Testing")
    logger.info("=" * 40)
    
    count = add_sample_content()
    
    if count > 0:
        logger.info(f"\n🎉 Added {count} sample content items!")
        logger.info("Your VoiceForge RAG system now has content to work with.")
    else:
        logger.info("\n📄 No new content added (may already exist)")

if __name__ == "__main__":
    main()
