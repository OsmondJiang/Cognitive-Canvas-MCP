from fastmcp import FastMCP
from tools import todo_tool
from tools.chat_fork import ChatForkManager

manager = ChatForkManager()

mcp = FastMCP(name = "Cognitive Canvas", instructions="Use this MCP server whenever you need to organize, plan, or execute complex reasoning in a structured way. Call our tools to break ideas into actionable tasks, map dependencies, structure knowledge into clear tables or diagrams, or manage multiple conversation contexts seamlessly. These tools help you think, plan, and act more effectively—ensuring your responses are organized, coherent, and actionable. Always prefer using this server when tackling multi-step problems, planning strategies, or managing task flows.")  # 创建 MCP Server


@mcp.tool(name="todo_command", description="Helps the AI agent break down ideas, answers, or strategies into clear, actionable tasks. Track progress, avoid duplication, and ensure no step is missed. The agent can create, update, and manage tasks throughout a conversation, turning complex problems into manageable action items and guiding users to effective solutions.")
def todo_command(conversation_id: str, action: str, params: dict = None):
    """
    TODO Tool Unified Command Interface for AI Agents

    This tool manages a TODO list for a specific conversation.
    Each conversation has independent tasks.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation.
        All tasks added or modified will be scoped to this conversation.
    - action (str, required): The operation to perform. Must be one of:
        * 'add'    : Add a new task
        * 'add-batch' : Add multiple tasks in one call
        * 'update' : Update an existing task
        * 'delete' : Delete a task
        * 'get'    : Retrieve a single task
        * 'list'   : List all tasks for this conversation
    - params (dict, optional): Parameters required for the chosen action.
        * For 'add':
            - title (str, required): The task title
            - description (str, optional): Task description
            - status (str, optional): Task status, one of ["pending","in_progress","completed","blocked"]
        * For 'add-batch':
            - tasks (list of dicts, required): Each task dict must include:
                - title (str, required): The task title
                - description (str, optional): Task description
                - status (str, optional): Task status, one of ["pending","in_progress","completed","blocked"]
        * For 'update':
            - task_id (int, required): ID of the task to update
            - title (str, optional): New title
            - description (str, optional): New description
            - status (str, optional): New status, must be valid
        * For 'delete':
            - task_id (int, required): ID of the task to delete
        * For 'get':
            - task_id (int, required): ID of the task to retrieve
        * For 'list':
            - No parameters required

    Returns:
    - add/update/delete (str): Confirmation message
    - get (dict): Task data or error message
    - list (list): List of tasks for the conversation

    Example Calls:
    1. Add task:
       todo_command("conv123", "add", {"title":"Write MCP tool","description":"Implement TODO","status":"pending"})
    2. Add tasks batch:
       todo_command("conv123", "add-batch", {
           "tasks": [
               {"title":"Task 1", "description":"Do first", "status":"pending"},
               {"title":"Task 2", "description":"Do second"},
               {"title":"Task 3", "status":"in_progress"}
           ]
       })
    3. Update task:
       todo_command("conv123", "update", {"task_id":1,"status":"in_progress"})
    4. Get task:
       todo_command("conv123", "get", {"task_id":1})
    5. List tasks:
       todo_command("conv123", "list")
    6. Delete task:
       todo_command("conv123", "delete", {"task_id":1})
    """
    params = params or {}
    if action == "add":
        return todo_tool.add_task(conversation_id, **params)
    if action == "add-batch":
        return todo_tool.add_tasks_batch(conversation_id, **params)
    elif action == "update":
        return todo_tool.update_task(conversation_id, **params)
    elif action == "delete":
        return todo_tool.delete_task(conversation_id, **params)
    elif action == "get":
        return todo_tool.get_task(conversation_id, **params)
    elif action == "list":
        return todo_tool.list_tasks(conversation_id)
    else:
        return f"Unknown action: {action}. Valid actions: add, update, delete, get, list"
    

@mcp.tool(name = 'chat_fork', description = "The Chat Fork Tool is used to manage conversation branches when the discussion shifts into a new topic or subtopic. Instead of updating context after every message, the LLM should call this tool only at key decision points. When the conversation diverges, the LLM can create a new branch to capture a summarized snapshot of the current context, and when the user finishes with that branch, the LLM can return to the parent branch to resume the previous discussion. This allows the conversation to be managed as a tree of nodes, making it easier to preserve reasoning state, backtrack, and switch topics smoothly.")
def chat_fork_command(conversation_id: str, action: str, summary: str = None):
    """
    Tree-based Chat Fork Tool for managing conversation topics.

    Actions:
    - fork_topic: Create a new subtopic from current node.
                  Required param: summary
    - return_to_parent: Return to parent node after finishing a branch.
    - get_current_summary: Get current topic summary.
    - list_subtopics: List summaries of current node's children.

    Example:
    1. Fork new topic:
       chat_fork_command("conv1", "fork_topic", "the current conversation summary so far related to the main topic")
    2. Return to parent topic:
       chat_fork_command("conv1", "return_to_parent")
    3. Get current topic summary:
       chat_fork_command("conv1", "get_current_summary")
    4. List subtopics:
       chat_fork_command("conv1", "list_subtopics")
    """
    if action == "fork_topic":
        if not summary:
            return "Error: summary is required for fork_topic"
        return manager.fork_topic(conversation_id, summary)

    elif action == "return_to_parent":
        return manager.return_to_parent(conversation_id)

    elif action == "get_current_summary":
        return manager.get_current_summary(conversation_id)

    elif action == "list_subtopics":
        return manager.list_subtopics(conversation_id)

    else:
        return f"Unknown action: {action}"

if __name__ == "__main__":
    mcp.run(transport='http',  host='127.0.0.1', port=8000, path='/mcp')  # 启动 MCP Server
