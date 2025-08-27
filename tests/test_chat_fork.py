import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.chat_fork import ChatForkManager, ChatNode

class TestChatForkEnglish(unittest.TestCase):
    def setUp(self):
        self.manager = ChatForkManager()
        self.conv_id = "test_conversation"
    
    def test_pause_topic_basic(self):
        """Test basic pause_topic functionality"""
        result = self.manager.pause_topic(self.conv_id, "Database Design", "Starting e-commerce project")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["current_topic"], "Database Design")
        self.assertEqual(result["paused_topic"], "Main conversation")
        self.assertEqual(result["action"], "topic_paused")
    
    def test_resume_topic_basic(self):
        """Test basic resume_topic functionality"""
        # Pause first
        self.manager.pause_topic(self.conv_id, "API Design", "Database planning done")
        
        # Resume
        result = self.manager.resume_topic(self.conv_id, "API design completed")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["resumed_topic"], "Main conversation")
        self.assertEqual(result["completed_topic"], "API Design")
    
    def test_nested_vs_parallel_pause(self):
        """Test difference between nested and parallel pause"""
        # Start with a topic
        self.manager.pause_topic(self.conv_id, "Project Planning", "Initial setup")
        
        # Nested pause - should create child under Project Planning
        result1 = self.manager.pause_topic(
            self.conv_id, 
            "Technical Stack", 
            "Planning phase complete", 
            pause_type="nested"
        )
        self.assertEqual(result1["pause_type"], "nested")
        
        # Parallel pause - should create sibling under same parent
        result2 = self.manager.pause_topic(
            self.conv_id,
            "Team Meeting",
            "Tech stack discussion in progress", 
            pause_type="parallel"
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
        self.manager.pause_topic(self.conv_id, "Topic A", "Root context")
        self.manager.pause_topic(self.conv_id, "Topic B", "A progress", pause_type="nested")
        self.manager.pause_topic(self.conv_id, "Topic C", "B progress", pause_type="nested")
        
        # Parallel pause from C should create D as sibling of C under B
        result = self.manager.pause_topic(self.conv_id, "Topic D", "C context", pause_type="parallel")
        
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
        self.manager.pause_topic(self.conv_id, "Main Topic", "Starting discussion")
        self.manager.pause_topic(self.conv_id, "Sub Topic", "Main progress", pause_type="nested")
        
        # Resume from nested should go to parent
        result1 = self.manager.resume_topic(self.conv_id, "Sub completed", resume_type="auto")
        self.assertEqual(result1["resumed_topic"], "Main Topic")
        self.assertEqual(result1["actual_resume_type"], "nested")
        
        # Create parallel structure
        self.manager.pause_topic(self.conv_id, "Side Topic", "Main continues", pause_type="parallel")
        
        # Resume from parallel should go back to original paused location
        result2 = self.manager.resume_topic(self.conv_id, "Side completed", resume_type="auto")
        self.assertEqual(result2["resumed_topic"], "Main Topic")
        self.assertEqual(result2["actual_resume_type"], "parallel")
    
    def test_deep_nesting_workflow(self):
        """Test deep nesting and resuming workflow"""
        # Create deep nested structure
        self.manager.pause_topic(self.conv_id, "Layer1", "Base context")
        self.manager.pause_topic(self.conv_id, "Layer2", "L1 progress", pause_type="nested")
        self.manager.pause_topic(self.conv_id, "Layer3", "L2 progress", pause_type="nested")
        
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
        self.manager.pause_topic(self.conv_id, "System Design", "Architecture planning")
        
        # Nested: dive into database
        self.manager.pause_topic(self.conv_id, "Database", "System design ongoing", pause_type="nested")
        
        # Parallel: switch to urgent meeting (sibling of Database under System Design)
        self.manager.pause_topic(self.conv_id, "Urgent Meeting", "DB design halfway", pause_type="parallel")
        
        # Resume should go back to Database (the paused location)
        result = self.manager.resume_topic(self.conv_id, "Meeting done", resume_type="auto")
        self.assertEqual(result["resumed_topic"], "Database")
        
        # Complete Database, should go back to System Design
        result2 = self.manager.resume_topic(self.conv_id, "DB design done", resume_type="auto")
        self.assertEqual(result2["resumed_topic"], "System Design")
    
    def test_mixed_pause_types_workflow_fixed(self):
        """Test complete workflow mixing nested and parallel pauses"""
        # Start main discussion
        self.manager.pause_topic(self.conv_id, "System Architecture", "Starting overall design")
        
        # Nested: dive into database discussion
        self.manager.pause_topic(self.conv_id, "Database Design", "Architecture design in progress", pause_type="nested")
        
        # Nested again: dive into table structure
        self.manager.pause_topic(self.conv_id, "Table Structure Design", "Database selection completed", pause_type="nested")
        
        # Parallel switch: temporarily discuss urgent issue (should be sibling of Table Structure under Database Design)
        self.manager.pause_topic(self.conv_id, "Urgent Bug Fix", "Table structure design halfway", pause_type="parallel")
        
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

if __name__ == '__main__':
    unittest.main()
