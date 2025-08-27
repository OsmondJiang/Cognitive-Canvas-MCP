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
        """Test basic search functionality"""
        result = self.manager.search_conversation(self.conv_id, "database")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["query"], "database")
        self.assertGreater(result["total_results"], 0)
        self.assertIsInstance(result["results"], list)
    
    def test_search_nonexistent_conversation(self):
        """Test searching non-existent conversation"""
        result = self.manager.search_conversation("nonexistent", "test")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        result = self.manager.search_conversation(self.conv_id, "blockchain")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_results"], 0)
        self.assertEqual(len(result["results"]), 0)
    
    def test_search_relevance_scoring(self):
        """Test relevance scoring"""
        result = self.manager.search_conversation(self.conv_id, "Authentication")
        
        self.assertGreater(result["total_results"], 0)
        
        # Check that results are sorted by relevance score
        scores = [item["relevance_score"] for item in result["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # The exact match should have the highest score
        top_result = result["results"][0]
        self.assertIn("Authentication", top_result["node_summary"])
    
    def test_search_scope_all(self):
        """Test global search scope"""
        result = self.manager.search_conversation(self.conv_id, "React", search_scope="all")
        
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["total_results"], 0)
    
    def test_search_scope_bookmarks(self):
        """Test bookmark search scope"""
        result = self.manager.search_conversation(self.conv_id, "auth", search_scope="bookmarks")
        
        self.assertEqual(result["status"], "success")
        
        # Should only return bookmarked nodes
        for item in result["results"]:
            self.assertTrue(item["is_bookmarked"])
    
    def test_search_scope_current_branch(self):
        """Test current branch search scope"""
        result = self.manager.search_conversation(self.conv_id, "React", search_scope="current_branch")
        
        self.assertEqual(result["status"], "success")
        # Results should only be from current branch
    
    def test_search_max_results(self):
        """Test maximum results limit"""
        result = self.manager.search_conversation(self.conv_id, "e", max_results=2)
        
        self.assertEqual(result["status"], "success")
        self.assertLessEqual(len(result["results"]), 2)
    
    def test_search_result_structure(self):
        """Test search result structure"""
        result = self.manager.search_conversation(self.conv_id, "database")
        
        self.assertGreater(result["total_results"], 0)
        
        first_result = result["results"][0]
        
        # Check required fields
        required_fields = [
            'node_summary', 'path', 'relevance_score', 'match_details',
            'context', 'is_bookmarked', 'bookmark_name', 'is_current'
        ]
        
        for field in required_fields:
            self.assertIn(field, first_result)
        
        # Check context structure
        context = first_result["context"]
        context_fields = ['current_context', 'progress_status', 'next_steps', 'details']
        for field in context_fields:
            self.assertIn(field, context)
        
        # Check path is a list
        self.assertIsInstance(first_result["path"], list)
        
        # Check match_details structure
        if first_result["match_details"]:
            match = first_result["match_details"][0]
            match_fields = ['field', 'value', 'match_strength', 'weighted_score']
            for field in match_fields:
                self.assertIn(field, match)
    
    def test_search_match_strength_calculation(self):
        """Test match strength calculation"""
        # Test exact match
        exact_strength = self.manager._calculate_match_strength("test", "test")
        self.assertEqual(exact_strength, 1.0)
        
        # Test word boundary match  
        word_strength = self.manager._calculate_match_strength("auth", "authentication system")
        self.assertGreater(word_strength, 0.0)
        self.assertLess(word_strength, 1.0)
        
        # Test substring match
        substring_strength = self.manager._calculate_match_strength("data", "database design")
        self.assertGreater(substring_strength, 0.0)
        self.assertLess(substring_strength, 1.0)
        
        # Test no match
        no_match_strength = self.manager._calculate_match_strength("xyz", "abc def")
        self.assertEqual(no_match_strength, 0.0)
        
        # Test that exact match scores higher than substring
        exact = self.manager._calculate_match_strength("test", "test")
        substring = self.manager._calculate_match_strength("test", "testing framework")
        self.assertGreater(exact, substring)
    
    def test_search_node_path_calculation(self):
        """Test node path calculation"""
        # Get any node for testing
        current_node = self.manager.conversations[self.conv_id]
        path = self.manager._get_node_path(current_node)
        
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], "Main conversation")  # Root should be first
    
    def test_search_multiple_field_matching(self):
        """Test multiple field matching"""
        result = self.manager.search_conversation(self.conv_id, "JWT")
        
        if result["total_results"] > 0:
            # Should find matches in different fields
            for item in result["results"]:
                self.assertGreater(len(item["match_details"]), 0)
    
    def test_search_case_insensitive(self):
        """Test case insensitive search"""
        result1 = self.manager.search_conversation(self.conv_id, "DATABASE")
        result2 = self.manager.search_conversation(self.conv_id, "database")
        result3 = self.manager.search_conversation(self.conv_id, "Database")
        
        # All should return same results
        self.assertEqual(result1["total_results"], result2["total_results"])
        self.assertEqual(result2["total_results"], result3["total_results"])
    
    def test_search_empty_query(self):
        """Test empty query"""
        result = self.manager.search_conversation(self.conv_id, "")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_results"], 0)

if __name__ == '__main__':
    unittest.main()
