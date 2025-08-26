from typing import Dict, List, Optional

class ChatNode:
    def __init__(self, summary: str, details: str = "", parent: Optional['ChatNode'] = None):
        self.summary = summary
        self.details = details  # 新增详细信息字段
        self.parent = parent
        self.children: List['ChatNode'] = []

class ChatForkManager:
    def __init__(self):
        self.conversations: Dict[str, ChatNode] = {}

    def fork_topic(self, conversation_id: str, summary: str, details: str = "") -> str:
        """Create a new subtopic under current node."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ChatNode("Conversation Root")
        
        current = self.conversations[conversation_id]
        new_node = ChatNode(summary, details, parent=current)
        current.children.append(new_node)
        self.conversations[conversation_id] = new_node
        return f"Forked new topic: {summary}"

    def return_to_previous_context(self, conversation_id: str) -> dict:
        """Return to previous context and get its full context."""
        if conversation_id not in self.conversations:
            return {"error": "Conversation not found"}

        current = self.conversations[conversation_id]
        if current.parent:
            self.conversations[conversation_id] = current.parent
            return {
                "status": "success",
                "message": f"Returned to previous context: {current.parent.summary}",
                "summary": current.parent.summary,
                "details": current.parent.details,
                "has_details": bool(current.parent.details)
            }
        else:
            return {
                "status": "error",
                "message": "Already at root context, cannot return to previous context",
                "summary": current.summary,
                "details": current.details,
                "has_details": bool(current.details)
            }

    def get_current_context(self, conversation_id: str) -> dict:
        """Get both summary and details of current topic."""
        if conversation_id not in self.conversations:
            return {"error": "Conversation not found"}
        current = self.conversations[conversation_id]
        return {
            "summary": current.summary,
            "details": current.details,
            "has_details": bool(current.details)
        }

    def list_subtopics(self, conversation_id: str, include_details: bool = False) -> List[str]:
        """List all child subtopics of current node."""
        if conversation_id not in self.conversations:
            return []
        
        if include_details:
            subtopics = []
            for child in self.conversations[conversation_id].children:
                if child.details:
                    subtopics.append(f"{child.summary} | Details: {child.details}")
                else:
                    subtopics.append(f"{child.summary} | No details")
            return subtopics
        else:
            return [child.summary for child in self.conversations[conversation_id].children]
