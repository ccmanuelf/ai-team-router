#!/usr/bin/env python3
"""
Test suite for tool integration
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_team_router import AITeamRouter

class TestTools:
    def setup_method(self):
        self.router = AITeamRouter()
    
    def test_tool_identification(self):
        """Test that tool requirements are identified correctly"""
        tools = self.router._identify_tool_requirements(
            "Search the web for latest Python news"
        )
        assert tools["web_search"] == True
        
        tools = self.router._identify_tool_requirements(
            "Run this Python code and debug it"
        )
        assert tools["code_execution"] == True
        
        tools = self.router._identify_tool_requirements(
            "Process this Excel file with 150k rows"
        )
        assert tools["excel_optimizer"] == True
        
        tools = self.router._identify_tool_requirements(
            "Analyze this screenshot"
        )
        assert tools["vision"] == True
    
    def test_domain_identification(self):
        """Test domain identification"""
        domain = self.router._identify_domain("Create a Vue component", {})
        assert domain == "frontend"
        
        domain = self.router._identify_domain("Debug this Laravel controller", {})
        assert domain == "backend_php"
        
        domain = self.router._identify_domain("Process 150000 Excel rows", {})
        assert domain == "enterprise"
        
        domain = self.router._identify_domain("Analyze this image", {})
        assert domain == "visual"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])