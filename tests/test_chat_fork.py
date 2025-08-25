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
        self.assertIsNone(node.parent)
        self.assertEqual(node.children, [])
        
        # Test creating a child node
        parent_node = ChatNode("Parent Node")
        child_node = ChatNode("Child Node", parent=parent_node)
        self.assertEqual(child_node.summary, "Child Node")
        self.assertEqual(child_node.parent, parent_node)
        
    def test_fork_topic(self):
        # Test forking a topic in a new conversation
        result = self.manager.fork_topic(self.conv_id, "First Topic")
        self.assertEqual(result, "Forked new topic: First Topic")
        
        # Verify the conversation structure in detail
        self.assertIn(self.conv_id, self.manager.conversations)
        current_node = self.manager.conversations[self.conv_id]
        
        # Check current node properties
        self.assertEqual(current_node.summary, "First Topic")
        self.assertIsNotNone(current_node.parent)
        self.assertEqual(current_node.parent.summary, "Conversation Root")
        self.assertEqual(len(current_node.children), 0)  # No children yet
        
        # Check root node properties
        root_node = current_node.parent
        self.assertIsNone(root_node.parent)  # Root has no parent
        self.assertEqual(len(root_node.children), 1)  # One child (First Topic)
        self.assertEqual(root_node.children[0], current_node)  # Child references match
        
        # Test forking another topic
        result = self.manager.fork_topic(self.conv_id, "Second Topic")
        self.assertEqual(result, "Forked new topic: Second Topic")
        
        # Verify updated structure
        current_node = self.manager.conversations[self.conv_id]
        self.assertEqual(current_node.summary, "Second Topic")
        
        # Verify parent-child relationship
        parent_node = current_node.parent
        self.assertEqual(parent_node.summary, "First Topic")
        self.assertEqual(len(parent_node.children), 1)
        self.assertEqual(parent_node.children[0], current_node)
        
        # Verify grandparent relationship
        grandparent = parent_node.parent
        self.assertEqual(grandparent.summary, "Conversation Root")
        
        # Create a complex conversation tree
        self.manager.return_to_parent(self.conv_id)  # Back to First Topic
        self.manager.fork_topic(self.conv_id, "Branch A")
        self.manager.return_to_parent(self.conv_id)  # Back to First Topic
        self.manager.fork_topic(self.conv_id, "Branch B")
        
        # Verify tree structure
        current_node = self.manager.conversations[self.conv_id]
        self.assertEqual(current_node.summary, "Branch B")
        parent = current_node.parent
        self.assertEqual(parent.summary, "First Topic")
        self.assertEqual(len(parent.children), 3)  # Second Topic, Branch A, Branch B
        
        # Verify sibling summaries
        sibling_summaries = [child.summary for child in parent.children]
        self.assertIn("Second Topic", sibling_summaries)
        self.assertIn("Branch A", sibling_summaries)
        self.assertIn("Branch B", sibling_summaries)
        
    def test_return_to_parent(self):
        # Create a conversation with multiple levels
        self.manager.fork_topic(self.conv_id, "Level 1")
        self.manager.fork_topic(self.conv_id, "Level 2")
        self.manager.fork_topic(self.conv_id, "Level 3")
        
        # Test returning to parent
        result = self.manager.return_to_parent(self.conv_id)
        self.assertIn("Returned to parent topic: Level 2", result)
        
        current_node = self.manager.conversations[self.conv_id]
        self.assertEqual(current_node.summary, "Level 2")
        
        # Return to parent again
        result = self.manager.return_to_parent(self.conv_id)
        self.assertIn("Returned to parent topic: Level 1", result)
        
        # Return to root
        result = self.manager.return_to_parent(self.conv_id)
        self.assertIn("Returned to parent topic: Conversation Root", result)
        
        # Try to return past root
        result = self.manager.return_to_parent(self.conv_id)
        self.assertIn("Already at root topic", result)
        
        # Test returning in a non-existent conversation
        result = self.manager.return_to_parent("nonexistent")
        self.assertIn("Conversation not found", result)
        
    def test_get_current_summary(self):
        # Test getting summary for a non-existent conversation
        result = self.manager.get_current_summary("nonexistent")
        self.assertIn("Conversation not found", result)
        
        # Create a conversation and test
        self.manager.fork_topic(self.conv_id, "Test Topic")
        result = self.manager.get_current_summary(self.conv_id)
        self.assertEqual(result, "Test Topic")
        
        # Fork again and test
        self.manager.fork_topic(self.conv_id, "Subtopic")
        result = self.manager.get_current_summary(self.conv_id)
        self.assertEqual(result, "Subtopic")
        
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
        self.manager.return_to_parent(self.conv_id)
        self.manager.fork_topic(self.conv_id, "Subtopic 1")
        self.manager.return_to_parent(self.conv_id)
        self.manager.fork_topic(self.conv_id, "Subtopic 2")
        self.manager.return_to_parent(self.conv_id)
        
        # Test listing subtopics from the root
        result = self.manager.list_subtopics(self.conv_id)
        self.assertEqual(len(result), 3)  # Root Topic, Subtopic 1, Subtopic 2
        self.assertIn("Root Topic", result)
        self.assertIn("Subtopic 1", result)
        self.assertIn("Subtopic 2", result)
        
        # Test listing subtopics from a leaf node
        self.manager.fork_topic(self.conv_id, "Subtopic 3")
        result = self.manager.list_subtopics(self.conv_id)
        self.assertEqual(result, [])  # Leaf node has no children

if __name__ == "__main__":
    unittest.main()
