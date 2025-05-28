#!/usr/bin/env python3
"""
Enhanced Content Chunker for VoiceForge RAG System
Improved text splitting strategies with content-type awareness
"""
import re
import uuid
import logging
from typing import List, Dict, Any, Tuple, Union, Optional
from datetime import datetime
import html
import json

logger = logging.getLogger(__name__)

class EnhancedContentChunker:
    """
    Enhanced content chunker with intelligent text splitting strategies
    optimized for different content types and better retrieval performance.
    """
    
    # Content type specific configurations
    CONTENT_TYPE_CONFIGS = {
        'blog': {'chunk_size': 400, 'overlap': 80, 'respect_paragraphs': True},
        'article': {'chunk_size': 450, 'overlap': 90, 'respect_paragraphs': True},
        'api_docs': {'chunk_size': 600, 'overlap': 120, 'respect_code_blocks': True},
        'documentation': {'chunk_size': 550, 'overlap': 110, 'respect_headings': True},
        'faq': {'chunk_size': 300, 'overlap': 60, 'respect_qa_pairs': True},
        'product_page': {'chunk_size': 350, 'overlap': 70, 'respect_sections': True},
        'social_media': {'chunk_size': 200, 'overlap': 40, 'minimal_splitting': True},
        'landing_page': {'chunk_size': 400, 'overlap': 80, 'respect_sections': True},
        'default': {'chunk_size': 400, 'overlap': 80, 'balanced_approach': True}
    }
    
    def __init__(self, 
                 chunk_size: int = 400,
                 chunk_overlap: int = 80,
                 respect_sentences: bool = True,
                 min_chunk_size: int = 50,
                 max_chunk_size: int = 1000):
        """
        Initialize the enhanced content chunker.
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Overlap between consecutive chunks in tokens
            respect_sentences: Try to maintain sentence boundaries
            min_chunk_size: Minimum chunk size in tokens
            max_chunk_size: Maximum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.respect_sentences = respect_sentences
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        
        # Simple whitespace tokenizer for counting tokens
        self.tokenize = lambda text: text.split()
        
        # Initialize sentence tokenizer
        self._init_sentence_tokenizer()
        
        # Patterns for different content structures
        self._init_patterns()
    
    def _init_sentence_tokenizer(self):
        """Initialize sentence tokenization capability."""
        try:
            import nltk
            try:
                nltk.download('punkt', quiet=True)
                self.nltk_available = True
                self.sent_tokenize = nltk.sent_tokenize
                logger.debug("NLTK sentence tokenizer initialized")
            except Exception:
                logger.warning("NLTK punkt tokenizer not available, using fallback")
                self.nltk_available = False
                self.sent_tokenize = self._simple_sentence_tokenize
        except ImportError:
            logger.warning("NLTK not available, using simple sentence tokenizer")
            self.nltk_available = False
            self.sent_tokenize = self._simple_sentence_tokenize
    
    def _simple_sentence_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenization fallback."""
        # Enhanced regex for sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _init_patterns(self):
        """Initialize regex patterns for content structure detection."""
        self.patterns = {
            # Headings (Markdown and HTML)
            'headings': re.compile(r'^#{1,6}\s+.+$|<h[1-6][^>]*>.*?</h[1-6]>', re.MULTILINE | re.IGNORECASE),
            
            # Code blocks
            'code_blocks': re.compile(r'```[\s\S]*?```|<pre[\s\S]*?</pre>|<code[\s\S]*?</code>', re.IGNORECASE),
            
            # Lists (ordered and unordered)
            'lists': re.compile(r'^[\s]*[-*+•]\s+.+$|^[\s]*\d+\.\s+.+$', re.MULTILINE),
            
            # Paragraphs (double line breaks)
            'paragraphs': re.compile(r'\n\s*\n'),
            
            # Q&A pairs
            'qa_pairs': re.compile(r'(Q:|Question:|A:|Answer:|\?[\s]*\n)', re.IGNORECASE),
            
            # Sections (based on common patterns)
            'sections': re.compile(r'(?:^|\n)(?:SECTION|PART|CHAPTER|OVERVIEW|SUMMARY)[\s\S]*?(?=^(?:SECTION|PART|CHAPTER|OVERVIEW|SUMMARY)|\Z)', re.MULTILINE | re.IGNORECASE),
            
            # Features/benefits lists
            'feature_lists': re.compile(r'(?:Features?|Benefits?|Advantages?|Highlights?)[\s:]*\n((?:[-*•]\s+.+\n?)+)', re.IGNORECASE),
            
            # Testimonials/quotes
            'quotes': re.compile(r'"[^"]+"|\'[^\']+\'|"[^"]+"|'[^']+''|<blockquote[\s\S]*?</blockquote>', re.IGNORECASE)
        }
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate the number of tokens in a text."""
        return len(self.tokenize(text))
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better chunking."""
        # HTML decode
        text = html.unescape(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix broken sentences (no space after period)
        text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text)
        
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Clean up quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        return text.strip()
    
    def _detect_content_structure(self, text: str) -> Dict[str, Any]:
        """Detect the structure and characteristics of the content."""
        structure = {
            'has_headings': bool(self.patterns['headings'].search(text)),
            'has_code_blocks': bool(self.patterns['code_blocks'].search(text)),
            'has_lists': bool(self.patterns['lists'].search(text)),
            'has_qa_pairs': bool(self.patterns['qa_pairs'].search(text)),
            'has_quotes': bool(self.patterns['quotes'].search(text)),
            'paragraph_count': len(self.patterns['paragraphs'].split(text)),
            'avg_sentence_length': 0,
            'estimated_reading_level': 'medium'
        }
        
        # Calculate average sentence length
        sentences = self.sent_tokenize(text)
        if sentences:
            total_tokens = sum(self._estimate_token_count(sent) for sent in sentences)
            structure['avg_sentence_length'] = total_tokens / len(sentences)
        
        # Estimate reading level based on sentence length
        if structure['avg_sentence_length'] < 15:
            structure['estimated_reading_level'] = 'simple'
        elif structure['avg_sentence_length'] > 25:
            structure['estimated_reading_level'] = 'complex'
        
        return structure
    
    def _get_optimal_config(self, content_type: str, content_structure: Dict[str, Any], text_length: int) -> Dict[str, Any]:
        """Get optimal chunking configuration based on content analysis."""
        # Start with content type defaults
        config = self.CONTENT_TYPE_CONFIGS.get(content_type, self.CONTENT_TYPE_CONFIGS['default']).copy()
        
        # Adjust based on content structure
        if content_structure['has_code_blocks']:
            config['chunk_size'] = min(config['chunk_size'] + 200, self.max_chunk_size)
            config['overlap'] = min(config['overlap'] + 40, config['chunk_size'] // 4)
        
        if content_structure['estimated_reading_level'] == 'complex':
            config['chunk_size'] = min(config['chunk_size'] + 100, self.max_chunk_size)
        elif content_structure['estimated_reading_level'] == 'simple':
            config['chunk_size'] = max(config['chunk_size'] - 100, self.min_chunk_size)
        
        # Adjust for very short or very long content
        if text_length < 1000:
            config['chunk_size'] = max(config['chunk_size'] // 2, self.min_chunk_size)
            config['overlap'] = max(config['overlap'] // 2, 20)
        elif text_length > 20000:
            config['chunk_size'] = min(config['chunk_size'] + 150, self.max_chunk_size)
        
        return config
    
    def _split_on_structure(self, text: str, content_type: str, structure: Dict[str, Any]) -> List[str]:
        """Split text based on detected structural elements."""
        segments = []
        
        # Try to split on major structural elements first
        if structure['has_headings'] and content_type in ['documentation', 'api_docs']:
            # Split on headings for documentation
            heading_splits = self.patterns['headings'].split(text)
            current_segment = ""
            
            for i, segment in enumerate(heading_splits):
                if self.patterns['headings'].match(segment.strip()):
                    if current_segment:
                        segments.append(current_segment.strip())
                    current_segment = segment + "\n"
                else:
                    current_segment += segment
            
            if current_segment:
                segments.append(current_segment.strip())
        
        elif structure['has_qa_pairs']:
            # Split on Q&A pairs
            qa_splits = self.patterns['qa_pairs'].split(text)
            current_qa = ""
            
            for segment in qa_splits:
                if self.patterns['qa_pairs'].match(segment):
                    if current_qa:
                        segments.append(current_qa.strip())
                    current_qa = segment
                else:
                    current_qa += segment
            
            if current_qa:
                segments.append(current_qa.strip())
        
        elif structure['paragraph_count'] > 3:
            # Split on paragraphs for content with clear paragraph structure
            segments = [p.strip() for p in self.patterns['paragraphs'].split(text) if p.strip()]
        
        else:
            # Fallback to sentence-based splitting
            segments = [text]
        
        # Filter out very small segments
        segments = [seg for seg in segments if self._estimate_token_count(seg) >= self.min_chunk_size]
        
        return segments if segments else [text]
    
    def _create_overlapping_chunks(self, segments: List[str], chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Create overlapping chunks from text segments."""
        chunks = []
        current_chunk = ""
        current_size = 0
        segment_buffer = []
        
        for segment in segments:
            segment_size = self._estimate_token_count(segment)
            
            # If single segment is too large, split it further
            if segment_size > chunk_size * 1.5:
                # Split large segment into sentences
                sentences = self.sent_tokenize(segment)
                for sentence in sentences:
                    sentence_size = self._estimate_token_count(sentence)
                    
                    if current_size + sentence_size > chunk_size and current_chunk:
                        # Create chunk from current content
                        chunks.append({
                            'text': current_chunk.strip(),
                            'size': current_size,
                            'segments': segment_buffer.copy()
                        })
                        
                        # Handle overlap
                        overlap_text = self._create_overlap(current_chunk, overlap)
                        current_chunk = overlap_text + " " + sentence
                        current_size = self._estimate_token_count(current_chunk)
                        segment_buffer = [sentence]
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
                        current_size += sentence_size
                        segment_buffer.append(sentence)
            else:
                # Normal segment processing
                if current_size + segment_size > chunk_size and current_chunk:
                    # Create chunk from current content
                    chunks.append({
                        'text': current_chunk.strip(),
                        'size': current_size,
                        'segments': segment_buffer.copy()
                    })
                    
                    # Handle overlap
                    overlap_text = self._create_overlap(current_chunk, overlap)
                    current_chunk = overlap_text + " " + segment if overlap_text else segment
                    current_size = self._estimate_token_count(current_chunk)
                    segment_buffer = [segment]
                else:
                    current_chunk += " " + segment if current_chunk else segment
                    current_size += segment_size
                    segment_buffer.append(segment)
        
        # Add final chunk
        if current_chunk and current_size >= self.min_chunk_size:
            chunks.append({
                'text': current_chunk.strip(),
                'size': current_size,
                'segments': segment_buffer
            })
        
        return chunks
    
    def _create_overlap(self, text: str, overlap_tokens: int) -> str:
        """Create overlap text from the end of the previous chunk."""
        if not text or overlap_tokens <= 0:
            return ""
        
        # Try to use complete sentences for overlap
        sentences = self.sent_tokenize(text)
        if not sentences:
            # Fallback to word-based overlap
            words = self.tokenize(text)
            if len(words) <= overlap_tokens:
                return text
            return " ".join(words[-overlap_tokens:])
        
        # Use last few sentences that fit within overlap size
        overlap_text = ""
        remaining_tokens = overlap_tokens
        
        for sentence in reversed(sentences):
            sentence_tokens = self._estimate_token_count(sentence)
            if sentence_tokens <= remaining_tokens:
                overlap_text = sentence + " " + overlap_text if overlap_text else sentence
                remaining_tokens -= sentence_tokens
            else:
                break
        
        return overlap_text.strip()
    
    def chunk_content(self, 
                     content: str, 
                     content_type: str = 'default',
                     chunk_size: Optional[int] = None,
                     overlap: Optional[int] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk content using enhanced strategies.
        
        Args:
            content: Text content to chunk
            content_type: Type of content (blog, api_docs, etc.)
            chunk_size: Override default chunk size
            overlap: Override default overlap
            metadata: Additional metadata to include
            
        Returns:
            List of chunk dictionaries
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for chunking")
            return []
        
        try:
            # Clean and normalize text
            clean_text = self._clean_text(content)
            
            # Detect content structure
            structure = self._detect_content_structure(clean_text)
            
            # Get optimal configuration
            config = self._get_optimal_config(content_type, structure, len(clean_text))
            
            # Use provided parameters or defaults from config
            final_chunk_size = chunk_size or config['chunk_size']
            final_overlap = overlap or config['overlap']
            
            logger.debug(f"Chunking with size={final_chunk_size}, overlap={final_overlap}, type={content_type}")
            
            # Split content based on structure
            segments = self._split_on_structure(clean_text, content_type, structure)
            
            # Create overlapping chunks
            raw_chunks = self._create_overlapping_chunks(segments, final_chunk_size, final_overlap)
            
            # Post-process chunks
            final_chunks = []
            char_offset = 0
            
            for i, chunk_data in enumerate(raw_chunks):
                chunk_text = chunk_data['text']
                
                # Find the actual position in original text
                start_pos = content.find(chunk_text[:100])  # Use first 100 chars to find position
                if start_pos == -1:
                    start_pos = char_offset
                
                end_pos = start_pos + len(chunk_text)
                char_offset = end_pos
                
                chunk = {
                    'text': chunk_text,
                    'start_char': start_pos,
                    'end_char': min(end_pos, len(content)),
                    'chunk_index': i,
                    'size_tokens': chunk_data['size'],
                    'chunk_metadata': {
                        'content_type': content_type,
                        'chunking_strategy': 'enhanced_structural',
                        'chunk_size_config': final_chunk_size,
                        'overlap_config': final_overlap,
                        'structure_detected': structure,
                        'segments_count': len(chunk_data['segments']),
                        'created_at': datetime.utcnow().isoformat()
                    }
                }
                
                # Add provided metadata
                if metadata:
                    chunk['chunk_metadata'].update(metadata)
                
                final_chunks.append(chunk)
            
            logger.info(f"Enhanced chunking created {len(final_chunks)} chunks for {content_type} content")
            return final_chunks
            
        except Exception as e:
            logger.error(f"Error during enhanced chunking: {str(e)}")
            # Fallback to simple chunking
            return self._fallback_chunking(content, chunk_size or self.chunk_size, overlap or self.chunk_overlap)
    
    def _fallback_chunking(self, text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Simple fallback chunking strategy."""
        words = self.tokenize(text)
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                'text': chunk_text,
                'start_char': i * len(text) // len(words) if words else 0,
                'end_char': min((i + len(chunk_words)) * len(text) // len(words), len(text)) if words else len(text),
                'chunk_index': len(chunks),
                'size_tokens': len(chunk_words),
                'chunk_metadata': {
                    'chunking_strategy': 'fallback_simple',
                    'created_at': datetime.utcnow().isoformat()
                }
            })
        
        return chunks
    
    def process_content(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process content and generate enhanced chunks with full metadata.
        
        Args:
            content_data: Content dictionary with text and metadata
            
        Returns:
            List of enriched chunk dictionaries
        """
        content_id = content_data.get("content_id")
        text = content_data.get("text", "")
        metadata = content_data.get("metadata", {})
        
        # Determine content type
        content_type = metadata.get("content_type", "default")
        if isinstance(content_type, str):
            content_type = content_type.lower()
        
        # Generate chunks with enhanced strategy
        chunks = self.chunk_content(
            content=text,
            content_type=content_type,
            metadata={
                'title': metadata.get("title"),
                'domain': content_data.get("domain"),
                'url': content_data.get("url"),
                'author': metadata.get("author"),
                'categories': metadata.get("categories", []),
                'tags': metadata.get("tags", [])
            }
        )
        
        # Enrich chunks with additional metadata
        enriched_chunks = []
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            
            enhanced_chunk = {
                "id": chunk_id,
                "content_id": content_id,
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "start_char": chunk["start_char"],
                "end_char": chunk["end_char"],
                "embedding": None,  # To be filled by embedding generation
                "chunk_metadata": {
                    **chunk["chunk_metadata"],
                    "content_title": metadata.get("title"),
                    "content_url": content_data.get("url"),
                    "content_domain": content_data.get("domain"),
                    "content_language": metadata.get("language"),
                    "extraction_date": content_data.get("extracted_at"),
                    "chunk_quality_score": self._calculate_chunk_quality(chunk["text"]),
                    "contains_code": bool(self.patterns['code_blocks'].search(chunk["text"])),
                    "contains_list": bool(self.patterns['lists'].search(chunk["text"])),
                    "contains_heading": bool(self.patterns['headings'].search(chunk["text"])),
                }
            }
            
            enriched_chunks.append(enhanced_chunk)
        
        return enriched_chunks
    
    def _calculate_chunk_quality(self, text: str) -> float:
        """
        Calculate a quality score for a chunk based on various factors.
        
        Args:
            text: Chunk text
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not text:
            return 0.0
        
        score = 0.5  # Base score
        
        # Length factors
        token_count = self._estimate_token_count(text)
        if self.min_chunk_size <= token_count <= self.max_chunk_size:
            score += 0.2
        
        # Sentence completeness
        if text.strip().endswith(('.', '!', '?', ':', ';')):
            score += 0.1
        
        # Structure indicators
        if self.patterns['headings'].search(text):
            score += 0.1
        
        if self.patterns['lists'].search(text):
            score += 0.05
        
        # Readability factors
        sentences = self.sent_tokenize(text)
        if sentences and len(sentences) > 1:
            score += 0.05
        
        # Avoid very fragmented text
        if len(text.split('\n')) > token_count / 10:  # Too many line breaks
            score -= 0.1
        
        return max(0.0, min(1.0, score))

# Backwards compatibility wrapper
class ContentChunker(EnhancedContentChunker):
    """Backwards compatibility wrapper for the original ContentChunker."""
    
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 80, respect_sentences: bool = True):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            respect_sentences=respect_sentences
        )
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Backwards compatible chunk_text method."""
        return self.chunk_content(text, 'default')
