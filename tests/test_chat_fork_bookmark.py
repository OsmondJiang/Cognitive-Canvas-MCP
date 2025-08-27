import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.chat_fork import ChatForkManager, ChatNode

class TestChatForkBookmark(unittest.TestCase):
    def setUp(self):
        self.manager = ChatForkManager()
        self.conv_id = "test_bookmark_conversation"
    
    def test_pause_with_bookmark(self):
        """Test pause_topic with bookmark functionality"""
        result = self.manager.pause_topic(
            self.conv_id, 
            "Database Design", 
            current_context="Starting e-commerce project database design",
            progress_status="Requirements gathered",
            next_steps="Create ER diagram",
            bookmark="db_design_milestone"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["current_topic"], "Database Design")
        self.assertEqual(result["bookmark_created"], "db_design_milestone")
        
        # Check that bookmark was actually set
        root_node = self.manager._find_root(self.manager.conversations[self.conv_id])
        self.assertTrue(root_node.is_bookmarked)
        self.assertEqual(root_node.bookmark_name, "db_design_milestone")
    
    def test_pause_without_bookmark(self):
        """Test pause_topic without bookmark"""
        result = self.manager.pause_topic(
            self.conv_id, 
            "API Design", 
            current_context="Moving to API design phase"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["current_topic"], "API Design")
        self.assertIsNone(result["bookmark_created"])
        
        # Check that no bookmark was set
        root_node = self.manager._find_root(self.manager.conversations[self.conv_id])
        self.assertFalse(root_node.is_bookmarked)
    
    def test_resume_to_bookmark(self):
        """Test resume_topic using bookmark"""
        # Setup: Create a conversation with multiple topics and bookmarks
        
        # 1. Start main topic with bookmark
        self.manager.pause_topic(
            self.conv_id,
            "Architecture Planning",
            current_context="Planning system architecture",
            progress_status="Requirements analysis complete",
            next_steps="Design microservices",
            bookmark="architecture_milestone"
        )
        
        # 2. Nested topic with another bookmark
        self.manager.pause_topic(
            self.conv_id,
            "Database Design",
            current_context="Designing database schema",
            progress_status="Entity modeling complete",
            next_steps="Create tables and relationships",
            pause_type="nested",
            bookmark="database_milestone"
        )
        
        # 3. Parallel topic
        self.manager.pause_topic(
            self.conv_id,
            "API Development",
            current_context="Building REST API",
            progress_status="Basic endpoints created",
            next_steps="Add authentication",
            pause_type="parallel"
        )
        
        # Now resume to the database bookmark
        result = self.manager.resume_topic(
            self.conv_id,
            completed_summary="API development phase 1 completed",
            bookmark="database_milestone"
        )
        
        self.assertEqual(result["status"], "success")
        # The database bookmark is on the "Architecture Planning" node, so we resume to that
        self.assertEqual(result["resumed_topic"], "Architecture Planning")  
        self.assertEqual(result["resumed_to_bookmark"], "database_milestone")
        self.assertEqual(result["completed_topic"], "API Development")
        
        # Check restored context - this should be from the Architecture Planning node which has the bookmark
        restored = result["restored_context"]
        self.assertEqual(restored["current_context"], "Designing database schema")
    
    def test_resume_to_nonexistent_bookmark(self):
        """Test resume_topic with non-existent bookmark"""
        # Create a simple conversation
        self.manager.pause_topic(
            self.conv_id,
            "Some Topic",
            current_context="Some context"
        )
        
        # Try to resume to non-existent bookmark
        result = self.manager.resume_topic(
            self.conv_id,
            bookmark="nonexistent_bookmark"
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])
        self.assertEqual(result["action"], "bookmark_not_found")
    
    def test_multiple_bookmarks(self):
        """Test multiple bookmarks in a conversation tree"""
        # Create a complex conversation with multiple bookmarks
        
        # Root with bookmark
        self.manager.pause_topic(
            self.conv_id,
            "Project Planning",
            bookmark="project_start"
        )
        
        # Nested with bookmark
        self.manager.pause_topic(
            self.conv_id,
            "Technical Design",
            pause_type="nested",
            bookmark="tech_design"
        )
        
        # Parallel with bookmark
        self.manager.pause_topic(
            self.conv_id,
            "Team Setup",
            pause_type="parallel",
            bookmark="team_setup"
        )
        
        # Another nested without bookmark
        self.manager.pause_topic(
            self.conv_id,
            "Hiring Process",
            pause_type="nested"
        )
        
        # Test render shows all bookmarks
        tree_output = self.manager.search_conversation_tree(self.conv_id)
        
        # Check that all bookmarks are shown
        self.assertIn("🔖[project_start]", tree_output)
        self.assertIn("🔖[tech_design]", tree_output)
        self.assertIn("🔖[team_setup]", tree_output)
        
        # Check bookmarks summary
        self.assertIn("📖 Bookmarks:", tree_output)
        self.assertIn("project_start:", tree_output)
        self.assertIn("tech_design:", tree_output)
        self.assertIn("team_setup:", tree_output)
    
    def test_bookmark_navigation(self):
        """Test navigating between different bookmarks"""
        # Setup complex conversation
        self.manager.pause_topic(
            self.conv_id,
            "Phase 1: Research",
            current_context="Initial research phase",
            bookmark="phase1"
        )
        
        self.manager.pause_topic(
            self.conv_id,
            "Phase 2: Development",
            current_context="Development phase",
            pause_type="parallel",
            bookmark="phase2"
        )
        
        self.manager.pause_topic(
            self.conv_id,
            "Phase 3: Testing",
            current_context="Testing phase",
            pause_type="parallel",
            bookmark="phase3"
        )
        
        # Navigate to phase1
        result1 = self.manager.resume_topic(
            self.conv_id,
            bookmark="phase1"
        )
        self.assertEqual(result1["resumed_to_bookmark"], "phase1")
        
        # Navigate to phase2
        result2 = self.manager.resume_topic(
            self.conv_id,
            bookmark="phase2"
        )
        self.assertEqual(result2["resumed_to_bookmark"], "phase2")
        
        # Navigate to phase3
        result3 = self.manager.resume_topic(
            self.conv_id,
            bookmark="phase3"
        )
        self.assertEqual(result3["resumed_to_bookmark"], "phase3")
    
    def test_resume_type_bookmark_explicit(self):
        """Test resume_type='bookmark' explicitly"""
        # Setup
        self.manager.pause_topic(
            self.conv_id,
            "Important Topic",
            bookmark="important"
        )
        
        self.manager.pause_topic(
            self.conv_id,
            "Another Topic",
            pause_type="nested"
        )
        
        # Resume with explicit bookmark type
        result = self.manager.resume_topic(
            self.conv_id,
            resume_type="bookmark",
            bookmark="important"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["resumed_to_bookmark"], "important")
    
    def test_resume_type_bookmark_without_bookmark_name(self):
        """Test resume_type='bookmark' without providing bookmark name"""
        # Setup
        self.manager.pause_topic(
            self.conv_id,
            "Some Topic"
        )
        
        # Try resume with bookmark type but no bookmark name
        result = self.manager.resume_topic(
            self.conv_id,
            resume_type="bookmark"
            # No bookmark parameter provided
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("bookmark is required", result["message"])
    
    def test_bookmark_search_functionality(self):
        """Test internal bookmark search functionality"""
        # Setup conversation with bookmarks
        self.manager.pause_topic(
            self.conv_id,
            "Topic A",
            bookmark="bookmark_a"
        )
        
        self.manager.pause_topic(
            self.conv_id,
            "Topic B",
            pause_type="nested",
            bookmark="bookmark_b"
        )
        
        # Test _find_bookmark method
        node_a = self.manager._find_bookmark(self.conv_id, "bookmark_a")
        self.assertIsNotNone(node_a)
        self.assertEqual(node_a.bookmark_name, "bookmark_a")
        
        node_b = self.manager._find_bookmark(self.conv_id, "bookmark_b")
        self.assertIsNotNone(node_b)
        self.assertEqual(node_b.bookmark_name, "bookmark_b")
        
        # Test non-existent bookmark
        node_none = self.manager._find_bookmark(self.conv_id, "nonexistent")
        self.assertIsNone(node_none)
    
    def test_search_with_bookmarks(self):
        """Test that render properly shows bookmark information"""
        # Create conversation with mixed bookmarked and non-bookmarked topics
        self.manager.pause_topic(
            self.conv_id,
            "Main Phase",
            current_context="Main development phase",
            progress_status="Planning complete",
            next_steps="Start implementation",
            bookmark="main_phase"
        )
        
        self.manager.pause_topic(
            self.conv_id,
            "Sub Task",
            current_context="Working on subtask",
            pause_type="nested"
            # No bookmark
        )
        
        self.manager.pause_topic(
            self.conv_id,
            "Important Decision",
            current_context="Making critical decision",
            pause_type="parallel",
            bookmark="critical_decision"
        )
        
        tree_output = self.manager.search_conversation_tree(self.conv_id)
        
        # Should show bookmark indicators
        self.assertIn("🔖[main_phase]", tree_output)
        self.assertIn("🔖[critical_decision]", tree_output)
        
        # Should show bookmark summary
        self.assertIn("📖 Bookmarks:", tree_output)
        self.assertIn("main_phase: Main conversation", tree_output)
        self.assertIn("critical_decision: Sub Task", tree_output)  # The bookmark is actually on the Sub Task node
        
        # Should show current location
        self.assertIn("👈 [HERE]", tree_output)

if __name__ == '__main__':
    unittest.main()
