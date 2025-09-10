#!/usr/bin/env python3
"""
Test the workspace functionality of the Relationship Mapper tool.
"""

import sys
import os
import unittest

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.relationship_mapper import RelationshipMapper


class TestRelationshipMapperWorkspace(unittest.TestCase):
    """Test workspace functionality for RelationshipMapper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mapper = RelationshipMapper()
        self.conversation_id = "test_conv"
        self.workspace1 = "project1"
        self.workspace2 = "project2"
    
    def test_auto_workspace_creation(self):
        """Test that workspaces are auto-created on first use"""
        # Initially no conversations
        self.assertEqual(len(self.mapper.conversations), 0)
        
        # First use creates conversation and workspace
        result = self.mapper.set_visualization_type(self.conversation_id, self.workspace1, "flowchart")
        self.assertTrue(result["success"])
        
        # Verify structure was created
        self.assertIn(self.conversation_id, self.mapper.conversations)
        self.assertIn("workspaces", self.mapper.conversations[self.conversation_id])
        self.assertIn(self.workspace1, self.mapper.conversations[self.conversation_id]["workspaces"])
        
        # Verify workspace has correct structure
        workspace = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace1]
        self.assertIn("nodes", workspace)
        self.assertIn("edges", workspace)
        self.assertIn("visualization_type", workspace)
        self.assertEqual(workspace["visualization_type"], "flowchart")
    
    def test_workspace_isolation(self):
        """Test that different workspaces are isolated"""
        # Add nodes to workspace1
        nodes1 = [
            {"id": "node1", "label": "Node 1", "metadata": {"type": "start"}},
            {"id": "node2", "label": "Node 2", "metadata": {"type": "process"}}
        ]
        result1 = self.mapper.batch_add_nodes(self.conversation_id, self.workspace1, nodes1)
        self.assertTrue(result1["success"])
        
        # Add different nodes to workspace2
        nodes2 = [
            {"id": "nodeA", "label": "Node A", "metadata": {"type": "input"}},
            {"id": "nodeB", "label": "Node B", "metadata": {"type": "output"}}
        ]
        result2 = self.mapper.batch_add_nodes(self.conversation_id, self.workspace2, nodes2)
        self.assertTrue(result2["success"])
        
        # Verify isolation - workspace1 only has its nodes
        workspace1_nodes = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace1]["nodes"]
        self.assertEqual(len(workspace1_nodes), 2)
        self.assertIn("node1", workspace1_nodes)
        self.assertIn("node2", workspace1_nodes)
        self.assertNotIn("nodeA", workspace1_nodes)
        self.assertNotIn("nodeB", workspace1_nodes)
        
        # Verify isolation - workspace2 only has its nodes
        workspace2_nodes = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace2]["nodes"]
        self.assertEqual(len(workspace2_nodes), 2)
        self.assertIn("nodeA", workspace2_nodes)
        self.assertIn("nodeB", workspace2_nodes)
        self.assertNotIn("node1", workspace2_nodes)
        self.assertNotIn("node2", workspace2_nodes)
    
    def test_edges_workspace_isolation(self):
        """Test that edges are isolated between workspaces"""
        # Set up nodes in both workspaces
        nodes = [{"id": "n1", "label": "Node 1"}, {"id": "n2", "label": "Node 2"}]
        self.mapper.batch_add_nodes(self.conversation_id, self.workspace1, nodes)
        self.mapper.batch_add_nodes(self.conversation_id, self.workspace2, nodes)
        
        # Add edge to workspace1
        edges1 = [{"source": "n1", "target": "n2", "type": "connects", "metadata": {"weight": 1}}]
        result1 = self.mapper.batch_add_edges(self.conversation_id, self.workspace1, edges1)
        self.assertTrue(result1["success"])
        
        # Add different edge to workspace2
        edges2 = [{"source": "n2", "target": "n1", "type": "flows_to", "metadata": {"weight": 5}}]
        result2 = self.mapper.batch_add_edges(self.conversation_id, self.workspace2, edges2)
        self.assertTrue(result2["success"])
        
        # Verify edge isolation
        workspace1_edges = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace1]["edges"]
        workspace2_edges = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace2]["edges"]
        
        self.assertEqual(len(workspace1_edges), 1)
        self.assertEqual(len(workspace2_edges), 1)
        
        # Check edge details
        self.assertEqual(workspace1_edges[0].source, "n1")
        self.assertEqual(workspace1_edges[0].target, "n2")
        self.assertEqual(workspace1_edges[0].type, "connects")
        
        self.assertEqual(workspace2_edges[0].source, "n2")
        self.assertEqual(workspace2_edges[0].target, "n1")
        self.assertEqual(workspace2_edges[0].type, "flows_to")
    
    def test_visualization_type_isolation(self):
        """Test that visualization types are isolated per workspace"""
        # Set different visualization types
        result1 = self.mapper.set_visualization_type(self.conversation_id, self.workspace1, "flowchart")
        self.assertTrue(result1["success"])
        
        result2 = self.mapper.set_visualization_type(self.conversation_id, self.workspace2, "tree")
        self.assertTrue(result2["success"])
        
        # Verify isolation
        workspace1_type = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace1]["visualization_type"]
        workspace2_type = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace2]["visualization_type"]
        
        self.assertEqual(workspace1_type, "flowchart")
        self.assertEqual(workspace2_type, "tree")
    
    def test_list_workspaces(self):
        """Test listing workspaces"""
        # Initially no workspaces
        result = self.mapper.list_workspaces(self.conversation_id)
        self.assertTrue(result["success"])
        self.assertEqual(result["workspaces"], [])
        
        # Create workspaces by using them
        self.mapper.set_visualization_type(self.conversation_id, self.workspace1, "flowchart")
        self.mapper.set_visualization_type(self.conversation_id, self.workspace2, "tree")
        self.mapper.set_visualization_type(self.conversation_id, "default", "mindmap")
        
        # List workspaces
        result = self.mapper.list_workspaces(self.conversation_id)
        self.assertTrue(result["success"])
        workspaces = result["workspaces"]
        
        self.assertEqual(len(workspaces), 3)
        self.assertIn(self.workspace1, workspaces)
        self.assertIn(self.workspace2, workspaces)
        self.assertIn("default", workspaces)
    
    def test_batch_operations_workspace_isolation(self):
        """Test batch operations respect workspace isolation"""
        operations1 = [
            {"action": "add_node", "data": {"id": "start", "label": "Start"}},
            {"action": "add_node", "data": {"id": "end", "label": "End"}},
            {"action": "add_edge", "data": {"source": "start", "target": "end", "type": "flow"}}
        ]
        
        operations2 = [
            {"action": "add_node", "data": {"id": "input", "label": "Input"}},
            {"action": "add_node", "data": {"id": "output", "label": "Output"}},
            {"action": "add_edge", "data": {"source": "input", "target": "output", "type": "transform"}}
        ]
        
        # Execute operations in different workspaces
        result1 = self.mapper.batch_operations(self.conversation_id, self.workspace1, operations1)
        self.assertTrue(result1["success"])
        
        result2 = self.mapper.batch_operations(self.conversation_id, self.workspace2, operations2)
        self.assertTrue(result2["success"])
        
        # Verify isolation
        workspace1_nodes = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace1]["nodes"]
        workspace2_nodes = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace2]["nodes"]
        
        self.assertEqual(len(workspace1_nodes), 2)
        self.assertEqual(len(workspace2_nodes), 2)
        
        self.assertIn("start", workspace1_nodes)
        self.assertIn("end", workspace1_nodes)
        self.assertNotIn("input", workspace1_nodes)
        self.assertNotIn("output", workspace1_nodes)
        
        self.assertIn("input", workspace2_nodes)
        self.assertIn("output", workspace2_nodes)
        self.assertNotIn("start", workspace2_nodes)
        self.assertNotIn("end", workspace2_nodes)
    
    def test_get_visualization_content_workspace_specific(self):
        """Test that visualization content is workspace-specific"""
        # Set up workspace1 with flowchart
        self.mapper.set_visualization_type(self.conversation_id, self.workspace1, "flowchart")
        nodes1 = [{"id": "step1", "label": "Step 1"}, {"id": "step2", "label": "Step 2"}]
        self.mapper.batch_add_nodes(self.conversation_id, self.workspace1, nodes1)
        
        # Set up workspace2 with tree
        self.mapper.set_visualization_type(self.conversation_id, self.workspace2, "tree")
        nodes2 = [{"id": "root", "label": "Root"}, {"id": "child", "label": "Child"}]
        self.mapper.batch_add_nodes(self.conversation_id, self.workspace2, nodes2)
        
        # Get visualization content for each workspace
        content1 = self.mapper.get_visualization_content(self.conversation_id, self.workspace1)
        content2 = self.mapper.get_visualization_content(self.conversation_id, self.workspace2)
        
        # Verify content is different and workspace-specific
        self.assertIsInstance(content1, str)
        self.assertIsInstance(content2, str)
        self.assertNotEqual(content1, content2)
        
        # Verify workspace1 content contains its nodes
        self.assertIn("Step 1", content1)
        self.assertIn("Step 2", content1)
        self.assertNotIn("Root", content1)
        self.assertNotIn("Child", content1)
        
        # Verify workspace2 content contains its nodes
        self.assertIn("Root", content2)
        self.assertIn("Child", content2)
        self.assertNotIn("Step 1", content2)
        self.assertNotIn("Step 2", content2)
    
    def test_update_operations_workspace_isolation(self):
        """Test that update operations work within workspace boundaries"""
        # Set up nodes in both workspaces
        nodes = [{"id": "test_node", "label": "Original Label"}]
        self.mapper.batch_add_nodes(self.conversation_id, self.workspace1, nodes)
        self.mapper.batch_add_nodes(self.conversation_id, self.workspace2, nodes)
        
        # Update node in workspace1
        updates1 = [{"id": "test_node", "label": "Updated Label 1", "metadata": {"updated": True}}]
        result1 = self.mapper.batch_update_nodes(self.conversation_id, self.workspace1, updates1)
        self.assertTrue(result1["success"])
        
        # Update node in workspace2 with different values
        updates2 = [{"id": "test_node", "label": "Updated Label 2", "metadata": {"version": 2}}]
        result2 = self.mapper.batch_update_nodes(self.conversation_id, self.workspace2, updates2)
        self.assertTrue(result2["success"])
        
        # Verify updates are isolated
        workspace1_node = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace1]["nodes"]["test_node"]
        workspace2_node = self.mapper.conversations[self.conversation_id]["workspaces"][self.workspace2]["nodes"]["test_node"]
        
        self.assertEqual(workspace1_node.label, "Updated Label 1")
        self.assertEqual(workspace2_node.label, "Updated Label 2")
        
        self.assertIn("updated", workspace1_node.metadata)
        self.assertIn("version", workspace2_node.metadata)
        self.assertNotIn("version", workspace1_node.metadata)
        self.assertNotIn("updated", workspace2_node.metadata)


if __name__ == '__main__':
    unittest.main()
