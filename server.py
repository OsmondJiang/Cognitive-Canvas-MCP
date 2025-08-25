from fastmcp import FastMCP
from typing import Annotated, Optional
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
    action: Annotated[str, Field(description="The operation to perform on the diagram", enum=["set_diagram_type", "add_node", "update_node", "add_edge", "update_edge", "render"])], 
    # For diagram type
    diagram_type: Annotated[Optional[str], Field(description="Type of diagram to create", enum=["flowchart", "sequence", "mindmap", "orgchart", "tree"], default=None)],
    # For node operations
    node_id: Annotated[Optional[str], Field(description="Unique identifier for the node. Required for node operations.", default=None)],
    label: Annotated[Optional[str], Field(description="Display text/label for the node. Required for 'add_node', optional for 'update_node'.", default=None)],
    # For edge operations
    source: Annotated[Optional[str], Field(description="Source node ID for the edge. Required for 'add_edge'.", default=None)],
    target: Annotated[Optional[str], Field(description="Target node ID for the edge. Required for 'add_edge'.", default=None)],
    edge_type: Annotated[Optional[str], Field(description="Type/label of the relationship between nodes. Required for 'add_edge', optional for 'update_edge'.", default=None)],
    edge_index: Annotated[Optional[int], Field(description="Index of the edge to update. Required for 'update_edge'.", default=None)],
    # Optional metadata
    metadata: Annotated[Optional[dict], Field(description="Additional properties/metadata for nodes or edges", default=None)]
):
    """
    Diagram Tool with Simple Parameter Interface
    
    Manages diagram nodes and relationships with clear, direct parameters.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Must be one of ["set_diagram_type", "add_node", "update_node", "add_edge", "update_edge", "render"]
    - diagram_type (str): Type of diagram (required for "set_diagram_type") - one of ["flowchart", "sequence", "mindmap", "orgchart", "tree"]
    - node_id (str): Node identifier (required for node operations)
    - label (str): Node display label (required for "add_node", optional for "update_node")
    - source (str): Source node ID (required for "add_edge")
    - target (str): Target node ID (required for "add_edge")
    - edge_type (str): Edge relationship type (required for "add_edge", optional for "update_edge")
    - edge_index (int): Edge index (required for "update_edge")
    - metadata (dict): Additional properties (optional for all operations)

    Usage Examples:
    1. Set diagram type: diagram_command("conv1", "set_diagram_type", diagram_type="flowchart")
    2. Add node: diagram_command("conv1", "add_node", node_id="start", label="Start Process")
    3. Update node: diagram_command("conv1", "update_node", node_id="start", label="Begin Process")
    4. Add edge: diagram_command("conv1", "add_edge", source="start", target="process", edge_type="leads_to")
    5. Update edge: diagram_command("conv1", "update_edge", edge_index=0, edge_type="triggers")
    6. Render: diagram_command("conv1", "render")
    """
    
    if action == "set_diagram_type":
        if not diagram_type:
            return "Error: diagram_type is required for set_diagram_type action"
        return diagram_manager.set_diagram_type(conversation_id, diagram_type)
    
    elif action == "add_node":
        if not node_id or not label:
            return "Error: node_id and label are required for add_node action"
        return diagram_manager.add_node(conversation_id, node_id, label, metadata)
    
    elif action == "update_node":
        if not node_id:
            return "Error: node_id is required for update_node action"
        return diagram_manager.update_node(conversation_id, node_id, label, metadata)
    
    elif action == "add_edge":
        if not source or not target or not edge_type:
            return "Error: source, target, and edge_type are required for add_edge action"
        return diagram_manager.add_edge(conversation_id, source, target, edge_type, metadata)
    
    elif action == "update_edge":
        if edge_index is None:
            return "Error: edge_index is required for update_edge action"
        return diagram_manager.update_edge(conversation_id, edge_index, edge_type, metadata)
    
    elif action == "render":
        return diagram_manager.render(conversation_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: set_diagram_type, add_node, update_node, add_edge, update_edge, render"
    
@mcp.tool(
    name="structured_knowledge_tool",
    description="Use this tool whenever you need to create, update, and manage structured tables or lists within a conversation; each structure has a unique ID and a chosen template type such as simple_table, task_list, check_list, numbered_list, bulleted_list, voting_table, or progress_table; you can add or update rows, render the structure in Markdown and JSON, and automatically obtain metrics such as completion rates, checked rates, or voting distributions, allowing LLMs to reason over and present structured information efficiently."
)
def structured_knowledge_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on the structured knowledge", enum=["create", "add", "update", "render", "metrics"])], 
    # For all operations
    structure_id: Annotated[Optional[str], Field(description="Unique identifier for the structure. Required for all actions.", default=None)],
    # For create operation
    template_type: Annotated[Optional[str], Field(description="Type of structure to create", enum=["simple_table", "task_list", "check_list", "numbered_list", "bulleted_list", "voting_table", "progress_table"], default=None)],
    columns: Annotated[Optional[list], Field(description="List of column names for table structures. Optional for 'create' action.", default=None)],
    # For add operation
    row_data: Annotated[Optional[dict], Field(description="Dictionary containing the data for a new row or updates to an existing row. Keys should match column names.", default=None)],
    # For update operation  
    row_index: Annotated[Optional[int], Field(description="Zero-based index of the row to update. Required for 'update' action.", default=None)]
):
    """
    Structured Knowledge Tool with Simple Parameter Interface
    
    Manages tables and lists with clear, direct parameters.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Must be one of ["create", "add", "update", "render", "metrics"]
    - structure_id (str): Structure identifier (required for all actions)
    - template_type (str): Type of structure (required for "create") - one of ["simple_table", "task_list", "check_list", "numbered_list", "bulleted_list", "voting_table", "progress_table"]
    - columns (list): Column names (optional for "create")
    - row_data (dict): Row data to add/update (required for "add", "update")
    - row_index (int): Row index to update (required for "update")

    Usage Examples:
    1. Create structure: structured_knowledge_command("conv1", "create", structure_id="tasks", template_type="task_list", columns=["Task", "Owner", "Status"])
    2. Add row: structured_knowledge_command("conv1", "add", structure_id="tasks", row_data={"Task": "Review code", "Owner": "Alice", "Status": "Pending"})
    3. Update row: structured_knowledge_command("conv1", "update", structure_id="tasks", row_index=0, row_data={"Status": "Completed"})
    4. Render: structured_knowledge_command("conv1", "render", structure_id="tasks")
    5. Metrics: structured_knowledge_command("conv1", "metrics", structure_id="tasks")
    """
    
    if action == "create":
        if not structure_id or not template_type:
            return "Error: structure_id and template_type are required for create action"
        return structured_knowledge_manager.create_structure(conversation_id, structure_id, template_type, columns)
    
    elif action == "add":
        if not structure_id or not row_data:
            return "Error: structure_id and row_data are required for add action"
        return structured_knowledge_manager.add_row(conversation_id, structure_id, row_data)
    
    elif action == "update":
        if not structure_id or row_index is None or not row_data:
            return "Error: structure_id, row_index, and row_data are required for update action"
        return structured_knowledge_manager.update_row(conversation_id, structure_id, row_index, row_data)
    
    elif action == "render":
        if not structure_id:
            return "Error: structure_id is required for render action"
        return structured_knowledge_manager.render(conversation_id, structure_id)
    
    elif action == "metrics":
        if not structure_id:
            return "Error: structure_id is required for metrics action"
        return structured_knowledge_manager.get_metrics(conversation_id, structure_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: create, add, update, render, metrics"

if __name__ == "__main__":
    mcp.run(transport='http',  host='127.0.0.1', port=8000, path='/mcp')  # 启动 MCP Server
