"""
Content extractor for web pages.
"""
import logging
import re
import uuid
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse

from api.models import ContentType, ContentMetadata

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extract meaningful content from web pages."""
    
    def __init__(self):
        """Initialize the content extractor."""
        pass
    
    def extract(self, url: str, html: str, domain: str) -> Optional[Dict]:
        """
        Extract content from HTML.
        
        Args:
            url: The URL of the page
            html: The HTML content
            domain: The domain of the website
            
        Returns:
            Dict containing extracted content or None if no content was found
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            self._clean_html(soup)
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            main_content, content_type = self._extract_main_content(soup, url)
            if not main_content:
                logger.info(f"No main content found on {url}")
                return None
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url, content_type)
            
            # Generate a unique ID for this content
            content_id = str(uuid.uuid4())
            
            return {
                "content_id": content_id,
                "url": url,
                "domain": domain,
                "text": main_content,
                "html": str(soup),
                "metadata": metadata,
                "crawl_id": None,  # Will be set by the crawler
                "extracted_at": None  # Will be set by the crawler
            }
            
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {str(e)}")
            return None
    
    def _clean_html(self, soup: BeautifulSoup):
        """Remove unwanted elements from HTML."""
        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove script and style elements
        for tag in soup(["script", "style", "iframe", "noscript"]):
            tag.decompose()
        
        # Remove hidden elements
        for tag in soup.find_all(style=lambda value: value and "display:none" in value):
            tag.decompose()
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the title of the page."""
        # Try <title> tag first
        title_tag = soup.title
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try heading tags
        for heading in soup.find_all(["h1", "h2"]):
            text = heading.get_text().strip()
            if text:
                return text
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup, url: str) -> Tuple[Optional[str], ContentType]:
        """
        Extract the main content from the page.
        
        Returns:
            Tuple of (content_text, content_type)
        """
        content_type = self._identify_content_type(soup, url)
        
        # Try common content containers
        main_container = None
        
        # Try article tag
        article = soup.find("article")
        if article:
            main_container = article
        
        # Try main tag
        if not main_container:
            main_tag = soup.find("main")
            if main_tag:
                main_container = main_tag
        
        # Try common content div IDs/classes
        if not main_container:
            for id_value in ["content", "main-content", "post", "article"]:
                element = soup.find(id=id_value)
                if element:
                    main_container = element
                    break
            
            for class_value in ["content", "post", "article", "entry", "blog-post"]:
                element = soup.find(class_=class_value)
                if element:
                    main_container = element
                    break
        
        # Fallback to body if no container found
        if not main_container:
            main_container = soup.body
        
        if not main_container:
            return None, content_type
        
        # Extract text content
        paragraphs = []
        for p in main_container.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):
            text = p.get_text().strip()
            if text:
                paragraphs.append(text)
        
        # Join paragraphs into single text
        content = "\n\n".join(paragraphs)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content.strip(), content_type
    
    def _identify_content_type(self, soup: BeautifulSoup, url: str) -> ContentType:
        """Identify the type of content based on URL and HTML structure."""
        path = urlparse(url).path
        
        # Check URL path for clues
        if re.search(r'/blog/|/post/|/article/', path):
            return ContentType.BLOG_POST
        elif re.search(r'/product/|/shop/|/item/', path):
            return ContentType.PRODUCT_DESCRIPTION
        elif re.search(r'/about/', path):
            return ContentType.ABOUT_PAGE
        elif re.search(r'/news/|/press/', path):
            return ContentType.NEWS
        elif re.search(r'/faq/|/help/', path):
            return ContentType.FAQ
        elif re.search(r'/docs/|/documentation/', path):
            return ContentType.DOCUMENTATION
        
        # Check for product schemas
        if soup.find("div", {"itemtype": "http://schema.org/Product"}):
            return ContentType.PRODUCT_DESCRIPTION
        
        # Check for article schemas
        if soup.find("article") or soup.find("div", {"itemtype": "http://schema.org/Article"}):
            return ContentType.ARTICLE
        
        # Default to other
        return ContentType.OTHER
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str, content_type: ContentType) -> ContentMetadata:
        """Extract metadata from the page."""
        metadata = ContentMetadata(content_type=content_type)
        
        # Extract title
        metadata.title = self._extract_title(soup)
        
        # Extract author
        author_tag = soup.find("meta", {"name": "author"})
        if author_tag:
            metadata.author = author_tag.get("content")
        
        # Try schema.org author
        if not metadata.author:
            author_element = soup.find(itemprop="author")
            if author_element:
                metadata.author = author_element.get_text().strip()
        
        # Extract publication date
        date_tags = soup.find_all("meta", {"property": ["article:published_time", "og:published_time"]})
        if date_tags:
            try:
                metadata.publication_date = datetime.fromisoformat(date_tags[0].get("content").replace("Z", "+00:00"))
            except:
                pass
        
        # Extract last modified date
        modified_tags = soup.find_all("meta", {"property": ["article:modified_time", "og:updated_time"]})
        if modified_tags:
            try:
                metadata.last_modified = datetime.fromisoformat(modified_tags[0].get("content").replace("Z", "+00:00"))
            except:
                pass
        
        # Extract language
        lang_attr = soup.html.get("lang") if soup.html else None
        if lang_attr:
            metadata.language = lang_attr.split("-")[0]
        
        # Extract categories and tags
        for meta_tag in soup.find_all("meta", {"property": "article:section"}):
            metadata.categories.append(meta_tag.get("content"))
        
        for meta_tag in soup.find_all("meta", {"property": "article:tag"}):
            metadata.tags.append(meta_tag.get("content"))
        
        # Try to extract categories and tags from links
        category_links = soup.find_all("a", href=lambda href: href and "category" in href)
        for link in category_links:
            text = link.get_text().strip()
            if text and text not in metadata.categories:
                metadata.categories.append(text)
        
        tag_links = soup.find_all("a", href=lambda href: href and "tag" in href)
        for link in tag_links:
            text = link.get_text().strip()
            if text and text not in metadata.tags:
                metadata.tags.append(text)
        
        return metadata
