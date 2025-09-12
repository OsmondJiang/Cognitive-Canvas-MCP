from fastmcp import FastMCP
from typing import Annotated, Optional, List
from pydantic import Field
from tools import todo_tool
from tools.chat_fork import ChatForkManager
from tools.relationship_mapper import RelationshipMapper
from tools.table_builder import TableBuilder
from tools.statistical_analyzer import StatisticalAnalyzer
from tools.notes import NotesManager

chat_fork_manager = ChatForkManager()
relationship_mapper_manager = RelationshipMapper()
table_builder_manager = TableBuilder()
statistical_analyzer_manager = StatisticalAnalyzer()
notes_manager = NotesManager()

mcp = FastMCP(name = "Cognitive Canvas", instructions="""**REQUIRED: ALL TOOL OUTPUTS ARE HIDDEN FROM USERS** - Users cannot see any tool output. You MUST include relevant tool output content in your response when necessary. Each tool output contains a '_show_to_user' field with specific display requirements.

Use this MCP server to enhance your thinking and problem-solving capabilities through structured organization, knowledge management, and statistical analysis. This server transforms AI into a research-grade cognitive workspace with six specialized tools: 

**TODO_COMMAND** for systematic task and project management with status tracking AND auto-creating workspace isolation;

**NOTES** for recording and retrieving knowledge, experiences, and insights with intelligent search capabilities;

**RELATIONSHIP_MAPPER** for visualizing complex dependencies, relationships, and system architectures; 

**TABLE_BUILDER** for organizing unstructured information into structured formats with automated metrics; 

**CHAT_FORK** for managing conversation branches and maintaining context across topic switches; 

**STATISTICAL_ANALYZER** for automated statistical analysis, hypothesis testing, categorical data analysis (chi-square tests), and comprehensive data exploration. 

Together, these tools enable systematic reasoning, persistent memory, knowledge accumulation, data-driven insights, and PhD-level analytical capabilities. Choose tools strategically: use TODO for planning and project organization, NOTES for knowledge management and experience tracking, RELATIONSHIP_MAPPER for visualization, TABLE_BUILDER for data organization, CHAT_FORK for context management, and STATISTICAL_ANALYZER for both numerical and categorical data analysis.

**SIMPLIFIED: Auto-Creating Workspaces** - TODO_COMMAND now features zero-management workspace isolation. Just specify any workspace_id when adding tasks and the workspace will be automatically created with smart naming. No manual workspace management needed!""") 


@mcp.tool(name="todo_command", description="**REQUIRED: Tool output is not visible to users - you MUST display the tool's output in your response when necessary.** Use this tool specifically for task and project management - creating, tracking, and updating actionable work items with status tracking (pending, in_progress, completed, blocked). Best for breaking down complex projects into manageable tasks, monitoring progress, and ensuring nothing falls through the cracks. Use when you need to manage workflows, deadlines, or action items that require status updates over time.")
def todo_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation. All tasks will be scoped to this conversation.")], 
    action: Annotated[str, Field(description="The operation to perform on tasks", enum=["update", "delete", "get", "list", "add-batch", "list_workspaces", "list_all_tasks"])], 
    # Workspace support
    workspace_id: Annotated[Optional[str], Field(description="Workspace identifier for task isolation. Default: 'default'. Used to organize tasks by project, phase, or category. Auto-creates workspace if it doesn't exist.", default="default")],
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
    Enhanced TODO Tool with Auto-Creating Workspace Support
    
    Instead of using a complex 'params' dict, this tool accepts direct parameters
    making it easier for LLM to understand and call correctly.

    SIMPLIFIED: Auto-Creating Workspace Support
    - workspace_id: Organize tasks by project, phase, team, or category
    - Workspaces are automatically created when first used
    - No need to explicitly create workspaces

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Must be one of ["update", "delete", "get", "list", "add-batch", "list_workspaces", "list_all_tasks"]
    - workspace_id (str, optional): Workspace identifier (default: "default") - auto-creates if needed
    - title (str): Task title (optional for 'update')
    - description (str): Task description (optional, default: "")
    - status (str): Task status (optional, default: "pending") - one of ["pending","in_progress","completed","blocked"]
    - task_id (int): Task ID (required for 'update', 'delete', 'get')
    - task_list (list): List of task dictionaries for batch operations (required for 'add-batch')

    Usage Examples:
    1. Add tasks to workspace (auto-creates): todo_command("conv1", "add-batch", workspace_id="backend_dev", task_list=[{"title":"API Design", "status":"pending"}])
    2. Update task: todo_command("conv1", "update", workspace_id="backend_dev", task_id=1, status="completed") 
    3. List tasks in workspace: todo_command("conv1", "list", workspace_id="backend_dev")
    4. List all workspaces: todo_command("conv1", "list_workspaces")
    5. List tasks from all workspaces: todo_command("conv1", "list_all_tasks")

    Workspace Auto-Creation Examples:
    - Add task to "frontend_team" - workspace auto-created
    - Add task to "urgent_tasks" - workspace auto-created  
    - Add task to "phase_1" - workspace auto-created
    """
    
    if action == "add-batch":
        if not task_list:
            return "Error: task_list is required for add-batch action"
        return todo_tool.add_tasks_batch(conversation_id, tasks=task_list, workspace_id=workspace_id)
    
    elif action == "update":
        if task_id is None:
            return "Error: task_id is required for update action"
        return todo_tool.update_task(conversation_id, task_id, title, description, status, workspace_id=workspace_id)
    
    elif action == "delete":
        if task_id is None:
            return "Error: task_id is required for delete action"
        return todo_tool.delete_task(conversation_id, task_id, workspace_id=workspace_id)
    
    elif action == "get":
        if task_id is None:
            return "Error: task_id is required for get action"
        return todo_tool.get_task(conversation_id, task_id, workspace_id=workspace_id)
    
    elif action == "list":
        return todo_tool.list_tasks(conversation_id, workspace_id=workspace_id)
    
    elif action == "list_workspaces":
        return todo_tool.list_workspaces(conversation_id)
    
    elif action == "list_all_tasks":
        return todo_tool.list_all_tasks(conversation_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: add-batch, update, delete, get, list, list_workspaces, list_all_tasks"
    

@mcp.tool(name='chat_fork', description="**REQUIRED: Tool output is not visible to users - you MUST display the tool's output in your response when necessary.** The Chat Fork Tool manages conversation branches with pause/resume actions and search functionality. Use 'pause_topic' to save current state and switch topics, 'resume_topic' to return to paused discussions, and 'search' to search and visualize the conversation tree with current position marked. Perfect for managing complex multi-topic conversations with natural flow control.")
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
    

@mcp.tool(name="relationship_mapper", description="**REQUIRED: Tool output is not visible to users - you MUST display the tool's output in your response when necessary.** Use this tool for visualizing relationships, dependencies, and hierarchical structures between entities. Create flowcharts for processes, organizational charts for hierarchies, mind maps for concept exploration, or dependency trees for system architecture. Best for showing how things connect, flow, or depend on each other. Use when you need to map relationships, visualize system architecture, or show process flows rather than just listing items.")
def relationship_mapper_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on the relationship mapper", enum=["set_visualization_type", "batch_add_nodes", "batch_update_nodes", "batch_add_edges", "batch_update_edges", "batch_operations", "get_visualization_content", "list_workspaces"])], 
    # For workspace management
    workspace_id: Annotated[Optional[str], Field(description="Workspace identifier for task isolation. If not provided, defaults to 'default'. Auto-creates workspace if it doesn't exist.", default=None)],
    # For diagram type
    diagram_type: Annotated[Optional[str], Field(description="Type of diagram to create", enum=["flowchart", "sequence", "mindmap", "orgchart", "tree"], default=None)],
    # For batch operations
    nodes: Annotated[Optional[List[dict]], Field(description="Array of node objects for batch operations. Each object should have 'id', 'label', and optional 'metadata' fields.", default=None)],
    edges: Annotated[Optional[List[dict]], Field(description="Array of edge objects for batch operations. Each object should have 'source', 'target', 'type', and optional 'metadata' fields.", default=None)],
    operations: Annotated[Optional[List[dict]], Field(description="Array of mixed operations for batch_operations. Each object should have 'action' and 'data' fields.", default=None)]
):
    """
    Simplified Diagram Tool with Batch-Only Operations and Workspace Support
    
    Manages diagram nodes and relationships using only batch operations to reduce complexity.
    Auto-creates workspaces on first use with smart naming convention.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Operation type - ["set_visualization_type", "batch_add_nodes", "batch_update_nodes", "batch_add_edges", "batch_update_edges", "batch_operations", "get_visualization_content", "list_workspaces"]
    - workspace_id (str, optional): Workspace identifier for isolation. Defaults to 'default'. Auto-creates if needed.
    - visualization_type (str): Type of visualization (required for "set_visualization_type")
    - nodes (list): Array of node objects for batch node operations
    - edges (list): Array of edge objects for batch edge operations  
    - operations (list): Array of mixed operations for batch_operations

    Examples:
    1. Set visualization type: relationship_mapper_command("conv1", "set_visualization_type", workspace_id="project1", diagram_type="flowchart")
    2. Add nodes: relationship_mapper_command("conv1", "batch_add_nodes", workspace_id="project1", nodes=[{"id": "node1", "label": "Label1"}, {"id": "node2", "label": "Label2"}])
    3. Add edges: relationship_mapper_command("conv1", "batch_add_edges", workspace_id="project1", edges=[{"source": "node1", "target": "node2", "type": "connects"}])
    4. Update nodes: relationship_mapper_command("conv1", "batch_update_nodes", workspace_id="project1", nodes=[{"id": "node1", "label": "Updated Label1"}])
    5. Update edges: relationship_mapper_command("conv1", "batch_update_edges", workspace_id="project1", edges=[{"index": 0, "type": "new_type"}])
    6. Mixed operations: relationship_mapper_command("conv1", "batch_operations", workspace_id="project1", operations=[{"action": "add_node", "data": {"id": "n1", "label": "Node1"}}, {"action": "add_edge", "data": {"source": "n1", "target": "n2", "type": "link"}}])
    7. Get visualization content: relationship_mapper_command("conv1", "get_visualization_content", workspace_id="project1") - Returns formatted content that should be displayed to the user
    8. List workspaces: relationship_mapper_command("conv1", "list_workspaces")
    """
    
    # Auto-assign workspace_id if not provided
    if not workspace_id:
        workspace_id = "default"
    
    if action == "list_workspaces":
        return relationship_mapper_manager.list_workspaces(conversation_id)
    
    elif action == "set_visualization_type":
        if not diagram_type:
            return "Error: diagram_type is required for set_visualization_type action"
        return relationship_mapper_manager.set_visualization_type(conversation_id, workspace_id, diagram_type)
    
    elif action == "batch_add_nodes":
        if not nodes:
            return "Error: 'nodes' array is required for batch_add_nodes action"
        return relationship_mapper_manager.batch_add_nodes(conversation_id, workspace_id, nodes)
    
    elif action == "batch_update_nodes":
        if not nodes:
            return "Error: 'nodes' array is required for batch_update_nodes action"
        return relationship_mapper_manager.batch_update_nodes(conversation_id, workspace_id, nodes)
    
    elif action == "batch_add_edges":
        if not edges:
            return "Error: 'edges' array is required for batch_add_edges action"
        return relationship_mapper_manager.batch_add_edges(conversation_id, workspace_id, edges)
    
    elif action == "batch_update_edges":
        if not edges:
            return "Error: 'edges' array is required for batch_update_edges action"
        return relationship_mapper_manager.batch_update_edges(conversation_id, workspace_id, edges)
    
    elif action == "batch_operations":
        if not operations:
            return "Error: 'operations' array is required for batch_operations action"
        return relationship_mapper_manager.batch_operations(conversation_id, workspace_id, operations)
    
    elif action == "get_visualization_content":
        return relationship_mapper_manager.get_visualization_content(conversation_id, workspace_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: set_visualization_type, batch_add_nodes, batch_update_nodes, batch_add_edges, batch_update_edges, batch_operations, get_visualization_content, list_workspaces"
    
@mcp.tool(
    name="table_builder",
    description="**REQUIRED: Tool output is not visible to users - you MUST display the tool's output in your response when necessary.** Use this tool for organizing and presenting structured data in tables, lists, and specialized formats. Create comparison tables, checklists, voting matrices, progress tables, or formatted lists when you need to organize information systematically. Best for data collection, comparison analysis, surveys, or any scenario where you need structured presentation of information rather than task management or relationship mapping."
)
def table_builder_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")], 
    action: Annotated[str, Field(description="The operation to perform on the table builder", enum=["create", "batch_add_rows", "batch_update_rows", "batch_operations", "get_formatted_table", "metrics"])], 
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
    - action (str, required): Operation type - ["create", "batch_add_rows", "batch_update_rows", "batch_operations", "get_formatted_table", "metrics"]
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
    5. Get formatted table: table_builder_command("conv1", "get_formatted_table", structure_id="tasks") - Returns formatted content for user display
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
    
    elif action == "get_formatted_table":
        if not structure_id:
            return "Error: structure_id is required for get_formatted_table action"
        return table_builder_manager.get_formatted_table(conversation_id, structure_id)
    
    elif action == "metrics":
        if not structure_id:
            return "Error: structure_id is required for metrics action"
        return table_builder_manager.get_metrics(conversation_id, structure_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: create, batch_add_rows, batch_update_rows, batch_operations, get_formatted_table, metrics"

@mcp.tool(name="statistical_analyzer", description="**REQUIRED: Tool output is not visible to users - you MUST display the tool's output in your response when necessary.** Use this tool for automated statistical analysis and data exploration. Automatically selects appropriate statistical methods (t-tests, ANOVA, correlation analysis, chi-square tests) based on data structure. Supports both numerical data analysis (descriptive statistics, hypothesis testing) and categorical data analysis (frequency distributions, chi-square independence tests). Perfect for data exploration, comparing groups, validating hypotheses, analyzing categorical relationships, and generating statistical reports. Best for researchers, analysts, and anyone who needs comprehensive statistical analysis.")
def statistical_analyzer(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")],
    action: Annotated[str, Field(description="The operation to perform", enum=["analyze", "get_analysis_report"])],
    workspace_id: Annotated[str, Field(description="Unique identifier for the workspace. Use 'default' for main workspace.", default="default")],
    
    # Data input (supports multiple formats)
    data: Annotated[Optional[dict], Field(description="Single dataset or paired data (e.g., {'before': [1,2,3], 'after': [4,5,6]}) for analysis", default=None)],
    groups: Annotated[Optional[dict], Field(description="Multiple groups for comparison (e.g., {'group_a': [1,2,3], 'group_b': [4,5,6], 'group_c': [7,8,9]})", default=None)],
    
    # Analysis configuration
    analysis_type: Annotated[str, Field(description="Type of analysis - 'auto' automatically detects based on data structure", enum=["auto", "descriptive", "comprehensive_descriptive", "paired_comparison", "two_group_comparison", "multi_group_comparison", "correlation_analysis", "frequency_analysis", "chi_square_test"], default="auto")],
    
    # Output control
    output_format: Annotated[str, Field(description="Format of the analysis report", enum=["simple", "comprehensive", "academic", "business"], default="comprehensive")],
    confidence_level: Annotated[float, Field(description="Confidence level for statistical tests (e.g., 0.95 for 95%)", default=0.95)]
):
    """
    Statistical Evidence Tool for Evidence-Based Analysis
    
    Unified tool for all statistical analysis needs. Automatically performs appropriate statistical 
    analysis based on data structure and generates comprehensive reports with statistical conclusions.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Operation type - ["analyze", "get_analysis_report"]
    - workspace_id (str): Workspace identifier for data isolation (default: "default")
    - data (dict, optional): Data for analysis (paired/related variables)
    - groups (dict, optional): Groups for comparison (independent groups)
    - analysis_type (str): Type of analysis (default: "auto" for automatic detection)
    - output_format (str): Report format - "simple", "comprehensive", "academic", or "business"
    - confidence_level (float): Confidence level for statistical tests (default: 0.95)

    Usage Examples:
    1. Auto-detect analysis: statistical_analyzer("conv1", "analyze", workspace_id="default", data={"before": [70,72,68], "after": [78,80,76]})
    2. Group comparison: statistical_analyzer("conv1", "analyze", workspace_id="default", groups={"React": [85,87,83], "Vue": [78,82,80], "Angular": [88,90,85]})
    3. Paired comparison: statistical_analyzer("conv1", "analyze", workspace_id="default", data={"baseline": [70,72,68], "treatment": [78,80,76]}, analysis_type="paired_comparison")
    4. Correlation analysis: statistical_analyzer("conv1", "analyze", workspace_id="default", data={"experience": [1,3,5,7], "performance": [65,75,85,95]}, analysis_type="correlation_analysis")
    5. Chi-square test: statistical_analyzer("conv1", "analyze", workspace_id="default", data={"age_group": ["18-25", "26-35", "36-45"], "product_preference": ["Electronics", "Books", "Fashion"]}, analysis_type="chi_square_test")
    6. Frequency analysis: statistical_analyzer("conv1", "analyze", workspace_id="default", data={"feedback": ["Excellent", "Good", "Average", "Poor"]}, analysis_type="frequency_analysis")
    7. Generate analysis report: statistical_analyzer("conv1", "get_analysis_report", workspace_id="default") - Returns comprehensive statistical report for user presentation
    """
    
    if action == "analyze":
        if not data and not groups:
            return "Error: Either 'data' or 'groups' is required for analyze action"
        return statistical_analyzer_manager.analyze(conversation_id, workspace_id, data, groups, analysis_type, output_format)
    
    elif action == "get_analysis_report":
        return statistical_analyzer_manager.get_analysis_report(conversation_id, workspace_id, "summary")
    
    else:
        return f"Unknown action: {action}. Valid actions: analyze, get_analysis_report"

@mcp.tool(name="notes", description="**REQUIRED: Tool output is not visible to users - you MUST display the tool's output in your response when necessary.** Use this tool for recording and retrieving knowledge, experiences, and insights with intelligent search capabilities. Record solutions, lessons learned, progress updates, and problem insights. Search through historical notes to find relevant experience and avoid repeating work. Perfect for knowledge management, experience tracking, and building institutional memory.")
def notes_command(
    conversation_id: Annotated[str, Field(description="Unique identifier of the conversation")],
    action: Annotated[str, Field(description="The operation to perform", enum=["record", "search", "get_by_ids", "get_summary", "update", "delete"])],
    
    # Recording parameters
    content: Annotated[Optional[str], Field(description="Main content of the note", default=None)],
    title: Annotated[Optional[str], Field(description="Optional title for the note (auto-generated if not provided)", default=None)],
    note_type: Annotated[Optional[str], Field(description="Type of note", enum=["problem", "solution", "experience", "progress", "general"], default="general")],
    tags: Annotated[Optional[List[str]], Field(description="Tags for categorizing and searching the note", default=None)],
    metadata: Annotated[Optional[dict], Field(description="Additional metadata for the note", default=None)],
    
    # Search parameters
    query: Annotated[Optional[str], Field(description="Search query for finding relevant notes", default=None)],
    search_tags: Annotated[Optional[List[str]], Field(description="Tags to search for", default=None)],
    search_type: Annotated[Optional[str], Field(description="Type of search to perform", enum=["semantic", "tag", "combined"], default="combined")],
    limit: Annotated[Optional[int], Field(description="Maximum number of results to return", default=10)],
    include_other_conversations: Annotated[Optional[bool], Field(description="Whether to search across all conversations", default=False)],
    
    # Retrieval parameters
    note_ids: Annotated[Optional[List[str]], Field(description="List of note IDs to retrieve", default=None)],
    context_data: Annotated[Optional[dict], Field(description="Context information for filtering summary", default=None)],
    
    # Update parameters
    note_id: Annotated[Optional[str], Field(description="ID of note to update or delete", default=None)],
    effectiveness_score: Annotated[Optional[int], Field(description="Effectiveness score (1-5) for solution notes", default=None)]
):
    """
    Notes Tool for Knowledge Management and Experience Tracking
    
    Record and retrieve insights, solutions, and experiences to build persistent knowledge.
    Supports intelligent search across notes to find relevant historical information.

    Parameters:
    - conversation_id (str, required): Unique identifier of the conversation
    - action (str, required): Operation type - ["record", "search", "get_by_ids", "get_summary", "update", "delete"]
    
    For recording (action="record"):
    - content (str, required): Main content of the note
    - title (str, optional): Title for the note (auto-generated if not provided)  
    - note_type (str, optional): Type - "problem", "solution", "experience", "progress", "general"
    - tags (list, optional): Tags for categorization
    - metadata (dict, optional): Additional context information
    
    For searching (action="search"):
    - query (str, optional): Search query text
    - search_tags (list, optional): Tags to search for
    - search_type (str, optional): "semantic", "tag", or "combined" search
    - limit (int, optional): Maximum results to return (default: 10)
    - include_other_conversations (bool, optional): Search across all conversations
    
    For retrieval (action="get_by_ids"):
    - note_ids (list, required): List of specific note IDs to retrieve
    
    For summary (action="get_summary"):
    - context_data (dict, optional): Context for filtering summary
    
    For updates (action="update"):
    - note_id (str, required): ID of note to update
    - content/title/tags/effectiveness_score (optional): Fields to update
    
    For deletion (action="delete"):
    - note_id (str, required): ID of note to delete

    Usage Examples:
    1. Record solution: notes_command("conv1", "record", content="Fixed API timeout by increasing connection pool size from 10 to 50", note_type="solution", tags=["api", "performance", "timeout"])
    2. Record problem: notes_command("conv1", "record", content="Database queries are slow on user table, affecting login performance", note_type="problem", tags=["database", "performance", "users"])
    3. Search for solutions: notes_command("conv1", "search", query="API performance issues", search_type="combined", limit=5)
    4. Search by tags: notes_command("conv1", "search", search_tags=["database", "optimization"], search_type="tag")
    5. Get specific notes: notes_command("conv1", "get_by_ids", note_ids=["note_123", "note_456"])
    6. Get conversation summary: notes_command("conv1", "get_summary")
    7. Update note effectiveness: notes_command("conv1", "update", note_id="note_123", effectiveness_score=5)
    8. Delete note: notes_command("conv1", "delete", note_id="note_123")
    """
    
    if action == "record":
        if not content:
            return "Error: content is required for record action"
        return notes_manager.record_note(conversation_id, content, title, note_type, tags, metadata)
    
    elif action == "search":
        if not query and not search_tags:
            return "Error: either query or search_tags is required for search action"
        return notes_manager.search_notes(conversation_id, query, search_tags, search_type, limit, include_other_conversations)
    
    elif action == "get_by_ids":
        if not note_ids:
            return "Error: note_ids list is required for get_by_ids action"
        return notes_manager.get_notes_by_ids(conversation_id, note_ids)
    
    elif action == "get_summary":
        return notes_manager.get_conversation_summary(conversation_id, context_data)
    
    elif action == "update":
        if not note_id:
            return "Error: note_id is required for update action"
        return notes_manager.update_note(conversation_id, note_id, content, title, tags, effectiveness_score, metadata)
    
    elif action == "delete":
        if not note_id:
            return "Error: note_id is required for delete action"  
        return notes_manager.delete_note(conversation_id, note_id)
    
    else:
        return f"Unknown action: {action}. Valid actions: record, search, get_by_ids, get_summary, update, delete"

def main():
    """Main entry point for the MCP server when installed via pip"""
    mcp.run()


if __name__ == "__main__":
    main()
