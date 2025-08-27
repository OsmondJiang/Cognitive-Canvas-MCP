import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.chat_fork import ChatForkManager, ChatNode

class TestChatForkManager(unittest.TestCase):
    def setUp(self):
        self.manager = ChatForkManager()
        self.conv_id = "test_conversation"
    
    def test_pause_topic_basic(self):
        """Test basic pause_topic functionality"""
        result = self.manager.pause_topic(
            self.conv_id, 
            "Database Design", 
            current_context="Starting e-commerce project"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["current_topic"], "Database Design")
        self.assertEqual(result["paused_topic"], "Main conversation")
        self.assertEqual(result["action"], "topic_paused")
        self.assertIn("saved_context", result)
    
    def test_enhanced_context_pause(self):
        """Test enhanced context capture in pause_topic"""
        result = self.manager.pause_topic(
            self.conv_id,
            "API Development",
            current_context="Designing REST API for user management with authentication",
            progress_status="Completed user model and basic CRUD operations",
            next_steps="Implement JWT authentication, add input validation, write tests"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["current_topic"], "API Development")
        
        # Check that context is properly saved
        saved_context = result["saved_context"]
        self.assertEqual(saved_context["current_context"], "Designing REST API for user management with authentication")
        self.assertEqual(saved_context["progress_status"], "Completed user model and basic CRUD operations")
        self.assertEqual(saved_context["next_steps"], "Implement JWT authentication, add input validation, write tests")
    
    def test_resume_topic_basic(self):
        """Test basic resume_topic functionality"""
        # Pause first with enhanced context
        self.manager.pause_topic(
            self.conv_id, 
            "API Design", 
            current_context="Database planning done, moving to API design",
            progress_status="Database schema completed",
            next_steps="Design REST endpoints, implement authentication"
        )
        
        # Resume
        result = self.manager.resume_topic(self.conv_id, "API design completed")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["resumed_topic"], "Main conversation")
        self.assertEqual(result["completed_topic"], "API Design")
        self.assertEqual(result["completed_summary"], "API design completed")
        self.assertIn("restored_context", result)
    
    def test_enhanced_context_resume(self):
        """Test enhanced context restoration in resume_topic"""
        # Pause with rich context
        self.manager.pause_topic(
            self.conv_id,
            "Security Implementation", 
            current_context="Implementing OAuth2 and JWT authentication system",
            progress_status="Basic login/logout working, need token refresh",
            next_steps="Add refresh token rotation, implement rate limiting"
        )
        
        # Pause another topic nested
        self.manager.pause_topic(
            self.conv_id,
            "Token Validation",
            current_context="Building JWT token validation middleware",
            progress_status="Token parsing implemented",
            next_steps="Add expiration checking, implement blacklist",
            pause_type="nested"
        )
        
        # Resume back
        result = self.manager.resume_topic(
            self.conv_id, 
            "Token validation middleware completed with full security checks"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["resumed_topic"], "Security Implementation")
        
        # Check restored context
        restored = result["restored_context"]
        self.assertEqual(restored["current_context"], "Building JWT token validation middleware")
        self.assertEqual(restored["progress_status"], "Token parsing implemented")
        self.assertEqual(restored["next_steps"], "Add expiration checking, implement blacklist")
    
    def test_nested_vs_parallel_pause(self):
        """Test difference between nested and parallel pause"""
        # Start with a topic
        self.manager.pause_topic(self.conv_id, "Project Planning", current_context="Initial setup")
        
        # Nested pause - should create child under Project Planning
        result1 = self.manager.pause_topic(
            self.conv_id, 
            "Technical Stack", 
            current_context="Planning phase complete", 
            pause_type="nested"
        )
        self.assertEqual(result1["pause_type"], "nested")
        
        # Parallel pause - should create sibling under same parent
        result2 = self.manager.pause_topic(
            self.conv_id, "Team Meeting", current_context="Tech stack discussion in progress", pause_type="parallel"
        )
        self.assertEqual(result2["pause_type"], "parallel")
        
        # Verify structure
        current_node = self.manager.conversations[self.conv_id]  # Team Meeting
        self.assertEqual(current_node.summary, "Team Meeting")
        
        # Team Meeting should be sibling of Technical Stack under Project Planning
        project_node = current_node.parent
        self.assertEqual(project_node.summary, "Project Planning")
        
        # Verify both children exist under Project Planning
        children_names = [child.summary for child in project_node.children]
        self.assertIn("Technical Stack", children_names)
        self.assertIn("Team Meeting", children_names)
    
    def test_fixed_parallel_logic(self):
        """Test that parallel pause creates siblings correctly (not uncles)"""
        # Create nested structure: Root -> A -> B -> C
        self.manager.pause_topic(self.conv_id, "Topic A", current_context="Root context")
        self.manager.pause_topic(self.conv_id, "Topic B", current_context="A progress", pause_type="nested")
        self.manager.pause_topic(self.conv_id, "Topic C", current_context="B progress", pause_type="nested")
        
        # Parallel pause from C should create D as sibling of C under B
        result = self.manager.pause_topic(self.conv_id, "Topic D", current_context="C context", pause_type="parallel")
        
        topic_d = self.manager.conversations[self.conv_id]
        self.assertEqual(topic_d.summary, "Topic D")
        
        # D should be sibling of C, so parent should be B
        self.assertEqual(topic_d.parent.summary, "Topic B")
        
        # Verify B has both C and D as children
        topic_b = topic_d.parent
        children_names = [child.summary for child in topic_b.children]
        self.assertIn("Topic C", children_names)
        self.assertIn("Topic D", children_names)
    
    def test_auto_resume_behavior(self):
        """Test automatic resume behavior based on pause type"""
        # Create nested structure
        self.manager.pause_topic(self.conv_id, "Main Topic", current_context="Starting discussion")
        self.manager.pause_topic(self.conv_id, "Sub Topic", current_context="Main progress", pause_type="nested")
        
        # Resume from nested should go to parent
        result1 = self.manager.resume_topic(self.conv_id, "Sub completed", resume_type="auto")
        self.assertEqual(result1["resumed_topic"], "Main Topic")
        self.assertEqual(result1["actual_resume_type"], "nested")
        
        # Create parallel structure
        self.manager.pause_topic(self.conv_id, "Side Topic", current_context="Main continues", pause_type="parallel")
        
        # Resume from parallel should go back to original paused location
        result2 = self.manager.resume_topic(self.conv_id, "Side completed", resume_type="auto")
        self.assertEqual(result2["resumed_topic"], "Main Topic")
        self.assertEqual(result2["actual_resume_type"], "parallel")
    
    def test_deep_nesting_workflow(self):
        """Test deep nesting and resuming workflow"""
        # Create deep nested structure
        self.manager.pause_topic(self.conv_id, "Layer1", current_context="Base context")
        self.manager.pause_topic(self.conv_id, "Layer2", current_context="L1 progress", pause_type="nested")
        self.manager.pause_topic(self.conv_id, "Layer3", current_context="L2 progress", pause_type="nested")
        
        # Resume layer by layer
        result1 = self.manager.resume_topic(self.conv_id, "L3 done")
        self.assertEqual(result1["resumed_topic"], "Layer2")
        
        result2 = self.manager.resume_topic(self.conv_id, "L2 done")
        self.assertEqual(result2["resumed_topic"], "Layer1")
        
        result3 = self.manager.resume_topic(self.conv_id, "L1 done")
        self.assertEqual(result3["resumed_topic"], "Main conversation")
    
    def test_mixed_pause_types(self):
        """Test mixing nested and parallel pauses"""
        # Start main discussion
        self.manager.pause_topic(self.conv_id, "System Design", current_context="Architecture planning")
        
        # Nested: dive into database
        self.manager.pause_topic(self.conv_id, "Database", current_context="System design ongoing", pause_type="nested")
        
        # Parallel: switch to urgent meeting (sibling of Database under System Design)
        self.manager.pause_topic(self.conv_id, "Urgent Meeting", current_context="DB design halfway", pause_type="parallel")
        
        # Resume should go back to Database (the paused location)
        result = self.manager.resume_topic(self.conv_id, "Meeting done", resume_type="auto")
        self.assertEqual(result["resumed_topic"], "Database")
        
        # Complete Database, should go back to System Design
        result2 = self.manager.resume_topic(self.conv_id, "DB design done", resume_type="auto")
        self.assertEqual(result2["resumed_topic"], "System Design")
    
    def test_mixed_pause_types_workflow_fixed(self):
        """Test complete workflow mixing nested and parallel pauses"""
        # Start main discussion
        self.manager.pause_topic(self.conv_id, "System Architecture", current_context="Starting overall design")
        
        # Nested: dive into database discussion
        self.manager.pause_topic(self.conv_id, "Database Design", current_context="Architecture design in progress", pause_type="nested")
        
        # Nested again: dive into table structure
        self.manager.pause_topic(self.conv_id, "Table Structure Design", current_context="Database selection completed", pause_type="nested")
        
        # Parallel switch: temporarily discuss urgent issue (should be sibling of Table Structure under Database Design)
        self.manager.pause_topic(self.conv_id, "Urgent Bug Fix", current_context="Table structure design halfway", pause_type="parallel")
        
        # Complete urgent issue, auto resume to table structure design
        result1 = self.manager.resume_topic(self.conv_id, "Bug fixed", resume_type="auto")
        self.assertEqual(result1["resumed_topic"], "Table Structure Design")
        
        # Complete table structure, resume to database design
        result2 = self.manager.resume_topic(self.conv_id, "Table structure design completed", resume_type="auto")
        self.assertEqual(result2["resumed_topic"], "Database Design")
        
        # Complete database design, resume to system architecture
        result3 = self.manager.resume_topic(self.conv_id, "Database design completed", resume_type="auto")
        self.assertEqual(result3["resumed_topic"], "System Architecture")
        
        # Verify the entire discussion tree structure and content are correctly saved
        root = self.manager.conversations[self.conv_id]  # System Architecture
        self.assertEqual(root.summary, "System Architecture")
        
        # Navigate the tree structure
        arch_node = root  # We're currently at System Architecture
        
        # System Architecture should have Database Design as child
        self.assertEqual(len(arch_node.children), 1)
        db_node = arch_node.children[0]
        self.assertEqual(db_node.summary, "Database Design")
        self.assertEqual(db_node.details, "Database design completed")
        
        # Database Design should have both Table Structure and Bug Fix as children (siblings)
        self.assertEqual(len(db_node.children), 2)
        
        # Find the children by name
        children_by_name = {child.summary: child for child in db_node.children}
        
        table_node = children_by_name["Table Structure Design"]
        bug_node = children_by_name["Urgent Bug Fix"]
        
        self.assertEqual(table_node.summary, "Table Structure Design")
        self.assertEqual(table_node.details, "Table structure design completed")
        self.assertEqual(bug_node.summary, "Urgent Bug Fix")
        self.assertEqual(bug_node.details, "Bug fixed")

    def test_search_conversation_tree(self):
        """Test the search_conversation_tree functionality with enhanced context"""
        # Build a complex conversation tree with rich context
        self.manager.pause_topic(
            self.conv_id, 
            "Project Planning", 
            current_context="Starting new e-commerce project with microservices",
            progress_status="Completed initial requirements gathering",
            next_steps="Design system architecture and select technology stack"
        )
        
        # Nested pause - dive into technical details
        self.manager.pause_topic(
            self.conv_id, 
            "Database Design", 
            current_context="Designing schema for users, products, and orders",
            progress_status="Planning phase complete, technology selected",
            next_steps="Create ER diagram and define relationships",
            pause_type="nested"
        )
        
        # Parallel switch - discuss API design at same level
        self.manager.pause_topic(
            self.conv_id, 
            "API Design", 
            current_context="REST API with authentication and rate limiting",
            progress_status="DB design 70% complete",
            next_steps="Finish database design and start API development",
            pause_type="parallel"
        )
        
        # Nested dive into API details
        self.manager.pause_topic(
            self.conv_id, 
            "Authentication System", 
            current_context="JWT-based authentication with refresh tokens",
            progress_status="API structure planned and documented",
            next_steps="Implement JWT token generation and validation",
            pause_type="nested"
        )
        
        # Search the tree
        tree = self.manager.search_conversation_tree(self.conv_id)
        
        # Should return a string with the tree
        self.assertIsInstance(tree, str)
        self.assertIn("👈 [HERE]", tree)
        self.assertIn("Project Planning", tree)
        self.assertIn("Database Design", tree)
        self.assertIn("API Design", tree)
        self.assertIn("Authentication System", tree)
        
        # Check tree structure connectors
        self.assertIn("└──", tree)  # Tree connectors should be present
        self.assertIn("├──", tree)  # Multiple children indicators
        
        # Check context information display
        self.assertIn("└─ Context:", tree)  # Context lines should be present
        self.assertIn("└─ Progress:", tree)  # Progress lines should be present
        self.assertIn("└─ Next:", tree)  # Next steps lines should be present
        
        # Check specific context content
        self.assertIn("JWT-based authentication", tree)
        self.assertIn("microservices", tree)
        self.assertIn("API structure planned", tree)
        
        # Check tree structure indicators
        print("\n" + "="*50)
        print("SEARCHED CONVERSATION TREE:")
        print("="*50)
        print(tree)
        print("="*50)
        
        # Verify current position is marked
        self.assertIn("Authentication System", tree)
        self.assertIn("👈 [HERE]", tree)
        
        # Test tree after moving back
        self.manager.resume_topic(self.conv_id, "Auth system implemented", resume_type="auto")
        tree2 = self.manager.search_conversation_tree(self.conv_id)
        
        self.assertIn("API Design", tree2)
        self.assertIn("👈 [HERE]", tree2)

    def test_search_empty_conversation(self):
        """Test search with non-existent conversation"""
        result = self.manager.search_conversation_tree("non_existent")
        
        self.assertIsInstance(result, str)
        self.assertIn("Error", result)

    def test_search_single_topic(self):
        """Test search with only root topic with rich context"""
        # Create a simple conversation with rich context
        self.manager.pause_topic(
            self.conv_id, 
            "Simple Topic", 
            current_context="Just one topic with detailed context information",
            progress_status="Just started this single topic",
            next_steps="Continue working on this topic and add more features"
        )
        
        tree = self.manager.search_conversation_tree(self.conv_id)
        
        self.assertIsInstance(tree, str)
        self.assertIn("👈 [HERE]", tree)
        self.assertIn("Simple Topic", tree)
        # For single topic, should have tree connector from root
        self.assertIn("└──", tree)
        
        # Check context information is displayed
        self.assertIn("└─ Context:", tree)
        self.assertIn("└─ Progress:", tree) 
        self.assertIn("└─ Next:", tree)
        self.assertIn("detailed context information", tree)
        self.assertIn("Just started", tree)

    def test_enhanced_context_functionality(self):
        """Test the enhanced context features in pause and resume"""
        # Test initial pause with rich context
        result1 = self.manager.pause_topic(
            self.conv_id,
            "Context Test Topic",
            current_context="This is a detailed context about what we're discussing",
            progress_status="We have made significant progress on this topic", 
            next_steps="Need to implement the remaining features and run tests"
        )
        
        # Check saved context in pause result
        self.assertEqual(result1["status"], "success")
        saved_context = result1["saved_context"]
        self.assertEqual(saved_context["current_context"], "This is a detailed context about what we're discussing")
        self.assertEqual(saved_context["progress_status"], "We have made significant progress on this topic")
        self.assertEqual(saved_context["next_steps"], "Need to implement the remaining features and run tests")
        
        # Add a parallel topic to test context switching
        result2 = self.manager.pause_topic(
            self.conv_id,
            "Parallel Context Test",
            current_context="Different context for parallel topic",
            progress_status="Starting parallel work",
            next_steps="Complete parallel implementation",
            pause_type="parallel"
        )
        
        # Check parallel context is saved correctly (should be the original node's context that we paused)
        self.assertEqual(result2["status"], "success")
        saved_context2 = result2["saved_context"]
        self.assertEqual(saved_context2["current_context"], "This is a detailed context about what we're discussing")
        self.assertEqual(saved_context2["progress_status"], "We have made significant progress on this topic")
        self.assertEqual(saved_context2["next_steps"], "Need to implement the remaining features and run tests")
        
        # Resume and check context restoration
        result3 = self.manager.resume_topic(self.conv_id, "Parallel work completed successfully")
        
        self.assertEqual(result3["status"], "success")
        self.assertEqual(result3["resumed_topic"], "Context Test Topic")
        self.assertEqual(result3["completed_summary"], "Parallel work completed successfully")
        
        restored_context = result3["restored_context"]
        self.assertEqual(restored_context["current_context"], "This is a detailed context about what we're discussing")
        self.assertEqual(restored_context["progress_status"], "We have made significant progress on this topic")
        self.assertEqual(restored_context["next_steps"], "Need to implement the remaining features and run tests")
        
        # Test search shows all context information
        tree = self.manager.search_conversation_tree(self.conv_id)
        self.assertIn("detailed context about what we're discussing", tree)
        self.assertIn("significant progress", tree)
        self.assertIn("remaining features", tree)

if __name__ == '__main__':
    unittest.main()
