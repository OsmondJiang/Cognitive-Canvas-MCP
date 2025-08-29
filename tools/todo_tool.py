tasks_by_conversation = {}
task_counters = {}

VALID_STATUSES = ["pending", "in_progress", "completed", "blocked"]

def _get_tasks(conversation_id: str):
    return tasks_by_conversation.setdefault(conversation_id, [])

def _get_counter(conversation_id: str):
    if conversation_id not in task_counters:
        task_counters[conversation_id] = 1
    return task_counters[conversation_id]

def _increment_counter(conversation_id: str):
    task_counters[conversation_id] += 1

def add_task(conversation_id: str, title: str, description: str = "", status: str = "pending") -> dict:
    if status not in VALID_STATUSES:
        return {
            "success": False,
            "error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}. Example: add_task('conv1', 'Task Title', 'Description', 'pending')"
        }
    counter = _get_counter(conversation_id)
    task = {"id": counter, "title": title, "description": description, "status": status}
    _get_tasks(conversation_id).append(task)
    _increment_counter(conversation_id)
    return {
        "success": True,
        "data": _get_tasks(conversation_id)
    }

def add_tasks_batch(conversation_id: str, tasks: list):
    """
    Add multiple tasks to a conversation in order.

    Parameters:
    - conversation_id (str, required): Conversation ID
    - tasks (list of dicts, required): Each task dict must include:
        - title (str, required)
        - description (str, optional)
        - status (str, optional, one of ["pending","in_progress","completed","blocked"])

    Returns:
    - dict: Success with complete task list, or error with guidance

    Example:
    add_tasks_batch("conv123", [
        {"title":"Task 1", "description":"Do first", "status":"pending"},
        {"title":"Task 2", "description":"Do second"},
        {"title":"Task 3", "status":"in_progress"}
    ])
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
        counter = _get_counter(conversation_id)
        new_task = {"id": counter, "title": task_data["title"], "description": task_data["description"], "status": task_data["status"]}
        _get_tasks(conversation_id).append(new_task)
        _increment_counter(conversation_id)
    
    return {
        "success": True,
        "data": _get_tasks(conversation_id)
    }

def update_task(conversation_id: str, task_id: int, title: str = None, description: str = None, status: str = None) -> dict:
    for t in _get_tasks(conversation_id):
        if t["id"] == task_id:
            if status is not None and status not in VALID_STATUSES:
                return {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}. Example: update_task('conv1', {task_id}, status='completed')"
                }
            
            if title is not None:
                t["title"] = title
            if description is not None:
                t["description"] = description
            if status is not None:
                t["status"] = status
                
            return {
                "success": True,
                "data": _get_tasks(conversation_id)
            }
    
    return {
        "success": False,
        "error": f"Task {task_id} not found in conversation '{conversation_id}'. Use list_tasks() to see available tasks."
    }

def delete_task(conversation_id: str, task_id: int) -> dict:
    tasks = _get_tasks(conversation_id)
    original_count = len(tasks)
    tasks_by_conversation[conversation_id] = [t for t in tasks if t["id"] != task_id]
    new_count = len(tasks_by_conversation[conversation_id])
    
    if new_count < original_count:
        return {
            "success": True,
            "data": _get_tasks(conversation_id)
        }
    else:
        return {
            "success": False,
            "error": f"Task {task_id} not found in conversation '{conversation_id}'. Use list_tasks() to see available tasks."
        }

def get_task(conversation_id: str, task_id: int) -> dict:
    for t in _get_tasks(conversation_id):
        if t["id"] == task_id:
            return {
                "success": True,
                "data": [t]  # Return as single-item list for consistency
            }
    return {
        "success": False,
        "error": f"Task {task_id} not found in conversation '{conversation_id}'. Use list_tasks() to see available tasks."
    }

def list_tasks(conversation_id: str) -> dict:
    tasks = _get_tasks(conversation_id)
    return {
        "success": True,
        "data": tasks
    }
    