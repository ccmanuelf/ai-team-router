#!/usr/bin/env python3
"""
Router HTTP Connection Fixes
============================

Alternative HTTP implementations to fix connection timeout issues
Focus: Replace aiohttp with requests and improve TCP handling

Key Issues Identified:
- HTTPConnectionPool timeouts after 300s 
- Models work fine via Ollama CLI (under 3 minutes)
- Router HTTP overhead causing connection failures

Solutions:
1. Replace aiohttp with requests library
2. Improve TCP connection handling
3. Add connection debugging and monitoring
4. Test direct connection approaches
"""

import requests
import time
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import socket
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class OptimizedHTTPClient:
    """Optimized HTTP client for Ollama connections"""
    
    def __init__(self, base_url="http://localhost:11434", max_retries=3):
        self.base_url = base_url
        self.session = self._create_optimized_session(max_retries)
        
    def _create_optimized_session(self, max_retries):
        """Create session with optimized connection settings"""
        session = requests.Session()
    
        # Configure retry strategy (fix deprecated method_whitelist)
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],  # Updated from method_whitelist
            backoff_factor=1
        )        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'User-Agent': 'AI-Team-Router/1.0'
        })
        
        return session
    
    def test_connection(self):
        """Test basic connectivity to Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def send_generate_request(self, model_id, prompt, timeout=600, stream=False, options=None):
        """Send generation request with improved error handling"""
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": stream,
            "options": options or {}
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"Sending request to {model_id} (timeout: {timeout}s)")
            
            # Use requests instead of aiohttp
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
                stream=False  # Disable streaming for debugging
            )
            
            connection_time = time.time() - start_time
            logger.info(f"HTTP response received in {connection_time:.1f}s")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    total_time = time.time() - start_time
                    logger.info(f"✅ Request completed in {total_time:.1f}s")
                    return {
                        "success": True,
                        "data": result,
                        "response_time": total_time,
                        "connection_time": connection_time
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return {
                        "success": False,
                        "error": f"JSON decode error: {e}",
                        "response_time": time.time() - start_time
                    }
            else:
                logger.error(f"HTTP error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": time.time() - start_time
                }
                
        except requests.exceptions.Timeout as e:
            total_time = time.time() - start_time
            logger.error(f"Request timeout after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Timeout after {total_time:.1f}s: {e}",
                "response_time": total_time
            }
        except requests.exceptions.ConnectionError as e:
            total_time = time.time() - start_time
            logger.error(f"Connection error after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Connection error: {e}",
                "response_time": total_time
            }
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Unexpected error after {total_time:.1f}s: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {e}",
                "response_time": total_time
            }
    
    def send_unload_request(self, model_id, timeout=30):
        """Send unload request"""
        return self.send_generate_request(
            model_id=model_id,
            prompt="",
            timeout=timeout,
            options={"keep_alive": 0}
        )
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

class DirectTCPClient:
    """Direct TCP connection client for testing"""
    
    def __init__(self, host="localhost", port=11434):
        self.host = host
        self.port = port
    
    def test_tcp_connection(self):
        """Test raw TCP connection to Ollama"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                start_time = time.time()
                result = sock.connect_ex((self.host, self.port))
                connection_time = time.time() - start_time
                
                if result == 0:
                    logger.info(f"✅ TCP connection successful in {connection_time:.3f}s")
                    return True
                else:
                    logger.error(f"❌ TCP connection failed: {result}")
                    return False
        except Exception as e:
            logger.error(f"TCP connection error: {e}")
            return False
    
    def send_http_request_raw(self, payload, timeout=600):
        """Send raw HTTP request over TCP"""
        try:
            # Prepare HTTP request
            json_payload = json.dumps(payload)
            http_request = f"""POST /api/generate HTTP/1.1\r
Host: {self.host}:{self.port}\r
Content-Type: application/json\r
Content-Length: {len(json_payload)}\r
Connection: close\r
\r
{json_payload}"""
            
            # Send over raw TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                start_time = time.time()
                
                logger.info(f"Connecting via raw TCP...")
                sock.connect((self.host, self.port))
                
                logger.info(f"Sending HTTP request...")
                sock.sendall(http_request.encode('utf-8'))
                
                logger.info(f"Waiting for response...")
                response_data = b""
                while True:
                    try:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        response_data += chunk
                    except socket.timeout:
                        logger.warning("Socket timeout during response reading")
                        break
                
                total_time = time.time() - start_time
                logger.info(f"Raw TCP request completed in {total_time:.1f}s")
                
                # Parse HTTP response
                response_str = response_data.decode('utf-8', errors='ignore')
                
                # Split headers and body
                if '\\r\\n\\r\\n' in response_str:
                    headers, body = response_str.split('\\r\\n\\r\\n', 1)
                    
                    # Check status code
                    if 'HTTP/1.1 200' in headers:
                        try:
                            result = json.loads(body)
                            return {
                                "success": True,
                                "data": result,
                                "response_time": total_time,
                                "method": "raw_tcp"
                            }
                        except json.JSONDecodeError:
                            logger.error("Failed to parse JSON response")
                            return {
                                "success": False,
                                "error": "JSON parse error",
                                "response_time": total_time,
                                "raw_response": body[:500]
                            }
                    else:
                        logger.error(f"HTTP error in response: {headers}")
                        return {
                            "success": False,
                            "error": f"HTTP error: {headers}",
                            "response_time": total_time
                        }
                else:
                    logger.error("Invalid HTTP response format")
                    return {
                        "success": False,
                        "error": "Invalid HTTP response",
                        "response_time": total_time,
                        "raw_response": response_str[:500]
                    }
                    
        except Exception as e:
            total_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"Raw TCP request failed: {e}")
            return {
                "success": False,
                "error": f"TCP error: {e}",
                "response_time": total_time
            }

def test_connection_methods():
    """Test different connection methods"""
    
    print("🔧 TESTING HTTP CONNECTION METHODS")
    print("=" * 60)
    
    # Test 1: Optimized requests client
    print("\\n1. Testing Optimized Requests Client")
    print("-" * 40)
    
    requests_client = OptimizedHTTPClient()
    
    if requests_client.test_connection():
        print("✅ Basic connection test passed")
        
        # Test with simple prompt
        result = requests_client.send_generate_request(
            model_id="gemma3:1b",  # Start with small model
            prompt="Hello",
            timeout=120
        )
        
        if result["success"]:
            print(f"✅ Requests client: {result['response_time']:.1f}s")
        else:
            print(f"❌ Requests client failed: {result['error']}")
    else:
        print("❌ Basic connection test failed")
    
    requests_client.close()
    
    # Test 2: Direct TCP connection
    print("\\n2. Testing Direct TCP Connection")
    print("-" * 40)
    
    tcp_client = DirectTCPClient()
    
    if tcp_client.test_tcp_connection():
        print("✅ TCP connection test passed")
        
        # Test HTTP over TCP
        result = tcp_client.send_http_request_raw({
            "model": "gemma3:1b",
            "prompt": "Hello",
            "stream": False
        }, timeout=120)
        
        if result["success"]:
            print(f"✅ Raw TCP client: {result['response_time']:.1f}s")
        else:
            print(f"❌ Raw TCP client failed: {result['error']}")
    else:
        print("❌ TCP connection test failed")
    
    # Test 3: Connection timing comparison
    print("\\n3. Connection Timing Analysis")
    print("-" * 40)
    
    methods = [
        ("Basic requests", lambda: requests.get("http://localhost:11434/api/tags", timeout=10)),
        ("Session requests", lambda: requests_client.session.get("http://localhost:11434/api/tags", timeout=10)),
        ("TCP connection", lambda: tcp_client.test_tcp_connection())
    ]
    
    for method_name, method_func in methods:
        try:
            start_time = time.time()
            result = method_func()
            duration = time.time() - start_time
            status = "✅" if result else "❌"
            print(f"{status} {method_name}: {duration:.3f}s")
        except Exception as e:
            print(f"❌ {method_name}: {e}")

if __name__ == "__main__":
    test_connection_methods()
