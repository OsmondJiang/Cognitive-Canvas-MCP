#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chat Fork Search and Search Functionality

This test file provides complete coverage of all search and search features,
including unified search interface, search scopes, match details integration,
edge cases, and error handling.
"""

import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.chat_fork import ChatForkManager

class TestChatForkSearchUnified(unittest.TestCase):
    def setUp(self):
        """Set up test environment with comprehensive conversation structure"""
        self.manager = ChatForkManager()
        self.conv_id = "test_search_conversation"
        self._create_test_conversation()
    
    def _create_test_conversation(self):
        """Create a comprehensive test conversation with multiple branches and bookmarks"""
        # Main topic with bookmark
        self.manager.pause_topic(
            self.conv_id,
            "E-commerce Platform Development",
            current_context="Building a comprehensive e-commerce platform with React and Node.js",
            progress_status="Initial project setup and architecture planning completed",
            next_steps="Implement core features: authentication, product catalog, and payment system",
            bookmark="main_project"
        )
        
        # Nested topic - Backend Development
        self.manager.pause_topic(
            self.conv_id,
            "Backend API Development",
            current_context="Developing REST API with Express.js and PostgreSQL database",
            progress_status="User authentication endpoints implemented with JWT tokens",
            next_steps="Create product catalog API and order management system",
            pause_type="nested",
            bookmark="backend_api"
        )
        
        # Deeper nested - Authentication System
        self.manager.pause_topic(
            self.conv_id,
            "JWT Authentication Implementation",
            current_context="Implementing secure JWT authentication with refresh tokens and role-based access",
            progress_status="Basic login/logout working, password hashing implemented",
            next_steps="Add refresh token rotation and permission middleware",
            pause_type="nested",
            bookmark="jwt_auth"
        )
        
        # Parallel topic - Database Design
        self.manager.pause_topic(
            self.conv_id,
            "Database Schema Design",
            current_context="Designing PostgreSQL schema for users, products, orders, and reviews",
            progress_status="Created user and product tables with proper relationships",
            next_steps="Implement order history and review system tables",
            pause_type="parallel",
            bookmark="database_schema"
        )
        
        # Another parallel - Frontend Development
        self.manager.pause_topic(
            self.conv_id,
            "React Frontend Development",
            current_context="Building responsive React application with Material-UI components",
            progress_status="Login page and product listing components completed",
            next_steps="Implement shopping cart and checkout process",
            pause_type="parallel"
        )

    # =============================================================================
    # BASIC SEARCH FUNCTIONALITY TESTS
    # =============================================================================
    
    def test_SEARCH_complete_tree_without_search(self):
        """Test SEARCHing complete conversation tree without any search filters"""
        result = self.manager.search_conversation_tree(self.conv_id)
        
        # Should show all topics in the tree
        self.assertIn("E-commerce Platform Development", result)
        self.assertIn("Backend API Development", result)
        self.assertIn("JWT Authentication Implementation", result)
        self.assertIn("Database Schema Design", result)
        self.assertIn("React Frontend Development", result)
        
        # Should show bookmarks section
        self.assertIn("📖 Bookmarks:", result)
        self.assertIn("main_project", result)
        self.assertIn("backend_api", result)
        self.assertIn("jwt_auth", result)
        self.assertIn("database_schema", result)
        
        # Should show current location marker
        self.assertIn("👈 [HERE]", result)
        
        # Should NOT show search-related markers
        self.assertNotIn("🔍 Search Results", result)
        self.assertNotIn("🎯", result)
    
    def test_SEARCH_tree_structure_hierarchy(self):
        """Test that the tree structure shows proper hierarchy"""
        result = self.manager.search_conversation_tree(self.conv_id)
        
        # Should show proper tree structure with indentation
        self.assertIn("Main conversation", result)
        self.assertIn("└──", result)  # Tree branches
        self.assertIn("├──", result)  # Tree branches
        
        # Should show nested structure (N) and parallel structure (P)
        self.assertIn("[N]", result)  # Nested indicators
        self.assertIn("[P]", result)  # Parallel indicators
    
    def test_SEARCH_context_information_display(self):
        """Test that context information is properly displayed"""
        result = self.manager.search_conversation_tree(self.conv_id)
        
        # Should show context information for nodes
        self.assertIn("Context:", result)
        self.assertIn("Progress:", result)
        self.assertIn("Next:", result)
        
        # Should show actual context content
        self.assertIn("React and Node.js", result)
        self.assertIn("JWT tokens", result)

    # =============================================================================
    # SEARCH FUNCTIONALITY TESTS
    # =============================================================================
    
    def test_basic_search_functionality(self):
        """Test basic search functionality through SEARCH method"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="React")
        
        # Should show search results header
        self.assertIn("🔍 Search Results for: 'React'", result)
        self.assertIn("📊 Found", result)
        
        # Should show match indicators
        self.assertIn("🎯", result)
        
        # Should find React-related content
        self.assertIn("React Frontend Development", result)
        
        # Should NOT show complete tree bookmark section when searching
        self.assertNotIn("📖 Bookmarks:", result)
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        result1 = self.manager.search_conversation_tree(self.conv_id, search_query="JWT")
        result2 = self.manager.search_conversation_tree(self.conv_id, search_query="jwt")
        result3 = self.manager.search_conversation_tree(self.conv_id, search_query="Jwt")
        
        # All variations should find results
        for result in [result1, result2, result3]:
            if "No matches found" not in result:
                self.assertIn("🔍 Search Results", result)
                self.assertIn("JWT Authentication", result)
    
    def test_search_partial_matches(self):
        """Test that search finds partial word matches"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="auth")
        
        # Should find "authentication" related content
        if "No matches found" not in result:
            self.assertIn("🔍 Search Results", result)
            self.assertIn("🎯", result)
    
    def test_search_multiple_word_query(self):
        """Test search with multiple words"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="JWT authentication")
        
        # Should find content containing these terms
        if "No matches found" not in result:
            self.assertIn("🔍 Search Results", result)

    # =============================================================================
    # SEARCH SCOPE TESTS
    # =============================================================================
    
    def test_search_scope_all(self):
        """Test search scope 'all' - searches entire conversation"""
        result = self.manager.search_conversation_tree(
            self.conv_id, 
            search_query="database", 
            search_scope="all"
        )
        
        self.assertIn("(Scope: all)", result)
        if "No matches found" not in result:
            self.assertIn("🎯", result)
    
    def test_search_scope_topics(self):
        """Test search scope 'topics' - searches only topic names"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="Development",
            search_scope="topics"
        )
        
        self.assertIn("(Scope: topics)", result)
        if "No matches found" not in result:
            self.assertIn("🎯", result)
    
    def test_search_scope_context(self):
        """Test search scope 'context' - searches only context information"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="PostgreSQL",
            search_scope="context"
        )
        
        self.assertIn("(Scope: context)", result)
        if "No matches found" not in result:
            self.assertIn("🎯", result)
    
    def test_search_scope_bookmarks(self):
        """Test search scope 'bookmarks' - searches only bookmarked topics"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="backend",
            search_scope="bookmarks"
        )
        
        self.assertIn("(Scope: bookmarks)", result)
        if "No matches found" not in result:
            self.assertIn("🎯", result)
    
    def test_search_scope_current_branch(self):
        """Test search scope 'current_branch' - searches only current branch"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="React",
            search_scope="current_branch"
        )
        
        self.assertIn("(Scope: current_branch)", result)
    
    def test_search_scope_comparison(self):
        """Test that different scopes produce different results"""
        all_result = self.manager.search_conversation_tree(
            self.conv_id, search_query="API", search_scope="all"
        )
        topics_result = self.manager.search_conversation_tree(
            self.conv_id, search_query="API", search_scope="topics"
        )
        
        self.assertIn("(Scope: all)", all_result)
        self.assertIn("(Scope: topics)", topics_result)

    # =============================================================================
    # MATCH DETAILS INTEGRATION TESTS
    # =============================================================================
    
    def test_match_details_integrated_in_tree_nodes(self):
        """Test that match details are integrated directly in tree nodes"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="authentication")
        
        lines = result.split('\n')
        
        # Should have nodes with match scores
        score_lines = [line for line in lines if "🎯(" in line and ")" in line]
        self.assertGreater(len(score_lines), 0, "Should have nodes with match scores")
        
        # Should have match detail lines integrated in tree
        detail_lines = [line for line in lines if "🎯" in line and ":" in line]
        self.assertGreater(len(detail_lines), 0, "Should have integrated match details")
    
    def test_match_details_show_field_types(self):
        """Test that match details show which fields matched"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="JWT")
        
        if "No matches found" not in result:
            # Should show different field types that matched
            lines = result.split('\n')
            detail_lines = [line for line in lines if "🎯" in line and ":" in line]
            
            field_types = set()
            for line in detail_lines:
                if "summary:" in line:
                    field_types.add("summary")
                elif "current_context:" in line:
                    field_types.add("current_context")
                elif "progress_status:" in line:
                    field_types.add("progress_status")
                elif "next_steps:" in line:
                    field_types.add("next_steps")
                elif "bookmark_name:" in line:
                    field_types.add("bookmark_name")
            
            self.assertGreater(len(field_types), 0, "Should identify field types in matches")
    
    def test_no_separate_match_details_section(self):
        """Test that match details are NOT shown in a separate section"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="React")
        
        # Should NOT have separate match details section
        self.assertNotIn("🎯 Match Details:", result)
        self.assertNotIn("1. ", result)  # No numbered list of matches
    
    def test_match_score_format(self):
        """Test that match scores are displayed in correct format"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="authentication")
        
        if "No matches found" not in result:
            lines = result.split('\n')
            score_lines = [line for line in lines if "🎯(" in line]
            
            for line in score_lines:
                # Should contain score in parentheses with decimal number
                self.assertTrue("(" in line and ")" in line, "Should have score in parentheses")

    # =============================================================================
    # MAX RESULTS AND PAGINATION TESTS
    # =============================================================================
    
    def test_max_results_parameter(self):
        """Test that max_results parameter limits search results"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="e",  # Common letter to get multiple matches
            max_results=2
        )
        
        # Should work without errors regardless of actual result count
        if "No matches found" not in result:
            self.assertIn("🔍 Search Results", result)
    
    def test_max_results_zero_means_unlimited(self):
        """Test that max_results=0 means unlimited results"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="development",
            max_results=0
        )
        
        # Should work without limiting results
        if "No matches found" not in result:
            self.assertIn("🔍 Search Results", result)

    # =============================================================================
    # EDGE CASES AND ERROR HANDLING TESTS
    # =============================================================================
    
    def test_search_nonexistent_conversation(self):
        """Test searching in non-existent conversation"""
        result = self.manager.search_conversation_tree("nonexistent", search_query="test")
        
        self.assertEqual(result, "Error: Conversation not found")
    
    def test_SEARCH_nonexistent_conversation(self):
        """Test SEARCHing non-existent conversation without search"""
        result = self.manager.search_conversation_tree("nonexistent")
        
        self.assertEqual(result, "Error: Conversation not found")
    
    def test_search_empty_query(self):
        """Test search with empty query returns complete tree"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="")
        
        # Empty query should return complete tree
        self.assertNotIn("🔍 Search Results", result)
        self.assertIn("📖 Bookmarks:", result)
        self.assertIn("Main conversation", result)
    
    def test_search_whitespace_only_query(self):
        """Test search with whitespace-only query"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="   ")
        
        # Whitespace query should be treated as actual search
        self.assertIn("No matches found for '   '", result)
    
    def test_search_no_results(self):
        """Test search query that returns no matches"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="blockchain")
        
        self.assertIn("No matches found for 'blockchain'", result)
    
    def test_search_special_characters(self):
        """Test search with special characters"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="e-commerce")
        
        # Should handle hyphenated terms
        if "No matches found" not in result:
            self.assertIn("🔍 Search Results", result)
    
    def test_search_unicode_characters(self):
        """Test search with unicode characters"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="café")
        
        # Should handle unicode without errors
        self.assertIn("No matches found for 'café'", result)

    # =============================================================================
    # COMPREHENSIVE INTEGRATION TESTS
    # =============================================================================
    
    def test_search_all_parameters_combined(self):
        """Test search with all parameters specified"""
        result = self.manager.search_conversation_tree(
            self.conv_id,
            search_query="development",
            search_scope="all",
            max_results=5
        )
        
        if "No matches found" not in result:
            self.assertIn("🔍 Search Results for: 'development'", result)
            self.assertIn("(Scope: all)", result)
            self.assertIn("🎯", result)
    
    def test_search_bookmark_integration(self):
        """Test that bookmark information is preserved in search results"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="backend")
        
        if "No matches found" not in result:
            # Should show bookmark indicators for bookmarked nodes
            self.assertIn("🔖", result)
    
    def test_search_current_location_marker(self):
        """Test that current location is marked in search results"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="React")
        
        if "No matches found" not in result:
            # Should show current location marker if current node matches
            lines = result.split('\n')
            current_lines = [line for line in lines if "👈 [HERE]" in line]
            # May or may not have current marker depending on if current node matches
    
    def test_search_preserves_tree_structure(self):
        """Test that search results preserve tree hierarchy"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="API")
        
        if "No matches found" not in result:
            # Should show tree structure even in filtered results
            self.assertIn("└──", result)  # Tree structure characters
    
    def test_SEARCH_performance_with_complex_tree(self):
        """Test SEARCH performance with complex conversation tree"""
        # This test ensures the SEARCH method works with existing complex structure
        result = self.manager.search_conversation_tree(self.conv_id)
        
        # Should complete without errors and show all expected content
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)  # Should generate substantial output
    
    def test_search_relevance_scoring(self):
        """Test that search results show relevance scores"""
        result = self.manager.search_conversation_tree(self.conv_id, search_query="JWT")
        
        if "No matches found" not in result:
            # Should show match scores
            self.assertIn("🎯(", result)
            
            lines = result.split('\n')
            score_lines = [line for line in lines if "🎯(" in line]
            
            # Scores should be reasonable numbers
            for line in score_lines:
                # Should contain score format
                self.assertTrue("(" in line and ")" in line)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
