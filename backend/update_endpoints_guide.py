"""
Quick update script to add multi-tenant authentication to remaining endpoints.
This will show the pattern for updating the main.py file.
"""

# Pattern for updating endpoints:
# 1. Add current_user: AuthUser = Depends(get_current_user_with_org) to function signature
# 2. Add org_id = get_org_id_from_user(current_user) in the function body
# 3. Pass org_id to service calls

# Here are the remaining endpoints that need updating:

endpoints_to_update = [
    "get_content",
    "list_domains", 
    "search_chunks",
    "get_content_chunks",
    "process_content_for_rag",
    "generate_content",
    "create_template",
    "get_template", 
    "search_templates"
]

print("Endpoints that need multi-tenant authentication:")
for endpoint in endpoints_to_update:
    print(f"- {endpoint}")

print("\nPattern to apply:")
print("1. Add: current_user: AuthUser = Depends(get_current_user_with_org)")
print("2. Add: org_id = get_org_id_from_user(current_user)")
print("3. Pass org_id to service calls")
