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
        self.assertEqual(result["status"], "success")
        self.assertIn(f"Structure '{self.structure_id}' created", result["message"])
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
        self.assertEqual(result["status"], "success")
        self.assertIn("Structure 'custom_structure' created", result["message"])
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
        self.assertEqual(result["status"], "success")
        self.assertIn(f"Row added to '{self.structure_id}'", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][0],
            row_data
        )
        
        # Test adding another row
        row_data2 = {"Name": "Jane", "Age": 25}
        result2 = self.manager.add_row(self.conv_id, self.structure_id, row_data2)
        self.assertEqual(result2["status"], "success")
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][1],
            row_data2
        )
        
        # Test adding a row to non-existent structure
        result = self.manager.add_row(self.conv_id, "nonexistent", {"data": "value"})
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["message"])
    
    def test_update_row(self):
        # Create a structure and add rows
        self.manager.create_structure(self.conv_id, self.structure_id)
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "John", "Age": 30})
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "Jane", "Age": 25})
        
        # Test updating a row
        update_data = {"Age": 31}
        result = self.manager.update_row(self.conv_id, self.structure_id, 0, update_data)
        self.assertEqual(result["status"], "success")
        self.assertIn(f"Row 0 updated", result["message"])
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][0]["Age"],
            31
        )
        
        # Test updating a row with out-of-range index
        result = self.manager.update_row(self.conv_id, self.structure_id, 10, {"Name": "Invalid"})
        self.assertEqual(result["status"], "error")
        self.assertIn("out of range", result["message"])
        
        # Test updating a row in non-existent structure
        result = self.manager.update_row(self.conv_id, "nonexistent", 0, {"data": "value"})
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["message"])
    
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
        self.assertEqual(metrics["total_items"], 3)
        self.assertEqual(metrics["status_count"]["Completed"], 2)
        self.assertEqual(metrics["status_count"]["Pending"], 1)
        self.assertEqual(metrics["completion_rate"], "66.7%")
        
        # Test check_list metrics
        self.manager.create_structure(
            self.conv_id, 
            "checklist", 
            template_type="check_list"
        )
        self.manager.add_row(self.conv_id, "checklist", {"content": "Item 1", "checked": True})
        self.manager.add_row(self.conv_id, "checklist", {"content": "Item 2", "checked": False})
        
        metrics = self.manager.get_metrics(self.conv_id, "checklist")
        self.assertEqual(metrics["total_items"], 2)
        self.assertEqual(metrics["checked_items"], 1)
        self.assertEqual(metrics["checked_rate"], "50.0%")
        
        # Test voting_table metrics
        self.manager.create_structure(
            self.conv_id, 
            "votes", 
            template_type="voting_table"
        )
        self.manager.add_row(self.conv_id, "votes", {"Option": "Option A", "Votes": 5})
        self.manager.add_row(self.conv_id, "votes", {"Option": "Option B", "Votes": 3})
        
        metrics = self.manager.get_metrics(self.conv_id, "votes")
        self.assertEqual(metrics["total_votes"], 8)
        self.assertEqual(metrics["vote_distribution"]["Option A"], 5)
        self.assertEqual(metrics["vote_distribution"]["Option B"], 3)
        
        # Test metrics for non-existent structure
        result = self.manager.get_metrics(self.conv_id, "nonexistent")
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["message"])
    
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
        
        render_result = self.manager.render(self.conv_id, self.structure_id)
        
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
        
        render_result = self.manager.render(self.conv_id, "bullet_list")
        
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
        
        render_result = self.manager.render(self.conv_id, "check_list")
        
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
        
        render_result = self.manager.render(self.conv_id, "numbered_list")
        
        # Extract markdown section
        markdown_section = render_result.split('## Markdown\n')[1].split('\n\n')[0]
        markdown_lines = markdown_section.split('\n')
        
        # Verify correct numbered list format
        self.assertEqual(len(markdown_lines), 2)
        self.assertEqual(markdown_lines[0], "1. First item")
        self.assertEqual(markdown_lines[1], "2. Second item")
        
        # Test rendering non-existent structure
        result = self.manager.render(self.conv_id, "nonexistent")
        self.assertIn("does not exist", result)

    def test_batch_add_rows(self):
        """测试批量添加行功"""
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
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        # Check that all individual results are successful
        for i, result_item in enumerate(result["results"]):
            self.assertEqual(result_item["status"], "success")
            self.assertIn(f"Row {i} added", result_item["message"])
        
        # Verify rows are in the structure
        structure = self.manager.conversations[self.conv_id][self.structure_id]
        self.assertEqual(len(structure["rows"]), 3)
        self.assertEqual(structure["rows"][0]["Task"], "Task 1")
        self.assertEqual(structure["rows"][1]["Owner"], "Bob")
        self.assertEqual(structure["rows"][2]["Status"], "Completed")
        
        # Test with non-existent structure
        result = self.manager.batch_add_rows(self.conv_id, "nonexistent", rows_data)
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["message"])

    def test_batch_update_rows(self):
        """测试批量更新行功"""
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
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        # Check that all individual results are successful
        for i, result_item in enumerate(result["results"]):
            self.assertEqual(result_item["status"], "success")
            self.assertIn(f"Row {i} updated", result_item["message"])
        
        # Verify the updates
        structure = self.manager.conversations[self.conv_id][self.structure_id]
        self.assertEqual(structure["rows"][0]["Status"], "Completed")
        self.assertEqual(structure["rows"][1]["Status"], "In Progress")
        self.assertEqual(structure["rows"][2]["Status"], "Completed")
        self.assertEqual(structure["rows"][2]["Task"], "Updated Task 3")
        
        # Test with invalid index
        invalid_updates = [{"index": 10, "data": {"Status": "Invalid"}}]
        result = self.manager.batch_update_rows(self.conv_id, self.structure_id, invalid_updates)
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("out of range", result["results"][0]["message"])

    def test_batch_operations(self):
        """测试混合批量操作功能"""
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
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["successful_operations"], 4)
        self.assertEqual(result["failed_operations"], 0)
        # Check individual results
        add_results = [r for r in result["results"] if r["action"] == "add"]
        update_results = [r for r in result["results"] if r["action"] == "update"]
        self.assertEqual(len(add_results), 2)
        self.assertEqual(len(update_results), 2)
        for add_result in add_results:
            self.assertEqual(add_result["status"], "success")
            self.assertIn("Row added", add_result["message"])
        for update_result in update_results:
            self.assertEqual(update_result["status"], "success")
            self.assertIn("updated", update_result["message"])
        
        # Verify final state
        structure = self.manager.conversations[self.conv_id][self.structure_id]
        self.assertEqual(len(structure["rows"]), 3)  # 1 initial + 2 added
        self.assertEqual(structure["rows"][0]["Status"], "Inactive")  # Updated
        self.assertEqual(structure["rows"][1]["Quantity"], "10")  # Updated
        self.assertEqual(structure["rows"][2]["Item"], "New Item 2")  # Added
        
        # Test with invalid action
        invalid_ops = [{"action": "invalid", "data": {}}]
        result = self.manager.batch_operations(self.conv_id, self.structure_id, invalid_ops)
        self.assertEqual(result["status"], "success")  # Overall succeeds but with errors
        self.assertEqual(result["failed_operations"], 1)
        self.assertIn("Unknown action", result["results"][0]["message"])

    def test_server_batch_operations(self):
        """Test server-level batch operations with verification"""
        conversation_id = "test_server_batch"
        structure_id = "test_table"
        
        # Create structure through manager (since server tools can't be called directly in tests)
        result = cognitive_canvas_server.table_builder_manager.create_structure(
            conversation_id, structure_id, "simple_table", ["Name", "Status", "Priority"]
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("Structure 'test_table' created", result["message"])
        
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
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["results"]), 3)
        for i, result_item in enumerate(result["results"]):
            self.assertEqual(result_item["status"], "success")
            self.assertIn(f"Row {i} added", result_item["message"])
        
        # Verify structure exists and has correct data
        conv_data = cognitive_canvas_server.table_builder_manager.conversations[conversation_id]
        structure = conv_data[structure_id]
        self.assertEqual(len(structure["rows"]), 3)
        self.assertEqual(structure["rows"][0]["Name"], "Task 1")
        self.assertEqual(structure["rows"][1]["Status"], "Pending")
        self.assertEqual(structure["rows"][2]["Priority"], "Low")
        
        # Test rendering and verify content
        render_result = cognitive_canvas_server.table_builder_manager.render(
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
        self.assertEqual(metrics_result['total_items'], 3)
        
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
        self.assertEqual(update_result["status"], "success")
        self.assertEqual(len(update_result["results"]), 2)
        for i, result_item in enumerate(update_result["results"]):
            self.assertEqual(result_item["status"], "success")
            self.assertIn(f"Row {i} updated", result_item["message"])
        
        # Verify final state
        conv_data = cognitive_canvas_server.table_builder_manager.conversations[conversation_id]
        structure = conv_data[structure_id]
        self.assertEqual(structure["rows"][0]["Status"], "In Progress")
        self.assertEqual(structure["rows"][0]["Progress"], "25%")
        self.assertEqual(structure["rows"][1]["Status"], "Completed")
        self.assertEqual(structure["rows"][1]["Progress"], "100%")
        
        # Test rendering after updates
        render_result = cognitive_canvas_server.table_builder_manager.render(
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
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["message"])
        
        # Create structure for further tests
        cognitive_canvas_server.table_builder_manager.create_structure(
            conversation_id, structure_id, "simple_table"
        )
        
        # Test invalid update index
        result = cognitive_canvas_server.table_builder_manager.batch_update_rows(
            conversation_id, structure_id, [{"index": 999, "data": {"test": "value"}}]
        )
        self.assertEqual(result["status"], "success")  # Overall operation succeeds but with errors
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("out of range", result["results"][0]["message"])

if __name__ == "__main__":
    unittest.main()
