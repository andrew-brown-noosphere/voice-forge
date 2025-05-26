"""
Query reformulation for better chunk matching.
"""
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class QueryReformulator:
    """Reformulates queries for better chunk matching."""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        
    def reformulate(self, query, context=None):
        """
        Generate variations of the query for better matching.
        
        Args:
            query: Original query
            context: Optional context for reformulation
            
        Returns:
            List of reformulated queries
        """
        logger.info(f"Reformulating query: {query}")
        reformulations = [query]  # Always include the original query
        
        # Add keyword-based reformulations
        keywords = self._extract_keywords(query)
        if keywords:
            keyword_query = " ".join(keywords)
            if keyword_query != query:
                reformulations.append(keyword_query)
                logger.debug(f"Added keyword reformulation: {keyword_query}")
        
        # Add simplified query
        simplified = self._simplify_query(query)
        if simplified != query:
            reformulations.append(simplified)
            logger.debug(f"Added simplified reformulation: {simplified}")
        
        # Add expanded query
        expanded = self._expand_query(query)
        if expanded != query and expanded not in reformulations:
            reformulations.append(expanded)
            logger.debug(f"Added expanded reformulation: {expanded}")
        
        # Use LLM for advanced reformulation if available
        if self.llm_service:
            try:
                llm_reformulations = self._llm_reformulate(query, context)
                for r in llm_reformulations:
                    if r not in reformulations:
                        reformulations.append(r)
                        logger.debug(f"Added LLM reformulation: {r}")
            except Exception as e:
                logger.warning(f"LLM reformulation failed: {str(e)}")
        
        # Remove duplicates and return
        unique_reformulations = list(dict.fromkeys(reformulations))
        logger.info(f"Created {len(unique_reformulations)} reformulations")
        return unique_reformulations
    
    def _extract_keywords(self, query):
        """Extract keywords from query."""
        # Simple keyword extraction logic
        import re
        
        # Remove stop words and punctuation
        stop_words = {"the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are", "what", "how", "why", "when", "where", "which", "who", "whom"}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _simplify_query(self, query):
        """Simplify the query by removing modifiers and complex structures."""
        # Remove question words
        simplified = re.sub(r'^(what|how|who|when|where|why|which|can|could|would|should)\s+', '', query.lower())
        
        # Remove "tell me about" and similar phrases
        simplified = re.sub(r'^(tell me about|explain|describe|give me information on|i want to know about)\s+', '', simplified)
        
        # Remove "is there" and similar phrases
        simplified = re.sub(r'^(is there|are there|do you have|can you provide)\s+', '', simplified)
        
        return simplified
    
    def _expand_query(self, query):
        """Add potential synonyms or related terms to the query."""
        # This is a simplified version. In a production system, use WordNet or a thesaurus
        expansions = {
            "car": ["vehicle", "automobile"],
            "happy": ["joy", "glad"],
            "sad": ["unhappy", "depressed"],
            "big": ["large", "huge"],
            "small": ["tiny", "little"],
            "marketing": ["promotion", "advertising"],
            "sales": ["revenue", "business"],
            "customer": ["client", "consumer"],
            "product": ["item", "goods"],
            "strategy": ["plan", "approach"]
        }
        
        words = query.lower().split()
        expanded_words = words.copy()
        
        # Add expansions for matched words
        for word in words:
            if word in expansions:
                # Add first expansion if not already in query
                for expansion in expansions[word]:
                    if expansion not in words:
                        expanded_words.append(expansion)
                        break
        
        return " ".join(expanded_words)
    
    def _llm_reformulate(self, query, context=None):
        """Use LLM to reformulate the query."""
        # This would use the LLM service to generate reformulations
        # For now, return empty list if LLM service isn't provided
        if not self.llm_service:
            return []
        
        try:
            response = self.llm_service.generate(
                prompt_type="query_reformulation",
                params={"query": query, "context": context},
                use_cache=True
            )
            
            if response and "text" in response:
                # Parse response - expecting one query per line
                reformulations = [line.strip() for line in response["text"].split("\n") if line.strip()]
                return reformulations[:3]  # Limit to 3 reformulations
            
            return []
            
        except Exception as e:
            logger.warning(f"Error using LLM for query reformulation: {str(e)}")
            return []
