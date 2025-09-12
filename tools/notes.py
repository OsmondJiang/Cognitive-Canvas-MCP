from typing import List, Dict, Optional
from datetime import datetime
import uuid
import re
from .display_recommendations import DisplayRecommendations
from .semantic_search import NotesSemanticSearch

class Note:
    def __init__(self, id: str, content: str, title: str = None, note_type: str = "general", 
                 tags: List[str] = None, conversation_id: str = None, metadata: Dict = None):
        self.id = id
        self.content = content
        self.title = title or self._generate_title_from_content(content)
        self.note_type = note_type  # "problem", "solution", "experience", "progress", "general"
        self.tags = tags or []
        self.conversation_id = conversation_id
        self.timestamp = datetime.now().isoformat()
        self.last_accessed = self.timestamp
        self.access_count = 0
        self.effectiveness_score = None
        self.related_notes = []
        self.metadata = metadata or {}
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate a title from content if not provided"""
        # Take first sentence or first 50 characters
        sentences = content.split('.')
        if len(sentences) > 0 and len(sentences[0]) > 0:
            title = sentences[0].strip()
            return title[:50] + "..." if len(title) > 50 else title
        return content[:50] + "..." if len(content) > 50 else content
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "note_type": self.note_type,
            "tags": self.tags,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "effectiveness_score": self.effectiveness_score,
            "related_notes": self.related_notes,
            "metadata": self.metadata
        }

class NotesManager:
    def __init__(self):
        # Structure: conversation_id -> [notes]
        self.notes_by_conversation: Dict[str, List[Note]] = {}
        # Global notes index for cross-conversation search
        self.all_notes: List[Note] = []
        # Semantic search engine
        self.semantic_search = NotesSemanticSearch()
    
    def _ensure_conversation_exists(self, conversation_id: str):
        """Ensure conversation structure exists"""
        if conversation_id not in self.notes_by_conversation:
            self.notes_by_conversation[conversation_id] = []
    
    def record_note(self, conversation_id: str, content: str, title: str = None, 
                   note_type: str = "general", tags: List[str] = None, 
                   metadata: Dict = None) -> Dict:
        """Record a new note"""
        self._ensure_conversation_exists(conversation_id)
        
        note_id = str(uuid.uuid4())[:8]  # Short UUID
        note = Note(
            id=note_id,
            content=content,
            title=title,
            note_type=note_type,
            tags=tags or [],
            conversation_id=conversation_id,
            metadata=metadata or {}
        )
        
        self.notes_by_conversation[conversation_id].append(note)
        self.all_notes.append(note)
        
        result = {
            "success": True,
            "note_id": note_id,
            "title": note.title,
            "data": note.to_dict()
        }
        
        return DisplayRecommendations.add_to_json_result(result, "notes", "record")
    
    def search_notes(self, conversation_id: str, query: str = None, 
                    search_tags: List[str] = None, search_type: str = "combined",
                    limit: int = 10, include_other_conversations: bool = False) -> Dict:
        """Search notes with semantic search and tag filtering"""
        self._ensure_conversation_exists(conversation_id)
        
        search_pool = self.all_notes if include_other_conversations else self.notes_by_conversation[conversation_id]
        
        if not search_pool:
            return {
                "success": True,
                "results": [],
                "total_count": 0,
                "_show_to_user": "No relevant notes found"
            }
        
        # Convert notes to dictionaries for search
        search_documents = [note.to_dict() for note in search_pool]
        matched_notes = []
        search_method = "tag-based"
        
        # Semantic search (when query is provided)
        if query and search_type in ["semantic", "combined"]:
            try:
                semantic_results = self.semantic_search.semantic_search(
                    conversation_id=conversation_id,
                    notes=search_documents,
                    query=query,
                    limit=limit * 2  # Get more results for filtering
                )
                
                # Convert semantic results to our format
                for note_dict, similarity_score in semantic_results:
                    # Find the original Note object
                    note_obj = next((n for n in search_pool if n.id == note_dict['id']), None)
                    if note_obj:
                        note_obj.relevance_score = similarity_score
                        note_obj.access_count += 1
                        note_obj.last_accessed = datetime.now().isoformat()
                        matched_notes.append(note_obj)
                
                search_method = "semantic"
                        
            except Exception as e:
                # Don't fallback silently - return error information
                return {
                    "success": False,
                    "error": f"Semantic search failed: {str(e)}",
                    "error_type": "semantic_search_unavailable",
                    "suggestion": "Try using tag-based search instead",
                    "_show_to_user": f"Semantic search is not available: {str(e)}. Please try tag-based search."
                }
        
        # Tag-only search or when no query provided
        if search_tags and (search_type in ["tag", "combined"] or not query):
            tag_matched_notes = []
            for note in search_pool:
                tag_matches = len(set(search_tags).intersection(set(note.tags)))
                if tag_matches > 0:
                    # Calculate tag-based relevance score
                    tag_relevance = (tag_matches / len(search_tags)) * 1.0
                    note.relevance_score = tag_relevance
                    note.access_count += 1
                    note.last_accessed = datetime.now().isoformat()
                    tag_matched_notes.append(note)
            
            if search_type == "tag":
                matched_notes = tag_matched_notes
                search_method = "tag-based"
            elif search_type == "combined" and search_tags:
                # For combined search, boost scores for notes with matching tags
                tag_note_ids = {n.id for n in tag_matched_notes}
                for note in matched_notes:
                    if note.id in tag_note_ids:
                        # Boost semantic score with tag matching
                        current_score = getattr(note, 'relevance_score', 0)
                        tag_matches = len(set(search_tags).intersection(set(note.tags)))
                        tag_boost = (tag_matches / len(search_tags)) * 0.3
                        note.relevance_score = current_score + tag_boost
                
                # Add tag-only matches that weren't found by semantic search
                for tag_note in tag_matched_notes:
                    if tag_note.id not in {n.id for n in matched_notes}:
                        matched_notes.append(tag_note)
                
                search_method = "semantic + tag"
        
        # If no query and no tags, return error
        if not query and not search_tags:
            return {
                "success": False,
                "error": "Either query or search_tags must be provided",
                "_show_to_user": "Please provide either a search query or tags to search for"
            }
        
        # Remove duplicates and sort by relevance score and recency
        unique_notes = {}
        for note in matched_notes:
            if note.id not in unique_notes:
                unique_notes[note.id] = note
        
        final_notes = list(unique_notes.values())
        final_notes.sort(key=lambda x: (getattr(x, 'relevance_score', 0), x.timestamp), reverse=True)
        limited_results = final_notes[:limit]
        
        results = []
        for note in limited_results:
            result_item = note.to_dict()
            result_item["relevance_score"] = getattr(note, 'relevance_score', 0)
            result_item["preview"] = note.content[:150] + "..." if len(note.content) > 150 else note.content
            results.append(result_item)
        
        return {
            "success": True,
            "results": results,
            "total_count": len(final_notes),
            "search_query": query,
            "search_tags": search_tags,
            "search_type": search_type,
            "search_method": search_method,
            "_show_to_user": f"Found {len(final_notes)} relevant notes using {search_method} search, showing top {len(limited_results)} results"
        }
    
    def get_notes_by_ids(self, conversation_id: str, note_ids: List[str]) -> Dict:
        """Get specific notes by their IDs"""
        self._ensure_conversation_exists(conversation_id)
        
        found_notes = []
        not_found_ids = []
        
        for note_id in note_ids:
            note = self._find_note_by_id(note_id)
            if note:
                note.access_count += 1
                note.last_accessed = datetime.now().isoformat()
                found_notes.append(note.to_dict())
            else:
                not_found_ids.append(note_id)
        
        result = {
            "success": True,
            "notes": found_notes,
            "found_count": len(found_notes),
            "not_found_ids": not_found_ids
        }
        
        if not_found_ids:
            result["warning"] = f"Notes not found: {', '.join(not_found_ids)}"
        
        return DisplayRecommendations.add_to_json_result(result, "notes", "get_by_ids")
    
    def get_conversation_summary(self, conversation_id: str, context_data: Dict = None) -> Dict:
        """Get summary of notes for a conversation"""
        self._ensure_conversation_exists(conversation_id)
        
        notes = self.notes_by_conversation[conversation_id]
        
        if not notes:
            return {
                "success": True,
                "summary": {
                    "total_notes": 0,
                    "by_type": {},
                    "recent_notes": [],
                    "top_tags": []
                },
                "_show_to_user": "No notes recorded for this conversation"
            }
        
        # Group by type
        by_type = {}
        for note in notes:
            by_type[note.note_type] = by_type.get(note.note_type, 0) + 1
        
        # Get recent notes (last 5)
        recent_notes = sorted(notes, key=lambda x: x.timestamp, reverse=True)[:5]
        recent_summaries = [
            {
                "id": note.id,
                "title": note.title,
                "type": note.note_type,
                "tags": note.tags,
                "timestamp": note.timestamp
            }
            for note in recent_notes
        ]
        
        # Get top tags
        all_tags = []
        for note in notes:
            all_tags.extend(note.tags)
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        summary = {
            "total_notes": len(notes),
            "by_type": by_type,
            "recent_notes": recent_summaries,
            "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags]
        }
        
        result = {
            "success": True,
            "conversation_id": conversation_id,
            "summary": summary
        }
        
        return DisplayRecommendations.add_to_json_result(result, "notes", "get_summary")
    
    def update_note(self, conversation_id: str, note_id: str, content: str = None,
                   title: str = None, tags: List[str] = None, 
                   effectiveness_score: int = None, metadata: Dict = None) -> Dict:
        """Update an existing note"""
        note = self._find_note_by_id(note_id)
        
        if not note:
            return {
                "success": False,
                "error": f"Note {note_id} does not exist"
            }
        
        # Update fields
        if content is not None:
            note.content = content
        if title is not None:
            note.title = title
        if tags is not None:
            note.tags = tags
        if effectiveness_score is not None:
            note.effectiveness_score = effectiveness_score
        if metadata is not None:
            note.metadata.update(metadata)
        
        result = {
            "success": True,
            "note_id": note_id,
            "updated_note": note.to_dict()
        }
        
        return DisplayRecommendations.add_to_json_result(result, "notes", "update")
    
    def delete_note(self, conversation_id: str, note_id: str) -> Dict:
        """Delete a note"""
        note = self._find_note_by_id(note_id)
        
        if not note:
            return {
                "success": False,
                "error": f"Note {note_id} does not exist"
            }
        
        # Remove from conversation notes
        if conversation_id in self.notes_by_conversation:
            self.notes_by_conversation[conversation_id] = [
                n for n in self.notes_by_conversation[conversation_id] if n.id != note_id
            ]
        
        # Remove from global notes
        self.all_notes = [n for n in self.all_notes if n.id != note_id]
        
        result = {
            "success": True,
            "deleted_note_id": note_id,
            "message": f"Deleted note: {note.title}"
        }
        
        return DisplayRecommendations.add_to_json_result(result, "notes", "delete")
    
    def _find_note_by_id(self, note_id: str) -> Optional[Note]:
        """Find a note by ID across all conversations"""
        for note in self.all_notes:
            if note.id == note_id:
                return note
        return None
