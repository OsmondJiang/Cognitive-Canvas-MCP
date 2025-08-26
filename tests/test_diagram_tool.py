import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.diagram_tool import DiagramManager, Node, Edge
import server

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
        self.assertIn("Diagram", result)
        self.assertIn("Root Node", result)
        self.assertIn("Child 1", result)
        self.assertIn("Child 2", result)
        
        # Verify the Table section
        self.assertIn("Table", result)
        
        # Extract the table content if present
        if "| Node ID | Label | Level |" in result:
            # New format
            table_lines = [line for line in result.split('\n') if line.startswith('|')]
            
            # Verify table structure
            self.assertGreaterEqual(len(table_lines), 4)  # Header, separator, and at least 2 data rows
            
            # Verify table headers
            header_line = table_lines[0]
            self.assertIn("Node ID", header_line)
            self.assertIn("Label", header_line)
            self.assertIn("Level", header_line)
            
            # Verify separator line format
            separator_line = table_lines[1]
            self.assertIn("---", separator_line)  # Just check for separator characters
            
            # Verify data rows contain the correct content
            data_rows = "\n".join(table_lines[2:])
            self.assertIn("root", data_rows)
            self.assertIn("Root Node", data_rows)
            self.assertIn("child1", data_rows)
            self.assertIn("child2", data_rows)
        else:
            # Fall back to old format in case the test runs against old version
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
            self.assertIn("---", separator_line)  # Just check for separator characters
            
            # Verify data rows contain the correct content
            data_rows = "\n".join(table_lines[2:])
            self.assertIn("Root Node", data_rows)
        
        # Check all data values are present somewhere in the result
        self.assertIn("Child 1", result)
        self.assertIn("Child 2", result)
        
        # For flowchart (default), we only get table view
        # For tree/mindmap/orgchart, we only get text/tree view
        if "### Diagram (Table Style)" in result:
            # Table style - verify table structure
            self.assertIn("| Node ID | Label | Level |", result)
            self.assertIn("| root | Root Node | 0 |", result)
        elif "### Diagram (Tree Style)" in result:
            # Tree style - check for text representation with code block
            text_graph = result.split("```")[1].strip()
            self.assertIn("Root Node", text_graph)
            # Check for tree structure indicators
            self.assertTrue("└─" in text_graph or "├─" in text_graph)
            
            # Verify text graph structure
            text_lines = text_graph.split('\n')
            self.assertGreater(len(text_lines), 1)  # Should have at least the root and one child
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
        # Count nodes in the table
        table_rows = [line for line in result.split('\n') if '|' in line]
        # Skip header and separator lines
        table_rows = [row for row in table_rows if not '---' in row][1:]  
        self.assertEqual(len(table_rows), 4, "Should have 4 node entries in the table")
        
        # Verify the tree structure 
        self.assertIn("Root Node", result)
        self.assertIn("Child 1", result)
        self.assertIn("Child 2", result)
        self.assertIn("Grandchild 1", result)
        
        # Note: Current implementation doesn't display edge metadata in the render output
        # If metadata display is needed, the render method would need to be updated
        
        # Test diagram type change
        self.manager.set_diagram_type(self.conv_id, "mindmap")
        result = self.manager.render(self.conv_id)
        
        # Should still have the same content but mindmap should show tree style
        self.assertIn("### Diagram (Tree Style)", result)
        self.assertIn("Root Node", result)
        self.assertIn("Child 1", result)
        self.assertIn("Child 2", result)
        self.assertIn("Grandchild 1", result)
        
        # Test flowchart type shows table style
        self.manager.set_diagram_type(self.conv_id, "flowchart")
        result = self.manager.render(self.conv_id)
        self.assertIn("### Diagram (Table Style)", result)
        self.assertIn("Root Node", result)

    def test_batch_add_nodes(self):
        """Test batch adding nodes"""
        nodes = [
            {"id": "batch1", "label": "Batch Node 1", "metadata": {"type": "start"}},
            {"id": "batch2", "label": "Batch Node 2", "metadata": {"type": "process"}},
            {"id": "batch3", "label": "Batch Node 3", "metadata": {"type": "end"}}
        ]
        
        result = self.manager.batch_add_nodes(self.conv_id, nodes)
        
        # Check that all nodes were added
        self.assertIn("Batch Node 1", result)
        self.assertIn("Batch Node 2", result)
        self.assertIn("Batch Node 3", result)
        
        # Verify nodes exist in the conversation
        conv_nodes = self.manager.conversations[self.conv_id]["nodes"]
        self.assertIn("batch1", conv_nodes)
        self.assertIn("batch2", conv_nodes)
        self.assertIn("batch3", conv_nodes)
        
        # Check metadata
        self.assertEqual(conv_nodes["batch1"].metadata["type"], "start")
        self.assertEqual(conv_nodes["batch2"].metadata["type"], "process")
        self.assertEqual(conv_nodes["batch3"].metadata["type"], "end")

    def test_batch_add_edges(self):
        """Test batch adding edges"""
        # First add some nodes
        self.manager.add_node(self.conv_id, "source1", "Source 1")
        self.manager.add_node(self.conv_id, "target1", "Target 1")
        self.manager.add_node(self.conv_id, "target2", "Target 2")
        
        edges = [
            {"source": "source1", "target": "target1", "type": "connects", "metadata": {"weight": 1}},
            {"source": "target1", "target": "target2", "type": "flows_to", "metadata": {"weight": 2}}
        ]
        
        result = self.manager.batch_add_edges(self.conv_id, edges)
        
        # Check that edges were added
        self.assertIn("source1 -> target1 (connects) added", result)
        self.assertIn("target1 -> target2 (flows_to) added", result)
        
        # Verify edges exist
        conv_edges = self.manager.conversations[self.conv_id]["edges"]
        self.assertEqual(len(conv_edges), 2)
        self.assertEqual(conv_edges[0].source, "source1")
        self.assertEqual(conv_edges[0].target, "target1")
        self.assertEqual(conv_edges[0].type, "connects")
        self.assertEqual(conv_edges[0].metadata["weight"], 1)

    def test_batch_update_nodes(self):
        """Test batch updating nodes"""
        # First add some nodes
        self.manager.add_node(self.conv_id, "update1", "Original Label 1")
        self.manager.add_node(self.conv_id, "update2", "Original Label 2")
        
        updates = [
            {"id": "update1", "label": "Updated Label 1", "metadata": {"updated": True}},
            {"id": "update2", "label": "Updated Label 2", "metadata": {"version": 2}}
        ]
        
        result = self.manager.batch_update_nodes(self.conv_id, updates)
        
        # Check update results
        self.assertIn("Node 'update1' updated", result)
        self.assertIn("Node 'update2' updated", result)
        
        # Verify updates
        conv_nodes = self.manager.conversations[self.conv_id]["nodes"]
        self.assertEqual(conv_nodes["update1"].label, "Updated Label 1")
        self.assertEqual(conv_nodes["update2"].label, "Updated Label 2")
        self.assertTrue(conv_nodes["update1"].metadata["updated"])
        self.assertEqual(conv_nodes["update2"].metadata["version"], 2)

    def test_batch_update_edges(self):
        """Test batch updating edges"""
        # First add nodes and edges
        self.manager.add_node(self.conv_id, "edge_source", "Edge Source")
        self.manager.add_node(self.conv_id, "edge_target", "Edge Target")
        self.manager.add_edge(self.conv_id, "edge_source", "edge_target", "original_type")
        self.manager.add_edge(self.conv_id, "edge_target", "edge_source", "reverse_type")
        
        updates = [
            {"index": 0, "type": "updated_type", "metadata": {"updated": True}},
            {"index": 1, "type": "new_reverse_type", "metadata": {"version": 2}}
        ]
        
        result = self.manager.batch_update_edges(self.conv_id, updates)
        
        # Check update results
        self.assertIn("Edge at index 0 updated", result)
        self.assertIn("Edge at index 1 updated", result)
        
        # Verify updates
        conv_edges = self.manager.conversations[self.conv_id]["edges"]
        self.assertEqual(conv_edges[0].type, "updated_type")
        self.assertEqual(conv_edges[1].type, "new_reverse_type")
        self.assertTrue(conv_edges[0].metadata["updated"])
        self.assertEqual(conv_edges[1].metadata["version"], 2)

    def test_batch_operations(self):
        """Test mixed batch operations"""
        operations = [
            {"action": "add_node", "data": {"id": "mixed1", "label": "Mixed Node 1", "metadata": {"type": "start"}}},
            {"action": "add_node", "data": {"id": "mixed2", "label": "Mixed Node 2", "metadata": {"type": "end"}}},
            {"action": "add_edge", "data": {"source": "mixed1", "target": "mixed2", "type": "connects"}},
            {"action": "update_node", "data": {"id": "mixed1", "label": "Updated Mixed Node 1", "metadata": {"updated": True}}}
        ]
        
        result = self.manager.batch_operations(self.conv_id, operations)
        
        # Check that all operations were performed
        self.assertIn("Mixed Node 1", result)
        self.assertIn("Mixed Node 2", result)
        self.assertIn("mixed1 -> mixed2 (connects) added", result)
        self.assertIn("Node 'mixed1' updated", result)
        
        # Verify final state
        conv_nodes = self.manager.conversations[self.conv_id]["nodes"]
        conv_edges = self.manager.conversations[self.conv_id]["edges"]
        
        self.assertEqual(conv_nodes["mixed1"].label, "Updated Mixed Node 1")
        self.assertTrue(conv_nodes["mixed1"].metadata["updated"])
        self.assertEqual(len(conv_edges), 1)
        self.assertEqual(conv_edges[0].source, "mixed1")
        self.assertEqual(conv_edges[0].target, "mixed2")

    def test_batch_error_handling(self):
        """Test error handling in batch operations"""
        # Test batch add nodes with missing data
        invalid_nodes = [
            {"label": "Missing ID"},  # Missing id
            {"id": "valid", "label": "Valid Node"}
        ]
        
        result = self.manager.batch_add_nodes(self.conv_id, invalid_nodes)
        self.assertIn("Error: Missing id or label", result)
        self.assertIn("Valid Node", result)
        
        # Test batch update with non-existent node
        invalid_updates = [
            {"id": "nonexistent", "label": "This won't work"}
        ]
        
        result = self.manager.batch_update_nodes(self.conv_id, invalid_updates)
        self.assertIn("Error: Node nonexistent not found", result)
        
        # Test batch add edges with missing data
        invalid_edges = [
            {"source": "missing_target", "type": "incomplete"},  # Missing target
            {"source": "valid", "target": "valid", "type": "complete"}
        ]
        
        result = self.manager.batch_add_edges(self.conv_id, invalid_edges)
        self.assertIn("Error: Missing source, target, or type", result)

    def test_server_batch_operations(self):
        """Test server-level batch operations with verification"""
        conversation_id = "test_server_batch"
        
        # Test batch add nodes through manager (since server tools can't be called directly in tests)
        nodes_data = [
            {"id": "start", "label": "Start", "metadata": {"type": "start"}},
            {"id": "process", "label": "Process", "metadata": {"type": "process"}},
            {"id": "end", "label": "End", "metadata": {"type": "end"}}
        ]
        
        result = server.diagram_manager.batch_add_nodes(conversation_id, nodes_data)
        
        # Verify nodes were added
        self.assertIn("(id: start) added", result)
        self.assertIn("(id: process) added", result)
        self.assertIn("(id: end) added", result)
        
        # Verify nodes exist in manager
        conv_data = server.diagram_manager.conversations[conversation_id]
        self.assertEqual(len(conv_data["nodes"]), 3)
        self.assertIn("start", conv_data["nodes"])
        self.assertIn("process", conv_data["nodes"])
        self.assertIn("end", conv_data["nodes"])
        
        # Test batch add edges through manager
        edges_data = [
            {"source": "start", "target": "process", "type": "flows_to"},
            {"source": "process", "target": "end", "type": "completes_to"}
        ]
        
        result = server.diagram_manager.batch_add_edges(conversation_id, edges_data)
        
        # Verify edges were added
        self.assertIn("start -> process", result)
        self.assertIn("process -> end", result)
        self.assertEqual(len(conv_data["edges"]), 2)
        
        # Test rendering and verify structure
        render_result = server.diagram_manager.render(conversation_id)
        
        # Verify render contains expected elements
        self.assertIn("Start", render_result)
        self.assertIn("Process", render_result)
        self.assertIn("End", render_result)
        self.assertIn("### Diagram (Table Style)", render_result)
        
    def test_server_batch_update_operations(self):
        """Test server-level batch update operations with verification"""
        conversation_id = "test_server_update"
        
        # First add some nodes and edges
        server.diagram_manager.batch_add_nodes(conversation_id, [
            {"id": "node1", "label": "Original 1"},
            {"id": "node2", "label": "Original 2"}
        ])
        
        server.diagram_manager.batch_add_edges(conversation_id, [
            {"source": "node1", "target": "node2", "type": "original_type"}
        ])
        
        # Test batch update nodes
        update_result = server.diagram_manager.batch_update_nodes(conversation_id, [
            {"id": "node1", "label": "Updated 1", "metadata": {"updated": True}},
            {"id": "node2", "label": "Updated 2", "metadata": {"version": 2}}
        ])
        
        # Verify updates
        self.assertIn("node1", update_result)
        self.assertIn("node2", update_result)
        
        conv_data = server.diagram_manager.conversations[conversation_id]
        self.assertEqual(conv_data["nodes"]["node1"].label, "Updated 1")
        self.assertEqual(conv_data["nodes"]["node2"].label, "Updated 2")
        self.assertEqual(conv_data["nodes"]["node1"].metadata["updated"], True)
        self.assertEqual(conv_data["nodes"]["node2"].metadata["version"], 2)
        
        # Test batch update edges
        edge_update_result = server.diagram_manager.batch_update_edges(conversation_id, [
            {"index": 0, "type": "updated_type", "metadata": {"modified": True}}
        ])
        
        # Verify edge update
        self.assertIn("Edge at index 0 updated", edge_update_result)
        self.assertEqual(conv_data["edges"][0].type, "updated_type")
        self.assertEqual(conv_data["edges"][0].metadata["modified"], True)
        
    def test_server_mixed_batch_operations(self):
        """Test mixed batch operations through server with verification"""
        conversation_id = "test_mixed_batch"
        
        # Test mixed operations
        mixed_ops = [
            {"action": "add_node", "data": {"id": "root", "label": "Root Node"}},
            {"action": "add_node", "data": {"id": "child1", "label": "Child 1"}},
            {"action": "add_node", "data": {"id": "child2", "label": "Child 2"}},
            {"action": "add_edge", "data": {"source": "root", "target": "child1", "type": "parent_of"}},
            {"action": "add_edge", "data": {"source": "root", "target": "child2", "type": "parent_of"}},
            {"action": "update_node", "data": {"id": "root", "label": "Updated Root", "metadata": {"level": 0}}}
        ]
        
        result = server.diagram_manager.batch_operations(conversation_id, mixed_ops)
        
        # Verify all operations succeeded
        self.assertIn("(id: root) added", result)
        self.assertIn("(id: child1) added", result)
        self.assertIn("(id: child2) added", result)
        self.assertIn("parent_of", result)
        self.assertIn("'root' updated", result)
        
        # Verify final state
        conv_data = server.diagram_manager.conversations[conversation_id]
        self.assertEqual(len(conv_data["nodes"]), 3)
        self.assertEqual(len(conv_data["edges"]), 2)
        self.assertEqual(conv_data["nodes"]["root"].label, "Updated Root")
        self.assertEqual(conv_data["nodes"]["root"].metadata["level"], 0)
        
        # Test rendering of mixed operations result
        render_result = server.diagram_manager.render(conversation_id)
        
        # Verify render contains all elements
        self.assertIn("Updated Root", render_result)
        self.assertIn("Child 1", render_result)
        self.assertIn("Child 2", render_result)
        
    def test_server_error_handling(self):
        """Test server-level error handling for batch operations"""
        conversation_id = "test_server_errors"
        
        # Test invalid node data in batch
        result = server.diagram_manager.batch_add_nodes(conversation_id, [
            {"label": "Missing ID"}  # Missing required id field
        ])
        self.assertIn("Error: Missing id or label", result)
        
        # Test invalid edge data in batch
        result = server.diagram_manager.batch_add_edges(conversation_id, [
            {"source": "node1", "target": "node2"}  # Missing type field
        ])
        self.assertIn("Error: Missing source, target, or type", result)

if __name__ == "__main__":
    unittest.main()
