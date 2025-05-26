"""
Sample marketing templates for VoiceForge RAG system.
"""
import json
import uuid
from datetime import datetime
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.session import get_db_session
from database.db import Database

# Define sample templates
SAMPLE_TEMPLATES = [
    {
        "name": "Twitter Product Promotion",
        "description": "Short promotional tweet highlighting product features",
        "template_text": "✨ Introducing {{topic}}! {{key_points}} Learn more at our website. #{{platform}} #marketing",
        "platform": "twitter",
        "tone": "enthusiastic",
        "purpose": "promotion",
        "parameters": [
            {
                "name": "topic",
                "description": "The main product or feature being promoted",
                "default_value": "our new product"
            },
            {
                "name": "key_points",
                "description": "Key features or benefits to highlight",
                "default_value": "It's amazing and will transform how you work."
            }
        ],
        "created_by": "system"
    },
    {
        "name": "LinkedIn Company Update",
        "description": "Professional update for LinkedIn company page",
        "template_text": "Company Update: {{topic}}\n\n{{content}}\n\nLearn more about how we're innovating in this space. #{{platform}} #professional",
        "platform": "linkedin",
        "tone": "professional",
        "purpose": "announcement",
        "parameters": [
            {
                "name": "topic",
                "description": "The main subject of the update",
                "default_value": "our latest initiative"
            },
            {
                "name": "content",
                "description": "Detailed information about the update",
                "default_value": "We're excited to share our progress on this important project."
            }
        ],
        "created_by": "system"
    },
    {
        "name": "Email Newsletter",
        "description": "Email newsletter template with personalization",
        "template_text": "Subject: {{topic}} - Latest Updates\n\nHello,\n\nWe hope this email finds you well. Here's the latest on {{topic}}:\n\n{{key_points}}\n\nWant to learn more? Visit our website or reply to this email.\n\nBest regards,\nThe Team",
        "platform": "email",
        "tone": "friendly",
        "purpose": "newsletter",
        "parameters": [
            {
                "name": "topic",
                "description": "The main topic of the newsletter",
                "default_value": "our monthly updates"
            },
            {
                "name": "key_points",
                "description": "Bullet points of key information",
                "default_value": "- New features released\n- Upcoming events\n- Customer success stories"
            }
        ],
        "created_by": "system"
    },
    {
        "name": "Instagram Caption",
        "description": "Engaging caption for Instagram posts",
        "template_text": "✨ {{topic}} ✨\n\n{{content}}\n\n.\n.\n.\n#{{platform}} #trending #followus",
        "platform": "instagram",
        "tone": "casual",
        "purpose": "engagement",
        "parameters": [
            {
                "name": "topic",
                "description": "The main subject of the post",
                "default_value": "New collection"
            },
            {
                "name": "content",
                "description": "Main caption content",
                "default_value": "We're so excited to share this with you! Double tap if you love it as much as we do."
            }
        ],
        "created_by": "system"
    },
    {
        "name": "Customer Support Response",
        "description": "Template for responding to customer inquiries",
        "template_text": "Hi there,\n\nThank you for reaching out about {{topic}}. \n\n{{content}}\n\nPlease let me know if you have any other questions. We're here to help!\n\nBest regards,\nCustomer Support Team",
        "platform": "customer_support",
        "tone": "helpful",
        "purpose": "support",
        "parameters": [
            {
                "name": "topic",
                "description": "The customer's inquiry topic",
                "default_value": "your recent question"
            },
            {
                "name": "content",
                "description": "The main response to the inquiry",
                "default_value": "Here's the information you requested..."
            }
        ],
        "created_by": "system"
    }
]

def create_templates():
    """Create sample templates in the database."""
    # Initialize database connection
    db_session = get_db_session()
    db = Database(db_session)
    
    try:
        # Add each template
        for template_data in SAMPLE_TEMPLATES:
            # Add creation timestamp and ID
            template_data["id"] = str(uuid.uuid4())
            template_data["created_at"] = datetime.utcnow().isoformat()
            
            # Store template
            db.store_template(template_data)
            print(f"Created template: {template_data['name']}")
        
        print(f"Successfully created {len(SAMPLE_TEMPLATES)} templates")
        
    except Exception as e:
        print(f"Error creating templates: {str(e)}")
    finally:
        db_session.close()

if __name__ == "__main__":
    create_templates()
