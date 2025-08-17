
import sys
sys.path.append('.')
from http_connection_fixes import OptimizedHTTPClient

# Import and patch the existing router
import src.ai_team_router as original_router

# Replace the aiohttp client with our optimized requests client
original_router.AITeamRouter.__init__ = lambda self: self._init_with_http_fixes()

def _init_with_http_fixes(self):
    self.active_member = None
    self.team_members = self._initialize_team()
    self.request_history = []
    self.performance_metrics = {}
    self.emergency_mode = False
    self.min_system_memory_gb = 2.0
    
    # Use our optimized HTTP client instead of aiohttp
    self.ollama_client = OptimizedHTTPClient()
    
    if self.ollama_client.check_connection():
        print("✅ Ollama connection verified with HTTP fixes")
    else:
        print("❌ Ollama connection failed")

original_router.AITeamRouter._init_with_http_fixes = _init_with_http_fixes

# Run the patched router
if __name__ == "__main__":
    original_router.main()
