#!/usr/bin/env python3

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools import todo_tool
from tools.notes import NotesManager

class TestTodoNotesIntegration(unittest.TestCase):
    """Test suite for Todo and Notes integration features"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Reset todo tool state
        todo_tool.tasks_by_workspace.clear()
        todo_tool.task_counters_by_workspace.clear()
        todo_tool.workspaces_metadata.clear()
        
        self.notes_manager = NotesManager()
        todo_tool.set_notes_manager(self.notes_manager)
        self.conversation_id = "test-todo-integration"
    
    def test_get_task_with_related_notes_hint(self):
        """Test that get_task returns related notes hint"""
        # Record some notes first
        self.notes_manager.record_note(
            self.conversation_id,
            "Implemented authentication using JWT tokens and bcrypt password hashing",
            title="Auth system implementation",
            note_type="solution",
            tags=["auth", "jwt", "security"]
        )
        
        self.notes_manager.record_note(
            self.conversation_id,
            "Fixed critical bug in password validation that allowed empty passwords",
            title="Password validation bug fix",
            note_type="problem",
            tags=["auth", "bug", "security"]
        )
        
        # Add a task related to authentication
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Implement user authentication system",
            "Add JWT-based authentication with password hashing"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Get the task - should include related notes hint
        result = todo_tool.get_task(self.conversation_id, task_id)
        
        # Verify integration fields are present in task data
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        self.assertEqual(len(result["data"]), 1)
        
        # Check that related notes hint is in the task data, not at the top level
        task = result["data"][0]
        self.assertIn("related_notes_hint", task)
        self.assertIn("notes_hint_message", task)
        
        # Verify notes hint structure
        notes_hint = task["related_notes_hint"]
        self.assertIsInstance(notes_hint, list)
        self.assertGreater(len(notes_hint), 0)
        
        # Verify each note hint has required fields
        for note in notes_hint:
            self.assertIn("id", note)
            self.assertIn("title", note)
            self.assertIn("type", note)
            self.assertIn("relevance_score", note)
            self.assertIn("preview", note)
    
    def test_get_task_without_related_notes(self):
        """Test that get_task works when no related notes exist"""
        # Add a task without any related notes
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Unrelated task",
            "This task has no related notes"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Get the task - should not include notes hint in task data
        result = todo_tool.get_task(self.conversation_id, task_id)
        
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        # Check that the task data doesn't have notes hint
        task = result["data"][0]
        self.assertNotIn("related_notes_hint", task)
        self.assertNotIn("notes_hint_message", task)
    
    def test_update_task_completed_with_notes_hint(self):
        """Test that completing a task provides related notes hint"""
        # Record a relevant note with matching keywords
        self.notes_manager.record_note(
            self.conversation_id,
            "Database optimization reduced query time by 80% using proper indexing and query restructuring techniques",
            title="Database performance optimization success",
            note_type="experience",
            tags=["database", "performance", "optimization"]
        )
        
        # Add and complete a related task with similar content
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Optimize database queries",
            "Improve performance of slow database operations using indexing"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Complete the task
        result = todo_tool.update_task(
            self.conversation_id,
            task_id,
            status="completed"
        )
        
        # Should include notes hint in the updated task data
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        # Find the completed task in the data
        completed_task = None
        for task in result["data"]:
            if task["id"] == task_id and task["status"] == "completed":
                completed_task = task
                break
        
        self.assertIsNotNone(completed_task)
        self.assertIn("related_notes_hint", completed_task)
        self.assertIn("notes_hint_message", completed_task)
        self.assertIn("consider recording your experience", completed_task["notes_hint_message"])
    
    def test_update_task_in_progress_with_notes_hint(self):
        """Test that starting a task provides helpful notes hint"""
        # Record a relevant note with matching keywords
        self.notes_manager.record_note(
            self.conversation_id,
            "API rate limiting implementation using Redis sliding window algorithm works great for preventing abuse",
            title="Rate limiting solution guide",
            note_type="solution",
            tags=["api", "rate-limiting", "redis"]
        )
        
        # Add and start a related task with similar content
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Implement API rate limiting",
            "Add rate limiting to prevent API abuse using Redis"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Start the task
        result = todo_tool.update_task(
            self.conversation_id,
            task_id,
            status="in_progress"
        )
        
        # Should include helpful notes hint in the updated task data
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        # Find the in-progress task in the data
        in_progress_task = None
        for task in result["data"]:
            if task["id"] == task_id and task["status"] == "in_progress":
                in_progress_task = task
                break
        
        self.assertIsNotNone(in_progress_task)
        self.assertIn("related_notes_hint", in_progress_task)
        self.assertIn("notes_hint_message", in_progress_task)
        self.assertIn("potentially helpful notes", in_progress_task["notes_hint_message"])
    
    def test_update_task_other_status_no_notes_hint(self):
        """Test that other status updates don't trigger notes hint"""
        # Add a task
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Test task",
            "Test description"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Update to blocked status
        result = todo_tool.update_task(
            self.conversation_id,
            task_id,
            status="blocked"
        )
        
        # Should not include notes hint for blocked status in any task
        self.assertEqual(result["success"], True)
        self.assertIn("data", result)
        
        # Check that no task has notes hint
        for task in result["data"]:
            self.assertNotIn("related_notes_hint", task)
    
    def test_integration_without_notes_manager(self):
        """Test that todo tool works normally without notes manager"""
        # Reset notes manager
        todo_tool.set_notes_manager(None)
        
        # Should work normally
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Test task",
            "Test description"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Get task should work without notes integration
        result = todo_tool.get_task(self.conversation_id, task_id)
        self.assertEqual(result["success"], True)
        
        # Check that task data doesn't have notes hint
        task = result["data"][0]
        self.assertNotIn("related_notes_hint", task)
        
        # Update task should work without notes integration
        result = todo_tool.update_task(self.conversation_id, task_id, status="completed")
        self.assertEqual(result["success"], True)
        
        # Check that no task has notes hint
        for task in result["data"]:
            self.assertNotIn("related_notes_hint", task)
    
    def test_notes_hint_limit(self):
        """Test that notes hint is limited to maximum 3 notes"""
        # Create multiple related notes
        for i in range(5):
            self.notes_manager.record_note(
                self.conversation_id,
                f"Testing note {i} about API development and authentication systems",
                title=f"API Test Note {i}",
                note_type="general"
            )
        
        # Add related task
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Develop API endpoints",
            "Create REST API with authentication"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Get task
        result = todo_tool.get_task(self.conversation_id, task_id)
        
        # Should limit to 3 notes
        if "related_notes_hint" in result:
            self.assertLessEqual(len(result["related_notes_hint"]), 3)
    
    def test_notes_hint_relevance_scoring(self):
        """Test that notes hint includes relevance scores"""
        # Record a highly relevant note
        self.notes_manager.record_note(
            self.conversation_id,
            "Machine learning model training with TensorFlow and data preprocessing",
            title="ML Model Training Guide",
            note_type="experience"
        )
        
        # Add related task
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Train machine learning model",
            "Implement and train ML model using TensorFlow"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Get task
        result = todo_tool.get_task(self.conversation_id, task_id)
        
        # Verify relevance scores are included
        if "related_notes_hint" in result:
            for note in result["related_notes_hint"]:
                self.assertIn("relevance_score", note)
                self.assertIsInstance(note["relevance_score"], (int, float))
                self.assertGreaterEqual(note["relevance_score"], 0)
    
    def test_conversation_isolation(self):
        """Test that notes from different conversations are not included"""
        # Record note in different conversation
        self.notes_manager.record_note(
            "other-conversation",
            "Database setup and configuration for production environment",
            title="Database Setup Guide"
        )
        
        # Add task in our conversation
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Setup production database",
            "Configure database for production deployment"
        )
        task_id = todo_result["data"][-1]["id"]
        
        # Get task - should not include notes from other conversation
        result = todo_tool.get_task(self.conversation_id, task_id)
        
        self.assertEqual(result["success"], True)
        self.assertNotIn("related_notes_hint", result)
    
    def test_integration_error_handling(self):
        """Test that integration handles errors gracefully"""
        # Create a mock notes manager that raises exceptions
        class MockNotesManager:
            def search_notes(self, *args, **kwargs):
                raise Exception("Mock error")
        
        # Set problematic notes manager
        mock_notes = MockNotesManager()
        todo_tool.set_notes_manager(mock_notes)
        
        # Should still work without crashing
        todo_result = todo_tool.add_task(
            self.conversation_id,
            "Test task",
            "Test description"
        )
        task_id = todo_result["data"][-1]["id"]
        
        result = todo_tool.get_task(self.conversation_id, task_id)
        self.assertEqual(result["success"], True)
        self.assertNotIn("related_notes_hint", result)
    
    def test_list_tasks_with_notes(self):
        """Test that list_tasks includes related notes hints"""
        # Record a relevant note
        self.notes_manager.record_note(
            self.conversation_id,
            "Database optimization techniques and query performance improvements",
            title="Database Performance Guide"
        )
        
        # Add a task that should match the note
        todo_tool.add_task(
            self.conversation_id,
            "Optimize database queries",
            "Improve database performance for API endpoints"
        )
        
        # List all tasks
        result = todo_tool.list_tasks(self.conversation_id)
        self.assertEqual(result["success"], True)
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)
        
        # Check that tasks with relevant content have notes hints
        found_task_with_notes = False
        for task in result["data"]:
            if "database" in task["title"].lower() or "database" in task.get("description", "").lower():
                if "related_notes_hint" in task:
                    found_task_with_notes = True
                    self.assertIsInstance(task["related_notes_hint"], list)
                    self.assertGreater(len(task["related_notes_hint"]), 0)
                    self.assertIn("notes_hint_message", task)
                    # Verify note structure
                    for note in task["related_notes_hint"]:
                        self.assertIn("id", note)
                        self.assertIn("title", note)
                        self.assertIn("type", note)
                        self.assertIn("relevance_score", note)
        
        self.assertTrue(found_task_with_notes, "Should find at least one task with related notes")
    
    def test_list_all_tasks_with_notes(self):
        """Test that list_all_tasks includes related notes hints"""
        # Record a relevant note
        self.notes_manager.record_note(
            self.conversation_id,
            "Authentication system setup with JWT tokens and Redis session storage",
            title="Auth System Implementation"
        )
        
        # Add tasks in different workspaces
        todo_tool.add_task(
            self.conversation_id,
            "Implement JWT authentication",
            "Set up user authentication system",
            workspace_id="backend"
        )
        
        todo_tool.add_task(
            self.conversation_id,
            "Create login UI",
            "Design authentication interface",
            workspace_id="frontend"
        )
        
        # List all tasks across workspaces
        result = todo_tool.list_all_tasks(self.conversation_id)
        self.assertEqual(result["success"], True)
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)
        
        # Check that tasks with relevant content have notes hints
        found_task_with_notes = False
        for task in result["data"]:
            if "auth" in task["title"].lower() or "auth" in task.get("description", "").lower():
                if "related_notes_hint" in task:
                    found_task_with_notes = True
                    self.assertIsInstance(task["related_notes_hint"], list)
                    self.assertGreater(len(task["related_notes_hint"]), 0)
                    self.assertIn("notes_hint_message", task)
                    # Verify workspace information is preserved
                    self.assertIn("workspace_id", task)
                    self.assertIn("workspace_name", task)
                    # Verify note structure
                    for note in task["related_notes_hint"]:
                        self.assertIn("id", note)
                        self.assertIn("title", note)
                        self.assertIn("type", note)
                        self.assertIn("relevance_score", note)
        
        self.assertTrue(found_task_with_notes, "Should find at least one task with related notes")

if __name__ == '__main__':
    unittest.main(verbosity=2)
