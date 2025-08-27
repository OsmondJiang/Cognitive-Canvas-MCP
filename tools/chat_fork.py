from typing import Dict, List, Optional

class ChatNode:
    def __init__(self, summary: str, details: str = "", parent: Optional['ChatNode'] = None):
        self.summary = summary
        self.details = details
        self.parent = parent
        self.children: List['ChatNode'] = []
        # Enhanced context fields
        self.current_context = ""
        self.progress_status = ""
        self.next_steps = ""

class ChatForkManager:
    def __init__(self):
        self.conversations: Dict[str, ChatNode] = {}

    def pause_topic(self, conversation_id: str, new_topic: str, current_context: str = "", 
                    progress_status: str = "", next_steps: str = "", pause_type: str = "nested") -> dict:
        """
        Pause current topic and switch to a new topic.
        Supports two pause modes: nested drilling vs parallel switching
        
        Args:
            conversation_id: Conversation ID
            new_topic: The new topic to switch to
            current_context: Current discussion context and details (optional)
            progress_status: Current progress and status (optional)
            next_steps: Next steps or pending tasks (optional)
            pause_type: Pause type
                       - "nested": Nested pause, drill deeper into current topic's subtopic
                       - "parallel": Parallel pause, switch to a sibling topic at the same level
        
        Returns:
            Dictionary containing operation result and context information
        """
        # If new conversation, create root node
        if conversation_id not in self.conversations:
            root_summary = "Main conversation"
            root_node = ChatNode(root_summary)
            if current_context:
                root_node.current_context = current_context
            if progress_status:
                root_node.progress_status = progress_status
            if next_steps:
                root_node.next_steps = next_steps
            self.conversations[conversation_id] = root_node
        else:
            # Existing conversation, update current node's context
            current = self.conversations[conversation_id]
            
            # Update context information
            if current_context:
                current.current_context = current_context
            if progress_status:
                current.progress_status = progress_status
            if next_steps:
                current.next_steps = next_steps
        
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
                "saved_context": {
                    "current_context": current.current_context,
                    "progress_status": current.progress_status,
                    "next_steps": current.next_steps
                },
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
                "saved_context": {
                    "current_context": current.current_context,
                    "progress_status": current.progress_status,
                    "next_steps": current.next_steps
                },
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
                "current_context": {
                    "current_context": current.current_context,
                    "progress_status": current.progress_status,
                    "next_steps": current.next_steps
                },
                "action": "already_at_main"
            }
        
        # Execute resume
        self.conversations[conversation_id] = target_node
        
        return {
            "status": "success",
            "message": f"Completed topic '{current.summary}' and resumed: {target_node.summary}",
            "completed_topic": current.summary,
            "completed_summary": completed_summary,
            "resumed_topic": target_node.summary,
            "restored_context": {
                "current_context": target_node.current_context,
                "progress_status": target_node.progress_status,
                "next_steps": target_node.next_steps
            },
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

    def render_conversation_tree(self, conversation_id: str) -> str:
        """
        Render the conversation tree as a text-based tree structure.
        Shows all topics in a hierarchical view with the current topic marked.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            String containing the rendered tree text
        """
        if conversation_id not in self.conversations:
            return "Error: Conversation not found"
        
        current_node = self.conversations[conversation_id]
        root_node = self._find_root(current_node)
        
        # Build the tree representation
        tree_lines = []
        self._render_node(root_node, current_node, tree_lines, "", True, True)  # Mark as root
        
        return "\n".join(tree_lines)
    
    def _render_node(self, node: ChatNode, current_node: ChatNode, tree_lines: List[str], 
                     prefix: str, is_last: bool, is_root: bool = False) -> None:
        """
        Recursively render a node and its children in tree format.
        
        Args:
            node: Node to render
            current_node: Current active node (for marking)
            tree_lines: List to append rendered lines to
            prefix: Prefix for the current line
            is_last: Whether this is the last child of its parent
            is_root: Whether this is the root node
        """
        # Determine the marker for current position
        current_marker = " 👈 [HERE]" if node == current_node else ""
        
        # Format the topic summary with context info
        topic_info = node.summary
        
        # Show context information if available
        context_parts = []
        if node.current_context:
            context_parts.append(node.current_context[:30] + "..." if len(node.current_context) > 30 else node.current_context)
        if node.progress_status:
            context_parts.append(f"Progress: {node.progress_status}")
        if node.next_steps:
            context_parts.append(f"Next: {node.next_steps[:20]}..." if len(node.next_steps) > 20 else f"Next: {node.next_steps}")
        
        if context_parts:
            topic_info += f" ({'; '.join(context_parts)})"
        
        # Add pause type indicator
        pause_type = getattr(node, '_pause_type', '')
        if pause_type:
            type_indicator = " [N]" if pause_type == "nested" else " [P]" if pause_type == "parallel" else ""
            topic_info += type_indicator
        
        # Determine the tree connector
        if is_root:
            # Root node - no connector, just the topic
            line = f"{topic_info}{current_marker}"
        else:
            # Child node - add tree connector
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{topic_info}{current_marker}"
        
        tree_lines.append(line)
        
        # Render children
        if len(node.children) > 0:
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                
                if is_root:
                    # For root node children, no prefix yet
                    child_prefix = ""
                else:
                    # For deeper level children
                    child_prefix = prefix + ("    " if is_last else "│   ")
                
                self._render_node(child, current_node, tree_lines, child_prefix, is_last_child, False)
    
    def _count_nodes(self, node: ChatNode) -> int:
        """Count total number of nodes in the tree starting from given node"""
        count = 1  # Count current node
        for child in node.children:
            count += self._count_nodes(child)
        return count
