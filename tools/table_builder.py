from typing import Dict, List, Optional
import json

class TableBuilder:
    def __init__(self):
        # conversation_id -> structure_id -> structure
        self.conversations: Dict[str, Dict[str, Dict]] = {}

    def _ensure_conv(self, conversation_id: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {}

    def create_structure(
        self,
        conversation_id: str,
        structure_id: str,
        template_type: str = "simple_table",
        columns: Optional[List[str]] = None,
    ):
        """
        Create a new table/list structure for a conversation.
        """
        self._ensure_conv(conversation_id)
        self.conversations[conversation_id][structure_id] = {
            "template_type": template_type,
            "columns": columns or [],
            "rows": []
        }
        return {
            "success": True,
            "data": {
                "structure_id": structure_id,
                "template_type": template_type,
                "columns": columns or [],
                "rows": [],
                "row_count": 0
            }
        }

    def add_row(
        self,
        conversation_id: str,
        structure_id: str,
        row_data: Dict
    ):
        """
        Add a new row/item to the structure.
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "success": False,
                "error": f"Structure '{structure_id}' does not exist in conversation '{conversation_id}'. Use create_structure() first with structure_id='{structure_id}' and template_type (e.g., 'simple_table', 'task_list')."
            }
        structure["rows"].append(row_data)
        return {
            "success": True,
            "data": {
                "structure_id": structure_id,
                "template_type": structure["template_type"],
                "columns": structure["columns"],
                "rows": structure["rows"],
                "row_count": len(structure["rows"])
            }
        }

    def update_row(
        self,
        conversation_id: str,
        structure_id: str,
        row_index: int,
        row_data: Dict
    ):
        """
        Update a specific row by index.
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "success": False,
                "error": f"Structure '{structure_id}' does not exist in conversation '{conversation_id}'. Use create_structure() first."
            }
        if row_index < 0 or row_index >= len(structure["rows"]):
            return {
                "success": False,
                "error": f"Row index {row_index} out of range. Structure has {len(structure['rows'])} rows (valid indices: 0-{len(structure['rows'])-1 if structure['rows'] else 'none'})."
            }
        structure["rows"][row_index].update(row_data)
        return {
            "success": True,
            "data": {
                "structure_id": structure_id,
                "template_type": structure["template_type"],
                "columns": structure["columns"],
                "rows": structure["rows"],
                "row_count": len(structure["rows"])
            }
        }

    # ---------------- Batch Operations ----------------
    def batch_add_rows(self, conversation_id: str, structure_id: str, rows: List[Dict]):
        """
        Batch add rows
        rows: [{"column1": "value1", "column2": "value2"}, ...]
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "success": False,
                "error": f"Structure '{structure_id}' does not exist in conversation '{conversation_id}'. Use create_structure() first."
            }
        
        # Validate all rows first (atomic operation)
        failed_validations = []
        validated_rows = []
        
        for i, row_data in enumerate(rows):
            if not isinstance(row_data, dict):
                failed_validations.append(f"Row {i}: must be a dictionary, got {type(row_data).__name__}")
                continue
            validated_rows.append(row_data)
        
        # If any validation failed, return error without adding any rows
        if failed_validations:
            return {
                "success": False,
                "error": "Some rows failed validation: " + "; ".join(failed_validations) + ". Example: [{'column1': 'value1', 'column2': 'value2'}]"
            }
        
        # Add all validated rows
        for row_data in validated_rows:
            structure["rows"].append(row_data)
        
        return {
            "success": True,
            "data": {
                "structure_id": structure_id,
                "template_type": structure["template_type"],
                "columns": structure["columns"],
                "rows": structure["rows"],
                "row_count": len(structure["rows"])
            }
        }

    def batch_update_rows(self, conversation_id: str, structure_id: str, updates: List[Dict]):
        """
        Batch update rows
        updates: [{"index": int, "data": dict}, ...]
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "success": False,
                "error": f"Structure '{structure_id}' does not exist in conversation '{conversation_id}'. Use create_structure() first."
            }
        
        # Validate all updates first (atomic operation)
        failed_validations = []
        validated_updates = []
        
        for i, update in enumerate(updates):
            row_index = update.get("index")
            row_data = update.get("data", {})
            
            if row_index is None:
                failed_validations.append(f"Update {i}: missing required 'index' field")
                continue
                
            if not isinstance(row_data, dict):
                failed_validations.append(f"Update {i}: 'data' must be a dictionary, got {type(row_data).__name__}")
                continue
                
            if row_index < 0 or row_index >= len(structure["rows"]):
                failed_validations.append(f"Update {i}: row index {row_index} out of range (structure has {len(structure['rows'])} rows)")
                continue
                
            validated_updates.append({"index": row_index, "data": row_data})
        
        # If any validation failed, return error without updating any rows
        if failed_validations:
            return {
                "success": False,
                "error": "Some updates failed validation: " + "; ".join(failed_validations) + ". Example: [{'index': 0, 'data': {'column': 'new_value'}}]"
            }
        
        # Apply all validated updates
        for update in validated_updates:
            structure["rows"][update["index"]].update(update["data"])
        
        return {
            "success": True,
            "data": {
                "structure_id": structure_id,
                "template_type": structure["template_type"],
                "columns": structure["columns"],
                "rows": structure["rows"],
                "row_count": len(structure["rows"])
            }
        }

    def batch_operations(self, conversation_id: str, structure_id: str, operations: List[Dict]):
        """
        operations: [
            {"action": "add", "data": dict},
            {"action": "update", "data": {"index": int, "row_data": dict}},
            ...
        ]
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "success": False,
                "error": f"Structure '{structure_id}' does not exist in conversation '{conversation_id}'. Use create_structure() first."
            }
        
        # Execute operations sequentially with individual validation
        for i, op in enumerate(operations):
            action = op.get("action")
            data = op.get("data", {})
            
            if action == "add":
                if not isinstance(data, dict):
                    return {
                        "success": False,
                        "error": f"Operation {i}: 'add' action requires 'data' to be a dictionary. Example: {{'action': 'add', 'data': {{'col': 'val'}}}}"
                    }
                # Execute add operation
                structure["rows"].append(data)
                
            elif action == "update":
                row_index = data.get("index")
                row_data = data.get("row_data", {})
                
                if row_index is None:
                    return {
                        "success": False,
                        "error": f"Operation {i}: 'update' action requires 'data.index'. Example: {{'action': 'update', 'data': {{'index': 0, 'row_data': {{'col': 'new_val'}}}}}}"
                    }
                    
                if not isinstance(row_data, dict):
                    return {
                        "success": False,
                        "error": f"Operation {i}: 'update' action requires 'data.row_data' to be a dictionary. Example: {{'action': 'update', 'data': {{'index': 0, 'row_data': {{'col': 'new_val'}}}}}}"
                    }
                    
                if row_index < 0 or row_index >= len(structure["rows"]):
                    return {
                        "success": False,
                        "error": f"Operation {i}: row index {row_index} out of range (structure has {len(structure['rows'])} rows). Valid indices: 0-{len(structure['rows'])-1 if structure['rows'] else 'none'}."
                    }
                
                # Execute update operation
                structure["rows"][row_index].update(row_data)
                
            else:
                return {
                    "success": False,
                    "error": f"Operation {i}: unknown action '{action}'. Supported actions: 'add', 'update'. Example: {{'action': 'add', 'data': {{'col': 'val'}}}}"
                }
        
        return {
            "success": True,
            "data": {
                "structure_id": structure_id,
                "template_type": structure["template_type"],
                "columns": structure["columns"],
                "rows": structure["rows"],
                "row_count": len(structure["rows"])
            }
        }

    def get_metrics(self, conversation_id: str, structure_id: str):
        """
        Automatically calculate indicators based on template type, such as completion rate, tick ratio, voting statistics, etc.
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "success": False,
                "error": f"Structure '{structure_id}' does not exist in conversation '{conversation_id}'. Use create_structure() first."
            }

        template_type = structure["template_type"]
        rows = structure["rows"]
        metrics = {}

        if template_type in ["task_list", "progress_table"]:
            status_count = {}
            for row in rows:
                status = row.get("Status", "Unknown")
                status_count[status] = status_count.get(status, 0) + 1
            total = len(rows)
            completed = status_count.get("Completed", 0)
            metrics = {
                "total_items": total,
                "status_count": status_count,
                "completion_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%"
            }

        elif template_type == "check_list":
            total = len(rows)
            checked = sum(1 for row in rows if row.get("checked"))
            metrics = {
                "total_items": total,
                "checked_items": checked,
                "checked_rate": f"{(checked / total * 100):.1f}%" if total > 0 else "0%"
            }

        elif template_type == "voting_table":
            vote_count = {}
            for row in rows:
                option = row.get("Option", "Unknown")
                count = row.get("Votes", 0)
                vote_count[option] = vote_count.get(option, 0) + count
            total_votes = sum(vote_count.values())
            metrics = {
                "total_votes": total_votes,
                "vote_distribution": vote_count
            }

        else:
            metrics = {"total_items": len(rows)}

        return {
            "success": True,
            "data": metrics
        }

    def render(self, conversation_id: str, structure_id: str):
        """
        Render the structure according to its template_type.
        Outputs Markdown + JSON + summary text, including metrics.
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return f"Structure '{structure_id}' does not exist."

        rows = structure["rows"]
        columns = structure["columns"]
        template_type = structure["template_type"]

        markdown = ""
        # Table-like templates
        if template_type in ["simple_table", "task_list", "progress_table", "voting_table"]:
            if not columns:
                columns = list({k for row in rows for k in row.keys()})
            # Column widths
            col_widths = [len(c) for c in columns]
            for row in rows:
                for i, col in enumerate(columns):
                    col_widths[i] = max(col_widths[i], len(str(row.get(col, ""))))
            # Header
            markdown += "| " + " | ".join([c.ljust(col_widths[i]) for i, c in enumerate(columns)]) + " |\n"
            markdown += "|-" + "-|-".join(["-"*w for w in col_widths]) + "-|\n"
            # Rows
            for row in rows:
                markdown += "| " + " | ".join([str(row.get(columns[i], "")).ljust(col_widths[i]) for i in range(len(columns))]) + " |\n"

        # List-like templates
        elif template_type == "bulleted_list":
            markdown = "\n".join(f"- {row.get('content', str(row))}" for row in rows)
        elif template_type == "numbered_list":
            markdown = "\n".join(f"{i+1}. {row.get('content', str(row))}" for i, row in enumerate(rows))
        elif template_type == "check_list":
            markdown = "\n".join(f"[{'x' if row.get('checked') else ' '}] {row.get('content', str(row))}" for row in rows)

        # JSON output
        json_output = json.dumps(rows, indent=2, ensure_ascii=False)

        # Summary text
        metrics_result = self.get_metrics(conversation_id, structure_id)
        if metrics_result["success"]:
            metrics = metrics_result["data"]
        else:
            metrics = {"error": "Failed to get metrics"}
            
        summary = f"Structure '{structure_id}' ({template_type}) with {len(rows)} items.\nMetrics: {metrics}"

        return f"{summary}\n\n## Markdown\n{markdown}"
