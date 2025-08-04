"""
API request/response logging for educational purposes.
"""

import json
import datetime
import os
from typing import Dict, Any


class APILogger:
    """Logs API requests and responses to help developers understand the raw API calls."""
    
    def __init__(self, log_file: str = "logs/api_requests.txt"):
        self.log_file = log_file
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure the log directory exists."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_request(self, 
                   endpoint: str, 
                   method: str, 
                   headers: Dict[str, str], 
                   request_body: Dict[str, Any],
                   response_status: int = None,
                   response_headers: Dict[str, str] = None,
                   response_body: Dict[str, Any] = None,
                   duration: float = None):
        """
        Log an API request and response.
        
        Args:
            endpoint: The API endpoint URL
            method: HTTP method (GET, POST, etc.)
            headers: Request headers
            request_body: Request payload
            response_status: HTTP response status code
            response_headers: Response headers
            response_body: Response payload
            duration: Request duration in seconds
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Sanitize headers (remove API key)
        safe_headers = self._sanitize_headers(headers)
        safe_response_headers = self._sanitize_headers(response_headers or {})
        
        log_entry = f"""
=== API REQUEST ===
Timestamp: {timestamp}
Endpoint: {endpoint}
Method: {method}
Headers: {json.dumps(safe_headers, indent=2)}
Request Body: {json.dumps(request_body, indent=2)}
"""
        
        if response_status is not None:
            log_entry += f"""
=== API RESPONSE ===
Status Code: {response_status}
Response Headers: {json.dumps(safe_response_headers, indent=2)}
"""
            if response_body:
                log_entry += f"Response Body: {json.dumps(response_body, indent=2)}\n"
            
            if duration:
                log_entry += f"Duration: {duration:.3f}s\n"
        
        log_entry += "=" * 50 + "\n"
        
        # Write to log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        print(f"✅ API call logged to {self.log_file}")
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers."""
        safe_headers = headers.copy()
        
        # List of header keys that should be redacted
        sensitive_keys = ["api-key", "authorization", "x-api-key", "authorization"]
        
        for key in sensitive_keys:
            if key.lower() in [h.lower() for h in safe_headers.keys()]:
                # Find the actual key (case-insensitive)
                actual_key = next(h for h in safe_headers.keys() if h.lower() == key.lower())
                safe_headers[actual_key] = "[REDACTED]"
        
        return safe_headers
    
    def clear_logs(self):
        """Clear the log file."""
        if os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f"Log cleared at {datetime.datetime.now()}\n")
            print(f"✅ Log file cleared: {self.log_file}")


# Global logger instance
api_logger = APILogger()
