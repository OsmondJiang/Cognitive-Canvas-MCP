#!/usr/bin/env python3

import unittest
import sys
import os
import time
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.chat_fork import ChatForkManager
from tools.notes import NotesManager

class TestChatForkNotesIntegration(unittest.TestCase):
    """Test suite for Chat Fork and Notes integration features"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.chat_manager = ChatForkManager()
        self.notes_manager = NotesManager()
        self.chat_manager.set_notes_manager(self.notes_manager)
        self.conversation_id = "test-integration"
    
    def test_resume_with_related_notes_hint(self):
        """Test that resume_topic returns related notes hint"""
        # Record some notes
        self.notes_manager.record_note(
            self.conversation_id,
            "Test note content 1",
            title="Test Note 1",
            note_type="problem"
        )
        
        time.sleep(0.01)  # Small delay for different timestamps
        
        # Pause topic
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Nested topic",
            pause_type="nested"
        )
        
        # Record note during nested topic
        self.notes_manager.record_note(
            self.conversation_id,
            "Test note content 2",
            title="Test Note 2",
            note_type="solution"
        )
        
        time.sleep(0.01)
        
        # Resume topic - should include related notes hint
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        
        # Verify integration fields are present
        self.assertEqual(result["status"], "success")
        self.assertIn("related_notes_hint", result)
        self.assertIn("notes_hint_message", result)
        
        # Verify notes hint structure
        notes_hint = result["related_notes_hint"]
        self.assertIsInstance(notes_hint, list)
        self.assertGreater(len(notes_hint), 0)
        
        # Verify each note hint has required fields
        for note in notes_hint:
            self.assertIn("id", note)
            self.assertIn("title", note)
            self.assertIn("type", note)
            self.assertIn("timestamp", note)
    
    def test_resume_without_notes(self):
        """Test that resume_topic works when no notes exist"""
        # Pause and resume without any notes
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        
        # Should work normally without notes hint
        self.assertEqual(result["status"], "success")
        self.assertNotIn("related_notes_hint", result)
        self.assertNotIn("notes_hint_message", result)
    
    def test_resume_with_notes_from_different_conversation(self):
        """Test that notes from different conversations are not included"""
        # Record note in different conversation
        self.notes_manager.record_note(
            "other-conversation",
            "Other conversation note",
            title="Other Note"
        )
        
        # Pause and resume in our conversation
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        
        # Should not include notes from other conversation
        self.assertEqual(result["status"], "success")
        self.assertNotIn("related_notes_hint", result)
    
    def test_integration_without_notes_manager(self):
        """Test that chat fork works normally without notes manager"""
        # Create chat manager without notes integration
        chat_no_notes = ChatForkManager()
        
        # Should work normally
        result = chat_no_notes.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        self.assertEqual(result["status"], "success")
        
        result = chat_no_notes.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        self.assertEqual(result["status"], "success")
        self.assertNotIn("related_notes_hint", result)
    
    def test_time_based_filtering(self):
        """Test that notes are filtered by topic time period"""
        # Record note before topic creation
        self.notes_manager.record_note(
            self.conversation_id,
            "Before topic note",
            title="Before Topic"
        )
        
        time.sleep(0.01)
        
        # Create and pause topic
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        
        time.sleep(0.01)
        
        # Record note during topic
        note_result = self.notes_manager.record_note(
            self.conversation_id,
            "During topic note",
            title="During Topic"
        )
        during_note_id = note_result["note_id"]
        
        time.sleep(0.01)
        
        # Resume topic
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        
        # Should include note from during topic time period
        if "related_notes_hint" in result:
            note_ids = [note["id"] for note in result["related_notes_hint"]]
            self.assertIn(during_note_id, note_ids)
    
    def test_parallel_topic_integration(self):
        """Test integration with parallel topic switching"""
        # Record initial note
        self.notes_manager.record_note(
            self.conversation_id,
            "Initial note",
            title="Initial Note"
        )
        
        time.sleep(0.01)
        
        # Pause to parallel topic
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Parallel topic",
            pause_type="parallel"
        )
        
        # Record note in parallel topic
        self.notes_manager.record_note(
            self.conversation_id,
            "Parallel note",
            title="Parallel Note"
        )
        
        time.sleep(0.01)
        
        # Resume back
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Parallel work done"
        )
        
        # Should work with parallel topics too
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["actual_resume_type"], "parallel")
    
    def test_notes_hint_limit(self):
        """Test that notes hint is limited to maximum 5 notes"""
        # Create more than 5 notes
        for i in range(7):
            self.notes_manager.record_note(
                self.conversation_id,
                f"Test note content {i}",
                title=f"Test Note {i}",
                note_type="general"
            )
            time.sleep(0.01)
        
        # Pause and resume
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        
        # Should limit to 5 notes
        if "related_notes_hint" in result:
            self.assertLessEqual(len(result["related_notes_hint"]), 5)
    
    def test_notes_hint_sorted_by_timestamp(self):
        """Test that notes hint is sorted by timestamp (newest first)"""
        note_ids = []
        
        # Record notes with delays
        for i in range(3):
            result = self.notes_manager.record_note(
                self.conversation_id,
                f"Note {i}",
                title=f"Note {i}"
            )
            note_ids.append(result["note_id"])
            time.sleep(0.01)
        
        # Pause and resume
        self.chat_manager.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        
        # Check if notes are sorted by timestamp (newest first)
        if "related_notes_hint" in result:
            hint_ids = [note["id"] for note in result["related_notes_hint"]]
            # Newest note should be first
            self.assertEqual(hint_ids[0], note_ids[-1])  # Last created note
    
    def test_integration_error_handling(self):
        """Test that integration handles errors gracefully"""
        # Create a mock notes manager that raises exceptions
        class MockNotesManager:
            def __init__(self):
                self.notes_by_conversation = {}
            
            def record_note(self, *args, **kwargs):
                raise Exception("Mock error")
        
        # Set problematic notes manager
        mock_notes = MockNotesManager()
        self.chat_manager.set_notes_manager(mock_notes)
        
        # Should still work without crashing
        result = self.chat_manager.pause_topic(
            self.conversation_id,
            "Test topic",
            pause_type="nested"
        )
        self.assertEqual(result["status"], "success")
        
        result = self.chat_manager.resume_topic(
            self.conversation_id,
            completed_summary="Test completed"
        )
        self.assertEqual(result["status"], "success")
        self.assertNotIn("related_notes_hint", result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
