from fastmcp import FastMCP
from typing import Annotated, Optional, List
from pydantic import Field
from tools import todo_tool
from tools.chat_fork import ChatForkManager
from tools.diagram_tool import DiagramManager
from tools.table_builder import TableBuilder

chat_fork_manager = ChatForkManager()
diagram_manager = DiagramManager()
table_builder_manager = TableBuilder()

mcp = FastMCP(name = "Cognitive Canvas", instructions="Use this MCP server to enhance your thinking and problem-solving capabilities through structured organization. This server helps you break down complex problems, visualize relationships, organize information systematically, and manage conversation contexts effectively. Choose the most appropriate tool for your specific need: TODO_COMMAND excels at task and project management with status tracking; DIAGRAM_TOOL is perfect for visualizing relationships, dependencies, and hierarchical structures; TABLE_BUILDER creates and manages tables and lists for data organization; CHAT_FORK manages conversation branches and contexts. While each tool has its specialty, you can combine them when tackling multi-faceted problems that require both planning and visualization.") 


@mcp.tool(name="todo_command", description="Use this tool specifically for task and project management - creating, tracking, and updating actionable work items with status tracking (pending, in_progress, completed, blocked). Best for breaking down complex projects into manageable tasks, monitoring progress, and ensuring nothing falls through the cracks. Use when you need to manage workflows, deadlines, or action items that require status updates over time.")
def todo_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation. All tasks will be scoped to this conversation.")], 
    action: Annotated[str, Field(description="The operation to perform on tasks", enum=["update", "delete", "get", "list", "add-batch"])], 
    # For update operations
    title: Annotated[Optional[str], Field(description="Task title/name. Optional for 'update'.", default=None)],
    description: Annotated[Optional[str], Field(description="Detailed description of the task", default="")],
    status: Annotated[Optional[str], Field(description="Task status", enum=["pending", "in_progress", "completed", "blocked"], default="pending")],
    # For update/delete/get operations
    task_id: Annotated[Optional[int], Field(description="Task ID. Required for 'update', 'delete', and 'get' actions.", default=None)],
    # For batch operations
    task_list: Annotated[Optional[list], Field(description="List of task dictionaries for batch operations. Each dict should contain 'title', optional 'description' and 'status'.", default=None)]
):
    """
    TODO Tool with Simple Parameter Interface
    
    Instead of using a complex 'params' dict, this tool accepts direct parameters
    making it easier for LLM to understand and call correctly.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Must be one of ["update", "delete", "get", "list", "add-batch"]
    - title (str): Task title (optional for 'update')
    - description (str): Task description (optional, default: "")
    - status (str): Task status (optional, default: "pending") - one of ["pending","in_progress","completed","blocked"]
    - task_id (int): Task ID (required for 'update', 'delete', 'get')
    - task_list (list): List of task dictionaries for batch operations (required for 'add-batch')

    Usage Examples:
    1. Update task: todo_command("conv1", "update", task_id=1, status="completed") 
    2. Delete task: todo_command("conv1", "delete", task_id=1)
    3. Get task: todo_command("conv1", "get", task_id=1)
    4. List tasks: todo_command("conv1", "list")
    5. Add batch: todo_command("conv1", "add-batch", task_list=[{"title":"Task1", "description":"Desc1"}, {"title":"Task2"}])
    """
    
    if action == "add-batch":
        if not task_list:
            return "Error: task_list is required for add-batch action"
        return todo_tool.add_tasks_batch(conversation_id, tasks=task_list)
    
    elif action == "update":
        if task_id is None:
            return "Error: task_id is required for update action"
        return todo_tool.update_task(conversation_id, task_id, title, description, status)
    
    elif action == "delete":
        if task_id is None:
            return "Error: task_id is required for delete action"
        return todo_tool.delete_task(conversation_id, task_id)
    
    elif action == "get":
        if task_id is None:
            return "Error: task_id is required for get action"
        return todo_tool.get_task(conversation_id, task_id)
    
    elif action == "list":
        return todo_tool.list_tasks(conversation_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: add-batch, update, delete, get, list"
    

@mcp.tool(name='chat_fork', description="The Chat Fork Tool manages conversation branches with pause/resume actions and search functionality. Use 'pause_topic' to save current state and switch topics, 'resume_topic' to return to paused discussions, and 'search' to search and visualize the conversation tree with current position marked. Perfect for managing complex multi-topic conversations with natural flow control.")
def chat_fork_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on conversation branches", enum=["pause_topic", "resume_topic", "search"])], 
    new_topic: Annotated[Optional[str], Field(description="The new topic to switch to. Required for 'pause_topic' action.", default=None)],
    current_context: Annotated[Optional[str], Field(description="Current discussion context and details. Optional for 'pause_topic' action.", default="")],
    progress_status: Annotated[Optional[str], Field(description="Current progress and status. Optional for 'pause_topic' action.", default="")],
    next_steps: Annotated[Optional[str], Field(description="Next steps or pending tasks. Optional for 'pause_topic' action.", default="")],
    pause_type: Annotated[Optional[str], Field(description="Type of pause: 'nested' (dive deeper into current topic) or 'parallel' (switch to different topic). Optional for 'pause_topic' action.", enum=["nested", "parallel"], default="nested")],
    bookmark: Annotated[Optional[str], Field(description="Bookmark name - for 'pause_topic': mark current topic as important bookmark; for 'resume_topic': jump to specific bookmark. Optional for both actions.", default="")],
    resume_type: Annotated[Optional[str], Field(description="How to resume: 'auto' (smart resume based on pause type), 'parent' (to parent topic), 'root' (to main topic), 'bookmark' (to specific bookmark). Optional for 'resume_topic' action.", enum=["auto", "parent", "root", "bookmark"], default="auto")],
    completed_summary: Annotated[Optional[str], Field(description="Summary of the completed topic when resuming. Optional for 'resume_topic' action.", default="")],
    # Render with optional search parameters
    search_query: Annotated[Optional[str], Field(description="Search query string for filtering search results. Optional for 'search' action.", default="")],
    search_scope: Annotated[Optional[str], Field(description="Search scope for filtering: 'all' (all content), 'topics' (topic names), 'context' (context info), 'bookmarks' (bookmarked topics), 'current_branch' (current branch only). Optional for 'search' action.", enum=["all", "topics", "context", "bookmarks", "current_branch"], default="all")],
    max_results: Annotated[Optional[int], Field(description="Maximum number of matching nodes to show in filtered search. Optional for 'search' action.", default=10)]
):
    """
    Chat Fork Tool - Intuitive Pause/Resume Interface
    
    Manages conversation topic branches with natural pause/resume actions.

    Core Actions:
    - pause_topic: Pause current discussion and switch to a new topic (automatically saves state)
    - resume_topic: Complete current topic and resume the previously paused discussion
    - search: Search and visualize the conversation tree structure with current position marked, optionally filtered by search

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): One of ["pause_topic", "resume_topic", "search"]
    
    For pause_topic:
    - new_topic (str, required): The new topic to switch to
    - current_context (str, optional): Current discussion context and details
    - progress_status (str, optional): Current progress and status
    - next_steps (str, optional): Next steps or pending tasks
    - pause_type (str, optional): "nested" for diving deeper, "parallel" for switching topics
    - bookmark (str, optional): Bookmark name to mark current topic as important
    
    For resume_topic:
    - completed_summary (str, optional): Summary of what was completed in the current topic
    - resume_type (str, optional): "auto" for smart resume, "parent" for parent topic, "root" for main topic, "bookmark" for specific bookmark
    - bookmark (str, optional): Name of bookmark to resume to (when resume_type="bookmark" or as direct target)
    
    For search:
    - search_query (str, optional): Search query to filter the tree display
    - search_scope (str, optional): "all", "topics", "context", "bookmarks", or "current_branch"  
    - max_results (int, optional): Maximum number of matching nodes to show (default: 10)

    Usage Examples:
    1. Nested pause with bookmark: chat_fork_command("conv1", "pause_topic", new_topic="API security details", current_context="Designing user authentication system", progress_status="Completed basic auth flow", next_steps="Implement JWT tokens", pause_type="nested", bookmark="auth_design")
    2. Parallel pause: chat_fork_command("conv1", "pause_topic", new_topic="Team meeting discussion", current_context="Working on database design", progress_status="50% complete", pause_type="parallel")  
    3. Auto resume: chat_fork_command("conv1", "resume_topic", completed_summary="Security implementation completed")
    4. Resume to bookmark: chat_fork_command("conv1", "resume_topic", bookmark="auth_design", completed_summary="Meeting done")
    5. Resume to specific level: chat_fork_command("conv1", "resume_topic", completed_summary="Meeting done", resume_type="root")
    6. Visualize conversation tree: chat_fork_command("conv1", "search")
    7. Filtered tree display: chat_fork_command("conv1", "search", search_query="database design")
    8. Search in bookmarks: chat_fork_command("conv1", "search", search_query="authentication", search_scope="bookmarks")
    9. Search current branch: chat_fork_command("conv1", "search", search_query="API", search_scope="current_branch", max_results=5)
    """
    
    if action == "pause_topic":
        if not new_topic:
            return "Error: new_topic is required for pause_topic action"
        return chat_fork_manager.pause_topic(
            conversation_id, 
            new_topic, 
            current_context or "", 
            progress_status or "", 
            next_steps or "", 
            pause_type or "nested",
            bookmark or ""
        )
    
    elif action == "resume_topic":
        return chat_fork_manager.resume_topic(
            conversation_id, 
            completed_summary or "", 
            resume_type or "auto",
            bookmark or ""
        )
    
    elif action == "search":
        # Return only the search result as a string, not wrapped in a dictionary
        return chat_fork_manager.search_conversation_tree(
            conversation_id=conversation_id, 
            search_query=search_query or "",
            search_scope=search_scope or "all",
            max_results=max_results or 10
        )

    else:
        return f"Unknown action: {action}. Valid actions: pause_topic, resume_topic, search"
    

@mcp.tool(name="diagram_tool", description="Use this tool for visualizing relationships, dependencies, and hierarchical structures between entities. Create flowcharts for processes, organizational charts for hierarchies, mind maps for concept exploration, or dependency trees for system architecture. Best for showing how things connect, flow, or depend on each other. Use when you need to map relationships, visualize system architecture, or show process flows rather than just listing items.")
def diagram_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on the diagram", enum=["set_diagram_type", "batch_add_nodes", "batch_update_nodes", "batch_add_edges", "batch_update_edges", "batch_operations", "render"])], 
    # For diagram type
    diagram_type: Annotated[Optional[str], Field(description="Type of diagram to create", enum=["flowchart", "sequence", "mindmap", "orgchart", "tree"], default=None)],
    # For batch operations
    nodes: Annotated[Optional[List[dict]], Field(description="Array of node objects for batch operations. Each object should have 'id', 'label', and optional 'metadata' fields.", default=None)],
    edges: Annotated[Optional[List[dict]], Field(description="Array of edge objects for batch operations. Each object should have 'source', 'target', 'type', and optional 'metadata' fields.", default=None)],
    operations: Annotated[Optional[List[dict]], Field(description="Array of mixed operations for batch_operations. Each object should have 'action' and 'data' fields.", default=None)]
):
    """
    Simplified Diagram Tool with Batch-Only Operations
    
    Manages diagram nodes and relationships using only batch operations to reduce complexity.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Operation type - ["set_diagram_type", "batch_add_nodes", "batch_update_nodes", "batch_add_edges", "batch_update_edges", "batch_operations", "render"]
    - diagram_type (str): Type of diagram (required for "set_diagram_type")
    - nodes (list): Array of node objects for batch node operations
    - edges (list): Array of edge objects for batch edge operations  
    - operations (list): Array of mixed operations for batch_operations

    Examples:
    1. Set diagram type: diagram_command("conv1", "set_diagram_type", diagram_type="flowchart")
    2. Add nodes: diagram_command("conv1", "batch_add_nodes", nodes=[{"id": "node1", "label": "Label1"}, {"id": "node2", "label": "Label2"}])
    3. Add edges: diagram_command("conv1", "batch_add_edges", edges=[{"source": "node1", "target": "node2", "type": "connects"}])
    4. Update nodes: diagram_command("conv1", "batch_update_nodes", nodes=[{"id": "node1", "label": "Updated Label1"}])
    5. Update edges: diagram_command("conv1", "batch_update_edges", edges=[{"index": 0, "type": "new_type"}])
    6. Mixed operations: diagram_command("conv1", "batch_operations", operations=[{"action": "add_node", "data": {"id": "n1", "label": "Node1"}}, {"action": "add_edge", "data": {"source": "n1", "target": "n2", "type": "link"}}])
    7. Render: diagram_command("conv1", "render")
    """
    
    if action == "set_diagram_type":
        if not diagram_type:
            return "Error: diagram_type is required for set_diagram_type action"
        return diagram_manager.set_diagram_type(conversation_id, diagram_type)
    
    elif action == "batch_add_nodes":
        if not nodes:
            return "Error: 'nodes' array is required for batch_add_nodes action"
        return diagram_manager.batch_add_nodes(conversation_id, nodes)
    
    elif action == "batch_update_nodes":
        if not nodes:
            return "Error: 'nodes' array is required for batch_update_nodes action"
        return diagram_manager.batch_update_nodes(conversation_id, nodes)
    
    elif action == "batch_add_edges":
        if not edges:
            return "Error: 'edges' array is required for batch_add_edges action"
        return diagram_manager.batch_add_edges(conversation_id, edges)
    
    elif action == "batch_update_edges":
        if not edges:
            return "Error: 'edges' array is required for batch_update_edges action"
        return diagram_manager.batch_update_edges(conversation_id, edges)
    
    elif action == "batch_operations":
        if not operations:
            return "Error: 'operations' array is required for batch_operations action"
        return diagram_manager.batch_operations(conversation_id, operations)
    
    elif action == "render":
        return diagram_manager.render(conversation_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: set_diagram_type, batch_add_nodes, batch_update_nodes, batch_add_edges, batch_update_edges, batch_operations, render"
    
@mcp.tool(
    name="table_builder",
    description="Use this tool for organizing and presenting structured data in tables, lists, and specialized formats. Create comparison tables, checklists, voting matrices, progress tables, or formatted lists when you need to organize information systematically. Best for data collection, comparison analysis, surveys, or any scenario where you need structured presentation of information rather than task management or relationship mapping."
)
def table_builder_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on the table builder", enum=["create", "batch_add_rows", "batch_update_rows", "batch_operations", "render", "metrics"])], 
    # For all operations
    structure_id: Annotated[Optional[str], Field(description="Unique identifier for the structure. Required for all actions.", default=None)],
    # For create operation
    template_type: Annotated[Optional[str], Field(description="Type of structure to create", enum=["simple_table", "task_list", "check_list", "numbered_list", "bulleted_list", "voting_table", "progress_table"], default=None)],
    columns: Annotated[Optional[List[str]], Field(description="List of column names for table structures. Optional for 'create' action.", default=None)],
    # For batch operations
    rows: Annotated[Optional[List[dict]], Field(description="Array of row objects for batch_add_rows. Each object should contain key-value pairs matching the structure columns.", default=None)],
    updates: Annotated[Optional[List[dict]], Field(description="Array of update objects for batch_update_rows. Each object should have 'index' and 'data' fields.", default=None)],
    operations: Annotated[Optional[List[dict]], Field(description="Array of mixed operations for batch_operations. Each object should have 'action' and 'data' fields.", default=None)]
):
    """
    Enhanced Table Builder Tool with Batch Operations Only
    
    Manages tables and lists with support for batch operations to reduce LLM tool calls.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Operation type - ["create", "batch_add_rows", "batch_update_rows", "batch_operations", "render", "metrics"]
    - structure_id (str): Structure identifier (required for all actions)
    - template_type (str): Type of structure (required for "create")
    - columns (list): Column names (optional for "create")
    - rows (list): Array of row data for batch_add_rows
    - updates (list): Array of update objects for batch_update_rows
    - operations (list): Array of mixed operations for batch_operations

    Usage Examples:
    1. Create structure: table_builder_command("conv1", "create", structure_id="tasks", template_type="task_list", columns=["Task", "Owner", "Status"])
    2. Batch add rows: table_builder_command("conv1", "batch_add_rows", structure_id="tasks", rows=[{"Task": "Review code", "Owner": "Alice", "Status": "Pending"}, {"Task": "Write tests", "Owner": "Bob", "Status": "In Progress"}])
    3. Batch update rows: table_builder_command("conv1", "batch_update_rows", structure_id="tasks", updates=[{"index": 0, "data": {"Status": "Completed"}}, {"index": 1, "data": {"Status": "Completed"}}])
    4. Mixed operations: table_builder_command("conv1", "batch_operations", structure_id="tasks", operations=[{"action": "add", "data": {"Task": "Deploy", "Owner": "Charlie", "Status": "Pending"}}, {"action": "update", "data": {"index": 0, "row_data": {"Status": "Done"}}}])
    5. Render: table_builder_command("conv1", "render", structure_id="tasks")
    6. Metrics: table_builder_command("conv1", "metrics", structure_id="tasks")
    """
    
    if action == "create":
        if not structure_id or not template_type:
            return "Error: structure_id and template_type are required for create action"
        return table_builder_manager.create_structure(conversation_id, structure_id, template_type, columns)
    
    elif action == "batch_add_rows":
        if not structure_id or not rows:
            return "Error: structure_id and rows array are required for batch_add_rows action"
        return table_builder_manager.batch_add_rows(conversation_id, structure_id, rows)
    
    elif action == "batch_update_rows":
        if not structure_id or not updates:
            return "Error: structure_id and updates array are required for batch_update_rows action"
        return table_builder_manager.batch_update_rows(conversation_id, structure_id, updates)
    
    elif action == "batch_operations":
        if not structure_id or not operations:
            return "Error: structure_id and operations array are required for batch_operations action"
        return table_builder_manager.batch_operations(conversation_id, structure_id, operations)
    
    elif action == "render":
        if not structure_id:
            return "Error: structure_id is required for render action"
        return table_builder_manager.render(conversation_id, structure_id)
    
    elif action == "metrics":
        if not structure_id:
            return "Error: structure_id is required for metrics action"
        return table_builder_manager.get_metrics(conversation_id, structure_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: create, batch_add_rows, batch_update_rows, batch_operations, render, metrics"

def main():
    """Main entry point for the MCP server when installed via pip"""
    mcp.run()


if __name__ == "__main__":
    main()
