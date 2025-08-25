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
    def render(self, conversation_id: str):
        self._ensure_conv(conversation_id)
        nodes = self.conversations[conversation_id]["nodes"]
        edges = self.conversations[conversation_id]["edges"]
        dtype = self.conversations[conversation_id]["diagram_type"]

        # ----------------- Markdown Table -----------------
        # 自动计算每列最大宽度
        headers = ["Level", "Entity A", "Relationship", "Entity B", "Condition", "Weight"]
        rows = []

        # 计算层级（Level）
        parent_map = {nid: [] for nid in nodes}
        child_set = set()
        for e in edges:
            parent_map[e.source].append(e.target)
            child_set.add(e.target)
        roots = [nid for nid in nodes if nid not in child_set]

        level_map = {}

        def assign_level(nid, level=0):
            level_map[nid] = level
            for child in parent_map.get(nid, []):
                assign_level(child, level + 1)
        for r in roots:
            assign_level(r)

        # 构建 rows
        for e in edges:
            row = [
                str(level_map.get(e.source, 0)),
                nodes[e.source].label,
                e.type,
                nodes[e.target].label,
                e.metadata.get("condition", ""),
                str(e.metadata.get("weight", "")),
            ]
            rows.append(row)

        # 计算每列最大宽度
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(val))

        # 构建 Markdown Table 字符串
        markdown = "| " + " | ".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)]) + " |\n"
        markdown += "|-" + "-|-".join(["-" * col_widths[i] for i in range(len(headers))]) + "-|\n"
        for row in rows:
            markdown += "| " + " | ".join([row[i].ljust(col_widths[i]) for i in range(len(headers))]) + " |\n"

        # ----------------- Text Graph -----------------
        def render_node(nid, prefix="", is_last=True):
            line_symbol = "└─ " if is_last else "├─ "
            line = f"{prefix}{line_symbol}{nodes[nid].label}"
            # metadata
            meta_parts = [f"{k}:{v}" for k,v in (edges_meta_map.get(nid, []) or [])]
            if meta_parts:
                line += f" [{', '.join(meta_parts)}]"
            lines = [line]
            children = parent_map.get(nid, [])
            for idx, child in enumerate(children):
                sub_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(render_node(child, sub_prefix, idx == len(children)-1))
            return lines

        # 为每个 source 节点收集 edges metadata
        edges_meta_map = {}
        for e in edges:
            if e.source not in edges_meta_map:
                edges_meta_map[e.source] = []
            edges_meta_map[e.source].append((e.type, e.metadata.get("condition", "")))

        # 生成树状文本
        text_lines = []
        for r in roots:
            text_lines.extend(render_node(r))
        text_graph = "\n".join(text_lines)

        # ----------------- Summary -----------------
        summary = f"Diagram Summary: {len(nodes)} nodes, {len(edges)} edges, max depth {max(level_map.values(), default=0)}"

        return f"{summary}\n\n## Markdown Table\n\n{markdown}\n## Text Graph\n\n{text_graph}"