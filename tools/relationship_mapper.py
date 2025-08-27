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

class RelationshipMapper:
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}  # conversation_id -> {"nodes": {}, "edges": [], "visualization_type": str}

    def _ensure_conv(self, conversation_id: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {"nodes": {}, "edges": [], "visualization_type": "flowchart"}

    # ---------------- Node / Edge Operations ----------------
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

    # ---------------- Batch Operations ----------------
    def batch_add_nodes(self, conversation_id: str, nodes: List[Dict]):
        """
        Batch add nodes
        nodes: [{"id": str, "label": str, "metadata": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        for node_data in nodes:
            node_id = node_data.get("id")
            label = node_data.get("label")
            metadata = node_data.get("metadata")
            
            if not node_id or not label:
                results.append(f"Error: Missing id or label for node {node_data}")
                continue
                
            self.conversations[conversation_id]["nodes"][node_id] = Node(node_id, label, metadata)
            results.append(f"Node '{label}' (id: {node_id}) added.")
        
        return "\n".join(results)

    def batch_update_nodes(self, conversation_id: str, nodes: List[Dict]):
        """
        Batch update nodes
        nodes: [{"id": str, "label": str (optional), "metadata": dict (optional)}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        for node_data in nodes:
            node_id = node_data.get("id")
            label = node_data.get("label")
            metadata = node_data.get("metadata")
            
            if not node_id:
                results.append(f"Error: Missing id for node update {node_data}")
                continue
                
            node = self.conversations[conversation_id]["nodes"].get(node_id)
            if not node:
                results.append(f"Error: Node {node_id} not found.")
                continue
                
            if label:
                node.label = label
            if metadata:
                node.metadata.update(metadata)
            results.append(f"Node '{node_id}' updated.")
        
        return "\n".join(results)

    def batch_add_edges(self, conversation_id: str, edges: List[Dict]):
        """
        Batch add edges
        edges: [{"source": str, "target": str, "type": str, "metadata": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        for edge_data in edges:
            source = edge_data.get("source")
            target = edge_data.get("target")
            edge_type = edge_data.get("type")
            metadata = edge_data.get("metadata")
            
            if not source or not target or not edge_type:
                results.append(f"Error: Missing source, target, or type for edge {edge_data}")
                continue
                
            self.conversations[conversation_id]["edges"].append(Edge(source, target, edge_type, metadata))
            results.append(f"Edge {source} -> {target} ({edge_type}) added.")
        
        return "\n".join(results)

    def batch_update_edges(self, conversation_id: str, edges: List[Dict]):
        """
        Batch update edges
        edges: [{"index": int, "type": str (optional), "metadata": dict (optional)}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        conversation_edges = self.conversations[conversation_id]["edges"]
        
        for edge_data in edges:
            index = edge_data.get("index")
            edge_type = edge_data.get("type")
            metadata = edge_data.get("metadata")
            
            if index is None:
                results.append(f"Error: Missing index for edge update {edge_data}")
                continue
                
            if index >= len(conversation_edges):
                results.append(f"Error: Edge index {index} out of range.")
                continue
                
            edge = conversation_edges[index]
            if edge_type:
                edge.type = edge_type
            if metadata:
                edge.metadata.update(metadata)
            results.append(f"Edge at index {index} updated.")
        
        return "\n".join(results)

    def batch_operations(self, conversation_id: str, operations: List[Dict]):
        """
        Batch execute mixed operations
        operations: [
            {"action": "add_node", "data": {"id": str, "label": str, "metadata": dict}},
            {"action": "add_edge", "data": {"source": str, "target": str, "type": str, "metadata": dict}},
            {"action": "update_node", "data": {"id": str, "label": str, "metadata": dict}},
            {"action": "update_edge", "data": {"index": int, "type": str, "metadata": dict}},
            ...
        ]
        """
        self._ensure_conv(conversation_id)
        results = []
        
        for op in operations:
            action = op.get("action")
            data = op.get("data", {})
            
            if action == "add_node":
                node_id = data.get("id")
                label = data.get("label")
                metadata = data.get("metadata")
                if node_id and label:
                    self.conversations[conversation_id]["nodes"][node_id] = Node(node_id, label, metadata)
                    results.append(f"Node '{label}' (id: {node_id}) added.")
                else:
                    results.append(f"Error: Missing id or label for add_node operation")
                    
            elif action == "add_edge":
                source = data.get("source")
                target = data.get("target")
                edge_type = data.get("type")
                metadata = data.get("metadata")
                if source and target and edge_type:
                    self.conversations[conversation_id]["edges"].append(Edge(source, target, edge_type, metadata))
                    results.append(f"Edge {source} -> {target} ({edge_type}) added.")
                else:
                    results.append(f"Error: Missing source, target, or type for add_edge operation")
                    
            elif action == "update_node":
                node_id = data.get("id")
                label = data.get("label")
                metadata = data.get("metadata")
                if node_id:
                    node = self.conversations[conversation_id]["nodes"].get(node_id)
                    if node:
                        if label:
                            node.label = label
                        if metadata:
                            node.metadata.update(metadata)
                        results.append(f"Node '{node_id}' updated.")
                    else:
                        results.append(f"Error: Node {node_id} not found.")
                else:
                    results.append(f"Error: Missing id for update_node operation")
                    
            elif action == "update_edge":
                index = data.get("index")
                edge_type = data.get("type")
                metadata = data.get("metadata")
                if index is not None:
                    edges = self.conversations[conversation_id]["edges"]
                    if index < len(edges):
                        edge = edges[index]
                        if edge_type:
                            edge.type = edge_type
                        if metadata:
                            edge.metadata.update(metadata)
                        results.append(f"Edge at index {index} updated.")
                    else:
                        results.append(f"Error: Edge index {index} out of range.")
                else:
                    results.append(f"Error: Missing index for update_edge operation")
            else:
                results.append(f"Error: Unknown action '{action}' in batch operations")
        
        return "\n".join(results)

    # ---------------- Visualization Type ----------------
    def set_visualization_type(self, conversation_id: str, visualization_type: str):
        self._ensure_conv(conversation_id)
        if visualization_type not in ["flowchart", "sequence", "mindmap", "orgchart", "tree"]:
            return f"Unknown visualization type: {visualization_type}"
        self.conversations[conversation_id]["visualization_type"] = visualization_type
        return f"Visualization type set to {visualization_type}"

    # ---------------- Render ----------------
    def render(self,conversation_id: str):
        """
        Render the relationship map for the conversation as Markdown table or tree.
        Supports visualization types: flowchart, sequence, mindmap, orgchart, tree.
        Returns a string with both structured table and readable text-based visualization.
        """
        visualization_type = self.conversations[conversation_id]["visualization_type"]
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

        # Return based on visualization type
        if visualization_type in ["tree", "orgchart", "mindmap"]:
            return f"### Relationship Map (Tree Style)\n```\n{tree_text}\n```"
        else:  # flowchart, sequence
            return f"### Relationship Map (Table Style)\n{table_text}"
