from typing import List, Dict, Optional

class Node:
    def __init__(self, id: str, label: str, metadata: Optional[dict] = None):
        self.id = id
        self.label = label
        self.metadata = metadata or {}

class Edge:
    def __init__(self, source: str, target: str, type: str, metadata: Optional[dict] = None):
        self.source = source
        self.target = target
        self.type = type
        self.metadata = metadata or {}

class DiagramManager:
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}  # conversation_id -> {"nodes": {}, "edges": [], "diagram_type": str}

    def _ensure_conv(self, conversation_id: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {"nodes": {}, "edges": [], "diagram_type": "flowchart"}

    # ---------------- Node / Edge 操作 ----------------
    def add_node(self, conversation_id: str, node_id: str, label: str, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        self.conversations[conversation_id]["nodes"][node_id] = Node(node_id, label, metadata)
        return f"Node '{label}' added."

    def update_node(self, conversation_id: str, node_id: str, label: Optional[str] = None, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        node = self.conversations[conversation_id]["nodes"].get(node_id)
        if not node:
            return f"Node {node_id} not found."
        if label:
            node.label = label
        if metadata:
            node.metadata.update(metadata)
        return f"Node '{node_id}' updated."

    def add_edge(self, conversation_id: str, source: str, target: str, type: str, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        self.conversations[conversation_id]["edges"].append(Edge(source, target, type, metadata))
        return f"Edge {source} -> {target} ({type}) added."

    def update_edge(self, conversation_id: str, index: int, type: Optional[str] = None, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        edges = self.conversations[conversation_id]["edges"]
        if index >= len(edges):
            return "Edge index out of range."
        edge = edges[index]
        if type:
            edge.type = type
        if metadata:
            edge.metadata.update(metadata)
        return f"Edge at index {index} updated."

    # ---------------- Diagram Type ----------------
    def set_diagram_type(self, conversation_id: str, diagram_type: str):
        self._ensure_conv(conversation_id)
        if diagram_type not in ["flowchart", "sequence", "mindmap", "orgchart", "tree"]:
            return f"Unknown diagram type: {diagram_type}"
        self.conversations[conversation_id]["diagram_type"] = diagram_type
        return f"Diagram type set to {diagram_type}"

    # ---------------- Render ----------------
    def render(self,conversation_id: str):
        """
        Render the diagram for the conversation as Markdown table or tree.
        Supports diagram types: flowchart, sequence, mindmap, orgchart, tree.
        Returns a string with both structured table and readable text-based diagram.
        """
        diagram_type = self.conversations[conversation_id]["diagram_type"]
        nodes = self.conversations[conversation_id]["nodes"]
        edges = self.conversations[conversation_id]["edges"]

        if not nodes:
            return "No nodes to render."

        # Build child mapping
        node_children = {nid: [] for nid in nodes}
        for e in edges:
            source = e.source
            target = e.target
            if source in node_children:
                node_children[source].append(target)

        # Assign levels for tree-like render
        node_levels = {}

        def assign_level(node_id, level, visited=None):
            if visited is None:
                visited = set()
            if node_id in visited:
                return  # Avoid infinite loop
            visited.add(node_id)
            node_levels[node_id] = max(node_levels.get(node_id, 0), level)
            for child in node_children.get(node_id, []):
                assign_level(child, level + 1, visited.copy())

        # Find root nodes (nodes with no incoming edges)
        all_targets = {e.target for e in edges}
        root_nodes = [nid for nid in nodes if nid not in all_targets]
        if not root_nodes:
            root_nodes = list(nodes.keys())  # fallback

        for root in root_nodes:
            assign_level(root, 0)

        # Sort nodes by level then by node id
        sorted_nodes = sorted(nodes.items(), key=lambda x: (node_levels.get(x[0], 0), x[0]))

        # Build Markdown table
        table_lines = ["| Node ID | Label | Level |"]
        table_lines.append("| --- | --- | --- |")
        for nid, node in sorted_nodes:
            table_lines.append(f"| {nid} | {node.label} | {node_levels.get(nid,0)} |")
        table_text = "\n".join(table_lines)

        # Build text tree
        tree_lines = []

        def build_tree(node_id, prefix="", visited=None):
            if visited is None:
                visited = set()
            if node_id in visited:
                tree_lines.append(f"{prefix}{nodes[node_id].label} (loop)")
                return
            visited.add(node_id)
            tree_lines.append(f"{prefix}{nodes[node_id].label}")
            children = node_children.get(node_id, [])
            for i, child in enumerate(children):
                branch_prefix = prefix + ("└─ " if i == len(children) - 1 else "├─ ")
                build_tree(child, prefix=branch_prefix, visited=visited.copy())

        for root in root_nodes:
            build_tree(root)

        tree_text = "\n".join(tree_lines)

        # Return based on diagram type
        if diagram_type in ["tree", "orgchart", "mindmap"]:
            return f"### Diagram (Tree Style)\n```\n{tree_text}\n```\n\n### Table View\n{table_text}"
        else:  # flowchart, sequence
            return f"### Diagram (Table Style)\n{table_text}\n\n### Text View\n```\n{tree_text}\n```"
