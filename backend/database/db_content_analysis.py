"""
Additional method for Database class to support content analysis for prompt generation.
This should be merged into the main db.py file.
"""

def get_content_analysis(self, org_id: str, domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Get content analysis for prompt generation.
    Returns analysis of all content for an organization.
    """
    def _get_content_analysis_operation():
        # Start with base query
        query_obj =