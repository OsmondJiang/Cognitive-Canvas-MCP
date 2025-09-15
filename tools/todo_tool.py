from .display_recommendations import DisplayRecommendations

# Optional reference to notes manager for integration
_notes_manager = None

def set_notes_manager(notes_manager):
    """Set notes manager for integration features"""
    global _notes_manager
    _notes_manager = notes_manager

def _get_related_notes_hint(conversation_id: str, task_content: str, limit: int = 3) -> list:
    """Get related notes hint based on task content (weak integration)"""
    if not _notes_manager:
        return []
    
    try:
        # First try semantic search
        search_result = _notes_manager.search_notes(
            conversation_id=conversation_id,
            query=task_content,
            limit=limit,
            include_other_conversations=False
        )
        
        if search_result.get("success") and search_result.get("results"):
            # Extract relevant note information
            related_notes = []
            for note in search_result["results"]:
                related_notes.append({
                    "id": note["id"],
                    "title": note["title"],
                    "type": note["note_type"],
                    "relevance_score": note.get("relevance_score", 0),
                    "preview": note.get("preview", "")
                })
            return related_notes
        
        # If semantic search fails, try to get recent notes as fallback
        summary_result = _notes_manager.get_conversation_summary(conversation_id)
        if summary_result.get("success") and summary_result.get("summary", {}).get("recent_notes"):
            # Return recent notes as fallback
            recent_notes = summary_result["summary"]["recent_notes"][:limit]
            related_notes = []
            for note in recent_notes:
                related_notes.append({
                    "id": note["id"],
                    "title": note["title"],
                    "type": note["type"],
                    "relevance_score": 0.5,  # Default relevance for fallback
                    "preview": f"Recent note: {note['title']}"
                })
            return related_notes
        
        return []
        
    except Exception:
        # Silent fallback - integration should not break main functionality
        return []

# Updated data structure to support workspaces
# Format: {conversation_id: {workspace_id: [tasks]}}
tasks_by_workspace = {}
# Format: {conversation_id: {workspace_id: counter}}
task_counters_by_workspace = {}
# Format: {conversation_id: {workspace_id: {"name": str, "created_at": str}}}
workspaces_metadata = {}

VALID_STATUSES = ["pending", "in_progress", "completed", "blocked"]

def _get_effective_id(conversation_id: str, workspace_id: str = "default") -> str:
    """Generate effective ID for workspace isolation"""
    return f"{conversation_id}:{workspace_id}"

def _ensure_conversation_exists(conversation_id: str):
    """Ensure conversation structure exists"""
    if conversation_id not in tasks_by_workspace:
        tasks_by_workspace[conversation_id] = {}
    if conversation_id not in task_counters_by_workspace:
        task_counters_by_workspace[conversation_id] = {}
    if conversation_id not in workspaces_metadata:
        workspaces_metadata[conversation_id] = {}

def _ensure_workspace_exists(conversation_id: str, workspace_id: str = "default"):
    """Ensure workspace structure exists - auto-creates workspace if needed"""
    _ensure_conversation_exists(conversation_id)
    
    if workspace_id not in tasks_by_workspace[conversation_id]:
        tasks_by_workspace[conversation_id][workspace_id] = []
    if workspace_id not in task_counters_by_workspace[conversation_id]:
        task_counters_by_workspace[conversation_id][workspace_id] = 1
    if workspace_id not in workspaces_metadata[conversation_id]:
        # Auto-create workspace with ID as default name
        display_name = "Default Workspace" if workspace_id == "default" else workspace_id.replace("_", " ").title()
        workspaces_metadata[conversation_id][workspace_id] = {
            "name": display_name,
            "created_at": "auto-created"
        }

def _get_tasks(conversation_id: str, workspace_id: str = "default"):
    """Get tasks for specific workspace"""
    _ensure_workspace_exists(conversation_id, workspace_id)
    return tasks_by_workspace[conversation_id][workspace_id]

def _get_counter(conversation_id: str, workspace_id: str = "default"):
    """Get counter for specific workspace"""
    _ensure_workspace_exists(conversation_id, workspace_id)
    return task_counters_by_workspace[conversation_id][workspace_id]

def _increment_counter(conversation_id: str, workspace_id: str = "default"):
    """Increment counter for specific workspace"""
    _ensure_workspace_exists(conversation_id, workspace_id)
    task_counters_by_workspace[conversation_id][workspace_id] += 1

def add_task(conversation_id: str, title: str, description: str = "", status: str = "pending", workspace_id: str = "default") -> dict:
    if status not in VALID_STATUSES:
        return {
            "success": False,
            "error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}. Example: add_task('conv1', 'Task Title', 'Description', 'pending', 'workspace1')"
        }
    counter = _get_counter(conversation_id, workspace_id)
    task = {"id": counter, "title": title, "description": description, "status": status}
    _get_tasks(conversation_id, workspace_id).append(task)
    _increment_counter(conversation_id, workspace_id)
    result = {
        "success": True,
        "data": _get_tasks(conversation_id, workspace_id),
        "workspace_id": workspace_id
    }
    return DisplayRecommendations.add_to_json_result(result, "todo", "add_task")

def add_tasks_batch(conversation_id: str, tasks: list, workspace_id: str = "default"):
    """
    Add multiple tasks to a conversation workspace in order.

    Parameters:
    - conversation_id (str, required): Conversation ID
    - tasks (list of dicts, required): Each task dict must include:
        - title (str, required)
        - description (str, optional)
        - status (str, optional, one of ["pending","in_progress","completed","blocked"])
    - workspace_id (str, optional): Workspace ID (default: "default")

    Returns:
    - dict: Success with complete task list, or error with guidance

    Example:
    add_tasks_batch("conv123", [
        {"title":"Task 1", "description":"Do first", "status":"pending"},
        {"title":"Task 2", "description":"Do second"},
        {"title":"Task 3", "status":"in_progress"}
    ], "backend_dev")
    """
    if not isinstance(tasks, list):
        return {
            "success": False,
            "error": "Tasks parameter must be a list of dictionaries. Example: [{'title': 'Task 1'}, {'title': 'Task 2'}]"
        }
    
    failed_tasks = []
    validated_tasks = []
    
    # First pass: validate all tasks without adding any (atomic operation)
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            failed_tasks.append(f"Task {i}: must be a dictionary")
            continue
        if "title" not in task:
            failed_tasks.append(f"Task {i}: missing required 'title' field")
            continue
        
        title = task.get("title")
        description = task.get("description", "")
        status = task.get("status", "pending")
        
        if status not in VALID_STATUSES:
            failed_tasks.append(f"Task {i} ('{title}'): invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
            continue
            
        # Store validated task for later addition
        validated_tasks.append({"title": title, "description": description, "status": status})
    
    # If any validation failed, return error without adding any tasks
    if failed_tasks:
        return {
            "success": False,
            "error": "Some tasks failed validation: " + "; ".join(failed_tasks)
        }
    
    # Second pass: add all validated tasks
    for task_data in validated_tasks:
        counter = _get_counter(conversation_id, workspace_id)
        new_task = {"id": counter, "title": task_data["title"], "description": task_data["description"], "status": task_data["status"]}
        _get_tasks(conversation_id, workspace_id).append(new_task)
        _increment_counter(conversation_id, workspace_id)
    
    result = {
        "success": True,
        "data": _get_tasks(conversation_id, workspace_id),
        "workspace_id": workspace_id
    }
    return DisplayRecommendations.add_to_json_result(result, "todo", "add_tasks_batch")

def update_task(conversation_id: str, task_id: int, title: str = None, description: str = None, status: str = None, workspace_id: str = "default") -> dict:
    for t in _get_tasks(conversation_id, workspace_id):
        if t["id"] == task_id:
            if status is not None and status not in VALID_STATUSES:
                return {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}. Example: update_task('conv1', {task_id}, status='completed', workspace_id='workspace1')"
                }
            
            if title is not None:
                t["title"] = title
            if description is not None:
                t["description"] = description
            if status is not None:
                t["status"] = status
            
            # Create a copy of all tasks for the response
            tasks_copy = []
            for task in _get_tasks(conversation_id, workspace_id):
                task_copy = task.copy()
                
                # Add related notes hint only to the updated task
                if task["id"] == task_id and (status == "completed" or status == "in_progress"):
                    task_content = f"{task['title']} {task.get('description', '')}"
                    related_notes = _get_related_notes_hint(conversation_id, task_content)
                    if related_notes:
                        task_copy["related_notes_hint"] = related_notes
                        if status == "completed":
                            task_copy["notes_hint_message"] = f"Task completed! Found {len(related_notes)} related notes - consider recording your experience"
                        else:
                            task_copy["notes_hint_message"] = f"Found {len(related_notes)} potentially helpful notes for this task"
                
                tasks_copy.append(task_copy)
                
            result = {
                "success": True,
                "data": tasks_copy,
                "workspace_id": workspace_id
            }
            
            return DisplayRecommendations.add_to_json_result(result, "todo", "update_task")
    
    return {
        "success": False,
        "error": f"Task {task_id} not found in conversation '{conversation_id}' workspace '{workspace_id}'. Use list_tasks() to see available tasks."
    }

def delete_task(conversation_id: str, task_id: int, workspace_id: str = "default") -> dict:
    tasks = _get_tasks(conversation_id, workspace_id)
    original_count = len(tasks)
    tasks_by_workspace[conversation_id][workspace_id] = [t for t in tasks if t["id"] != task_id]
    new_count = len(tasks_by_workspace[conversation_id][workspace_id])
    
    if new_count < original_count:
        result = {
            "success": True,
            "data": _get_tasks(conversation_id, workspace_id),
            "workspace_id": workspace_id
        }
        return DisplayRecommendations.add_to_json_result(result, "todo", "delete_task")
    else:
        return {
            "success": False,
            "error": f"Task {task_id} not found in conversation '{conversation_id}' workspace '{workspace_id}'. Use list_tasks() to see available tasks."
        }

def get_task(conversation_id: str, task_id: int, workspace_id: str = "default") -> dict:
    for t in _get_tasks(conversation_id, workspace_id):
        if t["id"] == task_id:
            # Create a copy of the task to avoid modifying the original
            task_copy = t.copy()
            
            # Add related notes hint directly to the task data if notes integration is available
            task_content = f"{t['title']} {t.get('description', '')}"
            related_notes = _get_related_notes_hint(conversation_id, task_content)
            if related_notes:
                task_copy["related_notes_hint"] = related_notes
                task_copy["notes_hint_message"] = f"Found {len(related_notes)} potentially relevant notes - use notes tool to view details"
            
            result = {
                "success": True,
                "data": [task_copy],  # Return as single-item list for consistency
                "workspace_id": workspace_id
            }
            
            return DisplayRecommendations.add_to_json_result(result, "todo", "get_task")
    return {
        "success": False,
        "error": f"Task {task_id} not found in conversation '{conversation_id}' workspace '{workspace_id}'. Use list_tasks() to see available tasks."
    }

def list_tasks(conversation_id: str, workspace_id: str = "default") -> dict:
    tasks = _get_tasks(conversation_id, workspace_id)
    
    # Create copies of tasks with related notes hints
    tasks_with_notes = []
    for task in tasks:
        task_copy = task.copy()
        
        # Add related notes hint for each task if notes integration is available
        task_content = f"{task['title']} {task.get('description', '')}"
        related_notes = _get_related_notes_hint(conversation_id, task_content)
        if related_notes:
            task_copy["related_notes_hint"] = related_notes
            task_copy["notes_hint_message"] = f"Found {len(related_notes)} potentially relevant notes - use notes tool to view details"
        
        tasks_with_notes.append(task_copy)
    
    result = {
        "success": True,
        "data": tasks_with_notes,
        "workspace_id": workspace_id
    }
    return DisplayRecommendations.add_to_json_result(result, "todo", "list_tasks")

# Workspace management functions
def list_workspaces(conversation_id: str) -> dict:
    """List all workspaces in a conversation"""
    _ensure_conversation_exists(conversation_id)
    
    workspaces = []
    for workspace_id, metadata in workspaces_metadata.get(conversation_id, {}).items():
        task_count = len(tasks_by_workspace.get(conversation_id, {}).get(workspace_id, []))
        workspaces.append({
            "workspace_id": workspace_id,
            "workspace_name": metadata.get("name", workspace_id),
            "task_count": task_count,
            "created_at": metadata.get("created_at", "auto-created")
        })
    
    result = {
        "success": True,
        "data": workspaces
    }
    return DisplayRecommendations.add_to_json_result(result, "todo", "list_workspaces")

def list_all_tasks(conversation_id: str) -> dict:
    """List tasks from all workspaces in a conversation"""
    _ensure_conversation_exists(conversation_id)
    
    all_tasks = []
    for workspace_id, tasks in tasks_by_workspace.get(conversation_id, {}).items():
        for task in tasks:
            task_with_workspace = task.copy()
            task_with_workspace["workspace_id"] = workspace_id
            task_with_workspace["workspace_name"] = workspaces_metadata[conversation_id][workspace_id]["name"]
            
            # Add related notes hint for each task if notes integration is available
            task_content = f"{task['title']} {task.get('description', '')}"
            related_notes = _get_related_notes_hint(conversation_id, task_content)
            if related_notes:
                task_with_workspace["related_notes_hint"] = related_notes
                task_with_workspace["notes_hint_message"] = f"Found {len(related_notes)} potentially relevant notes - use notes tool to view details"
            
            all_tasks.append(task_with_workspace)
    
    result = {
        "success": True,
        "data": all_tasks
    }
    return DisplayRecommendations.add_to_json_result(result, "todo", "list_all_tasks")