import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.chat_fork import ChatForkManager, ChatNode

class TestChatForkManager(unittest.TestCase):
    def setUp(self):
        self.manager = ChatForkManager()
        self.conv_id = "test_conversation"
        
    def test_chat_node_class(self):
        # Test creating a ChatNode
        node = ChatNode("Root Node")
        self.assertEqual(node.summary, "Root Node")
        self.assertEqual(node.details, "")
        self.assertIsNone(node.parent)
        self.assertEqual(node.children, [])
        
        # Test creating a ChatNode with details
        node_with_details = ChatNode("Detailed Node", "This is detailed information")
        self.assertEqual(node_with_details.summary, "Detailed Node")
        self.assertEqual(node_with_details.details, "This is detailed information")
        
        # Test creating a child node
        parent_node = ChatNode("Parent Node")
        child_node = ChatNode("Child Node", "Child details", parent=parent_node)
        self.assertEqual(child_node.summary, "Child Node")
        self.assertEqual(child_node.details, "Child details")
        self.assertEqual(child_node.parent, parent_node)
        
    def test_fork_topic(self):
        # Test forking a topic in a new conversation
        result = self.manager.fork_topic(self.conv_id, "First Topic")
        self.assertEqual(result, "Forked new topic: First Topic")
        
        # Test forking a topic with details
        result = self.manager.fork_topic(self.conv_id, "Detailed Topic", "This topic has detailed information")
        self.assertEqual(result, "Forked new topic: Detailed Topic")
        
        # Verify the conversation structure in detail
        self.assertIn(self.conv_id, self.manager.conversations)
        current_node = self.manager.conversations[self.conv_id]
        
        # Check current node properties
        self.assertEqual(current_node.summary, "Detailed Topic")
        self.assertEqual(current_node.details, "This topic has detailed information")
        self.assertIsNotNone(current_node.parent)
        self.assertEqual(current_node.parent.summary, "First Topic")
        self.assertEqual(len(current_node.children), 0)  # No children yet
        
        # Check parent node properties
        parent_node = current_node.parent
        self.assertEqual(parent_node.summary, "First Topic")
        self.assertEqual(parent_node.details, "")  # No details for first topic
        self.assertIsNotNone(parent_node.parent)  # Has grandparent (root)
        self.assertEqual(len(parent_node.children), 1)  # One child (Detailed Topic)
        
        # Check root node properties
        root_node = parent_node.parent
        self.assertEqual(root_node.summary, "Conversation Root")
        self.assertIsNone(root_node.parent)  # Root has no parent
        self.assertEqual(len(root_node.children), 1)  # One child (First Topic)
        
        # Test forking another topic
        result = self.manager.fork_topic(self.conv_id, "Second Topic")
        self.assertEqual(result, "Forked new topic: Second Topic")
        
        # Verify updated structure
        current_node = self.manager.conversations[self.conv_id]
        self.assertEqual(current_node.summary, "Second Topic")
        
        # Verify parent-child relationship
        parent_node = current_node.parent
        self.assertEqual(parent_node.summary, "Detailed Topic")
        self.assertEqual(len(parent_node.children), 1)
        self.assertEqual(parent_node.children[0], current_node)
        
        # Verify grandparent relationship
        grandparent = parent_node.parent
        self.assertEqual(grandparent.summary, "First Topic")
        
        # Create a complex conversation tree
        self.manager.return_to_previous_context(self.conv_id)  # Back to Detailed Topic
        self.manager.fork_topic(self.conv_id, "Branch A")
        self.manager.return_to_previous_context(self.conv_id)  # Back to Detailed Topic
        self.manager.fork_topic(self.conv_id, "Branch B")
        
        # Verify tree structure
        current_node = self.manager.conversations[self.conv_id]
        self.assertEqual(current_node.summary, "Branch B")
        parent = current_node.parent
        self.assertEqual(parent.summary, "Detailed Topic")
        self.assertEqual(len(parent.children), 3)  # Second Topic, Branch A, Branch B
        
        # Verify sibling summaries
        sibling_summaries = [child.summary for child in parent.children]
        self.assertIn("Second Topic", sibling_summaries)
        self.assertIn("Branch A", sibling_summaries)
        self.assertIn("Branch B", sibling_summaries)
        
    def test_return_to_previous_context(self):
        # Create a conversation with multiple levels
        self.manager.fork_topic(self.conv_id, "Level 1")
        self.manager.fork_topic(self.conv_id, "Level 2", "Details for level 2")
        self.manager.fork_topic(self.conv_id, "Level 3")
        
        # Test returning to previous context
        result = self.manager.return_to_previous_context(self.conv_id)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertIn("Returned to previous context: Level 2", result["message"])
        self.assertEqual(result["summary"], "Level 2")
        self.assertEqual(result["details"], "Details for level 2")
        self.assertTrue(result["has_details"])
        
        current_node = self.manager.conversations[self.conv_id]
        self.assertEqual(current_node.summary, "Level 2")
        
        # Return to previous context again
        result = self.manager.return_to_previous_context(self.conv_id)
        self.assertEqual(result["status"], "success")
        self.assertIn("Returned to previous context: Level 1", result["message"])
        self.assertEqual(result["summary"], "Level 1")
        self.assertEqual(result["details"], "")
        self.assertFalse(result["has_details"])
        
        # Return to root
        result = self.manager.return_to_previous_context(self.conv_id)
        self.assertEqual(result["status"], "success")
        self.assertIn("Returned to previous context: Conversation Root", result["message"])
        
        # Try to return past root
        result = self.manager.return_to_previous_context(self.conv_id)
        self.assertEqual(result["status"], "error")
        self.assertIn("Already at root context", result["message"])
        
        # Test returning in a non-existent conversation
        result = self.manager.return_to_previous_context("nonexistent")
        self.assertIn("error", result)
        self.assertIn("Conversation not found", result["error"])
        
    def test_get_current_context(self):
        # Test getting context for a non-existent conversation
        result = self.manager.get_current_context("nonexistent")
        self.assertIn("error", result)
        self.assertIn("Conversation not found", result["error"])
        
        # Create a conversation and test
        self.manager.fork_topic(self.conv_id, "Test Topic")
        result = self.manager.get_current_context(self.conv_id)
        self.assertEqual(result["summary"], "Test Topic")
        self.assertEqual(result["details"], "")
        self.assertFalse(result["has_details"])
        
        # Fork again with details and test
        self.manager.fork_topic(self.conv_id, "Subtopic", "Detailed information about subtopic")
        result = self.manager.get_current_context(self.conv_id)
        self.assertEqual(result["summary"], "Subtopic")
        self.assertEqual(result["details"], "Detailed information about subtopic")
        self.assertTrue(result["has_details"])
        
    def test_list_subtopics(self):
        # Test listing subtopics for a non-existent conversation
        result = self.manager.list_subtopics("nonexistent")
        self.assertEqual(result, [])
        
        # Create a conversation root
        self.manager.fork_topic(self.conv_id, "Root Topic")
        
        # Initially, there should be no subtopics
        result = self.manager.list_subtopics(self.conv_id)
        self.assertEqual(result, [])
        
        # Go back to root and add multiple subtopics
        self.manager.return_to_previous_context(self.conv_id)
        self.manager.fork_topic(self.conv_id, "Subtopic 1", "Details for subtopic 1")
        self.manager.return_to_previous_context(self.conv_id)
        self.manager.fork_topic(self.conv_id, "Subtopic 2")
        self.manager.return_to_previous_context(self.conv_id)
        
        # Test listing subtopics from the root without details
        result = self.manager.list_subtopics(self.conv_id)
        self.assertEqual(len(result), 3)  # Root Topic, Subtopic 1, Subtopic 2
        self.assertIn("Root Topic", result)
        self.assertIn("Subtopic 1", result)
        self.assertIn("Subtopic 2", result)
        
        # Test listing subtopics with details
        result = self.manager.list_subtopics(self.conv_id, include_details=True)
        self.assertEqual(len(result), 3)
        # Check that details are included in the output
        subtopic_1_found = False
        subtopic_2_found = False
        for item in result:
            if "Subtopic 1" in item:
                self.assertIn("Details for subtopic 1", item)
                subtopic_1_found = True
            elif "Subtopic 2" in item:
                self.assertIn("No details", item)
                subtopic_2_found = True
        self.assertTrue(subtopic_1_found)
        self.assertTrue(subtopic_2_found)
        
        # Test listing subtopics from a leaf node
        self.manager.fork_topic(self.conv_id, "Subtopic 3")
        result = self.manager.list_subtopics(self.conv_id)
        self.assertEqual(result, [])  # Leaf node has no children

if __name__ == "__main__":
    unittest.main()
