# Cognitive Canvas 🧠✨

> An MCP-powered cognitive workspace that enables AI agents to think, plan, and execute complex tasks with human-like organizational abilities.

## What is Cognitive Canvas?

Cognitive Canvas is a comprehensive Model Context Protocol (MCP) server that provides AI agents, LLMs, and Copilot-style systems with advanced cognitive tools. It transforms how AI handles complex reasoning by offering structured approaches to task management, dependency mapping, knowledge organization, and context switching.

Think of it as giving AI agents a "second brain" - a workspace where they can organize thoughts, break down complex problems, visualize relationships, and maintain coherent reasoning across extended conversations.

## 🚀 What Can It Do?

### 1. **Task Management & Action Planning** 
- Break down complex problems into actionable tasks
- Track progress and ensure nothing is missed
- Batch operations for efficient task creation
- Status tracking (pending, in_progress, completed, blocked)

### 2. **Dependency & Relationship Mapping**
- Create visual diagrams of task dependencies
- Map relationships between concepts and ideas
- Support for flowcharts, sequence diagrams, mindmaps, org charts, and trees
- Generate both structured tables and readable text-based graphs

### 3. **Structured Knowledge Organization**
- Transform unstructured information into organized tables
- Support for various template types (task lists, checklists, voting tables, progress tables)
- Automatic metrics calculation (completion rates, voting distributions)
- JSON and Markdown export capabilities

### 4. **Context Management & Conversation Forking**
- Create conversation branches for handling interruptions
- Maintain reasoning state across topic switches
- Seamless context switching and restoration
- Tree-like conversation management

## 🎯 Transform Any AI into a Deep-Thinking Research Agent

Cognitive Canvas transforms ordinary Copilot/Agent/AI into sophisticated **research-agent** and **deep-thinking mode** capabilities, enabling systematic reasoning and persistent memory.

### Key Transformations

🧠 **From Simple Chat → Research Agent**
- **Before**: AI gives quick answers and forgets context
- **After**: AI builds knowledge systematically, maintains research state, and develops insights over time

🔍 **From Linear Responses → Deep-Thinking Mode**
- **Before**: AI provides immediate, surface-level responses  
- **After**: AI breaks down complex problems, maps dependencies, and reasons through multi-step solutions

📊 **From Stateless → Persistent Intelligence**
- **Before**: Each conversation starts from scratch
- **After**: AI accumulates knowledge, tracks progress, and builds upon previous work

### Real-World Impact Examples

**Software Development**
```
Normal AI: "Here's how to build an API..."
Enhanced AI: Systematically plans project phases → tracks implementation progress → 
             manages dependencies → maintains technical decisions context
```

**Research & Analysis** 
```
Normal AI: "Based on this paper..."
Enhanced AI: Organizes literature systematically → builds concept maps → 
             tracks hypothesis development → synthesizes findings coherently
```

**Business Planning**
```
Normal AI: "You should consider these factors..."
Enhanced AI: Breaks down strategic goals → maps resource dependencies → 
             tracks milestone progress → maintains decision rationale
```

**Learning & Education**
```
Normal AI: "This concept means..."
Enhanced AI: Structures learning progression → tracks mastery → 
             maps prerequisite relationships → adapts difficulty systematically
```

### The Core Difference

**Without Cognitive Canvas**: AI = Smart autocomplete with no memory or systematic thinking
**With Cognitive Canvas**: AI = Research assistant with structured reasoning, persistent memory, and goal-oriented planning

**Result**: Any AI system becomes capable of PhD-level systematic thinking and research methodology.

## 🛠 How to Use It

### Prerequisites
- Python 3.7+
- MCP-compatible AI system (like Claude Desktop, VS Code Copilot, etc.)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/OsmondJiang/Cognitive-Canvas.git
cd Cognitive-Canvas
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the MCP server:**
```bash
python server.py
```

### Configuration

Add Cognitive Canvas to your MCP client configuration. For Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cognitive-canvas": {
      "command": "python",
      "args": ["path/to/Cognitive-Canvas/server.py"]
    }
  }
}
```

### Usage Examples

#### Task Management
```python
# Add multiple tasks at once
todo_command("project1", "add-batch", task_list=[
    {"title": "Design database schema", "status": "pending"},
    {"title": "Implement API endpoints", "status": "pending"},
    {"title": "Write unit tests", "status": "pending"}
])

# Update task status
todo_command("project1", "update", task_id=1, status="completed")

# List all tasks
todo_command("project1", "list")
```

#### Diagram Creation
```python
# Create a dependency diagram
diagram_tool("project1", "create", {
    "diagram_type": "flowchart",
    "title": "Development Workflow"
})

# Add nodes and relationships
diagram_tool("project1", "add_node", {
    "node_id": "design",
    "label": "Database Design",
    "metadata": {"priority": "high"}
})
```

#### Structured Knowledge
```python
# Create a progress tracking table
structured_knowledge_tool("project1", "create", {
    "structure_id": "progress",
    "template_type": "progress_table",
    "title": "Project Progress"
})

# Add progress entries
structured_knowledge_tool("project1", "add_row", {
    "structure_id": "progress",
    "row_data": {"task": "Database Design", "progress": 80, "status": "In Progress"}
})
```

## 🔧 Development Guide

### Project Structure
```
Cognitive-Canvas/
├── server.py              # Main MCP server
├── requirements.txt        # Python dependencies
├── tools/                 # Core tool implementations
│   ├── __init__.py
│   ├── todo_tool.py       # Task management
│   ├── diagram_tool.py    # Diagram creation
│   ├── structured_knowledge_tool.py  # Knowledge organization
│   └── chat_fork.py       # Context management
└── tests/                 # Test suite
    ├── test_server.py
    ├── test_todo_tool.py
    └── ...
```

### Adding New Features

1. **Create a new tool module** in the `tools/` directory
2. **Implement the core functionality** following existing patterns
3. **Add MCP endpoint** in `server.py`
4. **Write tests** in the `tests/` directory
5. **Update documentation**

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_todo_tool.py

# Run with coverage
python -m pytest tests/ --cov=tools
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters
- Include comprehensive docstrings
- Maintain consistent error handling patterns

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Architecture

Cognitive Canvas is built on the FastMCP framework, providing:

- **Modular Design**: Each cognitive tool is independently implemented
- **Conversation Scoping**: All data is organized by conversation ID
- **Memory Management**: In-memory storage for fast access during sessions
- **Extensible Framework**: Easy to add new cognitive tools
- **Type Safety**: Full type hints and validation using Pydantic

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Inspired by human cognitive processes and knowledge management systems
- Designed for the Model Context Protocol ecosystem

---

**Ready to enhance your AI's cognitive abilities?** Start using Cognitive Canvas today and experience structured, organized, and effective AI reasoning!
