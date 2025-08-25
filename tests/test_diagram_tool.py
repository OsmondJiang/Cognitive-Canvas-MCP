import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.diagram_tool import DiagramManager, Node, Edge

class TestDiagramTool(unittest.TestCase):
    def setUp(self):
        self.manager = DiagramManager()
        self.conv_id = "test_conversation"
        
    def test_node_class(self):
        # Test creating a Node
        node = Node("node1", "Test Node")
        self.assertEqual(node.id, "node1")
        self.assertEqual(node.label, "Test Node")
        self.assertEqual(node.metadata, {})
        
        # Test creating a Node with metadata
        metadata = {"color": "blue", "shape": "circle"}
        node = Node("node2", "Test Node 2", metadata)
        self.assertEqual(node.metadata, metadata)
        
    def test_edge_class(self):
        # Test creating an Edge
        edge = Edge("node1", "node2", "connects_to")
        self.assertEqual(edge.source, "node1")
        self.assertEqual(edge.target, "node2")
        self.assertEqual(edge.type, "connects_to")
        self.assertEqual(edge.metadata, {})
        
        # Test creating an Edge with metadata
        metadata = {"weight": 5, "color": "red"}
        edge = Edge("node1", "node2", "depends_on", metadata)
        self.assertEqual(edge.metadata, metadata)
        
    def test_add_node(self):
        # Test adding a node
        result = self.manager.add_node(self.conv_id, "node1", "Test Node")
        self.assertIn("Node 'Test Node' added", result)
        self.assertIn(self.conv_id, self.manager.conversations)
        self.assertIn("nodes", self.manager.conversations[self.conv_id])
        self.assertIn("node1", self.manager.conversations[self.conv_id]["nodes"])
        
        # Test adding a node with metadata
        metadata = {"color": "blue"}
        result = self.manager.add_node(self.conv_id, "node2", "Test Node 2", metadata)
        self.assertIn("Node 'Test Node 2' added", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["nodes"]["node2"].metadata,
            metadata
        )
        
    def test_update_node(self):
        # Add a node first
        self.manager.add_node(self.conv_id, "node1", "Original Label")
        
        # Test updating label
        result = self.manager.update_node(self.conv_id, "node1", label="Updated Label")
        self.assertIn("Node 'node1' updated", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["nodes"]["node1"].label,
            "Updated Label"
        )
        
        # Test updating metadata
        metadata = {"color": "red"}
        result = self.manager.update_node(self.conv_id, "node1", metadata=metadata)
        self.assertIn("Node 'node1' updated", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["nodes"]["node1"].metadata,
            metadata
        )
        
        # Test updating both
        result = self.manager.update_node(
            self.conv_id, 
            "node1", 
            label="Final Label", 
            metadata={"size": "large"}
        )
        self.assertIn("Node 'node1' updated", result)
        node = self.manager.conversations[self.conv_id]["nodes"]["node1"]
        self.assertEqual(node.label, "Final Label")
        self.assertEqual(node.metadata, {"color": "red", "size": "large"})  # Metadata is merged
        
        # Test updating a non-existent node
        result = self.manager.update_node(self.conv_id, "nonexistent", label="Invalid")
        self.assertIn("not found", result)
        
    def test_add_edge(self):
        # Add nodes first
        self.manager.add_node(self.conv_id, "node1", "Node 1")
        self.manager.add_node(self.conv_id, "node2", "Node 2")
        
        # Test adding an edge
        result = self.manager.add_edge(self.conv_id, "node1", "node2", "connects_to")
        self.assertIn("Edge node1 -> node2 (connects_to) added", result)
        self.assertEqual(len(self.manager.conversations[self.conv_id]["edges"]), 1)
        
        # Test adding an edge with metadata
        metadata = {"weight": 5}
        result = self.manager.add_edge(
            self.conv_id, 
            "node2", 
            "node1", 
            "depends_on", 
            metadata
        )
        self.assertIn("Edge node2 -> node1 (depends_on) added", result)
        self.assertEqual(len(self.manager.conversations[self.conv_id]["edges"]), 2)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["edges"][1].metadata,
            metadata
        )
        
    def test_update_edge(self):
        # Add nodes and edges first
        self.manager.add_node(self.conv_id, "node1", "Node 1")
        self.manager.add_node(self.conv_id, "node2", "Node 2")
        self.manager.add_edge(self.conv_id, "node1", "node2", "original_type")
        
        # Test updating edge type
        result = self.manager.update_edge(self.conv_id, 0, type="updated_type")
        self.assertIn("Edge at index 0 updated", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["edges"][0].type,
            "updated_type"
        )
        
        # Test updating edge metadata
        metadata = {"weight": 10}
        result = self.manager.update_edge(self.conv_id, 0, metadata=metadata)
        self.assertIn("Edge at index 0 updated", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["edges"][0].metadata,
            metadata
        )
        
        # Test updating both
        result = self.manager.update_edge(
            self.conv_id, 
            0, 
            type="final_type", 
            metadata={"condition": "if x > 0"}
        )
        self.assertIn("Edge at index 0 updated", result)
        edge = self.manager.conversations[self.conv_id]["edges"][0]
        self.assertEqual(edge.type, "final_type")
        # Metadata should be merged
        self.assertEqual(edge.metadata, {"weight": 10, "condition": "if x > 0"})
        
        # Test updating with an invalid index
        result = self.manager.update_edge(self.conv_id, 999, type="invalid")
        self.assertIn("Edge index out of range", result)
        
    def test_set_diagram_type(self):
        # Test setting a valid diagram type
        result = self.manager.set_diagram_type(self.conv_id, "mindmap")
        self.assertIn("Diagram type set to mindmap", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["diagram_type"],
            "mindmap"
        )
        
        # Test setting an invalid diagram type
        result = self.manager.set_diagram_type(self.conv_id, "invalid_type")
        self.assertIn("Unknown diagram type", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["diagram_type"],
            "mindmap"  # Should remain unchanged
        )
        
    def test_render(self):
        # Create a simple diagram
        self.manager.add_node(self.conv_id, "root", "Root Node")
        self.manager.add_node(self.conv_id, "child1", "Child 1")
        self.manager.add_node(self.conv_id, "child2", "Child 2")
        self.manager.add_edge(self.conv_id, "root", "child1", "contains")
        self.manager.add_edge(self.conv_id, "root", "child2", "contains")
        
        # Test rendering
        result = self.manager.render(self.conv_id)
        
        # Check that the result contains expected components
        self.assertIn("Diagram Summary", result)
        self.assertIn("3 nodes", result)
        self.assertIn("2 edges", result)
        
        # Verify the Markdown Table section
        self.assertIn("## Markdown Table", result)
        
        # Extract the table content
        table_section = result.split('## Markdown Table\n\n')[1].split('\n\n')[0]
        table_lines = table_section.split('\n')
        
        # Verify table structure
        self.assertGreaterEqual(len(table_lines), 4)  # Header, separator, and at least 2 data rows
        
        # Verify table headers
        header_line = table_lines[0]
        self.assertIn("Level", header_line)
        self.assertIn("Entity A", header_line)
        self.assertIn("Relationship", header_line)
        self.assertIn("Entity B", header_line)
        
        # Verify separator line format
        separator_line = table_lines[1]
        self.assertRegex(separator_line, r'\|-+\|-+\|-+\|-+\|')
        
        # Verify data rows contain the correct content
        data_rows = "\n".join(table_lines[2:])
        self.assertIn("Root Node", data_rows)
        self.assertIn("Child 1", data_rows)
        self.assertIn("Child 2", data_rows)
        self.assertIn("contains", data_rows)
        
        # Verify the Text Graph section
        self.assertIn("## Text Graph", result)
        
        # Extract the text graph content
        text_graph = result.split('## Text Graph\n\n')[1]
        
        # Verify text graph structure
        self.assertIn("Root Node", text_graph)
        
        # Check for hierarchical structure markers (should show parent-child relationships)
        text_lines = text_graph.split('\n')
        root_line_idx = next(i for i, line in enumerate(text_lines) if "Root Node" in line)
        
        # Verify children are indented under the root
        child_lines = text_lines[root_line_idx+1:]
        child_found = 0
        for line in child_lines:
            if "Child 1" in line or "Child 2" in line:
                # Check for tree structure markers - at least one of these should be in the line
                self.assertTrue("└─ " in line or "├─ " in line, f"Tree structure marker not found in line: {line}")
                child_found += 1
                
        self.assertEqual(child_found, 2)  # Both children should be found
        
        # Test rendering a more complex diagram
        self.manager.add_node(self.conv_id, "grandchild1", "Grandchild 1")
        self.manager.add_edge(
            self.conv_id, 
            "child1", 
            "grandchild1", 
            "contains",
            {"condition": "if needed", "weight": 5}
        )
        
        result = self.manager.render(self.conv_id)
        
        # Verify overall structure
        self.assertIn("4 nodes", result)
        self.assertIn("3 edges", result)
        
        # Verify max depth is calculated correctly
        self.assertIn("max depth 2", result)
        
        # Verify metadata appears in both table and text graph
        self.assertIn("if needed", result)  # Metadata condition should appear
        
        # Test diagram type change
        self.manager.set_diagram_type(self.conv_id, "mindmap")
        result = self.manager.render(self.conv_id)
        
        # Should still have the same content but possibly different formatting
        self.assertIn("Diagram Summary", result)
        self.assertIn("4 nodes", result)
        self.assertIn("3 edges", result)
        self.assertIn("Root Node", result)
        self.assertIn("Child 1", result)
        self.assertIn("Child 2", result)
        self.assertIn("Grandchild 1", result)

if __name__ == "__main__":
    unittest.main()
