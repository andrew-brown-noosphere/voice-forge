"""
Content chunking module for RAG system.
"""
import re
import uuid
import logging
from typing import List, Dict, Any, Tuple, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# For Python 3.13 compatibility, we'll use a more basic sentence splitting approach
# rather than relying on NLTK if it's not available
def simple_sentence_tokenize(text: str) -> List[str]:
    """Simple sentence tokenization fallback."""
    # Basic regex for sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

class ContentChunker:
    """
    Manages chunking of content for efficient retrieval in the RAG system.
    Creates overlapping chunks with proper handling of sentence boundaries.
    """
    
    def __init__(
        self, 
        chunk_size: int = 500, 
        chunk_overlap: int = 100,
        respect_sentences: bool = True
    ):
        """
        Initialize the content chunker.
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Overlap between consecutive chunks in tokens
            respect_sentences: Try to maintain sentence boundaries
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.respect_sentences = respect_sentences
        
        # Simple whitespace tokenizer for counting tokens
        # In a production environment, consider using a proper tokenizer
        self.tokenize = lambda text: text.split()
        
        # Try to import NLTK, but have a fallback
        try:
            import nltk
            try:
                nltk.download('punkt', quiet=True)
                self.nltk_available = True
                self.sent_tokenize = nltk.sent_tokenize
            except Exception as e:
                logger.warning(f"Failed to download NLTK resources: {str(e)}")
                self.nltk_available = False
                self.sent_tokenize = simple_sentence_tokenize
        except ImportError:
            logger.warning("NLTK not available, using simple sentence tokenizer")
            self.nltk_available = False
            self.sent_tokenize = simple_sentence_tokenize
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate the number of tokens in a text."""
        return len(self.tokenize(text))
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        try:
            text = re.sub(r'\s+', ' ', text).strip()
            return self.sent_tokenize(text)
        except Exception as e:
            logger.warning(f"Error during sentence tokenization: {str(e)}. Falling back to simpler method.")
            # Fallback to a simpler method
            return simple_sentence_tokenize(text)
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text content to chunk
            
        Returns:
            List of dictionaries containing chunk data
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        try:
            chunks = []
            
            if self.respect_sentences:
                # Try to respect sentence boundaries
                sentences = self._split_into_sentences(text)
                current_chunk = []
                current_size = 0
                current_start_char = 0
                
                # Track the character positions
                char_index = 0
                sentence_positions = []
                
                # Calculate the start and end positions of each sentence
                for sentence in sentences:
                    sentence_start = text.find(sentence, char_index)
                    if sentence_start == -1:
                        # If the exact sentence isn't found, just use the current index
                        sentence_start = char_index
                    
                    sentence_end = sentence_start + len(sentence)
                    sentence_positions.append((sentence_start, sentence_end))
                    char_index = sentence_end
                
                # Now create chunks
                current_sentences = []
                current_start = 0
                current_end = 0
                
                for i, sentence in enumerate(sentences):
                    sentence_size = self._estimate_token_count(sentence)
                    start_pos, end_pos = sentence_positions[i]
                    
                    # Handle case where a single sentence exceeds chunk size
                    if sentence_size > self.chunk_size:
                        # Store current chunk if there's anything
                        if current_sentences:
                            chunk_text = " ".join(current_sentences)
                            chunks.append({
                                "text": chunk_text,
                                "start_char": current_start,
                                "end_char": current_end,
                                "chunk_index": len(chunks)
                            })
                            current_sentences = []
                        
                        # Split the long sentence without respecting boundaries
                        words = self.tokenize(sentence)
                        word_start = 0
                        
                        for j in range(0, len(words), self.chunk_size - self.chunk_overlap):
                            chunk_words = words[j:j + self.chunk_size]
                            chunk_text = " ".join(chunk_words)
                            
                            # Calculate approximate character positions
                            chunk_start = start_pos + j * len(sentence) // len(words)
                            chunk_end = start_pos + (j + len(chunk_words)) * len(sentence) // len(words)
                            
                            chunks.append({
                                "text": chunk_text,
                                "start_char": chunk_start,
                                "end_char": chunk_end,
                                "chunk_index": len(chunks)
                            })
                    else:
                        # If adding this sentence exceeds the chunk size
                        if current_size + sentence_size > self.chunk_size and current_sentences:
                            # Store current chunk
                            chunk_text = " ".join(current_sentences)
                            chunks.append({
                                "text": chunk_text,
                                "start_char": current_start,
                                "end_char": current_end,
                                "chunk_index": len(chunks)
                            })
                            
                            # Handle overlap - keep some sentences for continuity
                            overlap_sentences = []
                            overlap_size = 0
                            
                            # Add sentences from the end until we reach desired overlap
                            for sent in reversed(current_sentences):
                                sent_size = self._estimate_token_count(sent)
                                if overlap_size + sent_size <= self.chunk_overlap:
                                    overlap_sentences.insert(0, sent)
                                    overlap_size += sent_size
                                else:
                                    break
                            
                            current_sentences = overlap_sentences
                            current_size = overlap_size
                            
                            # Recalculate the start position for the new chunk
                            if current_sentences:
                                # Find the position of the first overlapping sentence
                                first_overlap_sentence = current_sentences[0]
                                for sen_idx in range(i - len(current_sentences), i):
                                    if sen_idx >= 0 and sentences[sen_idx] == first_overlap_sentence:
                                        current_start = sentence_positions[sen_idx][0]
                                        break
                            else:
                                current_start = start_pos
                        
                        # Add the current sentence
                        current_sentences.append(sentence)
                        current_size += sentence_size
                        current_end = end_pos
                        
                        # If we're just starting a new chunk, set the start position
                        if len(current_sentences) == 1:
                            current_start = start_pos
                
                # Add the last chunk if it's not empty
                if current_sentences:
                    chunk_text = " ".join(current_sentences)
                    chunks.append({
                        "text": chunk_text,
                        "start_char": current_start,
                        "end_char": current_end,
                        "chunk_index": len(chunks)
                    })
            else:
                # Simple chunking without respecting sentence boundaries
                words = self.tokenize(text)
                for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                    chunk_words = words[i:i + self.chunk_size]
                    chunk_text = " ".join(chunk_words)
                    
                    # Calculate approximate character positions
                    chunk_start = i * len(text) // len(words)
                    chunk_end = min((i + len(chunk_words)) * len(text) // len(words), len(text))
                    
                    chunks.append({
                        "text": chunk_text,
                        "start_char": chunk_start,
                        "end_char": chunk_end,
                        "chunk_index": len(chunks)
                    })
            
            logger.info(f"Successfully chunked text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error during content chunking: {str(e)}")
            # Return text as a single chunk in case of error
            return [{
                "text": text,
                "start_char": 0,
                "end_char": len(text),
                "chunk_index": 0
            }]
    
    def process_content(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process content and generate chunks with metadata.
        
        Args:
            content: Content dictionary with text and metadata
            
        Returns:
            List of chunk dictionaries with metadata
        """
        content_id = content.get("content_id")
        text = content.get("text", "")
        metadata = content.get("metadata", {})
        
        # Generate chunks
        basic_chunks = self.chunk_text(text)
        
        # Enrich chunks with metadata
        enriched_chunks = []
        for chunk in basic_chunks:
            chunk_id = str(uuid.uuid4())
            
            # Add content ID and chunk ID
            chunk["id"] = chunk_id
            chunk["content_id"] = content_id
            
            # Add metadata from content
            chunk["chunk_metadata"] = {
                "title": metadata.get("title"),
                "content_type": metadata.get("content_type"),
                "domain": content.get("domain"),
                "url": content.get("url"),
                "chunking_method": "sentence_aware" if self.respect_sentences else "fixed_size",
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "created_at": datetime.utcnow().isoformat()
            }
            
            enriched_chunks.append(chunk)
        
        return enriched_chunks
