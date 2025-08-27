#!/usr/bin/env python3
"""
Test improved unified render interface - match details integrated in tree display
"""

import unittest
from tools.chat_fork import ChatForkManager

class TestIntegratedMatches(unittest.TestCase):
    
    def setUp(self):
        """Setup test conversation"""
        self.manager = ChatForkManager()
        
        # Create test conversation
        self.manager.pause_topic("test", "React Project Development", 
                                "Developing a React application, need to discuss component design", 
                                "Completed basic architecture", 
                                "Implement user authentication", 
                                "nested", "React Project")
        
        self.manager.pause_topic("test", "User Authentication Module", 
                                "Implement JWT authentication and permission management system", 
                                "Researched JWT implementation approaches", 
                                "Write authentication middleware", 
                                "nested", "Auth System")
    
    def test_unified_render_without_search(self):
        """Test unified render interface - without search (complete tree)"""
        result = self.manager.render_conversation_tree("test")
        
        # Should include complete conversation tree
        self.assertIn("Main conversation", result)
        self.assertIn("React Project Development", result)
        self.assertIn("User Authentication Module", result)
        self.assertIn("📖 Bookmarks:", result)
        
        # Should not include search-related markers
        self.assertNotIn("🔍 Search Results", result)
        self.assertNotIn("🎯", result)
    
    def test_unified_render_with_search(self):
        """Test unified render interface - with search (filtered tree)"""
        result = self.manager.render_conversation_tree("test", search_query="React")
        
        # Should include search markers
        self.assertIn("🔍 Search Results for: 'React'", result)
        self.assertIn("📊 Found", result)
        
        # Should include match markers and details
        self.assertIn("🎯", result)
        
        # Should not include complete tree bookmark summary
        self.assertNotIn("📖 Bookmarks:", result)
    
    def test_match_details_integrated_in_tree(self):
        """Test if match details are properly integrated in tree display"""
        result = self.manager.render_conversation_tree("test", search_query="authentication")
        
        # Check match details displayed directly under nodes
        lines = result.split('\n')
        
        # Find lines with match scores
        match_score_lines = [line for line in lines if "🎯(" in line]
        self.assertGreater(len(match_score_lines), 0, "Should have nodes with match scores")
        
        # Check match detail lines (should start with 🎯)
        match_detail_lines = [line for line in lines if "└─ 🎯" in line]
        self.assertGreater(len(match_detail_lines), 0, "Should have match detail lines")
        
        # Verify match detail format
        for detail_line in match_detail_lines:
            self.assertRegex(detail_line, r"└─ 🎯 \w+:", "Match details should have correct format")
    
    def test_no_separate_match_details_section(self):
        """Test that there should be no separate match details section"""
        result = self.manager.render_conversation_tree("test", search_query="React")
        
        # Should not include separate match details section
        self.assertNotIn("🎯 Match Details:", result)
        self.assertNotIn("1. React Project Development (Score:", result)
    
    def test_multiple_field_matches_display(self):
        """Test display of multiple field matches"""
        result = self.manager.render_conversation_tree("test", search_query="user")
        
        lines = result.split('\n')
        
        # Should display multiple match fields
        match_detail_lines = [line for line in lines if "└─ 🎯" in line or "└─   " in line]
        
        # Check for different types of matches (summary, current_context, etc.)
        field_types = set()
        for line in match_detail_lines:
            if "summary:" in line:
                field_types.add("summary")
            elif "current_context:" in line:
                field_types.add("current_context")
            elif "progress_status:" in line:
                field_types.add("progress_status")
        
        # Should have at least one field type match
        self.assertGreater(len(field_types), 0, "Should have at least one field match")
    
    def test_search_scope_filtering(self):
        """Test search scope filtering"""
        # Search in bookmarks
        result = self.manager.render_conversation_tree("test", search_query="React", search_scope="bookmarks")
        
        self.assertIn("(Scope: bookmarks)", result)
        
        # Search in all content
        result_all = self.manager.render_conversation_tree("test", search_query="React", search_scope="all")
        
        self.assertIn("(Scope: all)", result_all)
    
    def test_no_matches_message(self):
        """Test message when no matches found"""
        result = self.manager.render_conversation_tree("test", search_query="Python")
        
        self.assertEqual(result, "🔍 No matches found for 'Python'")

if __name__ == "__main__":
    unittest.main()
