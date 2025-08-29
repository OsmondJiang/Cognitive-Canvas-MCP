import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.relationship_mapper import RelationshipMapper, Node, Edge
import cognitive_canvas_server

class TestRelationshipMapper(unittest.TestCase):
    def setUp(self):
        self.manager = RelationshipMapper()
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
        self.assertEqual(result["status"], "success")
        self.assertIn("Node 'Test Node' added", result["message"])
        self.assertIn(self.conv_id, self.manager.conversations)
        self.assertIn("nodes", self.manager.conversations[self.conv_id])
        self.assertIn("node1", self.manager.conversations[self.conv_id]["nodes"])
        
        # Test adding a node with metadata
        metadata = {"color": "blue"}
        result = self.manager.add_node(self.conv_id, "node2", "Test Node 2", metadata)
        self.assertEqual(result["status"], "success")
        self.assertIn("Node 'Test Node 2' added", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id]["nodes"]["node2"].metadata,
            metadata
        )
        
    def test_update_node(self):
        # Add a node first
        self.manager.add_node(self.conv_id, "node1", "Original Label")
        
        # Test updating label
        result = self.manager.update_node(self.conv_id, "node1", label="Updated Label")
        self.assertEqual(result["status"], "success")
        self.assertIn("Node 'node1' updated", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id]["nodes"]["node1"].label,
            "Updated Label"
        )
        
        # Test updating metadata
        metadata = {"color": "red"}
        result = self.manager.update_node(self.conv_id, "node1", metadata=metadata)
        self.assertEqual(result["status"], "success")
        self.assertIn("Node 'node1' updated", result["message"])
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
        self.assertEqual(result["status"], "success")
        self.assertIn("Node 'node1' updated", result["message"])
        node = self.manager.conversations[self.conv_id]["nodes"]["node1"]
        self.assertEqual(node.label, "Final Label")
        self.assertEqual(node.metadata, {"color": "red", "size": "large"})  # Metadata is merged
        
        # Test updating a non-existent node
        result = self.manager.update_node(self.conv_id, "nonexistent", label="Invalid")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])
        
    def test_add_edge(self):
        # Add nodes first
        self.manager.add_node(self.conv_id, "node1", "Node 1")
        self.manager.add_node(self.conv_id, "node2", "Node 2")
        
        # Test adding an edge
        result = self.manager.add_edge(self.conv_id, "node1", "node2", "connects_to")
        self.assertEqual(result["status"], "success")
        self.assertIn("Edge node1 -> node2 (connects_to) added", result["message"])
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
        self.assertEqual(result["status"], "success")
        self.assertIn("Edge node2 -> node1 (depends_on) added", result["message"])
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
        self.assertEqual(result["status"], "success")
        self.assertIn("Edge at index 0 updated", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id]["edges"][0].type,
            "updated_type"
        )
        
        # Test updating edge metadata
        metadata = {"weight": 10}
        result = self.manager.update_edge(self.conv_id, 0, metadata=metadata)
        self.assertEqual(result["status"], "success")
        self.assertIn("Edge at index 0 updated", result["message"])
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
        self.assertEqual(result["status"], "success")
        self.assertIn("Edge at index 0 updated", result["message"])
        edge = self.manager.conversations[self.conv_id]["edges"][0]
        self.assertEqual(edge.type, "final_type")
        # Metadata should be merged
        self.assertEqual(edge.metadata, {"weight": 10, "condition": "if x > 0"})
        
        # Test updating with an invalid index
        result = self.manager.update_edge(self.conv_id, 999, type="invalid")
        self.assertEqual(result["status"], "error")
        self.assertIn("Edge index out of range", result["message"])
        
    def test_set_visualization_type(self):
        # Test setting a valid Relationship Map type
        result = self.manager.set_visualization_type(self.conv_id, "mindmap")
        self.assertEqual(result["status"], "success")
        self.assertIn("Visualization type set to mindmap", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id]["visualization_type"],
            "mindmap"
        )
        
        # Test setting an invalid Relationship Map type
        result = self.manager.set_visualization_type(self.conv_id, "invalid_type")
        self.assertEqual(result["status"], "error")
        self.assertIn("Unknown visualization type", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id]["visualization_type"],
            "mindmap"  # Should remain unchanged
        )
        
    def test_render(self):
        # Create a simple Relationship Map
        self.manager.add_node(self.conv_id, "root", "Root Node")
        self.manager.add_node(self.conv_id, "child1", "Child 1")
        self.manager.add_node(self.conv_id, "child2", "Child 2")
        self.manager.add_edge(self.conv_id, "root", "child1", "contains")
        self.manager.add_edge(self.conv_id, "root", "child2", "contains")
        
        # Test rendering
        result = self.manager.render(self.conv_id)
        
        # Check that the result contains expected components
        self.assertIn("Relationship Map", result)
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
        if "### Relationship Map (Table Style)" in result:
            # Table style - verify table structure
            self.assertIn("| Node ID | Label | Level |", result)
            self.assertIn("| root | Root Node | 0 |", result)
        elif "### Relationship Map (Tree Style)" in result:
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
        
        # Test rendering a more complex Relationship Map
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
        
        # Test Relationship Map type change
        self.manager.set_visualization_type(self.conv_id, "mindmap")
        result = self.manager.render(self.conv_id)
        
        # Should still have the same content but mindmap should show tree style
        self.assertIn("### Relationship Map (Tree Style)", result)
        self.assertIn("Root Node", result)
        self.assertIn("Child 1", result)
        self.assertIn("Child 2", result)
        self.assertIn("Grandchild 1", result)
        
        # Test flowchart type shows table style
        self.manager.set_visualization_type(self.conv_id, "flowchart")
        result = self.manager.render(self.conv_id)
        self.assertIn("### Relationship Map (Table Style)", result)
        self.assertIn("Root Node", result)

    def test_batch_add_nodes(self):
        """Test batch adding nodes"""
        nodes = [
            {"id": "batch1", "label": "Batch Node 1", "metadata": {"type": "start"}},
            {"id": "batch2", "label": "Batch Node 2", "metadata": {"type": "process"}},
            {"id": "batch3", "label": "Batch Node 3", "metadata": {"type": "end"}}
        ]
        
        result = self.manager.batch_add_nodes(self.conv_id, nodes)
        
        # Check that the batch operation succeeded
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        # Check that all individual operations succeeded
        for i, result_item in enumerate(result["results"]):
            self.assertEqual(result_item["status"], "success")
            self.assertIn(f"Batch Node {i+1}", result_item["message"])
        
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
        
        # Check that the batch operation succeeded
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 2)
        # Check that all individual operations succeeded
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
            self.assertIn("added", result_item["message"])
        
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
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 2)
        # Check that all individual operations succeeded
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
            self.assertIn("updated", result_item["message"])
        
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
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 2)
        # Check that all individual operations succeeded
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
            self.assertIn("updated", result_item["message"])
        
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
        
        # Check that the batch operation succeeded
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["successful_operations"], 4)
        self.assertEqual(result["failed_operations"], 0)
        # Check individual results
        add_node_results = [r for r in result["results"] if r["action"] == "add_node"]
        add_edge_results = [r for r in result["results"] if r["action"] == "add_edge"]
        update_node_results = [r for r in result["results"] if r["action"] == "update_node"]
        self.assertEqual(len(add_node_results), 2)
        self.assertEqual(len(add_edge_results), 1)
        self.assertEqual(len(update_node_results), 1)
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
        
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
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(len(result["added_nodes"]), 1)
        # Check individual results
        error_result = [r for r in result["results"] if r["status"] == "error"][0]
        self.assertIn("Missing id or label", error_result["message"])
        success_result = [r for r in result["results"] if r["status"] == "success"][0]
        self.assertIn("Valid Node", success_result["message"])
        
        # Test batch update with non-existent node
        invalid_updates = [
            {"id": "nonexistent", "label": "This won't work"}
        ]
        
        result = self.manager.batch_update_nodes(self.conv_id, invalid_updates)
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Node nonexistent not found", result["errors"][0])
        
        # Test batch add edges with missing data
        invalid_edges = [
            {"source": "missing_target", "type": "incomplete"},  # Missing target
            {"source": "valid", "target": "valid", "type": "complete"}
        ]
        
        result = self.manager.batch_add_edges(self.conv_id, invalid_edges)
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        # Check that one operation failed due to missing data
        error_result = [r for r in result["results"] if r["status"] == "error"][0]
        self.assertIn("Missing", error_result["message"])

    def test_server_batch_operations(self):
        """Test server-level batch operations with verification"""
        conversation_id = "test_server_batch"
        
        # Test batch add nodes through manager (since server tools can't be called directly in tests)
        nodes_data = [
            {"id": "start", "label": "Start", "metadata": {"type": "start"}},
            {"id": "process", "label": "Process", "metadata": {"type": "process"}},
            {"id": "end", "label": "End", "metadata": {"type": "end"}}
        ]
        
        result = cognitive_canvas_server.relationship_mapper_manager.batch_add_nodes(conversation_id, nodes_data)
        
        # Verify nodes were added
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
            self.assertIn("added", result_item["message"])
        
        # Verify nodes exist in manager
        conv_data = cognitive_canvas_server.relationship_mapper_manager.conversations[conversation_id]
        self.assertEqual(len(conv_data["nodes"]), 3)
        self.assertIn("start", conv_data["nodes"])
        self.assertIn("process", conv_data["nodes"])
        self.assertIn("end", conv_data["nodes"])
        
        # Test batch add edges through manager
        edges_data = [
            {"source": "start", "target": "process", "type": "flows_to"},
            {"source": "process", "target": "end", "type": "completes_to"}
        ]
        
        result = cognitive_canvas_server.relationship_mapper_manager.batch_add_edges(conversation_id, edges_data)
        
        # Verify edges were added
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 2)
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
            self.assertIn("added", result_item["message"])
        self.assertEqual(len(conv_data["edges"]), 2)
        
        # Test rendering and verify structure
        render_result = cognitive_canvas_server.relationship_mapper_manager.render(conversation_id)
        
        # Verify render contains expected elements
        self.assertIn("Start", render_result)
        self.assertIn("Process", render_result)
        self.assertIn("End", render_result)
        self.assertIn("### Relationship Map (Table Style)", render_result)
        
    def test_server_batch_update_operations(self):
        """Test server-level batch update operations with verification"""
        conversation_id = "test_server_update"
        
        # First add some nodes and edges
        cognitive_canvas_server.relationship_mapper_manager.batch_add_nodes(conversation_id, [
            {"id": "node1", "label": "Original 1"},
            {"id": "node2", "label": "Original 2"}
        ])
        
        cognitive_canvas_server.relationship_mapper_manager.batch_add_edges(conversation_id, [
            {"source": "node1", "target": "node2", "type": "original_type"}
        ])
        
        # Test batch update nodes
        update_result = cognitive_canvas_server.relationship_mapper_manager.batch_update_nodes(conversation_id, [
            {"id": "node1", "label": "Updated 1", "metadata": {"updated": True}},
            {"id": "node2", "label": "Updated 2", "metadata": {"version": 2}}
        ])
        
        # Verify updates
        self.assertEqual(update_result["status"], "success")
        self.assertEqual(len(update_result["results"]), 2)
        for result_item in update_result["results"]:
            self.assertEqual(result_item["status"], "success")
            self.assertIn("updated", result_item["message"])
        
        conv_data = cognitive_canvas_server.relationship_mapper_manager.conversations[conversation_id]
        self.assertEqual(conv_data["nodes"]["node1"].label, "Updated 1")
        self.assertEqual(conv_data["nodes"]["node2"].label, "Updated 2")
        self.assertEqual(conv_data["nodes"]["node1"].metadata["updated"], True)
        self.assertEqual(conv_data["nodes"]["node2"].metadata["version"], 2)
        
        # Test batch update edges
        edge_update_result = cognitive_canvas_server.relationship_mapper_manager.batch_update_edges(conversation_id, [
            {"index": 0, "type": "updated_type", "metadata": {"modified": True}}
        ])
        
        # Verify edge update
        self.assertEqual(edge_update_result["status"], "success")
        self.assertEqual(len(edge_update_result["results"]), 1)
        self.assertEqual(edge_update_result["results"][0]["status"], "success")
        self.assertIn("Edge at index 0 updated", edge_update_result["results"][0]["message"])
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
        
        result = cognitive_canvas_server.relationship_mapper_manager.batch_operations(conversation_id, mixed_ops)
        
        # Verify all operations succeeded
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["successful_operations"], 6)
        self.assertEqual(result["failed_operations"], 0)
        # Check individual results
        for result_item in result["results"]:
            self.assertEqual(result_item["status"], "success")
        
        # Verify final state
        conv_data = cognitive_canvas_server.relationship_mapper_manager.conversations[conversation_id]
        self.assertEqual(len(conv_data["nodes"]), 3)
        self.assertEqual(len(conv_data["edges"]), 2)
        self.assertEqual(conv_data["nodes"]["root"].label, "Updated Root")
        self.assertEqual(conv_data["nodes"]["root"].metadata["level"], 0)
        
        # Test rendering of mixed operations result
        render_result = cognitive_canvas_server.relationship_mapper_manager.render(conversation_id)
        
        # Verify render contains all elements
        self.assertIn("Updated Root", render_result)
        self.assertIn("Child 1", render_result)
        self.assertIn("Child 2", render_result)
        
    def test_server_error_handling(self):
        """Test server-level error handling for batch operations"""
        conversation_id = "test_server_errors"
        
        # Test invalid node data in batch
        result = cognitive_canvas_server.relationship_mapper_manager.batch_add_nodes(conversation_id, [
            {"label": "Missing ID"}  # Missing required id field
        ])
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Missing id or label", result["errors"][0])
        
        # Test invalid edge data in batch
        result = cognitive_canvas_server.relationship_mapper_manager.batch_add_edges(conversation_id, [
            {"source": "node1", "target": "node2"}  # Missing type field
        ])
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        # The actual error message should be about missing type
        self.assertTrue(any("type" in error.lower() for error in result["errors"]))

if __name__ == "__main__":
    unittest.main()
