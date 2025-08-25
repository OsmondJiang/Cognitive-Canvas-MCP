import sys
import os
import unittest
from unittest.mock import MagicMock, patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual tool implementation functions directly
from tools.todo_tool import add_task, add_tasks_batch, update_task, delete_task, get_task, list_tasks
from tools.chat_fork import ChatForkManager
from tools.diagram_tool import DiagramManager
from tools.structured_knowledge_tool import StructuredKnowledgeManager

# Rather than importing server directly, we'll patch/mock the necessary parts
class TestServer(unittest.TestCase):
    def setUp(self):
        # Create fresh instances of each manager for testing
        self.chat_manager = ChatForkManager()
        self.diagram_manager = DiagramManager()
        self.structured_knowledge_manager = StructuredKnowledgeManager()
        
        # Set up testing conversation ID
        self.conv_id = "test_conversation"
        
    def test_todo_command(self):
        # Test add action
        result = add_task(
            self.conv_id, 
            "Test Task", 
            "Task description",
            "pending"
        )
        self.assertIn("Task added: 1 - Test Task", result)
        
        # Test add-batch action
        tasks = [
            {"title": "Task 1"},
            {"title": "Task 2", "status": "in_progress"}
        ]
        result = add_tasks_batch(self.conv_id, tasks)
        self.assertEqual(len(result), 2)
        self.assertIn("Task added", result[0])
        self.assertIn("Task added", result[1])
        
        # Test update action
        result = update_task(
            self.conv_id, 
            1, 
            status="completed"
        )
        self.assertIn("Task 1 updated", result)
        
        # Test get action
        result = get_task(self.conv_id, 1)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["title"], "Test Task")
        self.assertEqual(result["status"], "completed")
        
        # Test list action
        result = list_tasks(self.conv_id)
        self.assertEqual(len(result), 3)  # 3 tasks added so far
        
        # Test delete action
        result = delete_task(self.conv_id, 1)
        self.assertIn("Task 1 deleted", result)
        
        # Test with an unknown action type
        # This would normally be handled by the server's todo_command function
        # but we're testing the underlying tools directly
        
    def test_chat_fork_command(self):
        # Test fork_topic action
        result = self.chat_manager.fork_topic(
            self.conv_id, 
            "Test Topic"
        )
        self.assertIn("Forked new topic: Test Topic", result)
        
        # Test return_to_parent action
        result = self.chat_manager.return_to_parent(self.conv_id)
        self.assertIn("Returned to parent topic", result)
        
        # Test get_current_summary action
        result = self.chat_manager.get_current_summary(self.conv_id)
        self.assertEqual(result, "Conversation Root")
        
        # Test list_subtopics action
        result = self.chat_manager.list_subtopics(self.conv_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Test Topic")
        
    def test_diagram_command(self):
        # Test set_diagram_type action
        result = self.diagram_manager.set_diagram_type(
            self.conv_id, 
            "mindmap"
        )
        self.assertIn("Diagram type set to mindmap", result)
        
        # Test add_node action
        result = self.diagram_manager.add_node(
            self.conv_id, 
            "node1", 
            "Test Node"
        )
        self.assertIn("Node 'Test Node' added", result)
        
        # Test update_node action
        result = self.diagram_manager.update_node(
            self.conv_id, 
            "node1", 
            label="Updated Node"
        )
        self.assertIn("Node 'node1' updated", result)
        
        # Test add_edge action
        # Add another node first
        self.diagram_manager.add_node(
            self.conv_id, 
            "node2", 
            "Node 2"
        )
        result = self.diagram_manager.add_edge(
            self.conv_id, 
            "node1", 
            "node2", 
            "connects_to"
        )
        self.assertIn("Edge node1 -> node2 (connects_to) added", result)
        
        # Test update_edge action
        result = self.diagram_manager.update_edge(
            self.conv_id, 
            0, 
            type="depends_on"
        )
        self.assertIn("Edge at index 0 updated", result)
        
        # Test render action
        result = self.diagram_manager.render(self.conv_id)
        self.assertIn("Diagram Summary", result)
        self.assertIn("2 nodes", result)
        self.assertIn("1 edges", result)
        
    def test_structured_knowledge_command(self):
        # Test create action
        result = self.structured_knowledge_manager.create_structure(
            self.conv_id, 
            "test_structure", 
            template_type="simple_table", 
            columns=["Name", "Age"]
        )
        self.assertIn("Structure 'test_structure' created", result)
        
        # Test add action
        result = self.structured_knowledge_manager.add_row(
            self.conv_id, 
            "test_structure", 
            {"Name": "John", "Age": 30}
        )
        self.assertIn("Row added to 'test_structure'", result)
        
        # Test update action
        result = self.structured_knowledge_manager.update_row(
            self.conv_id, 
            "test_structure", 
            0, 
            {"Age": 31}
        )
        self.assertIn("Row 0 updated in 'test_structure'", result)
        
        # Test metrics action
        result = self.structured_knowledge_manager.get_metrics(
            self.conv_id, 
            "test_structure"
        )
        self.assertIn("total_items", result)
        
        # Test render action
        result = self.structured_knowledge_manager.render(
            self.conv_id, 
            "test_structure"
        )
        self.assertIn("Structure 'test_structure'", result)
        self.assertIn("Markdown", result)
        self.assertIn("JSON", result)

if __name__ == "__main__":
    unittest.main()
