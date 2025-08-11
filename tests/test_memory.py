#!/usr/bin/env python3
"""
Test suite for memory management
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_team_router import AITeamRouter

class TestMemory:
    def setup_method(self):
        self.router = AITeamRouter()
    
    def test_memory_calculation(self):
        """Test memory availability calculation"""
        available = self.router._get_available_memory_gb()
        assert available > 0
        assert available < 18  # Total system memory
    
    def test_model_fits_memory(self):
        """Test that models are selected within memory constraints"""
        # Simulate low memory
        original_method = self.router._get_available_memory_gb
        self.router._get_available_memory_gb = lambda: 2.0
        
        requirements = {
            "complexity": 1,
            "domain": "general",
            "needs_vision": False,
            "needs_uncensored": False,
            "needs_large_context": False,
            "needs_338_languages": False,
            "tool_requirements": {},
            "priority": "normal"
        }
        
        member_id, member = self.router.select_team_member(requirements)
        assert member.memory_gb < 2.0  # Should select small model
        
        # Restore original method
        self.router._get_available_memory_gb = original_method
    
    def test_emergency_fallback(self):
        """Test emergency fallback selection"""
        # Simulate no memory
        self.router._get_available_memory_gb = lambda: 0.5
        
        requirements = {
            "complexity": 5,
            "domain": "coding",
            "needs_vision": False,
            "needs_uncensored": False,
            "needs_large_context": True,
            "needs_338_languages": False,
            "tool_requirements": {},
            "priority": "high"
        }
        
        member_id, member = self.router.select_team_member(requirements)
        assert member_id == "gemma_tiny"  # Emergency fallback

if __name__ == "__main__":
    pytest.main([__file__, "-v"])