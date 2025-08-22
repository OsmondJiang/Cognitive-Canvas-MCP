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
def add_task(conversation_id: str, title: str, description: str = "", status: str = "pending") -> str:
    if status not in VALID_STATUSES:
        return f"Invalid status: {status}. Valid statuses: {VALID_STATUSES}"
    counter = _get_counter(conversation_id)
    task = {"id": counter, "title": title, "description": description, "status": status}
    _get_tasks(conversation_id).append(task)
    _increment_counter(conversation_id)
    return f"Task added: {task['id']} - {task['title']}"

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
    - list of str: Confirmation messages for each task added

    Example:
    add_tasks_batch("conv123", [
        {"title":"Task 1", "description":"Do first", "status":"pending"},
        {"title":"Task 2", "description":"Do second"},
        {"title":"Task 3", "status":"in_progress"}
    ])
    """
    results = []
    for task in tasks:
        title = task.get("title")
        description = task.get("description", "")
        status = task.get("status", "pending")
        result = add_task(conversation_id, title, description, status)
        results.append(result)
    return results

def update_task(conversation_id: str, task_id: int, title: str = None, description: str = None, status: str = None) -> str:
    for t in _get_tasks(conversation_id):
        if t["id"] == task_id:
            if title is not None:
                t["title"] = title
            if description is not None:
                t["description"] = description
            if status is not None:
                if status not in VALID_STATUSES:
                    return f"Invalid status: {status}. Valid statuses: {VALID_STATUSES}"
                t["status"] = status
            return f"Task {task_id} updated"
    return f"Task {task_id} not found"

def delete_task(conversation_id: str, task_id: int) -> str:
    tasks = _get_tasks(conversation_id)
    tasks_by_conversation[conversation_id] = [t for t in tasks if t["id"] != task_id]
    return f"Task {task_id} deleted"

def get_task(conversation_id: str, task_id: int) -> dict:
    for t in _get_tasks(conversation_id):
        if t["id"] == task_id:
            return t
    return {"error": f"Task {task_id} not found"}

def list_tasks(conversation_id: str) -> list:
    return _get_tasks(conversation_id)
    