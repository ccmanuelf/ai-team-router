#!/usr/bin/env python3
"""
Test suite for AI Team Router routing logic
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_team_router import AITeamRouter

class TestRouting:
    def setup_method(self):
        self.router = AITeamRouter()
    
    def test_vue_routing(self):
        """Test that Vue requests route to DeepCoder"""
        requirements = self.router._analyze_task(
            "Create a Vue component",
            {}
        )
        assert requirements["domain"] == "frontend"
        
        member_id, member = self.router.select_team_member(requirements)
        assert member_id == "deepcoder_primary"
    
    def test_excel_routing(self):
        """Test that Excel requests route to Qwen"""
        requirements = self.router._analyze_task(
            "Process 150000 rows in Excel",
            {}
        )
        assert requirements["domain"] == "enterprise"
        
        member_id, member = self.router.select_team_member(requirements)
        assert member_id == "qwen_analyst"
    
    def test_vision_routing(self):
        """Test that image requests route to Granite Vision"""
        requirements = self.router._analyze_task(
            "Analyze this screenshot",
            {"has_image": True}
        )
        assert requirements["needs_vision"] == True
        
        member_id, member = self.router.select_team_member(requirements)
        assert member_id == "granite_vision"
    
    def test_complexity_estimation(self):
        """Test complexity estimation"""
        simple = self.router._estimate_complexity("What is 2+2?")
        assert simple <= 2
        
        complex = self.router._estimate_complexity(
            "Refactor this complex algorithm with optimization and comprehensive testing"
        )
        assert complex >= 4

if __name__ == "__main__":
    pytest.main([__file__, "-v"])