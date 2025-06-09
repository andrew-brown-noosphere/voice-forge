"""
Content Extraction API for Gypsum Integration
Extracts products, use cases, industries, and testimonials from crawled content
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import re
from datetime import datetime

from auth.clerk_auth import get_current_user_with_org, AuthUser, get_org_id_from_user
from api.dependencies import get_rag_service
from processor.rag_service import RAGService

router = APIRouter(prefix="/api/content", tags=["content_extraction"])
logger = logging.getLogger(__name__)

class ContentExtractionRequest(BaseModel):
    domain: Optional[str] = None
    extract_products: bool = True
    extract_use_cases: bool = True
    extract_industries: bool = True 
    extract_testimonials: bool = True
    confidence_threshold: float = 0.7

class ContentExtractionResponse(BaseModel):
    job_id: str
    status: str
    extracted_items: Dict[str, Any]
    summary: Dict[str, int]

@router.post("/extract", response_model=ContentExtractionResponse)
async def extract_content_for_gypsum(
    request: ContentExtractionRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_user_with_org),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Extract products, use cases, industries, and testimonials from crawled content
    Returns structured data with evidence for Gypsum consumption
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        logger.info(f"Starting content extraction for org {org_id}, domain: {request.domain}")
        
        # Initialize extraction results
        extraction_results = {
            "products": [],
            "use_cases": [],
            "industries": [], 
            "testimonials": [],
            "extraction_metadata": {
                "org_id": org_id,
                "domain": request.domain,
                "timestamp": datetime.now().isoformat(),
                "confidence_threshold": request.confidence_threshold
            }
        }
        
        # 1. Extract Products if requested
        if request.extract_products:
            try:
                products = await extract_products_from_rag(
                    rag_service, org_id, request.domain, request.confidence_threshold
                )
                extraction_results["products"] = products
                logger.info(f"Extracted {len(products)} products")
            except Exception as e:
                logger.error(f"Product extraction failed: {e}")
                extraction_results["products"] = []
        
        # 2. Extract Use Cases if requested
        if request.extract_use_cases:
            try:
                use_cases = await extract_use_cases_from_rag(
                    rag_service, org_id, request.domain, request.confidence_threshold
                )
                extraction_results["use_cases"] = use_cases
                logger.info(f"Extracted {len(use_cases)} use cases")
            except Exception as e:
                logger.error(f"Use case extraction failed: {e}")
                extraction_results["use_cases"] = []
        
        # 3. Extract Industries if requested
        if request.extract_industries:
            try:
                industries = await extract_industries_from_rag(
                    rag_service, org_id, request.domain, request.confidence_threshold
                )
                extraction_results["industries"] = industries
                logger.info(f"Extracted {len(industries)} industries")
            except Exception as e:
                logger.error(f"Industry extraction failed: {e}")
                extraction_results["industries"] = []
        
        # 4. Extract Testimonials if requested
        if request.extract_testimonials:
            try:
                testimonials = await extract_testimonials_from_rag(
                    rag_service, org_id, request.domain, request.confidence_threshold
                )
                extraction_results["testimonials"] = testimonials
                logger.info(f"Extracted {len(testimonials)} testimonials")
            except Exception as e:
                logger.error(f"Testimonial extraction failed: {e}")
                extraction_results["testimonials"] = []
        
        # Generate summary
        summary = {
            "total_products": len(extraction_results["products"]),
            "total_use_cases": len(extraction_results["use_cases"]), 
            "total_industries": len(extraction_results["industries"]),
            "total_testimonials": len(extraction_results["testimonials"]),
            "total_items": sum([
                len(extraction_results["products"]),
                len(extraction_results["use_cases"]),
                len(extraction_results["industries"]),
                len(extraction_results["testimonials"])
            ])
        }
        
        return ContentExtractionResponse(
            job_id=f"extract_{org_id}_{int(datetime.now().timestamp())}",
            status="completed",
            extracted_items=extraction_results,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Content extraction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content extraction failed: {str(e)}"
        )

async def extract_products_from_rag(
    rag_service: RAGService, 
    org_id: str, 
    domain: str = None,
    confidence_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Extract product information using RAG system"""
    
    product_queries = [
        "product features and capabilities",
        "what we offer platform solutions",
        "technology tools and services", 
        "product benefits and advantages"
    ]
    
    products = []
    
    for query in product_queries:
        try:
            # Use existing RAG service to search for relevant content
            chunks = rag_service.search_chunks(
                query=query,
                domain=domain,
                top_k=10,
                org_id=org_id
            )
            
            # Filter high-relevance chunks
            relevant_chunks = [chunk for chunk in chunks if chunk.similarity > confidence_threshold]
            
            if relevant_chunks:
                # Extract product info from chunks
                product_info = await extract_product_from_chunks(relevant_chunks, query)
                if product_info:
                    products.append(product_info)
                    
        except Exception as e:
            logger.error(f"Error extracting products for query '{query}': {e}")
            continue
    
    # Deduplicate products by name
    unique_products = {}
    for product in products:
        name = product.get("name", "").lower()
        if name and name not in unique_products:
            unique_products[name] = product
    
    return list(unique_products.values())

async def extract_use_cases_from_rag(
    rag_service: RAGService,
    org_id: str,
    domain: str = None, 
    confidence_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Extract use case information using RAG system"""
    
    use_case_queries = [
        "customer success story case study",
        "how companies use our solution",
        "implementation examples and results",
        "customer deployment and migration"
    ]
    
    use_cases = []
    
    for query in use_case_queries:
        try:
            chunks = rag_service.search_chunks(
                query=query,
                domain=domain,
                top_k=8,
                org_id=org_id
            )
            
            relevant_chunks = [chunk for chunk in chunks if chunk.similarity > confidence_threshold]
            
            if relevant_chunks:
                use_case_info = await extract_use_case_from_chunks(relevant_chunks, query)
                if use_case_info:
                    use_cases.append(use_case_info)
                    
        except Exception as e:
            logger.error(f"Error extracting use cases for query '{query}': {e}")
            continue
    
    return use_cases

async def extract_industries_from_rag(
    rag_service: RAGService,
    org_id: str,
    domain: str = None,
    confidence_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Extract industry information using RAG system"""
    
    industry_queries = [
        "financial services fintech banking",
        "healthcare medical compliance", 
        "gaming entertainment real-time",
        "enterprise large companies",
        "regulatory compliance requirements"
    ]
    
    industries = []
    
    for query in industry_queries:
        try:
            chunks = rag_service.search_chunks(
                query=query,
                domain=domain,
                top_k=6,
                org_id=org_id
            )
            
            relevant_chunks = [chunk for chunk in chunks if chunk.similarity > confidence_threshold]
            
            if relevant_chunks:
                industry_info = await extract_industry_from_chunks(relevant_chunks, query)
                if industry_info:
                    industries.append(industry_info)
                    
        except Exception as e:
            logger.error(f"Error extracting industries for query '{query}': {e}")
            continue
    
    return industries

async def extract_testimonials_from_rag(
    rag_service: RAGService,
    org_id: str,
    domain: str = None,
    confidence_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Extract testimonial information using RAG system"""
    
    testimonial_queries = [
        "customer testimonial quote review",
        "according to engineering manager",
        "says senior engineer developer",
        "customer feedback success story"
    ]
    
    testimonials = []
    
    for query in testimonial_queries:
        try:
            chunks = rag_service.search_chunks(
                query=query,
                domain=domain,
                top_k=5,
                org_id=org_id
            )
            
            relevant_chunks = [chunk for chunk in chunks if chunk.similarity > confidence_threshold]
            
            for chunk in relevant_chunks:
                testimonial_info = await extract_testimonial_from_chunk(chunk)
                if testimonial_info:
                    testimonials.append(testimonial_info)
                    
        except Exception as e:
            logger.error(f"Error extracting testimonials for query '{query}': {e}")
            continue
    
    return testimonials

async def extract_product_from_chunks(chunks, query_context: str) -> Optional[Dict[str, Any]]:
    """Extract structured product information from content chunks"""
    
    # Combine chunk content
    combined_content = "\n\n".join([chunk.text for chunk in chunks[:3]])
    source_urls = list(set([chunk.metadata.get("url", "") for chunk in chunks]))
    
    # Simple extraction logic (could be enhanced with LLM)
    product_keywords = ["product", "platform", "solution", "tool", "service", "technology"]
    feature_keywords = ["feature", "capability", "function", "support", "enable", "provide"]
    
    # Extract product name from content
    content_lower = combined_content.lower()
    
    # Look for product mentions
    product_name = None
    for chunk in chunks:
        text = chunk.text
        # Simple heuristic: look for capitalized product names
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in product_keywords and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word[0].isupper():
                    product_name = next_word
                    break
        if product_name:
            break
    
    if not product_name:
        return None
    
    # Extract features
    features = []
    sentences = combined_content.split('.')
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in feature_keywords):
            features.append({
                "name": sentence.strip()[:50],
                "description": sentence.strip(),
                "evidence_quote": sentence.strip()[:100]
            })
    
    return {
        "name": product_name,
        "description": combined_content[:300] + "..." if len(combined_content) > 300 else combined_content,
        "category": query_context.split()[0].title() if query_context else "General",
        "features": features[:5],  # Limit to 5 features
        "benefits": [],  # Could be extracted similarly
        "source_urls": source_urls,
        "content_evidence": {
            "extraction_date": datetime.now().isoformat(),
            "content_snippets": [chunk.text[:200] for chunk in chunks[:2]],
            "extraction_method": "rag_analysis"
        },
        "confidence_score": sum([chunk.similarity for chunk in chunks]) / len(chunks)
    }

async def extract_use_case_from_chunks(chunks, query_context: str) -> Optional[Dict[str, Any]]:
    """Extract structured use case information from content chunks"""
    
    combined_content = "\n\n".join([chunk.text for chunk in chunks[:2]])
    source_urls = list(set([chunk.metadata.get("url", "") for chunk in chunks]))
    
    # Simple extraction for demonstration
    # In production, this would use more sophisticated NLP/LLM
    
    # Look for customer mentions
    customer_indicators = ["company", "customer", "client", "organization", "team"]
    problem_indicators = ["problem", "challenge", "issue", "difficulty", "pain"]
    solution_indicators = ["solution", "approach", "resolved", "solved", "implemented"]
    
    customer_name = None
    problem_statement = ""
    solution_approach = ""
    
    sentences = combined_content.split('.')
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Extract customer name
        if not customer_name and any(indicator in sentence_lower for indicator in customer_indicators):
            words = sentence.split()
            for i, word in enumerate(words):
                if word.lower() in customer_indicators and i + 1 < len(words):
                    potential_name = words[i + 1]
                    if potential_name[0].isupper():
                        customer_name = potential_name
                        break
        
        # Extract problem statement
        if any(indicator in sentence_lower for indicator in problem_indicators):
            problem_statement = sentence.strip()
        
        # Extract solution approach
        if any(indicator in sentence_lower for indicator in solution_indicators):
            solution_approach = sentence.strip()
    
    if not customer_name and not problem_statement:
        return None
    
    return {
        "title": f"Use Case: {customer_name or 'Customer Implementation'}",
        "description": combined_content[:300] + "..." if len(combined_content) > 300 else combined_content,
        "industry": extract_industry_from_content(combined_content),
        "company_size": "Unknown",
        "problem_statement": problem_statement or "Problem not specified",
        "solution_approach": solution_approach or "Solution approach not specified",
        "results_achieved": "",
        "customer_name": customer_name,
        "customer_title": None,
        "customer_company": customer_name,
        "tech_stack": extract_tech_stack_from_content(combined_content),
        "metrics": {},
        "source_urls": source_urls,
        "content_evidence": {
            "extraction_date": datetime.now().isoformat(),
            "content_snippets": [chunk.text[:200] for chunk in chunks[:2]]
        },
        "confidence_score": sum([chunk.similarity for chunk in chunks]) / len(chunks)
    }

async def extract_industry_from_chunks(chunks, query_context: str) -> Optional[Dict[str, Any]]:
    """Extract industry information from chunks"""
    
    combined_content = "\n\n".join([chunk.text for chunk in chunks[:2]])
    source_urls = list(set([chunk.metadata.get("url", "") for chunk in chunks]))
    
    industry_name = extract_industry_from_content(combined_content)
    if not industry_name or industry_name == "Unknown":
        return None
    
    # Extract pain points and requirements
    pain_points = []
    requirements = []
    
    sentences = combined_content.split('.')
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        if any(indicator in sentence_lower for indicator in ["problem", "challenge", "issue", "pain"]):
            pain_points.append(sentence.strip())
        
        if any(indicator in sentence_lower for indicator in ["requirement", "need", "must", "compliance"]):
            requirements.append(sentence.strip())
    
    return {
        "name": industry_name,
        "description": f"Industry characteristics extracted from content",
        "pain_points": pain_points[:3],  # Limit to 3
        "requirements": requirements[:3],
        "success_metrics": [],
        "compliance_requirements": extract_compliance_requirements(combined_content),
        "key_trends": [],
        "source_urls": source_urls,
        "content_evidence": {
            "extraction_date": datetime.now().isoformat(),
            "content_snippets": [chunk.text[:200] for chunk in chunks[:2]]
        },
        "confidence_score": sum([chunk.similarity for chunk in chunks]) / len(chunks)
    }

async def extract_testimonial_from_chunk(chunk) -> Optional[Dict[str, Any]]:
    """Extract testimonial information from a single chunk"""
    
    content = chunk.text
    
    # Look for quote patterns
    quote_patterns = [
        r'"([^"]+)"',  # Text in quotes
        r"'([^']+)'",  # Text in single quotes
        r'says ([^.]+)',  # "says" pattern
        r'according to ([^,]+), "([^"]+)"',  # "according to" pattern
    ]
    
    quote = None
    customer_name = None
    customer_title = None
    customer_company = None
    
    # Extract quotes
    for pattern in quote_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                quote = matches[0][-1]  # Get the quote part
                if len(matches[0]) > 1:
                    customer_info = matches[0][0]
                    # Parse customer info
                    customer_parts = customer_info.split(',')
                    if len(customer_parts) >= 2:
                        customer_name = customer_parts[0].strip()
                        customer_title = customer_parts[1].strip()
            else:
                quote = matches[0]
            break
    
    if not quote or len(quote) < 20:  # Too short to be meaningful
        return None
    
    # Look for customer information in surrounding text
    if not customer_name:
        # Simple heuristic: look for names (capitalized words)
        words = content.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2 and not word.lower() in ['the', 'and', 'but']:
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    customer_name = f"{word} {words[i + 1]}"
                    break
    
    # Extract company from context
    company_indicators = ["at", "from", "of"]
    for indicator in company_indicators:
        if indicator in content.lower():
            parts = content.split(indicator)
            if len(parts) > 1:
                potential_company = parts[1].split()[0:2]  # Get next 1-2 words
                customer_company = " ".join(potential_company).strip(' .,\"')
                break
    
    credibility_score = 0.5  # Base score
    if customer_name: credibility_score += 0.2
    if customer_title: credibility_score += 0.1
    if customer_company: credibility_score += 0.2
    
    return {
        "quote": quote,
        "context": content[:200] + "..." if len(content) > 200 else content,
        "customer_name": customer_name or "Unknown",
        "customer_title": customer_title or "",
        "customer_company": customer_company or "",
        "customer_industry": extract_industry_from_content(content),
        "testimonial_type": "review",  # Default type
        "publication_date": None,
        "source_url": chunk.metadata.get("url", ""),
        "content_evidence": {
            "extraction_date": datetime.now().isoformat(),
            "full_context": content
        },
        "credibility_score": min(credibility_score, 1.0),
        "confidence_score": chunk.similarity
    }

# Helper functions
def extract_industry_from_content(content: str) -> str:
    """Extract industry from content keywords"""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["financial", "fintech", "banking"]):
        return "Financial Services"
    elif any(word in content_lower for word in ["healthcare", "medical", "hospital"]):
        return "Healthcare"
    elif any(word in content_lower for word in ["gaming", "game", "entertainment"]):
        return "Gaming"
    elif any(word in content_lower for word in ["enterprise", "corporation", "business"]):
        return "Enterprise"
    elif any(word in content_lower for word in ["technology", "startup", "developer"]):
        return "Technology"
    else:
        return "Unknown"

def extract_tech_stack_from_content(content: str) -> List[str]:
    """Extract technology stack from content"""
    tech_keywords = [
        "kubernetes", "docker", "python", "go", "java", "javascript", "react",
        "nodejs", "postgresql", "mysql", "redis", "kafka", "grpc", "rest",
        "microservices", "aws", "gcp", "azure", "terraform", "jenkins"
    ]
    
    content_lower = content.lower()
    found_tech = []
    
    for tech in tech_keywords:
        if tech in content_lower:
            found_tech.append(tech.title())
    
    return found_tech[:5]  # Limit to 5 technologies

def extract_compliance_requirements(content: str) -> List[str]:
    """Extract compliance requirements from content"""
    compliance_keywords = [
        "sox", "sarbanes-oxley", "gdpr", "hipaa", "pci", "iso", "soc",
        "compliance", "regulation", "audit", "security", "privacy"
    ]
    
    content_lower = content.lower()
    found_compliance = []
    
    for keyword in compliance_keywords:
        if keyword in content_lower:
            found_compliance.append(keyword.upper())
    
    return list(set(found_compliance))  # Remove duplicates
