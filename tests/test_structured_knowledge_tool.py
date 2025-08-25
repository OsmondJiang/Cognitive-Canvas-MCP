import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.structured_knowledge_tool import StructuredKnowledgeManager

class TestStructuredKnowledgeManager(unittest.TestCase):
    def setUp(self):
        self.manager = StructuredKnowledgeManager()
        self.conv_id = "test_conversation"
        self.structure_id = "test_structure"
    
    def test_create_structure(self):
        # Test creating a structure with default template
        result = self.manager.create_structure(self.conv_id, self.structure_id)
        self.assertIn(f"Structure '{self.structure_id}' created", result)
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
        self.assertIn("Structure 'custom_structure' created", result)
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
        self.assertIn(f"Row added to '{self.structure_id}'", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][0],
            row_data
        )
        
        # Test adding another row
        row_data2 = {"Name": "Jane", "Age": 25}
        self.manager.add_row(self.conv_id, self.structure_id, row_data2)
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][1],
            row_data2
        )
        
        # Test adding a row to non-existent structure
        result = self.manager.add_row(self.conv_id, "nonexistent", {"data": "value"})
        self.assertIn("does not exist", result)
    
    def test_update_row(self):
        # Create a structure and add rows
        self.manager.create_structure(self.conv_id, self.structure_id)
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "John", "Age": 30})
        self.manager.add_row(self.conv_id, self.structure_id, {"Name": "Jane", "Age": 25})
        
        # Test updating a row
        update_data = {"Age": 31}
        result = self.manager.update_row(self.conv_id, self.structure_id, 0, update_data)
        self.assertIn(f"Row 0 updated", result)
        self.assertEqual(
            self.manager.conversations[self.conv_id][self.structure_id]["rows"][0]["Age"],
            31
        )
        
        # Test updating a row with out-of-range index
        result = self.manager.update_row(self.conv_id, self.structure_id, 10, {"Name": "Invalid"})
        self.assertIn("out of range", result)
        
        # Test updating a row in non-existent structure
        result = self.manager.update_row(self.conv_id, "nonexistent", 0, {"data": "value"})
        self.assertIn("does not exist", result)
    
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
        self.assertIn("does not exist", result)
    
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
        self.assertIn("## JSON", render_result)
        
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
        
        # Verify JSON format
        import json
        json_section = render_result.split('## JSON\n')[1].strip()
        data = json.loads(json_section)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["Name"], "John")
        self.assertEqual(data[0]["Age"], 30)
        self.assertEqual(data[1]["Name"], "Jane")
        self.assertEqual(data[1]["Age"], 25)
        
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
        
        # Verify JSON content
        json_section = render_result.split('## JSON\n')[1].strip()
        data = json.loads(json_section)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["content"], "Item 1")
        self.assertEqual(data[1]["content"], "Item 2")
        
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
        
        # Verify JSON format includes checked status
        json_section = render_result.split('## JSON\n')[1].strip()
        data = json.loads(json_section)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["content"], "Item 1")
        self.assertTrue(data[0]["checked"])
        self.assertEqual(data[1]["content"], "Item 2")
        self.assertFalse(data[1]["checked"])
        
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

if __name__ == "__main__":
    unittest.main()
