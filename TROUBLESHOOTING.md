# Azure OpenAI Connection Troubleshooting Guide

Based on [Microsoft's Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages)

## 🔒 SSL Certificate Error (Quick Fix)

**If you see: "certificate verify failed: self-signed certificate in certificate chain"**

This is common in corporate environments. Quick fix:

```bash
# Set environment variable to disable SSL verification
export DISABLE_SSL_VERIFY=true

# Then run your application
python simple_chat.py
```

⚠️ **Security Note:** Only use this in corporate environments with SSL inspection. Never use in production with real certificates.

## 🚀 Quick Diagnostic Steps

1. **Run the diagnostic tool first:**
   ```bash
   python diagnose.py
   ```

2. **If you get SSL certificate errors (corporate networks):**
   ```bash
   export DISABLE_SSL_VERIFY=true
   python diagnose.py
   ```

3. **Enable debug logging:**
   ```bash
   export DEBUG_AZURE_OPENAI=true
   python simple_chat.py
   ```

4. **Check your logs:**
   ```bash
   cat logs/api_requests.txt
   ```

## 🔧 Common Connection Issues

### 1. APIConnectionError (Network Issues)

**Symptoms:** Cannot reach Azure OpenAI endpoint
```
APIConnectionError: Connection error
```

**Solutions:**
- **Test basic connectivity:** Try `curl https://management.azure.com/`
- **Check firewall/proxy:** Corporate networks often block Azure endpoints
- **Try different network:** Use mobile hotspot to test
- **Verify endpoint URL:** Should be `https://your-resource.openai.azure.com/`
- **Check DNS:** Try using `8.8.8.8` as DNS server

### 2. 401 Unauthorized (Authentication)

**Symptoms:** Invalid API key or permissions
```
APIError: 401 Unauthorized
```

**Solutions:**
- **Verify API key:** Should be 32+ characters from Azure portal
- **Check key permissions:** Ensure key has "Cognitive Services OpenAI User" role
- **Regenerate key:** Try creating a new API key in Azure portal
- **Try Entra ID auth:** More secure alternative to API keys

### 3. 404 Not Found (Deployment Issues)

**Symptoms:** Model deployment not found
```
APIError: 404 Not Found
```

**Solutions:**
- **Case-sensitive deployment name:** Verify exact spelling in Azure portal
- **Check model deployment:** Ensure model is deployed and "Ready" status
- **Verify region:** Deployment must be in same region as endpoint
- **Check model availability:** Some models are region-specific

### 4. 429 Rate Limit (Quota Issues)

**Symptoms:** Too many requests
```
RateLimitError: 429 Too Many Requests
```

**Solutions:**
- **Wait and retry:** Rate limits reset over time
- **Check quota:** Review usage limits in Azure portal
- **Upgrade plan:** Consider higher tier if consistently hitting limits

## 🔑 Configuration Checklist

### Required Environment Variables
```bash
AZURE_OPENAI_API_KEY=your-32-character-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-10-21
```

### Validate Your Configuration
1. **Endpoint format:** Must start with `https://` and end with `/`
2. **API key length:** Should be 32+ characters
3. **Deployment name:** Exact match from Azure portal (case-sensitive)
4. **API version:** Use YYYY-MM-DD format

## 🌐 Network Troubleshooting

### Corporate Networks
- **Proxy settings:** Configure `HTTP_PROXY` and `HTTPS_PROXY` if needed
- **Firewall rules:** Azure OpenAI uses port 443 (HTTPS)
- **DNS resolution:** Ensure `*.openai.azure.com` can be resolved

### SSL/Certificate Issues (Corporate Networks)
- **Most common fix:** `export DISABLE_SSL_VERIFY=true` then run the app
- **Corporate SSL inspection:** Many companies use self-signed certificates
- **System time:** Ensure computer clock is accurate
- **Certificate store:** Update system certificates if needed
- **Antivirus/Security:** Some security software blocks API calls
- **Alternative:** Ask IT to add `*.openai.azure.com` to SSL inspection bypass list

## 🔄 Alternative API Versions to Try

If `2024-10-21` doesn't work, try these versions:
```bash
# Stable versions
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_API_VERSION=2023-05-15

# Latest preview (may have new features but less stable)
AZURE_OPENAI_API_VERSION=2025-03-01-preview
```

## 🔐 Alternative Authentication (More Secure)

Instead of API keys, use Microsoft Entra ID:

1. **Install azure-identity:**
   ```bash
   pip install azure-identity
   ```

2. **Login to Azure:**
   ```bash
   az login
   ```

3. **Use DefaultAzureCredential:**
   ```python
   from azure.identity import DefaultAzureCredential, get_bearer_token_provider
   from openai import AzureOpenAI
   
   credential = DefaultAzureCredential()
   token_provider = get_bearer_token_provider(
       credential, "https://cognitiveservices.azure.com/.default"
   )
   
   client = AzureOpenAI(
       azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
       azure_ad_token_provider=token_provider,
       api_version="2024-10-21"
   )
   ```

## 📊 Azure Portal Verification

1. **Resource Status:** Ensure Azure OpenAI resource is "Running"
2. **Model Deployments:** Check that your model shows "Succeeded" status
3. **Keys and Endpoint:** Copy exact values from "Keys and Endpoint" section
4. **Network settings:** If using private endpoints, verify network access
5. **Quota usage:** Check current usage vs. allocated quota

## 🔍 Advanced Debugging

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("openai").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
```

### Test Minimal API Call
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="your-key",
    azure_endpoint="your-endpoint",
    api_version="2024-10-21"
)

# Minimal test
response = client.chat.completions.create(
    model="your-deployment",
    messages=[{"role": "user", "content": "Hi"}],
    max_tokens=1
)
```

### Check HTTP Response Details
Our diagnostic tool captures full HTTP request/response details in `logs/api_requests.txt`.

## 📞 Getting Help

1. **Run diagnostics:** `python diagnose.py`
2. **Copy output:** Share diagnostic results for faster troubleshooting
3. **Check Azure status:** [Azure Status Page](https://status.azure.com/)
4. **Azure Support:** Submit ticket through Azure portal if needed

## 📚 References

- [Azure OpenAI Supported Languages](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages)
- [Azure OpenAI Authentication](https://learn.microsoft.com/en-us/azure/developer/ai/get-started-securing-your-ai-app)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
