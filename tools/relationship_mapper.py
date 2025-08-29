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
            "status": "success",
            "message": f"Node '{label}' added.",
            "node": {
                "id": node_id,
                "label": label,
                "metadata": metadata or {}
            }
        }

    def update_node(self, conversation_id: str, node_id: str, label: Optional[str] = None, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        node = self.conversations[conversation_id]["nodes"].get(node_id)
        if not node:
            return {
                "status": "error",
                "message": f"Node {node_id} not found."
            }
        
        updated_fields = {}
        if label:
            node.label = label
            updated_fields["label"] = label
        if metadata:
            node.metadata.update(metadata)
            updated_fields["metadata"] = metadata
            
        return {
            "status": "success",
            "message": f"Node '{node_id}' updated.",
            "node": {
                "id": node_id,
                "label": node.label,
                "metadata": node.metadata
            },
            "updated_fields": updated_fields
        }

    def add_edge(self, conversation_id: str, source: str, target: str, type: str, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        edge = Edge(source, target, type, metadata)
        self.conversations[conversation_id]["edges"].append(edge)
        return {
            "status": "success",
            "message": f"Edge {source} -> {target} ({type}) added.",
            "edge": {
                "source": source,
                "target": target,
                "type": type,
                "metadata": metadata or {}
            }
        }

    def update_edge(self, conversation_id: str, index: int, type: Optional[str] = None, metadata: Optional[dict] = None):
        self._ensure_conv(conversation_id)
        edges = self.conversations[conversation_id]["edges"]
        if index >= len(edges):
            return {
                "status": "error",
                "message": "Edge index out of range.",
                "max_index": len(edges) - 1
            }
        
        edge = edges[index]
        updated_fields = {}
        if type:
            edge.type = type
            updated_fields["type"] = type
        if metadata:
            edge.metadata.update(metadata)
            updated_fields["metadata"] = metadata
            
        return {
            "status": "success",
            "message": f"Edge at index {index} updated.",
            "edge": {
                "index": index,
                "source": edge.source,
                "target": edge.target,
                "type": edge.type,
                "metadata": edge.metadata
            },
            "updated_fields": updated_fields
        }

    # ---------------- Batch Operations ----------------
    def batch_add_nodes(self, conversation_id: str, nodes: List[Dict]):
        """
        Batch add nodes
        nodes: [{"id": str, "label": str, "metadata": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        added_nodes = []
        errors = []
        
        for node_data in nodes:
            node_id = node_data.get("id")
            label = node_data.get("label")
            metadata = node_data.get("metadata")
            
            if not node_id or not label:
                error_msg = f"Missing id or label for node {node_data}"
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            self.conversations[conversation_id]["nodes"][node_id] = Node(node_id, label, metadata)
            node_info = {"id": node_id, "label": label, "metadata": metadata or {}}
            added_nodes.append(node_info)
            results.append({"status": "success", "message": f"Node '{label}' (id: {node_id}) added.", "node": node_info})
        
        return {
            "status": "success",
            "message": f"Batch add nodes completed. {len(added_nodes)} nodes added, {len(errors)} errors.",
            "added_nodes": added_nodes,
            "errors": errors,
            "results": results
        }

    def batch_update_nodes(self, conversation_id: str, nodes: List[Dict]):
        """
        Batch update nodes
        nodes: [{"id": str, "label": str (optional), "metadata": dict (optional)}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        updated_nodes = []
        errors = []
        
        for node_data in nodes:
            node_id = node_data.get("id")
            label = node_data.get("label")
            metadata = node_data.get("metadata")
            
            if not node_id:
                error_msg = f"Missing id for node update {node_data}"
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            node = self.conversations[conversation_id]["nodes"].get(node_id)
            if not node:
                error_msg = f"Node {node_id} not found."
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            updated_fields = {}
            if label:
                node.label = label
                updated_fields["label"] = label
            if metadata:
                node.metadata.update(metadata)
                updated_fields["metadata"] = metadata
                
            node_info = {"id": node_id, "label": node.label, "metadata": node.metadata, "updated_fields": updated_fields}
            updated_nodes.append(node_info)
            results.append({"status": "success", "message": f"Node '{node_id}' updated.", "node": node_info})
        
        return {
            "status": "success",
            "message": f"Batch update nodes completed. {len(updated_nodes)} nodes updated, {len(errors)} errors.",
            "updated_nodes": updated_nodes,
            "errors": errors,
            "results": results
        }

    def batch_add_edges(self, conversation_id: str, edges: List[Dict]):
        """
        Batch add edges
        edges: [{"source": str, "target": str, "type": str, "metadata": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        added_edges = []
        errors = []
        
        for edge_data in edges:
            source = edge_data.get("source")
            target = edge_data.get("target")
            edge_type = edge_data.get("type")
            metadata = edge_data.get("metadata")
            
            if not source or not target or not edge_type:
                error_msg = f"Missing source, target, or type for edge {edge_data}"
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            edge = Edge(source, target, edge_type, metadata)
            self.conversations[conversation_id]["edges"].append(edge)
            edge_info = {"source": source, "target": target, "type": edge_type, "metadata": metadata or {}}
            added_edges.append(edge_info)
            results.append({"status": "success", "message": f"Edge {source} -> {target} ({edge_type}) added.", "edge": edge_info})
        
        return {
            "status": "success",
            "message": f"Batch add edges completed. {len(added_edges)} edges added, {len(errors)} errors.",
            "added_edges": added_edges,
            "errors": errors,
            "results": results
        }

    def batch_update_edges(self, conversation_id: str, edges: List[Dict]):
        """
        Batch update edges
        edges: [{"index": int, "type": str (optional), "metadata": dict (optional)}, ...]
        """
        self._ensure_conv(conversation_id)
        results = []
        updated_edges = []
        errors = []
        conversation_edges = self.conversations[conversation_id]["edges"]
        
        for edge_data in edges:
            index = edge_data.get("index")
            edge_type = edge_data.get("type")
            metadata = edge_data.get("metadata")
            
            if index is None:
                error_msg = f"Missing index for edge update {edge_data}"
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            if index >= len(conversation_edges):
                error_msg = f"Edge index {index} out of range."
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            edge = conversation_edges[index]
            updated_fields = {}
            if edge_type:
                edge.type = edge_type
                updated_fields["type"] = edge_type
            if metadata:
                edge.metadata.update(metadata)
                updated_fields["metadata"] = metadata
                
            edge_info = {
                "index": index,
                "source": edge.source,
                "target": edge.target,
                "type": edge.type,
                "metadata": edge.metadata,
                "updated_fields": updated_fields
            }
            updated_edges.append(edge_info)
            results.append({"status": "success", "message": f"Edge at index {index} updated.", "edge": edge_info})
        
        return {
            "status": "success",
            "message": f"Batch update edges completed. {len(updated_edges)} edges updated, {len(errors)} errors.",
            "updated_edges": updated_edges,
            "errors": errors,
            "results": results
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
        results = []
        success_count = 0
        error_count = 0
        
        for op in operations:
            action = op.get("action")
            data = op.get("data", {})
            
            if action == "add_node":
                node_id = data.get("id")
                label = data.get("label")
                metadata = data.get("metadata")
                if node_id and label:
                    self.conversations[conversation_id]["nodes"][node_id] = Node(node_id, label, metadata)
                    results.append({"status": "success", "action": "add_node", "message": f"Node '{label}' (id: {node_id}) added."})
                    success_count += 1
                else:
                    results.append({"status": "error", "action": "add_node", "message": "Missing id or label for add_node operation"})
                    error_count += 1
                    
            elif action == "add_edge":
                source = data.get("source")
                target = data.get("target")
                edge_type = data.get("type")
                metadata = data.get("metadata")
                if source and target and edge_type:
                    self.conversations[conversation_id]["edges"].append(Edge(source, target, edge_type, metadata))
                    results.append({"status": "success", "action": "add_edge", "message": f"Edge {source} -> {target} ({edge_type}) added."})
                    success_count += 1
                else:
                    results.append({"status": "error", "action": "add_edge", "message": "Missing source, target, or type for add_edge operation"})
                    error_count += 1
                    
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
                        results.append({"status": "success", "action": "update_node", "message": f"Node '{node_id}' updated."})
                        success_count += 1
                    else:
                        results.append({"status": "error", "action": "update_node", "message": f"Node {node_id} not found."})
                        error_count += 1
                else:
                    results.append({"status": "error", "action": "update_node", "message": "Missing id for update_node operation"})
                    error_count += 1
                    
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
                        results.append({"status": "success", "action": "update_edge", "message": f"Edge at index {index} updated."})
                        success_count += 1
                    else:
                        results.append({"status": "error", "action": "update_edge", "message": f"Edge index {index} out of range."})
                        error_count += 1
                else:
                    results.append({"status": "error", "action": "update_edge", "message": "Missing index for update_edge operation"})
                    error_count += 1
            else:
                results.append({"status": "error", "action": action, "message": f"Unknown action '{action}' in batch operations"})
                error_count += 1
        
        return {
            "status": "success",
            "message": f"Batch operations completed. {success_count} successful, {error_count} errors.",
            "total_operations": len(operations),
            "successful_operations": success_count,
            "failed_operations": error_count,
            "results": results
        }

    # ---------------- Visualization Type ----------------
    def set_visualization_type(self, conversation_id: str, visualization_type: str):
        self._ensure_conv(conversation_id)
        if visualization_type not in ["flowchart", "sequence", "mindmap", "orgchart", "tree"]:
            return {
                "status": "error",
                "message": f"Unknown visualization type: {visualization_type}",
                "valid_types": ["flowchart", "sequence", "mindmap", "orgchart", "tree"]
            }
        self.conversations[conversation_id]["visualization_type"] = visualization_type
        return {
            "status": "success",
            "message": f"Visualization type set to {visualization_type}",
            "visualization_type": visualization_type
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
