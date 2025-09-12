import unittest
import sys
import os

# Add the parent directory to the path to import tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.notes import NotesManager

class TestNotesManager(unittest.TestCase):
    def setUp(self):
        self.notes_manager = NotesManager()
        self.conversation_id = "test_conv_001"
    
    def test_record_note(self):
        """Test recording a basic note"""
        result = self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Test note content for API performance issue",
            note_type="problem",
            tags=["api", "performance"]
        )
        
        self.assertTrue(result["success"])
        self.assertIn("note_id", result)
        self.assertEqual(result["data"]["note_type"], "problem")
        self.assertEqual(result["data"]["tags"], ["api", "performance"])
    
    def test_record_note_with_title(self):
        """Test recording a note with custom title"""
        result = self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Detailed solution for fixing database timeout issues",
            title="Database Timeout Fix",
            note_type="solution",
            tags=["database", "timeout", "fix"]
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["title"], "Database Timeout Fix")
        self.assertEqual(result["data"]["note_type"], "solution")
    
    def test_search_notes_by_content(self):
        """Test searching notes by content"""
        # First, record some test notes
        self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="API response time is slow due to database queries",
            note_type="problem",
            tags=["api", "performance", "database"]
        )
        
        self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Fixed slow API by adding database indexes",
            note_type="solution", 
            tags=["api", "database", "optimization"]
        )
        
        # Search for API related notes
        result = self.notes_manager.search_notes(
            conversation_id=self.conversation_id,
            query="API performance",
            search_type="semantic"
        )
        
        self.assertTrue(result["success"])
        self.assertGreater(result["total_count"], 0)
        self.assertIn("results", result)
    
    def test_search_notes_by_tags(self):
        """Test searching notes by tags"""
        # Record a test note
        note_result = self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Database optimization techniques",
            note_type="experience",
            tags=["database", "optimization", "performance"]
        )
        
        # Search by tags
        result = self.notes_manager.search_notes(
            conversation_id=self.conversation_id,
            search_tags=["database", "optimization"],
            search_type="tag"
        )
        
        self.assertTrue(result["success"])
        self.assertGreater(result["total_count"], 0)
        
        # Check that the returned note has the expected tags
        found_note = result["results"][0]
        self.assertIn("database", found_note["tags"])
        self.assertIn("optimization", found_note["tags"])
    
    def test_get_notes_by_ids(self):
        """Test retrieving specific notes by ID"""
        # Record a test note
        record_result = self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Test content for ID retrieval",
            note_type="general",
            tags=["test"]
        )
        
        note_id = record_result["note_id"]
        
        # Retrieve by ID
        result = self.notes_manager.get_notes_by_ids(
            conversation_id=self.conversation_id,
            note_ids=[note_id]
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["found_count"], 1)
        self.assertEqual(len(result["notes"]), 1)
        self.assertEqual(result["notes"][0]["id"], note_id)
    
    def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        # Record multiple notes
        self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="First problem note",
            note_type="problem",
            tags=["issue1"]
        )
        
        self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="First solution note", 
            note_type="solution",
            tags=["fix1"]
        )
        
        # Get summary
        result = self.notes_manager.get_conversation_summary(self.conversation_id)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["summary"]["total_notes"], 2)
        self.assertIn("problem", result["summary"]["by_type"])
        self.assertIn("solution", result["summary"]["by_type"])
        self.assertEqual(result["summary"]["by_type"]["problem"], 1)
        self.assertEqual(result["summary"]["by_type"]["solution"], 1)
    
    def test_update_note(self):
        """Test updating an existing note"""
        # Record a test note
        record_result = self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Original content",
            note_type="general",
            tags=["original"]
        )
        
        note_id = record_result["note_id"]
        
        # Update the note
        result = self.notes_manager.update_note(
            conversation_id=self.conversation_id,
            note_id=note_id,
            content="Updated content",
            tags=["updated", "modified"],
            effectiveness_score=4
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["updated_note"]["content"], "Updated content")
        self.assertEqual(result["updated_note"]["tags"], ["updated", "modified"])
        self.assertEqual(result["updated_note"]["effectiveness_score"], 4)
    
    def test_delete_note(self):
        """Test deleting a note"""
        # Record a test note
        record_result = self.notes_manager.record_note(
            conversation_id=self.conversation_id,
            content="Note to be deleted",
            note_type="general"
        )
        
        note_id = record_result["note_id"]
        
        # Delete the note
        result = self.notes_manager.delete_note(self.conversation_id, note_id)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_note_id"], note_id)
        
        # Verify it's deleted by trying to retrieve it
        retrieve_result = self.notes_manager.get_notes_by_ids(
            self.conversation_id, [note_id]
        )
        self.assertEqual(len(retrieve_result["notes"]), 0)
        self.assertIn(note_id, retrieve_result["not_found_ids"])

if __name__ == '__main__':
    unittest.main()
