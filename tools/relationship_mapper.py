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
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    def update_node(self, conversation_id: str, node_id: str, label: Optional[str] = None, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        node = self.conversations[conversation_id]["nodes"].get(node_id)
        if not node:
            return {
                "success": False,
                "error": f"Node '{node_id}' not found in conversation '{conversation_id}'. Use add_node() first to create nodes before updating."
            }
        
        if label:
            node.label = label
        if metadata:
            node.metadata.update(metadata)
            
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    def add_edge(self, conversation_id: str, source: str, target: str, type: str, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        edge = Edge(source, target, type, metadata)
        self.conversations[conversation_id]["edges"].append(edge)
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    def update_edge(self, conversation_id: str, index: int, type: Optional[str] = None, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        edges = self.conversations[conversation_id]["edges"]
        if index >= len(edges):
            return {
                "success": False,
                "error": f"Edge index {index} out of range. Available indices: 0-{len(edges)-1 if edges else 'none'}. Use add_edge() to create edges first."
            }
        
        edge = edges[index]
        if type:
            edge.type = type
        if metadata:
            edge.metadata.update(metadata)
            
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    # ---------------- Batch Operations ----------------
    def batch_add_nodes(self, conversation_id: str, nodes: List[Dict]):
        """
        Batch add nodes
        nodes: [{"id": str, "label": str, "metadata": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        
        # Validate all nodes first (atomic operation)
        failed_validations = []
        validated_nodes = []
        
        for i, node_data in enumerate(nodes):
            node_id = node_data.get("id")
            label = node_data.get("label")
            metadata = node_data.get("metadata")
            
            if not node_id or not label:
                failed_validations.append(f"Node {i}: missing required 'id' or 'label' field")
                continue
                
            validated_nodes.append({"id": node_id, "label": label, "metadata": metadata})
        
        # If any validation failed, return error without adding any nodes
        if failed_validations:
            return {
                "success": False,
                "error": "Some nodes failed validation: " + "; ".join(failed_validations) + ". Example: [{'id': 'node1', 'label': 'Node 1', 'metadata': {'type': 'start'}}]"
            }
        
        # Add all validated nodes
        for node_data in validated_nodes:
            self.conversations[conversation_id]["nodes"][node_data["id"]] = Node(
                node_data["id"], node_data["label"], node_data["metadata"]
            )
        
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    def batch_update_nodes(self, conversation_id: str, nodes: List[Dict]):
        """
        Batch update nodes
        nodes: [{"id": str, "label": str (optional), "metadata": dict (optional)}, ...]
        """
        self._ensure_conv(conversation_id)
        
        # Validate all updates first (atomic operation)
        failed_validations = []
        validated_updates = []
        
        for i, node_data in enumerate(nodes):
            node_id = node_data.get("id")
            label = node_data.get("label")
            metadata = node_data.get("metadata")
            
            if not node_id:
                failed_validations.append(f"Update {i}: missing required 'id' field")
                continue
                
            node = self.conversations[conversation_id]["nodes"].get(node_id)
            if not node:
                failed_validations.append(f"Update {i}: node '{node_id}' not found")
                continue
                
            validated_updates.append({"id": node_id, "label": label, "metadata": metadata})
        
        # If any validation failed, return error without updating any nodes
        if failed_validations:
            return {
                "success": False,
                "error": "Some updates failed validation: " + "; ".join(failed_validations) + ". Example: [{'id': 'node1', 'label': 'New Label', 'metadata': {'updated': true}}]"
            }
        
        # Apply all validated updates
        for update_data in validated_updates:
            node = self.conversations[conversation_id]["nodes"][update_data["id"]]
            if update_data["label"]:
                node.label = update_data["label"]
            if update_data["metadata"]:
                node.metadata.update(update_data["metadata"])
        
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    def batch_add_edges(self, conversation_id: str, edges: List[Dict]):
        """
        Batch add edges
        edges: [{"source": str, "target": str, "type": str, "metadata": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        
        # Validate all edges first (atomic operation)
        failed_validations = []
        validated_edges = []
        
        for i, edge_data in enumerate(edges):
            source = edge_data.get("source")
            target = edge_data.get("target")
            edge_type = edge_data.get("type")
            metadata = edge_data.get("metadata")
            
            if not source or not target or not edge_type:
                failed_validations.append(f"Edge {i}: missing required 'source', 'target', or 'type' field")
                continue
                
            validated_edges.append({"source": source, "target": target, "type": edge_type, "metadata": metadata})
        
        # If any validation failed, return error without adding any edges
        if failed_validations:
            return {
                "success": False,
                "error": "Some edges failed validation: " + "; ".join(failed_validations) + ". Example: [{'source': 'node1', 'target': 'node2', 'type': 'connects_to', 'metadata': {'weight': 1}}]"
            }
        
        # Add all validated edges
        for edge_data in validated_edges:
            edge = Edge(edge_data["source"], edge_data["target"], edge_data["type"], edge_data["metadata"])
            self.conversations[conversation_id]["edges"].append(edge)
        
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    def batch_update_edges(self, conversation_id: str, edges: List[Dict]):
        """
        Batch update edges
        edges: [{"index": int, "type": str (optional), "metadata": dict (optional)}, ...]
        """
        self._ensure_conv(conversation_id)
        conversation_edges = self.conversations[conversation_id]["edges"]
        
        # Validate all updates first (atomic operation)
        failed_validations = []
        validated_updates = []
        
        for i, edge_data in enumerate(edges):
            index = edge_data.get("index")
            edge_type = edge_data.get("type")
            metadata = edge_data.get("metadata")
            
            if index is None:
                failed_validations.append(f"Update {i}: missing required 'index' field")
                continue
                
            if index >= len(conversation_edges):
                failed_validations.append(f"Update {i}: edge index {index} out of range (available: 0-{len(conversation_edges)-1 if conversation_edges else 'none'})")
                continue
                
            validated_updates.append({"index": index, "type": edge_type, "metadata": metadata})
        
        # If any validation failed, return error without updating any edges
        if failed_validations:
            return {
                "success": False,
                "error": "Some updates failed validation: " + "; ".join(failed_validations) + ". Example: [{'index': 0, 'type': 'new_type', 'metadata': {'weight': 5}}]"
            }
        
        # Apply all validated updates
        for update_data in validated_updates:
            edge = conversation_edges[update_data["index"]]
            if update_data["type"]:
                edge.type = update_data["type"]
            if update_data["metadata"]:
                edge.metadata.update(update_data["metadata"])
        
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

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
        
        # Execute operations sequentially to handle dependencies
        failed_operations = []
        
        for i, op in enumerate(operations):
            action = op.get("action")
            data = op.get("data", {})
            
            try:
                if action == "add_node":
                    node_id = data.get("id")
                    label = data.get("label")
                    metadata = data.get("metadata")
                    if not node_id or not label:
                        failed_operations.append(f"Operation {i}: 'add_node' requires 'id' and 'label'")
                        continue
                    self.conversations[conversation_id]["nodes"][node_id] = Node(node_id, label, metadata)
                    
                elif action == "add_edge":
                    source = data.get("source")
                    target = data.get("target")
                    edge_type = data.get("type")
                    metadata = data.get("metadata")
                    if not source or not target or not edge_type:
                        failed_operations.append(f"Operation {i}: 'add_edge' requires 'source', 'target', and 'type'")
                        continue
                    edge = Edge(source, target, edge_type, metadata)
                    self.conversations[conversation_id]["edges"].append(edge)
                    
                elif action == "update_node":
                    node_id = data.get("id")
                    label = data.get("label")
                    metadata = data.get("metadata")
                    if not node_id:
                        failed_operations.append(f"Operation {i}: 'update_node' requires 'id'")
                        continue
                    node = self.conversations[conversation_id]["nodes"].get(node_id)
                    if not node:
                        failed_operations.append(f"Operation {i}: node '{node_id}' not found")
                        continue
                    if label:
                        node.label = label
                    if metadata:
                        node.metadata.update(metadata)
                        
                elif action == "update_edge":
                    index = data.get("index")
                    edge_type = data.get("type")
                    metadata = data.get("metadata")
                    if index is None:
                        failed_operations.append(f"Operation {i}: 'update_edge' requires 'index'")
                        continue
                    edges = self.conversations[conversation_id]["edges"]
                    if index >= len(edges):
                        failed_operations.append(f"Operation {i}: edge index {index} out of range")
                        continue
                    edge = edges[index]
                    if edge_type:
                        edge.type = edge_type
                    if metadata:
                        edge.metadata.update(metadata)
                        
                else:
                    failed_operations.append(f"Operation {i}: unknown action '{action}'. Supported: add_node, add_edge, update_node, update_edge")
                    continue
                    
            except Exception as e:
                failed_operations.append(f"Operation {i}: {str(e)}")
                continue
        
        # If any operations failed, return error
        if failed_operations:
            return {
                "success": False,
                "error": "Some operations failed: " + "; ".join(failed_operations) + ". Example: [{'action': 'add_node', 'data': {'id': 'node1', 'label': 'Node 1'}}]"
            }
        
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

    # ---------------- Visualization Type ----------------
    def set_visualization_type(self, conversation_id: str, visualization_type: str):
        self._ensure_conv(conversation_id)
        valid_types = ["flowchart", "sequence", "mindmap", "orgchart", "tree"]
        if visualization_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid visualization type '{visualization_type}'. Must be one of: {', '.join(valid_types)}. Example: set_visualization_type('conv1', 'flowchart')"
            }
        self.conversations[conversation_id]["visualization_type"] = visualization_type
        return {
            "success": True,
            "data": {
                "nodes": {nid: {"id": n.id, "label": n.label, "metadata": n.metadata} 
                         for nid, n in self.conversations[conversation_id]["nodes"].items()},
                "edges": [{"source": e.source, "target": e.target, "type": e.type, "metadata": e.metadata} 
                         for e in self.conversations[conversation_id]["edges"]],
                "visualization_type": self.conversations[conversation_id]["visualization_type"]
            }
        }

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
