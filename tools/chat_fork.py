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
        # Bookmark functionality
        self.is_bookmarked = False
        self.bookmark_name = ""

class ChatForkManager:
    def __init__(self):
        self.conversations: Dict[str, ChatNode] = {}

    def pause_topic(self, conversation_id: str, new_topic: str, current_context: str = "", 
                    progress_status: str = "", next_steps: str = "", pause_type: str = "nested",
                    bookmark: str = "") -> dict:
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
            bookmark: If provided, mark the current topic as a bookmark with this name (optional)
        
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
            # Existing conversation - behavior depends on pause type
            current = self.conversations[conversation_id]
            
            if pause_type == "nested":
                # For nested pause: update current node's context
                if current_context:
                    current.current_context = current_context
                if progress_status:
                    current.progress_status = progress_status
                if next_steps:
                    current.next_steps = next_steps
            # For parallel pause: don't update current node, save original context
        
        current = self.conversations[conversation_id]
        
        # Handle bookmark functionality - mark current topic as bookmark if requested
        if bookmark:
            current.is_bookmarked = True
            current.bookmark_name = bookmark
        
        if pause_type == "nested":
            # Nested mode: create subtopic under current node
            new_topic_node = ChatNode(new_topic, "", parent=current)
            new_topic_node._pause_type = "nested"  # Mark pause type
            
            # The new subtopic should get the context information
            if current_context:
                new_topic_node.current_context = current_context
            if progress_status:
                new_topic_node.progress_status = progress_status
            if next_steps:
                new_topic_node.next_steps = next_steps
                
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
                "depth": self._get_conversation_depth(new_topic_node),
                "bookmark_created": bookmark if bookmark else None
            }
            
        elif pause_type == "parallel":
            # Parallel mode: create sibling topic under the same parent
            if current.parent is None:
                # If already at root, create under root (same as nested)
                parent_node = current
            else:
                # Create sibling under the same parent
                parent_node = current.parent
            
            # Store original context before any modifications
            original_context = {
                "current_context": current.current_context,
                "progress_status": current.progress_status,
                "next_steps": current.next_steps
            }
            
            # DON'T update current node context for parallel - we're switching topics, not updating
            # The parallel pause context describes the NEW topic we're starting
            new_topic_node = ChatNode(new_topic, "", parent=parent_node)
            new_topic_node._pause_type = "parallel"  # Mark pause type
            new_topic_node._paused_from = current  # Record which node we paused from
            
            # Set the new topic's context from the provided parameters
            if current_context:
                new_topic_node.current_context = current_context
            if progress_status:
                new_topic_node.progress_status = progress_status
            if next_steps:
                new_topic_node.next_steps = next_steps
                
            parent_node.children.append(new_topic_node)
            self.conversations[conversation_id] = new_topic_node
            
            return {
                "status": "success", 
                "message": f"Parallel pause: switched to '{new_topic}', can resume back to '{current.summary}'",
                "paused_topic": current.summary,
                "current_topic": new_topic,
                "saved_context": original_context,
                "pause_type": "parallel",
                "action": "topic_paused",
                "depth": self._get_conversation_depth(new_topic_node),
                "paused_from_depth": self._get_conversation_depth(current),
                "bookmark_created": bookmark if bookmark else None
            }
        
        else:
            return {
                "status": "error",
                "message": f"Invalid pause_type: {pause_type}. Must be 'nested' or 'parallel'"
            }

    def resume_topic(self, conversation_id: str, completed_summary: str = "", 
                    resume_type: str = "auto", bookmark: str = "") -> dict:
        """
        Complete current topic and resume previously paused topic.
        Smart resume based on pause type, or jump to specific bookmark.
        
        Args:
            conversation_id: Conversation ID
            completed_summary: Completion summary of current topic (optional)
            resume_type: Resume type
                        - "auto": Automatically decide resume location based on pause type
                        - "parent": Force resume to parent topic
                        - "root": Force resume to root topic
                        - "bookmark": Resume to specific bookmark (requires bookmark)
            bookmark: Name of bookmark to resume to (used when resume_type="bookmark" or as direct target)
        
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
        if bookmark:
            # If bookmark is provided, try to find and jump to that bookmark
            target_node = self._find_bookmark(conversation_id, bookmark)
            if target_node is None:
                return {
                    "status": "error",
                    "message": f"Bookmark '{bookmark}' not found",
                    "action": "bookmark_not_found"
                }
        elif resume_type == "auto":
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
        elif resume_type == "bookmark":
            if not bookmark:
                return {
                    "status": "error",
                    "message": "bookmark is required when resume_type is 'bookmark'"
                }
            target_node = self._find_bookmark(conversation_id, bookmark)
            if target_node is None:
                return {
                    "status": "error",
                    "message": f"Bookmark '{bookmark}' not found"
                }
        else:
            return {
                "status": "error",
                "message": f"Invalid resume_type: {resume_type}. Must be 'auto', 'parent', 'root', or 'bookmark'"
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
            "action": "topic_resumed",
            "resumed_to_bookmark": target_node.bookmark_name if target_node.is_bookmarked else None
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
    
    def _find_bookmark(self, conversation_id: str, bookmark_name: str) -> Optional[ChatNode]:
        """Find a node with the specified bookmark name"""
        if conversation_id not in self.conversations:
            return None
        
        current_node = self.conversations[conversation_id]
        root_node = self._find_root(current_node)
        
        # Search entire tree for the bookmark
        return self._search_bookmark_recursive(root_node, bookmark_name)
    
    def _search_bookmark_recursive(self, node: ChatNode, bookmark_name: str) -> Optional[ChatNode]:
        """Recursively search for a bookmark in the tree"""
        if node.is_bookmarked and node.bookmark_name == bookmark_name:
            return node
        
        for child in node.children:
            result = self._search_bookmark_recursive(child, bookmark_name)
            if result:
                return result
        
        return None
    
    def _list_bookmarks_recursive(self, node: ChatNode, bookmarks: List[dict]) -> None:
        """Recursively collect all bookmarks in the tree"""
        if node.is_bookmarked:
            bookmarks.append({
                "name": node.bookmark_name,
                "topic": node.summary,
                "context": node.current_context,
                "progress": node.progress_status
            })
        
        for child in node.children:
            self._list_bookmarks_recursive(child, bookmarks)

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
        
        # Collect bookmarks
        bookmarks = []
        self._list_bookmarks_recursive(root_node, bookmarks)
        
        result = "\n".join(tree_lines)
        
        # Add bookmarks summary if any exist
        if bookmarks:
            result += "\n\n📖 Bookmarks:\n"
            for bookmark in bookmarks:
                result += f"  🔖 {bookmark['name']}: {bookmark['topic']}\n"
        
        return result
    
    def _render_node(self, node: ChatNode, current_node: ChatNode, tree_lines: List[str], 
                     prefix: str, is_last: bool, is_root: bool = False) -> None:
        """
        Recursively render a node and its children in tree format with detailed context.
        
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
        
        # Add pause type and bookmark indicators
        pause_type = getattr(node, '_pause_type', '')
        type_indicator = ""
        if pause_type:
            type_indicator = " [N]" if pause_type == "nested" else " [P]" if pause_type == "parallel" else ""
        
        # Add bookmark indicator
        bookmark_indicator = f" 🔖[{node.bookmark_name}]" if node.is_bookmarked else ""
        
        # Main topic line
        if is_root:
            line = f"{node.summary}{type_indicator}{bookmark_indicator}{current_marker}"
        else:
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{node.summary}{type_indicator}{bookmark_indicator}{current_marker}"
        
        tree_lines.append(line)
        
        # Add context details as sub-lines if available
        if not is_root:
            detail_prefix = prefix + ("    " if is_last else "│   ")
        else:
            detail_prefix = ""
        
        if node.current_context:
            context_line = f"{detail_prefix}    └─ Context: {node.current_context}"
            tree_lines.append(context_line)
        
        if node.progress_status:
            progress_line = f"{detail_prefix}    └─ Progress: {node.progress_status}"
            tree_lines.append(progress_line)
        
        if node.next_steps:
            next_line = f"{detail_prefix}    └─ Next: {node.next_steps}"
            tree_lines.append(next_line)
        
        # Render children
        if len(node.children) > 0:
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                
                if is_root:
                    child_prefix = ""
                else:
                    child_prefix = prefix + ("    " if is_last else "│   ")
                
                self._render_node(child, current_node, tree_lines, child_prefix, is_last_child, False)
    
    def _count_nodes(self, node: ChatNode) -> int:
        """Count total number of nodes in the tree starting from given node"""
        count = 1  # Count current node
        for child in node.children:
            count += self._count_nodes(child)
        return count
