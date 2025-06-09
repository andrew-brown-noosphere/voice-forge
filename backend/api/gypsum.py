"""
Gypsum router for personas API.
Provides static persona data for Reddit signal discovery and other features.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from auth.clerk_auth import get_current_user_with_org, AuthUser, get_org_id_from_user

router = APIRouter(prefix="/gypsum", tags=["gypsum"])

# Static persona data for buf.build - can be expanded later
STATIC_PERSONAS = [
    {
        "id": "backend_dev_001",
        "role": "Backend Developer",
        "seniority_level": "Senior",
        "industry": "Technology",
        "company_size": "Mid-size (100-1000)",
        "communication_style": "Technical",
        "pain_points": [
            "API integration complexity",
            "Microservice communication overhead", 
            "Schema management across services",
            "Type safety in distributed systems",
            "gRPC service discovery issues"
        ],
        "goals": [
            "Reduce API integration time",
            "Improve system reliability",
            "Simplify service communication",
            "Better developer experience"
        ],
        "tech_stack": [
            "Go", "Python", "gRPC", "Protocol Buffers", 
            "Kubernetes", "Docker", "PostgreSQL"
        ],
        "focus_areas": ["gRPC", "Protocol Buffers", "API Design", "Microservices"]
    },
    {
        "id": "devops_eng_001", 
        "role": "DevOps Engineer",
        "seniority_level": "Mid-level",
        "industry": "Enterprise",
        "company_size": "Large (1000+)",
        "communication_style": "Pragmatic",
        "pain_points": [
            "Service discovery complexity",
            "Load balancing configuration",
            "Monitoring distributed systems",
            "Container orchestration",
            "CI/CD pipeline maintenance"
        ],
        "goals": [
            "Automate deployment processes",
            "Improve system observability", 
            "Reduce operational overhead",
            "Enhance system scalability"
        ],
        "tech_stack": [
            "Kubernetes", "Docker", "Terraform", "Prometheus",
            "Grafana", "Jenkins", "AWS", "gRPC"
        ],
        "focus_areas": ["Kubernetes", "Docker", "Service Mesh", "Observability"]
    },
    {
        "id": "fullstack_dev_001",
        "role": "Full Stack Developer", 
        "seniority_level": "Mid-level",
        "industry": "Startup",
        "company_size": "Small (10-100)",
        "communication_style": "Collaborative",
        "pain_points": [
            "Tool complexity and learning curve",
            "Code generation inconsistencies", 
            "Type safety across frontend/backend",
            "API documentation maintenance",
            "Development velocity bottlenecks"
        ],
        "goals": [
            "Faster feature development",
            "Better code quality",
            "Reduced maintenance burden",
            "Improved team productivity"
        ],
        "tech_stack": [
            "TypeScript", "React", "Node.js", "Python",
            "GraphQL", "REST APIs", "PostgreSQL"
        ],
        "focus_areas": ["TypeScript", "Code Generation", "Developer Experience", "API Design"]
    },
    {
        "id": "platform_eng_001",
        "role": "Platform Engineer",
        "seniority_level": "Senior", 
        "industry": "Technology",
        "company_size": "Large (1000+)",
        "communication_style": "Strategic",
        "pain_points": [
            "Service mesh complexity",
            "Cross-team API governance",
            "Developer tooling fragmentation",
            "Security and compliance overhead",
            "Performance optimization across services"
        ],
        "goals": [
            "Standardize development practices",
            "Improve developer experience",
            "Ensure system security",
            "Optimize platform performance"
        ],
        "tech_stack": [
            "Istio", "Envoy", "Kubernetes", "gRPC",
            "Protocol Buffers", "Terraform", "Vault"
        ],
        "focus_areas": ["Platform Engineering", "Service Mesh", "Developer Tools", "Security"]
    },
    {
        "id": "api_arch_001",
        "role": "API Architect",
        "seniority_level": "Staff",
        "industry": "Financial Services", 
        "company_size": "Large (1000+)",
        "communication_style": "Detailed",
        "pain_points": [
            "API versioning strategies",
            "Cross-service data consistency",
            "Performance at scale",
            "Security compliance requirements",
            "Documentation and governance"
        ],
        "goals": [
            "Design scalable API architecture",
            "Ensure data consistency",
            "Maintain high performance",
            "Meet compliance requirements"
        ],
        "tech_stack": [
            "gRPC", "Protocol Buffers", "OpenAPI",
            "Kong", "Kafka", "Redis", "PostgreSQL"
        ],
        "focus_areas": ["API Architecture", "Data Consistency", "Performance", "Governance"]
    }
]

@router.get("/personas")
async def get_personas(
    current_user: AuthUser = Depends(get_current_user_with_org),
) -> List[Dict[str, Any]]:
    """
    Get all personas for the current organization.
    Returns static persona data for buf.build targeting.
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        # For now, return the same static personas for all orgs
        # In the future, this could be customized per organization
        return STATIC_PERSONAS
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personas: {str(e)}"
        )

@router.get("/personas/{persona_id}")
async def get_persona(
    persona_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
) -> Dict[str, Any]:
    """
    Get a specific persona by ID.
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        # Find the persona by ID
        persona = next((p for p in STATIC_PERSONAS if p["id"] == persona_id), None)
        
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"Persona with ID {persona_id} not found"
            )
        
        return persona
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get persona: {str(e)}"
        )

@router.post("/personas")
async def create_persona(
    persona_data: Dict[str, Any],
    current_user: AuthUser = Depends(get_current_user_with_org),
) -> Dict[str, Any]:
    """
    Create a new persona (placeholder - returns static response).
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        # For now, just return a success response
        # In the future, this could store personas in the database
        return {
            "id": f"custom_{len(STATIC_PERSONAS) + 1:03d}",
            "message": "Persona creation not yet implemented - using static personas",
            "org_id": org_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create persona: {str(e)}"
        )

@router.put("/personas/{persona_id}")
async def update_persona(
    persona_id: str,
    persona_data: Dict[str, Any],
    current_user: AuthUser = Depends(get_current_user_with_org),
) -> Dict[str, Any]:
    """
    Update a persona (placeholder - returns static response).
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        # Check if persona exists
        persona = next((p for p in STATIC_PERSONAS if p["id"] == persona_id), None)
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"Persona with ID {persona_id} not found"
            )
        
        return {
            "id": persona_id,
            "message": "Persona updates not yet implemented - using static personas",
            "org_id": org_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update persona: {str(e)}"
        )

@router.delete("/personas/{persona_id}")
async def delete_persona(
    persona_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
) -> Dict[str, str]:
    """
    Delete a persona (placeholder - returns static response).
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        # Check if persona exists
        persona = next((p for p in STATIC_PERSONAS if p["id"] == persona_id), None)
        if not persona:
            raise HTTPException(
                status_code=404,
                detail=f"Persona with ID {persona_id} not found"
            )
        
        return {
            "message": "Persona deletion not yet implemented - using static personas"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete persona: {str(e)}"
        )
