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

    def pause_topic(self, conversation_id: str, new_topic: str, state_update: str = "", pause_type: str = "nested") -> dict:
        """
        Pause current topic and switch to a new topic.
        Supports two pause modes: nested drilling vs parallel switching
        
        Args:
            conversation_id: Conversation ID
            new_topic: The new topic to switch to
            state_update: Update description of current topic state (optional)
            pause_type: Pause type
                       - "nested": Nested pause, drill deeper into current topic's subtopic
                       - "parallel": Parallel pause, switch to a sibling topic at the same level
        
        Returns:
            Dictionary containing operation result and context information
        """
        # If new conversation, create root node
        if conversation_id not in self.conversations:
            root_summary = "Main conversation"
            self.conversations[conversation_id] = ChatNode(root_summary, state_update or "")
        else:
            # Existing conversation, update current node's state
            current = self.conversations[conversation_id]
            
            # Smart state update
            if state_update:
                if not current.details:
                    current.details = state_update
                elif len(current.details) < 50 or "..." in current.details:
                    current.details = state_update
                else:
                    current.details += f" | Latest progress: {state_update}"
        
        current = self.conversations[conversation_id]
        
        if pause_type == "nested":
            # Nested mode: create subtopic under current node
            new_topic_node = ChatNode(new_topic, "", parent=current)
            new_topic_node._pause_type = "nested"  # Mark pause type
            current.children.append(new_topic_node)
            self.conversations[conversation_id] = new_topic_node
            
            return {
                "status": "success",
                "message": f"Nested pause: diving deeper into '{new_topic}' from '{current.summary}'",
                "paused_topic": current.summary,
                "current_topic": new_topic,
                "paused_state": current.details,
                "pause_type": "nested",
                "action": "topic_paused",
                "depth": self._get_conversation_depth(new_topic_node)
            }
            
        elif pause_type == "parallel":
            # Parallel mode: create sibling topic under the same parent
            if current.parent is None:
                # If already at root, create under root (same as nested)
                parent_node = current
            else:
                # Create sibling under the same parent
                parent_node = current.parent
            
            new_topic_node = ChatNode(new_topic, "", parent=parent_node)
            new_topic_node._pause_type = "parallel"  # Mark pause type
            new_topic_node._paused_from = current  # Record which node we paused from
            parent_node.children.append(new_topic_node)
            self.conversations[conversation_id] = new_topic_node
            
            return {
                "status": "success", 
                "message": f"Parallel pause: switched to '{new_topic}', can resume back to '{current.summary}'",
                "paused_topic": current.summary,
                "current_topic": new_topic,
                "paused_state": current.details,
                "pause_type": "parallel",
                "action": "topic_paused",
                "depth": self._get_conversation_depth(new_topic_node),
                "paused_from_depth": self._get_conversation_depth(current)
            }
        
        else:
            return {
                "status": "error",
                "message": f"Invalid pause_type: {pause_type}. Must be 'nested' or 'parallel'"
            }

    def resume_topic(self, conversation_id: str, completed_summary: str = "", resume_type: str = "auto") -> dict:
        """
        Complete current topic and resume previously paused topic.
        Smart resume based on pause type.
        
        Args:
            conversation_id: Conversation ID
            completed_summary: Completion summary of current topic (optional)
            resume_type: Resume type
                        - "auto": Automatically decide resume location based on pause type
                        - "parent": Force resume to parent topic
                        - "root": Force resume to root topic
        
        Returns:
            Dictionary containing operation result and restored context information
        """
        if conversation_id not in self.conversations:
            return {
                "status": "error",
                "message": "Conversation not found",
                "action": "error"
            }

        current = self.conversations[conversation_id]
        
        # Save completion summary of current topic
        if completed_summary:
            current.details = completed_summary
        
        # Determine resume target based on resume_type
        if resume_type == "auto":
            # Auto mode: smart decision based on pause type
            pause_type = getattr(current, '_pause_type', 'nested')
            
            if pause_type == "nested":
                # Nested pause → resume to parent
                target_node = current.parent
            elif pause_type == "parallel":
                # Parallel pause → resume to originally paused location
                target_node = getattr(current, '_paused_from', current.parent)
            else:
                # Default resume to parent
                target_node = current.parent
                
        elif resume_type == "parent":
            target_node = current.parent
        elif resume_type == "root":
            target_node = self._find_root(current)
        else:
            return {
                "status": "error",
                "message": f"Invalid resume_type: {resume_type}. Must be 'auto', 'parent', or 'root'"
            }
        
        # Check if target node exists
        if target_node is None:
            return {
                "status": "warning",
                "message": "Already at main conversation, no topic to resume",
                "current_topic": current.summary,
                "current_state": current.details,
                "has_state": bool(current.details),
                "action": "already_at_main"
            }
        
        # Execute resume
        self.conversations[conversation_id] = target_node
        
        return {
            "status": "success",
            "message": f"Completed topic '{current.summary}' and resumed: {target_node.summary}",
            "completed_topic": current.summary,
            "resumed_topic": target_node.summary,
            "restored_state": target_node.details,
            "has_restored_state": bool(target_node.details),
            "resume_type": resume_type,
            "actual_resume_type": getattr(current, '_pause_type', 'nested'),
            "action": "topic_resumed"
        }

    def _get_conversation_depth(self, node: ChatNode) -> int:
        """Calculate the depth of a node in the conversation tree"""
        depth = 0
        current = node
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth
    
    def _find_root(self, node: ChatNode) -> ChatNode:
        """Find the root node of the conversation tree"""
        current = node
        while current.parent is not None:
            current = current.parent
        return current
