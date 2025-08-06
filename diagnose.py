#!/usr/bin/env python3
"""
Azure OpenAI Connection Diagnostic Tool
Run this on the problematic laptop to diagnose connection issues.
Based on: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages
"""

import os
import json
import logging
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
import requests

# Load environment variables
load_dotenv()

# Enable detailed logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("openai").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

def check_environment():
    """Check environment variables."""
    print("🔍 Checking Environment Variables...")
    
    required = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
    
    for var in required:
        value = os.getenv(var)
        if value:
            if "KEY" in var:
                print(f"   ✅ {var}: {'***' + value[-4:] if len(value) > 4 else 'Too Short'}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Missing!")
    
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    print(f"   📍 AZURE_OPENAI_API_VERSION: {api_version}")
    print()

def check_endpoint_format():
    """Validate endpoint format."""
    print("🔍 Checking Endpoint Format...")
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    
    if not endpoint:
        print("   ❌ No endpoint configured")
        return False
    
    print(f"   📍 Endpoint: {endpoint}")
    
    # Check format
    if not endpoint.endswith('/'):
        print("   ⚠️  Warning: Endpoint should end with '/'")
    
    if 'openai.azure.com' not in endpoint:
        print("   ⚠️  Warning: Endpoint should contain 'openai.azure.com'")
    
    if not endpoint.startswith('https://'):
        print("   ❌ Endpoint should start with 'https://'")
        return False
    
    print("   ✅ Endpoint format looks correct")
    print()
    return True

def test_basic_connectivity():
    """Test basic internet connectivity to Azure."""
    print("🔍 Testing Basic Connectivity...")
    
    try:
        response = requests.get("https://management.azure.com/", timeout=10)
        print("   ✅ Can reach Azure management endpoint")
    except requests.exceptions.ConnectTimeout:
        print("   ❌ Connection timeout to Azure - check internet/firewall")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error to Azure - check internet connection")
        return False
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")
    
    print()
    return True

def test_endpoint_reachability():
    """Test if the specific Azure OpenAI endpoint is reachable."""
    print("🔍 Testing Azure OpenAI Endpoint Reachability...")
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    if not endpoint:
        print("   ❌ No endpoint to test")
        return False
    
    try:
        # Just test if we can reach the endpoint
        response = requests.get(endpoint, timeout=10)
        print(f"   ✅ Can reach endpoint: {endpoint}")
    except requests.exceptions.ConnectTimeout:
        print(f"   ❌ Connection timeout to {endpoint}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error to {endpoint}")
        return False
    except Exception as e:
        print(f"   ⚠️  Response from endpoint (may be expected): {e}")
    
    print()
    return True

def test_openai_client():
    """Test Azure OpenAI client initialization and API call with detailed debugging."""
    print("🔍 Testing Azure OpenAI Client...")
    
    # Validate required environment variables first
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    
    if not all([api_key, endpoint, deployment]):
        print("   ❌ Missing required environment variables")
        return False
    
    print(f"   📍 Using API Version: {api_version}")
    print(f"   📍 Testing with deployment: {deployment}")
    
    try:
        # Initialize client with verbose logging
        print("   🔧 Initializing Azure OpenAI client...")
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        print("   ✅ Client initialized successfully")
        
        # Test API call with minimal payload
        print("   🔧 Making test API call...")
        messages = [{"role": "user", "content": "Hi"}]
        
        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=5,
            temperature=1
        )
        
        print("   ✅ API call successful!")
        print(f"   📍 Response: {response.choices[0].message.content}")
        print(f"   📍 Usage: {response.usage.total_tokens} tokens")
        
    except APIConnectionError as e:
        print(f"   ❌ API Connection Error: {e}")
        print(f"   💡 Full error details: {type(e).__name__}")
        if hasattr(e, 'response') and e.response:
            print(f"   💡 HTTP Status: {e.response.status_code}")
            print(f"   💡 Response Headers: {dict(e.response.headers)}")
        
        print("\n   🔧 Connection troubleshooting:")
        print("   - Check internet connection")
        print("   - Verify endpoint URL is reachable")
        print("   - Check firewall/proxy settings")
        print("   - Try different network (mobile hotspot)")
        return False
        
    except APIError as e:
        print(f"   ❌ API Error: {e}")
        print(f"   💡 Error type: {type(e).__name__}")
        
        if hasattr(e, 'response') and e.response:
            print(f"   💡 HTTP Status: {e.response.status_code}")
            print(f"   💡 Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        
        if "401" in str(e) or "Unauthorized" in str(e):
            print("\n   🔧 Authentication troubleshooting:")
            print("   - Verify API key is correct and active")
            print("   - Check if key has necessary permissions")
            print("   - Try regenerating the API key in Azure portal")
        elif "404" in str(e) or "NotFound" in str(e):
            print("\n   🔧 Deployment/Model troubleshooting:")
            print("   - Verify deployment name is correct and case-sensitive")
            print("   - Check if model is deployed and ready in Azure portal")
            print("   - Ensure deployment is in the same region as endpoint")
        elif "429" in str(e):
            print("\n   🔧 Rate limit troubleshooting:")
            print("   - Wait a few minutes and try again")
            print("   - Check quota limits in Azure portal")
        
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        print(f"   💡 Error type: {type(e).__name__}")
        print(f"   💡 Full exception: {str(e)}")
        
        # Check for specific error patterns
        error_str = str(e).lower()
        if "name resolution" in error_str or "dns" in error_str:
            print("\n   🔧 DNS troubleshooting:")
            print("   - Check DNS settings")
            print("   - Try using different DNS servers (8.8.8.8)")
        elif "timeout" in error_str:
            print("\n   🔧 Timeout troubleshooting:")
            print("   - Check network stability")
            print("   - Try increasing timeout in client settings")
        elif "certificate" in error_str or "ssl" in error_str:
            print("\n   🔧 SSL/Certificate troubleshooting:")
            print("   - Check system time is correct")
            print("   - Update certificates if needed")
        
        return False
    
    print()
    return True

def test_alternative_auth():
    """Test alternative authentication methods."""
    print("🔍 Testing Alternative Authentication...")
    
    try:
        # Check if azure-identity is available for Entra ID auth
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        
        print("   📍 azure-identity package is available")
        print("   💡 You can try Microsoft Entra ID authentication instead of API key")
        print("   💡 Run: pip install azure-identity")
        print("   💡 Then use DefaultAzureCredential for more secure auth")
        
        # Test if DefaultAzureCredential can get a token
        try:
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            print("   ✅ DefaultAzureCredential is available and configured")
            return True
        except Exception as e:
            print(f"   ⚠️  DefaultAzureCredential failed: {e}")
            print("   💡 This is normal if you haven't set up Azure authentication")
            return False
            
    except ImportError:
        print("   📍 azure-identity package not installed")
        print("   💡 For production use, consider: pip install azure-identity")
        return False

def main():
    """Run all diagnostic checks."""
    print("🚀 Azure OpenAI Connection Diagnostics")
    print("Based on: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages")
    print("=" * 80)
    print()
    
    # Run checks in order
    checks = [
        ("Environment Variables", check_environment),
        ("Endpoint Format", check_endpoint_format),
        ("Basic Connectivity", test_basic_connectivity),
        ("Endpoint Reachability", test_endpoint_reachability),
        ("Azure OpenAI Client", test_openai_client),
        ("Alternative Auth", test_alternative_auth)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            print(f"Running: {check_name}")
            result = check_func()
            results.append(result)
            if result:
                print(f"✅ {check_name}: PASSED\n")
            else:
                print(f"❌ {check_name}: FAILED\n")
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {e}\n")
            results.append(False)
    
    print("📊 Final Summary:")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print("🎉 All checks passed! Your configuration should work perfectly.")
    elif passed >= 4:  # Most checks passed
        print(f"✅ {passed}/{total} checks passed. Minor issues that might not affect functionality.")
    else:
        print(f"❌ Only {passed}/{total} checks passed. Configuration needs attention.")
        print()
        print("🔧 Next Steps:")
        print("1. Copy this diagnostic output")
        print("2. Focus on the failed checks above")
        print("3. Try these alternative API versions if connection fails:")
        print("   - AZURE_OPENAI_API_VERSION=2024-02-15-preview")
        print("   - AZURE_OPENAI_API_VERSION=2023-12-01-preview")
        print("4. Test from a different network (mobile hotspot) to rule out network issues")
        print("5. Check Azure portal to ensure your OpenAI resource is active and deployed")
        
    print("\n💡 For more help, visit:")
    print("   https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages")

if __name__ == "__main__":
    main()
