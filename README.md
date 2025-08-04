# Azure OpenAI Python Tutorial

A comprehensive Python application that demonstrates Azure OpenAI API usage from basic to advanced features. This educational tool helps developers understand how the OpenAI API works by providing practical examples and logging all raw API requests.

## Features

- ✅ **Basic Text Completion** - Legacy completions API with parameter exploration
- ✅ **Chat Completion** - Modern chat API with conversation history
- ✅ **Function Calling** - Advanced AI function calling with practical tools
- 🚧 **Streaming Responses** - Real-time response streaming (Coming Soon)
- ✅ **API Request Logging** - All HTTP requests saved to `logs/api_requests.txt`
- ✅ **Interactive Examples** - Learn by doing with hands-on examples
- ✅ **Error Handling** - Proper error handling and debugging guidance

## Prerequisites

- Python 3.8 or higher
- Azure subscription with OpenAI service
- Azure OpenAI resource with deployed model(s)

## Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd azure_openai_tutorial
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-10-21
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
   ```

## Getting Your Azure OpenAI Credentials

1. **API Key**: Found in Azure Portal → Your OpenAI Resource → Keys and Endpoint
2. **Endpoint**: Also in Keys and Endpoint section (e.g., `https://your-resource.openai.azure.com/`)
3. **Deployment Name**: Found in Azure Portal → Your OpenAI Resource → Model deployments

## Usage

### Quick Start

Run the interactive tutorial:
```bash
python main.py
```

### Individual Examples

Run specific examples directly:

**Basic Text Completion:**
```bash
python examples/basic_completion.py
```

**Chat Completion:**
```bash
python examples/chat_completion.py
```

**Function Calling:**
```bash
python examples/function_calling.py
```

### API Request Logging

All API requests are automatically logged to `logs/api_requests.txt`. This shows you:
- Request headers and body
- Response headers and body  
- Timestamps and duration
- Error details (if any)

Example log entry:
```
=== API REQUEST ===
Timestamp: 2024-01-01 12:00:00 UTC
Endpoint: https://your-resource.openai.azure.com/openai/deployments/gpt-35-turbo/completions
Method: POST
Headers: {
  "api-key": "[REDACTED]",
  "Content-Type": "application/json"
}
Request Body: {
  "model": "gpt-35-turbo",
  "prompt": "Hello, world!",
  "max_tokens": 100,
  "temperature": 0.7
}

=== API RESPONSE ===
Status Code: 200
Response Body: {
  "choices": [...],
  "usage": {...}
}
Duration: 1.234s
==================================================
```

## Project Structure

```
azure_openai_tutorial/
├── main.py                 # Main application entry point
├── config/
│   └── settings.py         # Configuration management
├── api/
│   ├── client.py           # Azure OpenAI client wrapper
│   └── logger.py           # API request/response logging
├── examples/
│   ├── basic_completion.py # Basic text completion examples
│   ├── chat_completion.py  # Chat completion examples
│   └── function_calling.py # Function calling examples
├── utils/
│   └── helpers.py          # Utility functions
├── logs/
│   └── api_requests.txt    # Raw API request logs (auto-created)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md             # This file
```

## Examples Included

### 1. Basic Text Completion
- Simple text completion
- Parameter exploration (temperature, max_tokens)
- Stop sequences
- Interactive completion mode

### 2. Chat Completion  
- Single-turn conversations
- System message usage
- Multi-turn conversations with history
- Different message roles
- Interactive chat mode

### 3. Function Calling
- Weather information retrieval
- Mathematical expression evaluation  
- Random number generation
- Knowledge base search
- Multiple function calls in sequence
- Interactive function calling mode

### 4. Streaming Responses (Coming Soon)
- Real-time response streaming
- Chunk processing
- Progress indicators

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | ✅ |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name | ✅ |
| `AZURE_OPENAI_API_VERSION` | API version (default: 2024-10-21) | ❌ |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | Chat model deployment (defaults to main deployment) | ❌ |

### API Parameters

The examples demonstrate various API parameters:

- **temperature**: Controls randomness (0.0 = deterministic, 2.0 = very random)
- **max_tokens**: Maximum number of tokens to generate
- **top_p**: Nucleus sampling parameter
- **stop**: Stop sequences to end generation
- **frequency_penalty**: Penalty for repeated tokens
- **presence_penalty**: Penalty for new topics

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure your `.env` file exists and contains all required variables
   - Check that variable names match exactly (case-sensitive)

2. **"Connection failed"**
   - Verify your API key is correct
   - Check that your endpoint URL is properly formatted
   - Ensure your Azure OpenAI resource is active

3. **"Model not found"**
   - Verify your deployment name matches exactly
   - Check that the model is deployed and active in Azure Portal

4. **Rate limiting errors**
   - Azure OpenAI has rate limits based on your tier
   - Wait a moment between requests during testing

### Debug Mode

Enable verbose logging by checking the `logs/api_requests.txt` file after running examples. This shows the exact API calls being made.

## Learning Path

1. **Start with Basic Completion** - Understand how text completion works
2. **Explore Chat Completion** - Learn modern conversational AI patterns  
3. **Try Different Parameters** - See how temperature, max_tokens affect output
4. **Study the Logs** - Examine raw API requests to understand the protocol
5. **Build Your Own** - Use the client wrapper to create custom applications

## Next Steps

After completing this tutorial, you'll be ready to:
- Build your own Azure OpenAI applications
- Understand API costs and optimization
- Implement proper error handling and retry logic
- Create conversational AI experiences
- Integrate AI into existing applications

## Security Best Practices

- ✅ Never commit `.env` files to version control
- ✅ Use environment variables for secrets
- ✅ API keys are redacted in logs
- ✅ Validate user inputs in production
- ✅ Implement proper rate limiting
- ✅ Monitor API usage and costs

## Contributing

This is an educational project. Feel free to:
- Add more examples
- Improve documentation  
- Fix bugs or issues
- Suggest new features

## License

This project is for educational purposes. Please respect Azure OpenAI's terms of service and usage policies.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review your Azure OpenAI configuration in Azure Portal
3. Examine the API logs in `logs/api_requests.txt`
4. Verify your environment variables in `.env`

---

Happy learning! 🚀
