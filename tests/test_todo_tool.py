import sys
import os
import unittest
import importlib

# Add parent directory to path at the beginning
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from tools.todo_tool import (
    add_task, add_tasks_batch, update_task, delete_task,
    get_task, list_tasks, list_workspaces, list_all_tasks, VALID_STATUSES,
    tasks_by_workspace, task_counters_by_workspace, workspaces_metadata
)

class TestTodoTool(unittest.TestCase):
    def setUp(self):
        # Clear the global dictionaries before each test
        tasks_by_workspace.clear()
        task_counters_by_workspace.clear()
        workspaces_metadata.clear()
        self.conv_id = "test_conversation"
    
    def test_add_task(self):
        # Test adding a task with default status to default workspace
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
        
        # Test adding a task to a specific workspace (auto-creates workspace)
        result = add_task(self.conv_id, "Workspace Task", "Test workspace", "pending", "test_workspace")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["success"], True)
        self.assertEqual(result["workspace_id"], "test_workspace")
        
        # Verify workspace was auto-created
        workspaces = list_workspaces(self.conv_id)
        self.assertEqual(len(workspaces["data"]), 2)  # default + test_workspace
        
        
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


class TestTodoWorkspaceFeatures(unittest.TestCase):
    """Test cases for workspace functionality"""
    
    def setUp(self):
        # Clear the global dictionaries before each test
        tasks_by_workspace.clear()
        task_counters_by_workspace.clear()
        workspaces_metadata.clear()
        self.conv_id = "test_workspace_conversation"
    
    def test_auto_create_workspace(self):
        """Test that workspaces are automatically created when adding tasks"""
        # Add tasks to a non-existent workspace
        result = add_tasks_batch(self.conv_id, [
            {"title": "Task 1", "description": "First task", "status": "pending"},
            {"title": "Task 2", "description": "Second task", "status": "in_progress"}
        ], "backend_dev")
        
        # Verify success
        self.assertTrue(result["success"])
        self.assertEqual(result["workspace_id"], "backend_dev")
        self.assertEqual(len(result["data"]), 2)
        
        # Verify workspace was auto-created
        workspaces = list_workspaces(self.conv_id)
        self.assertTrue(workspaces["success"])
        self.assertEqual(len(workspaces["data"]), 1)
        
        # Verify workspace metadata
        workspace = workspaces["data"][0]
        self.assertEqual(workspace["workspace_id"], "backend_dev")
        self.assertEqual(workspace["workspace_name"], "Backend Dev")
        self.assertEqual(workspace["task_count"], 2)
        self.assertEqual(workspace["created_at"], "auto-created")
    
    def test_workspace_naming_convention(self):
        """Test that workspace names are auto-generated correctly"""
        test_cases = [
            ("backend_dev", "Backend Dev"),
            ("frontend_team", "Frontend Team"),
            ("api_design", "Api Design"),
            ("user_auth_system", "User Auth System"),
            ("mobile_app", "Mobile App"),
            ("default", "Default Workspace")
        ]
        
        for workspace_id, expected_name in test_cases:
            # Add task to auto-create workspace
            add_tasks_batch(self.conv_id, [{"title": f"Test task for {workspace_id}"}], workspace_id)
            
            # Check workspace name
            workspaces = list_workspaces(self.conv_id)
            workspace = next(ws for ws in workspaces["data"] if ws["workspace_id"] == workspace_id)
            self.assertEqual(workspace["workspace_name"], expected_name)
    
    def test_workspace_isolation(self):
        """Test that workspaces maintain independent task lists and counters"""
        # Add tasks to different workspaces
        add_tasks_batch(self.conv_id, [{"title": "Backend Task 1"}], "backend")
        add_tasks_batch(self.conv_id, [{"title": "Frontend Task 1"}], "frontend")
        add_tasks_batch(self.conv_id, [{"title": "Backend Task 2"}], "backend")
        
        # Verify task IDs are independent
        backend_tasks = list_tasks(self.conv_id, "backend")
        frontend_tasks = list_tasks(self.conv_id, "frontend")
        
        self.assertEqual(len(backend_tasks["data"]), 2)
        self.assertEqual(len(frontend_tasks["data"]), 1)
        
        # Both workspaces should have task with ID 1
        self.assertEqual(backend_tasks["data"][0]["id"], 1)
        self.assertEqual(frontend_tasks["data"][0]["id"], 1)
        
        # But different titles
        self.assertEqual(backend_tasks["data"][0]["title"], "Backend Task 1")
        self.assertEqual(frontend_tasks["data"][0]["title"], "Frontend Task 1")
    
    def test_workspace_task_operations(self):
        """Test CRUD operations on tasks within workspaces"""
        # Create tasks in different workspaces
        add_tasks_batch(self.conv_id, [
            {"title": "Task 1", "status": "pending"},
            {"title": "Task 2", "status": "in_progress"}
        ], "test_workspace")
        
        # Update task in workspace
        update_result = update_task(self.conv_id, 1, status="completed", workspace_id="test_workspace")
        self.assertTrue(update_result["success"])
        self.assertEqual(update_result["workspace_id"], "test_workspace")
        
        # Get task from workspace
        get_result = get_task(self.conv_id, 1, workspace_id="test_workspace")
        self.assertTrue(get_result["success"])
        self.assertEqual(get_result["data"][0]["status"], "completed")
        self.assertEqual(get_result["workspace_id"], "test_workspace")
        
        # Delete task from workspace
        delete_result = delete_task(self.conv_id, 2, workspace_id="test_workspace")
        self.assertTrue(delete_result["success"])
        self.assertEqual(delete_result["workspace_id"], "test_workspace")
        
        # Verify only one task remains
        remaining_tasks = list_tasks(self.conv_id, "test_workspace")
        self.assertEqual(len(remaining_tasks["data"]), 1)
    
    def test_list_all_tasks_across_workspaces(self):
        """Test listing all tasks across multiple workspaces"""
        # Add tasks to multiple workspaces
        add_tasks_batch(self.conv_id, [{"title": "Backend Task"}], "backend")
        add_tasks_batch(self.conv_id, [{"title": "Frontend Task"}], "frontend")
        add_tasks_batch(self.conv_id, [{"title": "Default Task"}])  # default workspace
        
        # Get all tasks
        all_tasks = list_all_tasks(self.conv_id)
        self.assertTrue(all_tasks["success"])
        self.assertEqual(len(all_tasks["data"]), 3)
        
        # Verify workspace information is included
        workspace_ids = [task["workspace_id"] for task in all_tasks["data"]]
        workspace_names = [task["workspace_name"] for task in all_tasks["data"]]
        
        self.assertIn("backend", workspace_ids)
        self.assertIn("frontend", workspace_ids)
        self.assertIn("default", workspace_ids)
        self.assertIn("Backend", workspace_names)
        self.assertIn("Frontend", workspace_names)
        self.assertIn("Default Workspace", workspace_names)
    
    def test_workspace_edge_cases(self):
        """Test edge cases for workspace functionality"""
        # Test empty workspace_id (should use default)
        result = add_tasks_batch(self.conv_id, [{"title": "Empty workspace test"}], "")
        self.assertTrue(result["success"])
        # Should create/use default workspace
        
        # Test very long workspace name
        long_workspace = "very_long_workspace_name_with_many_underscores_and_words"
        result = add_tasks_batch(self.conv_id, [{"title": "Long workspace test"}], long_workspace)
        self.assertTrue(result["success"])
        self.assertEqual(result["workspace_id"], long_workspace)
        
        # Test workspace with numbers and special characters
        special_workspace = "api_v2_endpoints"
        result = add_tasks_batch(self.conv_id, [{"title": "Special workspace test"}], special_workspace)
        self.assertTrue(result["success"])
        self.assertEqual(result["workspace_id"], special_workspace)
        
        # Verify all workspaces exist
        workspaces = list_workspaces(self.conv_id)
        workspace_ids = [ws["workspace_id"] for ws in workspaces["data"]]
        self.assertIn(long_workspace, workspace_ids)
        self.assertIn(special_workspace, workspace_ids)
    
    def test_conversation_isolation_with_workspaces(self):
        """Test that workspaces are isolated between conversations"""
        conv1 = "conversation_1"
        conv2 = "conversation_2"
        
        # Add tasks to same workspace name in different conversations
        add_tasks_batch(conv1, [{"title": "Conv1 Task"}], "shared_workspace")
        add_tasks_batch(conv2, [{"title": "Conv2 Task"}], "shared_workspace")
        
        # Verify isolation
        conv1_tasks = list_tasks(conv1, "shared_workspace")
        conv2_tasks = list_tasks(conv2, "shared_workspace")
        
        self.assertEqual(len(conv1_tasks["data"]), 1)
        self.assertEqual(len(conv2_tasks["data"]), 1)
        self.assertEqual(conv1_tasks["data"][0]["title"], "Conv1 Task")
        self.assertEqual(conv2_tasks["data"][0]["title"], "Conv2 Task")
        
        # Verify workspace lists are separate
        conv1_workspaces = list_workspaces(conv1)
        conv2_workspaces = list_workspaces(conv2)
        
        self.assertEqual(len(conv1_workspaces["data"]), 1)
        self.assertEqual(len(conv2_workspaces["data"]), 1)
    
    def test_backward_compatibility(self):
        """Test that old API calls still work with default workspace"""
        # Old-style calls without workspace_id should use default workspace
        add_task(self.conv_id, "Legacy Task 1")
        add_tasks_batch(self.conv_id, [{"title": "Legacy Task 2"}])
        
        # Should be in default workspace
        tasks = list_tasks(self.conv_id)  # No workspace_id specified
        self.assertEqual(len(tasks["data"]), 2)
        self.assertEqual(tasks["workspace_id"], "default")
        
        # Operations should work on default workspace
        update_task(self.conv_id, 1, status="completed")
        get_result = get_task(self.conv_id, 1)
        self.assertEqual(get_result["data"][0]["status"], "completed")
        
        # Verify default workspace exists in workspace list
        workspaces = list_workspaces(self.conv_id)
        default_workspace = next(ws for ws in workspaces["data"] if ws["workspace_id"] == "default")
        self.assertEqual(default_workspace["workspace_name"], "Default Workspace")
        self.assertEqual(default_workspace["task_count"], 2)


if __name__ == "__main__":
    unittest.main()
