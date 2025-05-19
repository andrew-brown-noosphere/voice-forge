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
        for tag in soup(["script", "style", "iframe", "noscript", "header", "footer", "nav"]):
            tag.decompose()
        
        # Remove hidden elements
        for tag in soup.find_all(style=lambda value: value and "display:none" in value):
            tag.decompose()
        
        # Remove social media widgets
        for tag in soup.find_all(class_=lambda c: c and any(social in c.lower() for social in ['social', 'share', 'twitter', 'facebook', 'linkedin'])):
            tag.decompose()
        
        # Remove navigation elements
        for tag in soup.find_all(id=lambda i: i and any(nav in i.lower() for nav in ['nav', 'menu', 'header', 'footer'])):
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
            for id_value in ["content", "main-content", "post", "article", "entry-content", "post-content"]:
                element = soup.find(id=id_value)
                if element:
                    main_container = element
                    break
            
            for class_value in ["content", "post", "article", "entry", "blog-post", "post-content", "entry-content"]:
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
        
        # Remove very short content
        if len(content) < 100:
            logger.info(f"Content too short on {url}: {len(content)} characters")
            return None, content_type
        
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
        elif path == '/' or path == '':
            return ContentType.LANDING_PAGE
        
        # Check for schema.org types
        for item_type in soup.find_all(attrs={"itemtype": True}):
            item_type_value = item_type.get("itemtype", "").lower()
            if "product" in item_type_value:
                return ContentType.PRODUCT_DESCRIPTION
            elif "article" in item_type_value:
                return ContentType.ARTICLE
            elif "newsarticle" in item_type_value:
                return ContentType.NEWS
        
        # Check for typical about page content
        about_terms = ["about us", "our story", "our mission", "our team", "who we are"]
        page_text = soup.get_text().lower()
        if any(term in page_text for term in about_terms):
            return ContentType.ABOUT_PAGE
        
        # Check for blog indicators
        blog_indicators = ["posted on", "published on", "comments", "author", "categories", "tags"]
        if any(indicator in page_text for indicator in blog_indicators):
            return ContentType.BLOG_POST
        
        # Default to other
        return ContentType.OTHER
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str, content_type: ContentType) -> ContentMetadata:
        """Extract metadata from the page."""
        metadata = ContentMetadata(content_type=content_type)
        
        # Extract title
        metadata.title = self._extract_title(soup)
        
        # Extract author
        author_meta = soup.find("meta", {"name": "author"})
        if author_meta:
            metadata.author = author_meta.get("content")
        
        # Try schema.org author
        if not metadata.author:
            author_element = soup.find(itemprop="author")
            if author_element:
                metadata.author = author_element.get_text().strip()
        
        # Try byline
        if not metadata.author:
            byline = soup.find(class_=lambda c: c and any(byline in c.lower() for byline in ['byline', 'author']))
            if byline:
                metadata.author = byline.get_text().strip()
        
        # Extract publication date
        for meta_tag in soup.find_all("meta"):
            property_value = meta_tag.get("property", "").lower()
            name_value = meta_tag.get("name", "").lower()
            
            if property_value in ["article:published_time", "og:published_time"] or name_value == "pubdate":
                try:
                    date_str = meta_tag.get("content")
                    if date_str:
                        metadata.publication_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except:
                    pass
        
        # Try time tag with datetime attribute
        if not metadata.publication_date:
            time_tag = soup.find("time")
            if time_tag and time_tag.has_attr("datetime"):
                try:
                    date_str = time_tag["datetime"]
                    metadata.publication_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except:
                    pass
        
        # Extract last modified date
        for meta_tag in soup.find_all("meta"):
            property_value = meta_tag.get("property", "").lower()
            name_value = meta_tag.get("name", "").lower()
            
            if property_value in ["article:modified_time", "og:updated_time"] or name_value == "lastmod":
                try:
                    date_str = meta_tag.get("content")
                    if date_str:
                        metadata.last_modified = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except:
                    pass
        
        # Extract language
        html_tag = soup.html
        if html_tag and html_tag.has_attr("lang"):
            lang_attr = html_tag["lang"]
            if lang_attr:
                metadata.language = lang_attr.split("-")[0]
        
        # Extract categories
        for meta_tag in soup.find_all("meta", {"property": "article:section"}):
            category = meta_tag.get("content")
            if category and category not in metadata.categories:
                metadata.categories.append(category)
        
        # Try to extract categories from breadcrumbs or category links
        for element in soup.find_all(class_=lambda c: c and "category" in c.lower()):
            for link in element.find_all("a"):
                text = link.get_text().strip()
                if text and text not in metadata.categories:
                    metadata.categories.append(text)
        
        # Extract tags
        for meta_tag in soup.find_all("meta", {"property": "article:tag"}):
            tag = meta_tag.get("content")
            if tag and tag not in metadata.tags:
                metadata.tags.append(tag)
        
        # Try to extract tags from tag links
        for element in soup.find_all(class_=lambda c: c and "tag" in c.lower()):
            for link in element.find_all("a"):
                text = link.get_text().strip()
                if text and text not in metadata.tags and text not in metadata.categories:
                    metadata.tags.append(text)
        
        return metadata
