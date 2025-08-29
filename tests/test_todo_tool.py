import sys
import os
import unittest
import importlib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.todo_tool import (
    add_task, add_tasks_batch, update_task, delete_task,
    get_task, list_tasks, VALID_STATUSES,
    tasks_by_conversation, task_counters
)

class TestTodoTool(unittest.TestCase):
    def setUp(self):
        # Clear the global dictionaries before each test
        tasks_by_conversation.clear()
        task_counters.clear()
        self.conv_id = "test_conversation"
    
    def test_add_task(self):
        # Test adding a task with default status
        result = add_task(self.conv_id, "Test Task")
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        # Verify task was actually added to the conversation
        tasks = result["data"]
        self.assertEqual(len(tasks), 1)
        
        # Verify task properties
        task = tasks[0]
        self.assertEqual(task["id"], 1)
        self.assertEqual(task["title"], "Test Task")
        self.assertEqual(task["description"], "")  # Empty default description
        self.assertEqual(task["status"], "pending")  # Default status
        
        # Test adding a task with a specific status and description
        result = add_task(self.conv_id, "Another Task", "Task description", "in_progress")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        tasks = result["data"]
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[1]["title"], "Another Task")
        self.assertEqual(tasks[1]["status"], "in_progress")
        
        
        # Test adding a task with an invalid status
        result = add_task(self.conv_id, "Invalid Status", "", "invalid")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("Invalid status", result["error"])
        self.assertIn("invalid", result["error"])  # Should mention the invalid status
        
        # Verify no new task was added - list should still have 2 tasks
        tasks_result = list_tasks(self.conv_id)
        self.assertEqual(len(tasks_result["data"]), 2)  # Still only 2 tasks
    
    def test_add_tasks_batch(self):
        # Test adding multiple tasks at once
        tasks = [
            {"title": "Task 1", "description": "Description 1"},
            {"title": "Task 2", "description": "Description 2", "status": "in_progress"},
            {"title": "Task 3", "status": "completed"}
        ]
        result = add_tasks_batch(self.conv_id, tasks)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        # Check that all tasks were added correctly
        all_tasks = result["data"]
        self.assertEqual(len(all_tasks), 3)
        self.assertEqual(all_tasks[0]["title"], "Task 1")
        self.assertEqual(all_tasks[0]["status"], "pending")  # Default status
        self.assertEqual(all_tasks[1]["status"], "in_progress")
        self.assertEqual(all_tasks[2]["status"], "completed")
        
        # Test adding a batch with an invalid status
        invalid_tasks = [
            {"title": "Valid Task"},
            {"title": "Invalid Task", "status": "wrong_status"}
        ]
        result = add_tasks_batch(self.conv_id, invalid_tasks)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("invalid status", result["error"])
        
        # Check that no new tasks were added due to validation failure
        tasks_result = list_tasks(self.conv_id)
        self.assertEqual(len(tasks_result["data"]), 3)  # Still only 3 tasks from successful batch
    
    def test_update_task(self):
        # Add a task first
        add_task(self.conv_id, "Original Task", "Original description", "pending")
        
        # Test updating the title
        result = update_task(self.conv_id, 1, title="Updated Title")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        tasks = result["data"]
        task = tasks[0]  # Should be the only task
        self.assertEqual(task["title"], "Updated Title")
        self.assertEqual(task["description"], "Original description")  # Unchanged
        self.assertEqual(task["status"], "pending")  # Unchanged
        
        # Test updating the description
        result = update_task(self.conv_id, 1, description="New description")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        
        tasks = result["data"]
        task = tasks[0]
        self.assertEqual(task["description"], "New description")
        
        # Test updating the status
        result = update_task(self.conv_id, 1, status="completed")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        
        tasks = result["data"]
        task = tasks[0]
        self.assertEqual(task["status"], "completed")
        
        # Test updating multiple fields at once
        result = update_task(
            self.conv_id, 1, 
            title="Final Title", 
            description="Final description", 
            status="blocked"
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        
        tasks = result["data"]
        task = tasks[0]
        self.assertEqual(task["title"], "Final Title")
        self.assertEqual(task["description"], "Final description")
        self.assertEqual(task["status"], "blocked")
        
        # Test updating with an invalid status
        result = update_task(self.conv_id, 1, status="invalid")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("Invalid status", result["error"])
        
        # Test updating a non-existent task
        result = update_task(self.conv_id, 999, title="Nonexistent")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("Task 999 not found", result["error"])
    
    def test_delete_task(self):
        # Add a couple of tasks first
        add_task(self.conv_id, "Task 1")
        add_task(self.conv_id, "Task 2")
        result = list_tasks(self.conv_id)
        self.assertEqual(len(result["data"]), 2)
        
        # Test deleting a task
        result = delete_task(self.conv_id, 1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        tasks = result["data"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Task 2")
        
        # Test deleting a non-existent task (should return error)
        result = delete_task(self.conv_id, 999)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("Task 999 not found", result["error"])
    
    def test_get_task(self):
        # Add a task
        add_task(self.conv_id, "Get This Task", "Task description", "in_progress")
        
        # Test getting the task
        result = get_task(self.conv_id, 1)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        
        tasks = result["data"]
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["id"], 1)
        self.assertEqual(task["title"], "Get This Task")
        self.assertEqual(task["description"], "Task description")
        self.assertEqual(task["status"], "in_progress")
        
        # Test getting a non-existent task
        result = get_task(self.conv_id, 999)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], False)
        self.assertIn("error", result)
        self.assertIn("Task 999 not found", result["error"])
    
    def test_list_tasks(self):
        # Test with empty task list
        result = list_tasks(self.conv_id)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["data"], [])
        
        # Add some tasks
        add_task(self.conv_id, "Task 1")
        add_task(self.conv_id, "Task 2")
        add_task(self.conv_id, "Task 3")
        
        # Test listing all tasks
        result = list_tasks(self.conv_id)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        
        tasks = result["data"]
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["title"], "Task 1")
        self.assertEqual(tasks[1]["title"], "Task 2")
        self.assertEqual(tasks[2]["title"], "Task 3")
        
        # Test conversation isolation
        other_conv_id = "another_conversation"
        add_task(other_conv_id, "Other Task")
        
        current_result = list_tasks(self.conv_id)
        other_result = list_tasks(other_conv_id)
        
        self.assertEqual(len(current_result["data"]), 3)
        self.assertEqual(len(other_result["data"]), 1)

if __name__ == "__main__":
    unittest.main()
