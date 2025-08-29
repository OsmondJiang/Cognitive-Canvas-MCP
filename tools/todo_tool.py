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

# 原始函数
def add_task(conversation_id: str, title: str, description: str = "", status: str = "pending") -> dict:
    if status not in VALID_STATUSES:
        return {
            "status": "error",
            "message": f"Invalid status: {status}. Valid statuses: {VALID_STATUSES}",
            "valid_statuses": VALID_STATUSES
        }
    counter = _get_counter(conversation_id)
    task = {"id": counter, "title": title, "description": description, "status": status}
    _get_tasks(conversation_id).append(task)
    _increment_counter(conversation_id)
    return {
        "status": "success",
        "message": f"Task added: {task['id']} - {task['title']}",
        "task": task
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
    - dict: Results with status and details of each task added

    Example:
    add_tasks_batch("conv123", [
        {"title":"Task 1", "description":"Do first", "status":"pending"},
        {"title":"Task 2", "description":"Do second"},
        {"title":"Task 3", "status":"in_progress"}
    ])
    """
    results = []
    added_tasks = []
    for task in tasks:
        title = task.get("title")
        description = task.get("description", "")
        status = task.get("status", "pending")
        result = add_task(conversation_id, title, description, status)
        results.append(result)
        if result["status"] == "success":
            added_tasks.append(result["task"])
    
    return {
        "status": "success",
        "message": f"Batch operation completed. {len(added_tasks)} tasks added.",
        "added_tasks": added_tasks,
        "results": results
    }

def update_task(conversation_id: str, task_id: int, title: str = None, description: str = None, status: str = None) -> dict:
    for t in _get_tasks(conversation_id):
        if t["id"] == task_id:
            updated_fields = {}
            if title is not None:
                t["title"] = title
                updated_fields["title"] = title
            if description is not None:
                t["description"] = description
                updated_fields["description"] = description
            if status is not None:
                if status not in VALID_STATUSES:
                    return {
                        "status": "error",
                        "message": f"Invalid status: {status}. Valid statuses: {VALID_STATUSES}",
                        "valid_statuses": VALID_STATUSES
                    }
                t["status"] = status
                updated_fields["status"] = status
            return {
                "status": "success",
                "message": f"Task {task_id} updated",
                "task": t,
                "updated_fields": updated_fields
            }
    return {
        "status": "error",
        "message": f"Task {task_id} not found"
    }

def delete_task(conversation_id: str, task_id: int) -> dict:
    tasks = _get_tasks(conversation_id)
    original_count = len(tasks)
    tasks_by_conversation[conversation_id] = [t for t in tasks if t["id"] != task_id]
    new_count = len(tasks_by_conversation[conversation_id])
    
    if new_count < original_count:
        return {
            "status": "success",
            "message": f"Task {task_id} deleted"
        }
    else:
        return {
            "status": "error",
            "message": f"Task {task_id} not found"
        }

def get_task(conversation_id: str, task_id: int) -> dict:
    for t in _get_tasks(conversation_id):
        if t["id"] == task_id:
            return {
                "status": "success",
                "task": t
            }
    return {
        "status": "error", 
        "message": f"Task {task_id} not found"
    }

def list_tasks(conversation_id: str) -> dict:
    tasks = _get_tasks(conversation_id)
    return {
        "status": "success",
        "tasks": tasks,
        "total_count": len(tasks)
    }
    