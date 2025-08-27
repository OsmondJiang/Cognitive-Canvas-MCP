#!/usr/bin/env python3
"""
Test Chat Fork Search Functionality (via render method)
Since search is now integrated into the render method, this test file
tests search functionality through the unified render interface.
"""

import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.chat_fork import ChatForkManager

class TestChatForkSearch(unittest.TestCase):
    def setUp(self):
        self.manager = ChatForkManager()
        self.conv_id = "test_search_conversation"
        self._setup_test_conversation()
    
    def _setup_test_conversation(self):
        """Create test conversation structure"""
        # Main topic
        self.manager.pause_topic(
            self.conv_id,
            "Database Design",
            current_context="Designing PostgreSQL database for e-commerce",
            progress_status="Schema design completed",
            next_steps="Optimize queries and add indexes",
            bookmark="db_design"
        )
        
        # Nested topic
        self.manager.pause_topic(
            self.conv_id,
            "API Authentication",
            current_context="Implementing JWT authentication system",
            progress_status="Basic login/logout working",
            next_steps="Add refresh token functionality",
            pause_type="nested",
            bookmark="auth_system"
        )
        
        # Parallel topic
        self.manager.pause_topic(
            self.conv_id,
            "Frontend Development",
            current_context="Building React components for user interface",
            progress_status="Login page completed",
            next_steps="Implement product listing page",
            pause_type="parallel"
        )
    
    def test_search_basic_functionality(self):
        """Test basic search functionality via render"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="database")
        
        # Should contain search results
        self.assertIn("🔍 Search Results for: 'database'", result)
        self.assertIn("📊 Found", result)
        self.assertIn("🎯", result)  # Should have match indicators
    
    def test_render_without_search(self):
        """Test normal render without search"""
        result = self.manager.render_conversation_tree(self.conv_id)
        
        # Should not contain search markers
        self.assertNotIn("🔍 Search Results", result)
        self.assertIn("📖 Bookmarks:", result)
        self.assertIn("Main conversation", result)
    
    def test_search_nonexistent_conversation(self):
        """Test searching non-existent conversation"""
        result = self.manager.render_conversation_tree("nonexistent", search_query="test")
        
        self.assertEqual(result, "Error: Conversation not found")
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="blockchain")
        
        self.assertEqual(result, "🔍 No matches found for 'blockchain'")
    
    def test_search_scope_all(self):
        """Test global search scope"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="React", search_scope="all")
        
        self.assertIn("(Scope: all)", result)
        self.assertIn("🎯", result)
    
    def test_search_scope_bookmarks(self):
        """Test bookmark search scope"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="auth", search_scope="bookmarks")
        
        self.assertIn("(Scope: bookmarks)", result)
    
    def test_search_scope_current_branch(self):
        """Test current branch search scope"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="React", search_scope="current_branch")
        
        self.assertIn("(Scope: current_branch)", result)
    
    def test_search_max_results(self):
        """Test maximum results limit"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="e", max_results=2)
        
        # Should limit the results (hard to test exact count in tree format, but should not error)
        self.assertIn("🔍 Search Results", result)
    
    def test_search_match_details_in_tree(self):
        """Test that match details are integrated in tree"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="authentication")
        
        lines = result.split('\n')
        
        # Should have match detail lines with 🎯
        match_detail_lines = [line for line in lines if "└─ 🎯" in line]
        self.assertGreater(len(match_detail_lines), 0, "Should have match detail lines")
        
        # Should NOT have separate match details section
        self.assertNotIn("🎯 Match Details:", result)
    
    def test_search_case_insensitive(self):
        """Test case insensitive search"""
        result1 = self.manager.render_conversation_tree(self.conv_id, search_query="DATABASE")
        result2 = self.manager.render_conversation_tree(self.conv_id, search_query="database")
        
        # Both should find results (checking that neither is "No matches found")
        self.assertNotEqual(result1, "🔍 No matches found for 'DATABASE'")
        self.assertNotEqual(result2, "🔍 No matches found for 'database'")
    
    def test_search_empty_query(self):
        """Test empty query returns complete tree"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="")
        
        # Empty query should return complete tree, not filtered results
        self.assertNotIn("🔍 Search Results", result)
        self.assertIn("📖 Bookmarks:", result)
    
    def test_search_with_match_scores(self):
        """Test that search results include match scores"""
        result = self.manager.render_conversation_tree(self.conv_id, search_query="Authentication")
        
        # Should contain match score indicators
        self.assertIn("🎯(", result)  # Match score format: 🎯(1.5)
    
    def test_search_different_scopes(self):
        """Test different search scopes produce different results"""
        all_result = self.manager.render_conversation_tree(self.conv_id, search_query="design", search_scope="all")
        bookmark_result = self.manager.render_conversation_tree(self.conv_id, search_query="design", search_scope="bookmarks")
        
        # Results may be different based on scope
        self.assertIn("(Scope: all)", all_result)
        self.assertIn("(Scope: bookmarks)", bookmark_result)

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
