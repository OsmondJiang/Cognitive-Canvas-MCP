from fastmcp import FastMCP
from typing import Annotated, Optional, List
from pydantic import Field
from tools import todo_tool
from tools.chat_fork import ChatForkManager
from tools.diagram_tool import DiagramManager
from tools.structured_knowledge_tool import StructuredKnowledgeManager

chat_fork_manager = ChatForkManager()
diagram_manager = DiagramManager()
structured_knowledge_manager = StructuredKnowledgeManager()

mcp = FastMCP(name = "Cognitive Canvas", instructions="Use this MCP server whenever you need to organize, plan, or execute complex reasoning in a structured way. Call our tools to break ideas into actionable tasks, map dependencies, structure knowledge into clear tables or diagrams, or manage multiple conversation contexts seamlessly. These tools help you think, plan, and act more effectively—ensuring your responses are organized, coherent, and actionable. Always prefer using this server when tackling multi-step problems, planning strategies, or managing task flows.")  # 创建 MCP Server


@mcp.tool(name="todo_command", description="Helps the AI agent break down ideas, answers, or strategies into clear, actionable tasks. Track progress, avoid duplication, and ensure no step is missed. The agent can create, update, and manage tasks throughout a conversation, turning complex problems into manageable action items and guiding users to effective solutions.")
def todo_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation. All tasks will be scoped to this conversation.")], 
    action: Annotated[str, Field(description="The operation to perform on tasks", enum=["add", "update", "delete", "get", "list", "add-batch"])], 
    # For add/update operations
    title: Annotated[Optional[str], Field(description="Task title/name. Required for 'add' action, optional for 'update'.", default=None)],
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
    - action (str, required): Must be one of ["add", "update", "delete", "get", "list", "add-batch"]
    - title (str): Task title (required for 'add', optional for 'update')
    - description (str): Task description (optional, default: "")
    - status (str): Task status (optional, default: "pending") - one of ["pending","in_progress","completed","blocked"]
    - task_id (int): Task ID (required for 'update', 'delete', 'get')
    - task_list (list): List of task dictionaries for batch operations (required for 'add-batch')

    Usage Examples:
    1. Add task: todo_command("conv1", "add", title="Write docs", description="API documentation", status="pending")
    2. Update task: todo_command("conv1", "update", task_id=1, status="completed") 
    3. Delete task: todo_command("conv1", "delete", task_id=1)
    4. Get task: todo_command("conv1", "get", task_id=1)
    5. List tasks: todo_command("conv1", "list")
    6. Add batch: todo_command("conv1", "add-batch", task_list=[{"title":"Task1", "description":"Desc1"}, {"title":"Task2"}])
    """
    
    if action == "add":
        if not title:
            return "Error: title is required for add action"
        return todo_tool.add_task(conversation_id, title, description, status)
    
    elif action == "add-batch":
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
        return f"Unknown action: {action}. Valid actions: add, add-batch, update, delete, get, list"
    

@mcp.tool(name='chat_fork', description="The Chat Fork Tool is used to manage conversation branches when the discussion shifts into a new topic or subtopic. Instead of updating context after every message, the LLM should call this tool only at key decision points. When the conversation diverges, the LLM can create a new branch to capture a summarized snapshot of the current context, and when the user finishes with that branch, the LLM can return to the parent branch to resume the previous discussion. This allows the conversation to be managed as a tree of nodes, making it easier to preserve reasoning state, backtrack, and switch topics smoothly.")
def chat_fork_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on conversation branches", enum=["fork_topic", "return_to_parent", "get_current_summary", "list_subtopics"])], 
    summary: Annotated[Optional[str], Field(description="Summary description of the current topic/branch. Required only for 'fork_topic' action.", default=None)]
):
    """
    Chat Fork Tool with Simple Parameter Interface
    
    Manages conversation topic branches with clear, direct parameters.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Must be one of ["fork_topic", "return_to_parent", "get_current_summary", "list_subtopics"]
    - summary (str): Topic summary (required only for "fork_topic" action)

    Usage Examples:
    1. Fork new topic: chat_fork_command("conv1", "fork_topic", summary="Discussing authentication implementation")
    2. Return to parent: chat_fork_command("conv1", "return_to_parent") 
    3. Get current summary: chat_fork_command("conv1", "get_current_summary")
    4. List subtopics: chat_fork_command("conv1", "list_subtopics")
    """
    if action == "fork_topic":
        if not summary:
            return "Error: summary is required for fork_topic action"
        return chat_fork_manager.fork_topic(conversation_id, summary)

    elif action == "return_to_parent":
        return chat_fork_manager.return_to_parent(conversation_id)

    elif action == "get_current_summary":
        return chat_fork_manager.get_current_summary(conversation_id)

    elif action == "list_subtopics":
        return chat_fork_manager.list_subtopics(conversation_id)

    else:
        return f"Unknown action: {action}. Valid actions: fork_topic, return_to_parent, get_current_summary, list_subtopics"
    

@mcp.tool(name="diagram_tool", description="Use this tool whenever you need to capture, manage, and visualize complex relationships or dependencies between entities such as tasks, systems, or concepts within a conversation; you can add or update nodes and edges with optional metadata, set the desired diagram type from flowchart, sequence, mindmap, orgchart, or tree, and then render a complete textual diagram that includes both a structured Markdown table of relationships and a readable text-based graph, allowing you to easily track dependencies, hierarchies, and interactions for reasoning or presentation purposes.")
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
    name="structured_knowledge_tool",
    description="Use this tool whenever you need to create, update, and manage structured tables or lists within a conversation; each structure has a unique ID and a chosen template type such as simple_table, task_list, check_list, numbered_list, bulleted_list, voting_table, or progress_table; you can batch add or update rows, render the structure in Markdown and JSON, and automatically obtain metrics such as completion rates, checked rates, or voting distributions, allowing LLMs to reason over and present structured information efficiently."
)
def structured_knowledge_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on the structured knowledge", enum=["create", "batch_add_rows", "batch_update_rows", "batch_operations", "render", "metrics"])], 
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
    Enhanced Structured Knowledge Tool with Batch Operations Only
    
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
    1. Create structure: structured_knowledge_command("conv1", "create", structure_id="tasks", template_type="task_list", columns=["Task", "Owner", "Status"])
    2. Batch add rows: structured_knowledge_command("conv1", "batch_add_rows", structure_id="tasks", rows=[{"Task": "Review code", "Owner": "Alice", "Status": "Pending"}, {"Task": "Write tests", "Owner": "Bob", "Status": "In Progress"}])
    3. Batch update rows: structured_knowledge_command("conv1", "batch_update_rows", structure_id="tasks", updates=[{"index": 0, "data": {"Status": "Completed"}}, {"index": 1, "data": {"Status": "Completed"}}])
    4. Mixed operations: structured_knowledge_command("conv1", "batch_operations", structure_id="tasks", operations=[{"action": "add", "data": {"Task": "Deploy", "Owner": "Charlie", "Status": "Pending"}}, {"action": "update", "data": {"index": 0, "row_data": {"Status": "Done"}}}])
    5. Render: structured_knowledge_command("conv1", "render", structure_id="tasks")
    6. Metrics: structured_knowledge_command("conv1", "metrics", structure_id="tasks")
    """
    
    if action == "create":
        if not structure_id or not template_type:
            return "Error: structure_id and template_type are required for create action"
        return structured_knowledge_manager.create_structure(conversation_id, structure_id, template_type, columns)
    
    elif action == "batch_add_rows":
        if not structure_id or not rows:
            return "Error: structure_id and rows array are required for batch_add_rows action"
        return structured_knowledge_manager.batch_add_rows(conversation_id, structure_id, rows)
    
    elif action == "batch_update_rows":
        if not structure_id or not updates:
            return "Error: structure_id and updates array are required for batch_update_rows action"
        return structured_knowledge_manager.batch_update_rows(conversation_id, structure_id, updates)
    
    elif action == "batch_operations":
        if not structure_id or not operations:
            return "Error: structure_id and operations array are required for batch_operations action"
        return structured_knowledge_manager.batch_operations(conversation_id, structure_id, operations)
    
    elif action == "render":
        if not structure_id:
            return "Error: structure_id is required for render action"
        return structured_knowledge_manager.render(conversation_id, structure_id)
    
    elif action == "metrics":
        if not structure_id:
            return "Error: structure_id is required for metrics action"
        return structured_knowledge_manager.get_metrics(conversation_id, structure_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: create, batch_add_rows, batch_update_rows, batch_operations, render, metrics"

if __name__ == "__main__":
    mcp.run(transport='http',  host='127.0.0.1', port=8000, path='/mcp')  # 启动 MCP Server
