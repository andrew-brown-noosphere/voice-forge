#!/usr/bin/env python3
"""
JWT Token Debug Script for Clerk Authentication

This script helps debug JWT tokens from Clerk to understand
why some endpoints work while others fail.
"""

import jwt
import json
import sys
from datetime import datetime

def decode_jwt_payload(token):
    """Decode JWT token without signature verification."""
    try:
        # Decode without verification to see the payload
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        return {"error": f"Failed to decode token: {e}"}

def analyze_token(token):
    """Analyze a JWT token and provide detailed information."""
    print("🔍 JWT Token Analysis")
    print("=" * 50)
    
    # Decode the payload
    payload = decode_jwt_payload(token)
    
    if "error" in payload:
        print(f"❌ Error: {payload['error']}")
        return
    
    # Print the full payload
    print("📋 Full Token Payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    # Check critical fields for VoiceForge authentication
    print("🔑 Authentication Analysis:")
    print("-" * 30)
    
    # User ID
    user_id = payload.get("sub")
    print(f"User ID (sub): {'✅ ' + user_id if user_id else '❌ Missing'}")
    
    # Organization ID - this is the key field!
    org_id = payload.get("org_id")
    print(f"Organization ID: {'✅ ' + org_id if org_id else '❌ Missing - THIS IS THE PROBLEM!'}")
    
    # Organization Role
    org_role = payload.get("org_role")
    print(f"Organization Role: {'✅ ' + org_role if org_role else '❌ Missing'}")
    
    # Email
    email = payload.get("email")
    print(f"Email: {'✅ ' + email if email else '❌ Missing'}")
    
    # Expiration
    exp = payload.get("exp")
    if exp:
        exp_time = datetime.fromtimestamp(exp)
        current_time = datetime.now()
        if current_time > exp_time:
            print(f"Expiration: ❌ EXPIRED at {exp_time}")
        else:
            time_left = exp_time - current_time
            print(f"Expiration: ✅ Valid until {exp_time} ({time_left} remaining)")
    else:
        print("Expiration: ❌ Missing")
    
    print()
    
    # Diagnosis
    print("🩺 Diagnosis:")
    print("-" * 15)
    
    if not org_id:
        print("❌ PRIMARY ISSUE: Missing 'org_id' in token")
        print("   This explains why /crawl endpoints fail with 401")
        print("   The get_current_user_with_org dependency requires org_id")
        print()
        print("🔧 SOLUTIONS:")
        print("   1. Ensure user is properly added to 'arhoolie' organization in Clerk")
        print("   2. Check if user has selected the organization in frontend")
        print("   3. Verify Clerk organization configuration")
        print("   4. Try logging out and back in to refresh the token")
    elif not org_role:
        print("⚠️  Missing 'org_role' - user might not have proper organization membership")
    else:
        print("✅ Token appears to have required organization information")
        print("   The issue might be elsewhere in the authentication flow")

if __name__ == "__main__":
    print("JWT Token Debugger for VoiceForge")
    print("=" * 40)
    print()
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("Paste your JWT token (it's safe - this script runs locally):")
        token = input().strip()
    
    if token:
        analyze_token(token)
    else:
        print("❌ No token provided")

# Example usage:
# python debug_jwt_token.py "eyJhbGciOiJSUzI1NiIs..."
