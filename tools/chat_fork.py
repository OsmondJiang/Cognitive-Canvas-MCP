from typing import Dict, List, Optional

class ChatNode:
    def __init__(self, summary: str, parent: Optional['ChatNode'] = None):
        self.summary = summary
        self.parent = parent
        self.children: List['ChatNode'] = []

class ChatForkManager:
    def __init__(self):
        self.conversations: Dict[str, ChatNode] = {}

    def fork_topic(self, conversation_id: str, summary: str) -> str:
        """Create a new subtopic under current node."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ChatNode("Conversation Root")
        
        current = self.conversations[conversation_id]
        new_node = ChatNode(summary, parent=current)
        current.children.append(new_node)
        self.conversations[conversation_id] = new_node
        return f"Forked new topic: {summary}"

    def return_to_parent(self, conversation_id: str) -> str:
        """Return to parent node."""
        if conversation_id not in self.conversations:
            return "Conversation not found."

        current = self.conversations[conversation_id]
        if current.parent:
            self.conversations[conversation_id] = current.parent
            return f"Returned to parent topic: {current.parent.summary}"
        else:
            return "Already at root topic, cannot return to parent."

    def get_current_summary(self, conversation_id: str) -> str:
        """Get current topic summary."""
        if conversation_id not in self.conversations:
            return "Conversation not found."
        return self.conversations[conversation_id].summary

    def list_subtopics(self, conversation_id: str) -> List[str]:
        """List all child subtopics of current node."""
        if conversation_id not in self.conversations:
            return []
        return [child.summary for child in self.conversations[conversation_id].children]
