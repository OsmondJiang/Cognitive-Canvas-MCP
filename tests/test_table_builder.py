import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.table_builder import TableBuilder
import cognitive_canvas_server

class TestTableBuilder(unittest.TestCase):
    def setUp(self):
        self.manager = TableBuilder()
        self.conv_id = "test_conversation"
        self.structure_id = "test_structure"
    
    def test_create_structure(self):
        # Test creating a structure with default template
        result = self.manager.create_structure(self.conv_id, self.structure_id)
        self.assertEqual(result["success"], True)
        self.assertIn(self.conv_id, self.manager.conversations)
        self.assertIn(self.structure_id, self.manager.conversations[self.conv_id])
        
        # Test creating a structure with custom template and columns
        columns = ["Name", "Age", "Role"]
        result = self.manager.create_structure(
            self.conv_id, 
            "custom_structure", 
            template_type="task_list", 
            columns=columns
        )
        self.assertEqual(result["success"], True)
        self.assertEqual(
            self.manager.conversations[self.conv_id]["custom_structure"]["template_type"],
            "task_list"
        )
        self.assertEqual(
            self.manager.conversations[self.conv_id]["custom_structure"]["columns"],
            columns
        )
    
    def test_add_row(self):
        # Create a structure first
        self.manager.create_structure(
            self.conv_id, 
            self.structure_id, 
            template_type="simple_table", 
            columns=["Name", "Age"]
        )
        
        # Test adding a row
        row_data = {"Name": "John", "Age": 30}
        result = self.manager.add_row(self.conv_id, self.structure_id, row_data)
        self.assertEqual(result["success"], True)
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][0],
            row_data
        )
        
        # Test adding another row
        row_data2 = {"Name": "Jane", "Age": 25}
        result2 = self.manager.add_row(self.conv_id, self.structure_id, row_data2)
        self.assertEqual(result2["success"], True)
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][1],
            row_data2
        )
        
        # Test adding a row to non-existent structure
        result = self.manager.add_row(self.conv_id, "nonexistent", {"data": "value"})
        self.assertEqual(result["success"], False)
        self.assertIn("does not exist", result["error"])
    
    def test_update_row(self):
        # Create a structure and add rows
        self.manager.create_structure(self.conv_id, self.structure_id)
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "John", "Age": 30})
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "Jane", "Age": 25})
        
        # Test updating a row
        update_data = {"Age": 31}
        result = self.manager.update_row(self.conv_id, self.structure_id, 0, update_data)
        self.assertEqual(result["success"], True)
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][0]["Age"],
            31
        )
        
        # Test updating a row with out-of-range index
        result = self.manager.update_row(self.conv_id, self.structure_id, 10, {"Name": "Invalid"})
        self.assertEqual(result["success"], False)
        self.assertIn("out of range", result["error"])
        
        # Test updating a row in non-existent structure
        result = self.manager.update_row(self.conv_id, "nonexistent", 0, {"data": "value"})
        self.assertEqual(result["success"], False)
        self.assertIn("does not exist", result["error"])
    
    def test_get_metrics(self):
        # Test task_list metrics
        self.manager.create_structure(
            self.conv_id, 
            "tasks", 
            template_type="task_list",
            columns=["Task", "Status"]
        )
        self.manager.add_row(self.conv_id, "tasks", {"Task": "Task 1", "Status": "Completed"})
        self.manager.add_row(self.conv_id, "tasks", {"Task": "Task 2", "Status": "Pending"})
        self.manager.add_row(self.conv_id, "tasks", {"Task": "Task 3", "Status": "Completed"})
        
        metrics = self.manager.get_metrics(self.conv_id, "tasks")
        self.assertEqual(metrics["success"], True)
        metrics_data = metrics["data"]
        self.assertEqual(metrics_data["total_items"], 3)
        self.assertEqual(metrics_data["status_count"]["Completed"], 2)
        self.assertEqual(metrics_data["status_count"]["Pending"], 1)
        self.assertEqual(metrics_data["completion_rate"], "66.7%")
        
        # Test check_list metrics
        self.manager.create_structure(
            self.conv_id, 
            "checklist", 
            template_type="check_list"
        )
        self.manager.add_row(self.conv_id, "checklist", {"content": "Item 1", "checked": True})
        self.manager.add_row(self.conv_id, "checklist", {"content": "Item 2", "checked": False})
        
        metrics = self.manager.get_metrics(self.conv_id, "checklist")
        self.assertEqual(metrics["success"], True)
        metrics_data = metrics["data"]
        self.assertEqual(metrics_data["total_items"], 2)
        self.assertEqual(metrics_data["checked_items"], 1)
        self.assertEqual(metrics_data["checked_rate"], "50.0%")
        
        # Test voting_table metrics
        self.manager.create_structure(
            self.conv_id, 
            "votes", 
            template_type="voting_table"
        )
        self.manager.add_row(self.conv_id, "votes", {"Option": "Option A", "Votes": 5})
        self.manager.add_row(self.conv_id, "votes", {"Option": "Option B", "Votes": 3})
        
        metrics = self.manager.get_metrics(self.conv_id, "votes")
        self.assertEqual(metrics["success"], True)
        metrics_data = metrics["data"]
        self.assertEqual(metrics_data["total_votes"], 8)
        self.assertEqual(metrics_data["vote_distribution"]["Option A"], 5)
        self.assertEqual(metrics_data["vote_distribution"]["Option B"], 3)
        
        # Test metrics for non-existent structure
        result = self.manager.get_metrics(self.conv_id, "nonexistent")
        self.assertEqual(result["success"], False)
        self.assertIn("does not exist", result["error"])
    
    def test_render(self):
        # Test rendering a simple table
        self.manager.create_structure(
            self.conv_id, 
            self.structure_id,
            template_type="simple_table",
            columns=["Name", "Age"]
        )
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "John", "Age": 30})
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "Jane", "Age": 25})
        
        render_result = self.manager.get_formatted_table(self.conv_id, self.structure_id)
        
        # Verify structure of the result
        self.assertIn(f"Structure '{self.structure_id}' (simple_table) with 2 items", render_result)
        self.assertIn("## Markdown", render_result)
        
        # Verify table formatting is correct
        markdown_lines = [line for line in render_result.split('\n') if '|' in line]
        self.assertEqual(len(markdown_lines), 4)  # Header, separator, and 2 data rows
        
        # Verify header format
        self.assertRegex(markdown_lines[0], r'\|\s*Name\s*\|\s*Age\s*\|')
        
        # Verify separator line has correct format
        self.assertRegex(markdown_lines[1], r'\|-+\|-+\|')
        
        # Verify data rows
        self.assertRegex(markdown_lines[2], r'\|\s*John\s*\|\s*30\s*\|')
        self.assertRegex(markdown_lines[3], r'\|\s*Jane\s*\|\s*25\s*\|')
        
        # Test rendering a bulleted list
        self.manager.create_structure(
            self.conv_id, 
            "bullet_list",
            template_type="bulleted_list"
        )
        self.manager.add_row(self.conv_id, "bullet_list", {"content": "Item 1"})
        self.manager.add_row(self.conv_id, "bullet_list", {"content": "Item 2"})
        
        render_result = self.manager.get_formatted_table(self.conv_id, "bullet_list")
        
        # Verify structure and content
        self.assertIn("Structure 'bullet_list' (bulleted_list) with 2 items", render_result)
        
        # Extract markdown section
        markdown_section = render_result.split('## Markdown\n')[1].split('\n\n')[0]
        markdown_lines = markdown_section.split('\n')
        
        # Verify correct bulleted list format
        self.assertEqual(len(markdown_lines), 2)
        self.assertEqual(markdown_lines[0], "- Item 1")
        self.assertEqual(markdown_lines[1], "- Item 2")
        
        # Test rendering a check list
        self.manager.create_structure(
            self.conv_id, 
            "check_list",
            template_type="check_list"
        )
        self.manager.add_row(self.conv_id, "check_list", {"content": "Item 1", "checked": True})
        self.manager.add_row(self.conv_id, "check_list", {"content": "Item 2", "checked": False})
        
        render_result = self.manager.get_formatted_table(self.conv_id, "check_list")
        
        # Verify structure and content
        self.assertIn("Structure 'check_list' (check_list) with 2 items", render_result)
        
        # Extract markdown section
        markdown_section = render_result.split('## Markdown\n')[1].split('\n\n')[0]
        markdown_lines = markdown_section.split('\n')
        
        # Verify correct checkbox format
        self.assertEqual(len(markdown_lines), 2)
        self.assertEqual(markdown_lines[0], "[x] Item 1")
        self.assertEqual(markdown_lines[1], "[ ] Item 2")
        
        # Verify check list format
        self.assertEqual(len(markdown_lines), 2)
        self.assertEqual(markdown_lines[0], "[x] Item 1")
        self.assertEqual(markdown_lines[1], "[ ] Item 2")
        
        # Test rendering a numbered list
        self.manager.create_structure(
            self.conv_id, 
            "numbered_list",
            template_type="numbered_list"
        )
        self.manager.add_row(self.conv_id, "numbered_list", {"content": "First item"})
        self.manager.add_row(self.conv_id, "numbered_list", {"content": "Second item"})
        
        render_result = self.manager.get_formatted_table(self.conv_id, "numbered_list")
        
        # Extract markdown section
        markdown_section = render_result.split('## Markdown\n')[1].split('\n\n')[0]
        markdown_lines = markdown_section.split('\n')
        
        # Verify correct numbered list format
        self.assertEqual(len(markdown_lines), 2)
        self.assertEqual(markdown_lines[0], "1. First item")
        self.assertEqual(markdown_lines[1], "2. Second item")
        
        # Test rendering non-existent structure
        result = self.manager.get_formatted_table(self.conv_id, "nonexistent")
        self.assertIn("does not exist", result)

    def test_batch_add_rows(self):
        """Test batch add rows functionality"""
        # Create a structure first
        self.manager.create_structure(
            self.conv_id, 
            self.structure_id, 
            template_type="task_list", 
            columns=["Task", "Owner", "Status"]
        )
        
        # Test batch adding rows
        rows_data = [
            {"Task": "Task 1", "Owner": "Alice", "Status": "Pending"},
            {"Task": "Task 2", "Owner": "Bob", "Status": "In Progress"},
            {"Task": "Task 3", "Owner": "Charlie", "Status": "Completed"}
        ]
        
        result = self.manager.batch_add_rows(self.conv_id, self.structure_id, rows_data)
        
        # Verify all rows were added
        self.assertEqual(result["success"], True)
        self.assertEqual(len(result["data"]["rows"]), 3)
        
        # Verify rows are in the structure
        structure = self.manager.conversations[self.conv_id][self.structure_id]
        self.assertEqual(len(structure["rows"]), 3)
        self.assertEqual(structure["rows"][0]["Task"], "Task 1")
        self.assertEqual(structure["rows"][1]["Owner"], "Bob")
        self.assertEqual(structure["rows"][2]["Status"], "Completed")
        
        # Test with non-existent structure
        result = self.manager.batch_add_rows(self.conv_id, "nonexistent", rows_data)
        self.assertEqual(result["success"], False)
        self.assertIn("does not exist", result["error"])

    def test_batch_update_rows(self):
        """Test batch update rows functionality"""
        # Create structure and add initial rows
        self.manager.create_structure(
            self.conv_id, 
            self.structure_id, 
            template_type="task_list", 
            columns=["Task", "Status"]
        )
        
        initial_rows = [
            {"Task": "Task 1", "Status": "Pending"},
            {"Task": "Task 2", "Status": "Pending"},
            {"Task": "Task 3", "Status": "Pending"}
        ]
        self.manager.batch_add_rows(self.conv_id, self.structure_id, initial_rows)
        
        # Test batch updating rows
        updates_data = [
            {"index": 0, "data": {"Status": "Completed"}},
            {"index": 1, "data": {"Status": "In Progress"}},
            {"index": 2, "data": {"Status": "Completed", "Task": "Updated Task 3"}}
        ]
        
        result = self.manager.batch_update_rows(self.conv_id, self.structure_id, updates_data)
        
        # Verify all updates were applied
        self.assertEqual(result["success"], True)
        self.assertEqual(len(result["data"]["rows"]), 3)
        
        # Verify the updates
        structure = self.manager.conversations[self.conv_id][self.structure_id]
        self.assertEqual(structure["rows"][0]["Status"], "Completed")
        self.assertEqual(structure["rows"][1]["Status"], "In Progress")
        self.assertEqual(structure["rows"][2]["Status"], "Completed")
        self.assertEqual(structure["rows"][2]["Task"], "Updated Task 3")
        
        # Test with invalid index
        invalid_updates = [{"index": 10, "data": {"Status": "Invalid"}}]
        result = self.manager.batch_update_rows(self.conv_id, self.structure_id, invalid_updates)
        self.assertEqual(result["success"], False)  # Should fail validation
        self.assertIn("error", result)
        self.assertIn("out of range", result["error"])

    def test_batch_operations(self):
        """Test mixed batch operations functionality"""
        # Create structure
        self.manager.create_structure(
            self.conv_id, 
            self.structure_id, 
            template_type="simple_table", 
            columns=["Item", "Quantity", "Status"]
        )
        
        # Add initial row
        self.manager.batch_add_rows(self.conv_id, self.structure_id, [
            {"Item": "Initial Item", "Quantity": "1", "Status": "Active"}
        ])
        
        # Test mixed batch operations
        mixed_ops = [
            {"action": "add", "data": {"Item": "New Item 1", "Quantity": "5", "Status": "Pending"}},
            {"action": "add", "data": {"Item": "New Item 2", "Quantity": "3", "Status": "Active"}},
            {"action": "update", "data": {"index": 0, "row_data": {"Status": "Inactive"}}},
            {"action": "update", "data": {"index": 1, "row_data": {"Quantity": "10"}}}
        ]
        
        result = self.manager.batch_operations(self.conv_id, self.structure_id, mixed_ops)
        
        # Verify operations
        self.assertEqual(result["success"], True)
        
        # Verify final state
        structure = self.manager.conversations[self.conv_id][self.structure_id]
        self.assertEqual(len(structure["rows"]), 3)  # 1 initial + 2 added
        self.assertEqual(structure["rows"][0]["Status"], "Inactive")  # Updated
        self.assertEqual(structure["rows"][1]["Quantity"], "10")  # Updated
        self.assertEqual(structure["rows"][2]["Item"], "New Item 2")  # Added
        
        # Test with invalid action
        invalid_ops = [{"action": "invalid", "data": {}}]
        result = self.manager.batch_operations(self.conv_id, self.structure_id, invalid_ops)
        self.assertEqual(result["success"], False)  # Should fail validation
        self.assertIn("error", result)
        self.assertIn("unknown action", result["error"])

    def test_server_batch_operations(self):
        """Test server-level batch operations with verification"""
        conversation_id = "test_server_batch"
        structure_id = "test_table"
        
        # Create structure through manager (since server tools can't be called directly in tests)
        result = cognitive_canvas_server.table_builder_manager.create_structure(
            conversation_id, structure_id, "simple_table", ["Name", "Status", "Priority"]
        )
        self.assertEqual(result["success"], True)
        
        # Test batch add rows through manager
        rows_data = [
            {"Name": "Task 1", "Status": "Active", "Priority": "High"},
            {"Name": "Task 2", "Status": "Pending", "Priority": "Medium"},
            {"Name": "Task 3", "Status": "Completed", "Priority": "Low"}
        ]
        
        result = cognitive_canvas_server.table_builder_manager.batch_add_rows(
            conversation_id, structure_id, rows_data
        )
        
        # Verify rows were added
        self.assertEqual(result["success"], True)
        self.assertEqual(len(result["data"]["rows"]), 3)
        
        # Verify structure exists and has correct data
        conv_data = cognitive_canvas_server.table_builder_manager.conversations[conversation_id]
        structure = conv_data[structure_id]
        self.assertEqual(len(structure["rows"]), 3)
        self.assertEqual(structure["rows"][0]["Name"], "Task 1")
        self.assertEqual(structure["rows"][1]["Status"], "Pending")
        self.assertEqual(structure["rows"][2]["Priority"], "Low")
        
        # Test rendering and verify content
        render_result = cognitive_canvas_server.table_builder_manager.get_formatted_table(
            conversation_id, structure_id
        )
        
        # Verify render contains expected elements
        self.assertIn("Task 1", render_result)
        self.assertIn("Task 2", render_result)
        self.assertIn("Task 3", render_result)
        self.assertIn("Active", render_result)
        self.assertIn("High", render_result)
        
        # Test metrics
        metrics_result = cognitive_canvas_server.table_builder_manager.get_metrics(
            conversation_id, structure_id
        )
        
        # Verify metrics
        self.assertEqual(metrics_result["data"]["total_items"], 3)
        
    def test_server_batch_update_operations(self):
        """Test server-level batch update operations with verification"""
        conversation_id = "test_server_update"
        structure_id = "update_table"
        
        # Setup: create structure and add initial rows
        cognitive_canvas_server.table_builder_manager.create_structure(
            conversation_id, structure_id, "task_list", ["Task", "Status", "Progress"]
        )
        
        cognitive_canvas_server.table_builder_manager.batch_add_rows(
            conversation_id, structure_id, [
                {"Task": "Original Task 1", "Status": "To Do", "Progress": "0%"},
                {"Task": "Original Task 2", "Status": "In Progress", "Progress": "50%"}
            ]
        )
        
        # Test batch update rows
        updates_data = [
            {"index": 0, "data": {"Status": "In Progress", "Progress": "25%"}},
            {"index": 1, "data": {"Status": "Completed", "Progress": "100%"}}
        ]
        
        update_result = cognitive_canvas_server.table_builder_manager.batch_update_rows(
            conversation_id, structure_id, updates_data
        )
        
        # Verify updates
        self.assertEqual(update_result["success"], True)
        
        # Verify final state
        conv_data = cognitive_canvas_server.table_builder_manager.conversations[conversation_id]
        structure = conv_data[structure_id]
        self.assertEqual(structure["rows"][0]["Status"], "In Progress")
        self.assertEqual(structure["rows"][0]["Progress"], "25%")
        self.assertEqual(structure["rows"][1]["Status"], "Completed")
        self.assertEqual(structure["rows"][1]["Progress"], "100%")
        
        # Test rendering after updates
        render_result = cognitive_canvas_server.table_builder_manager.get_formatted_table(
            conversation_id, structure_id
        )
        
        # Verify updated content in render
        self.assertIn("25%", render_result)
        self.assertIn("100%", render_result)
        self.assertIn("Completed", render_result)
        
    def test_server_error_handling(self):
        """Test server-level error handling for batch operations"""
        conversation_id = "test_server_errors"
        structure_id = "error_table"
        
        # Test batch operations on non-existent structure
        result = cognitive_canvas_server.table_builder_manager.batch_add_rows(
            conversation_id, "nonexistent", [{"test": "data"}]
        )
        self.assertEqual(result["success"], False)
        self.assertIn("does not exist", result["error"])
        
        # Create structure for further tests
        cognitive_canvas_server.table_builder_manager.create_structure(
            conversation_id, structure_id, "simple_table"
        )
        
        # Test invalid update index
        result = cognitive_canvas_server.table_builder_manager.batch_update_rows(
            conversation_id, structure_id, [{"index": 999, "data": {"test": "value"}}]
        )
        self.assertEqual(result["success"], False)  # Should fail validation
        self.assertIn("error", result)
        self.assertIn("out of range", result["error"])

if __name__ == "__main__":
    unittest.main()
