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
            "status": "success",
            "message": f"Structure '{structure_id}' created with template '{template_type}'.",
            "structure": {
                "structure_id": structure_id,
                "template_type": template_type,
                "columns": columns or [],
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
                "status": "error",
                "message": f"Structure '{structure_id}' does not exist."
            }
        structure["rows"].append(row_data)
        return {
            "status": "success",
            "message": f"Row added to '{structure_id}'.",
            "structure_id": structure_id,
            "row_data": row_data,
            "total_rows": len(structure["rows"])
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
                "status": "error",
                "message": f"Structure '{structure_id}' does not exist."
            }
        if row_index < 0 or row_index >= len(structure["rows"]):
            return {
                "status": "error",
                "message": f"Row index {row_index} out of range.",
                "max_index": len(structure["rows"]) - 1
            }
        structure["rows"][row_index].update(row_data)
        return {
            "status": "success",
            "message": f"Row {row_index} updated in '{structure_id}'.",
            "structure_id": structure_id,
            "row_index": row_index,
            "updated_data": row_data,
            "total_rows": len(structure["rows"])
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
                "status": "error",
                "message": f"Structure '{structure_id}' does not exist."
            }
        
        results = []
        added_rows = []
        errors = []
        
        for i, row_data in enumerate(rows):
            if not isinstance(row_data, dict):
                error_msg = f"Row {i} is not a valid dictionary"
                errors.append(error_msg)
                results.append({"status": "error", "row_index": i, "message": error_msg})
                continue
            structure["rows"].append(row_data)
            added_rows.append(row_data)
            results.append({"status": "success", "row_index": i, "message": f"Row {i} added to '{structure_id}'.", "row_data": row_data})
        
        return {
            "status": "success",
            "message": f"Batch add rows completed. {len(added_rows)} rows added, {len(errors)} errors.",
            "structure_id": structure_id,
            "added_rows": added_rows,
            "errors": errors,
            "total_rows": len(structure["rows"]),
            "results": results
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
                "status": "error",
                "message": f"Structure '{structure_id}' does not exist."
            }
        
        results = []
        updated_rows = []
        errors = []
        
        for update in updates:
            row_index = update.get("index")
            row_data = update.get("data", {})
            
            if row_index is None:
                error_msg = f"Missing 'index' for update {update}"
                errors.append(error_msg)
                results.append({"status": "error", "message": error_msg})
                continue
                
            if not isinstance(row_data, dict):
                error_msg = f"Invalid 'data' for row {row_index}"
                errors.append(error_msg)
                results.append({"status": "error", "row_index": row_index, "message": error_msg})
                continue
                
            if row_index < 0 or row_index >= len(structure["rows"]):
                error_msg = f"Row index {row_index} out of range."
                errors.append(error_msg)
                results.append({"status": "error", "row_index": row_index, "message": error_msg})
                continue
                
            structure["rows"][row_index].update(row_data)
            updated_info = {"index": row_index, "data": row_data}
            updated_rows.append(updated_info)
            results.append({"status": "success", "row_index": row_index, "message": f"Row {row_index} updated in '{structure_id}'.", "updated_data": row_data})
        
        return {
            "status": "success",
            "message": f"Batch update rows completed. {len(updated_rows)} rows updated, {len(errors)} errors.",
            "structure_id": structure_id,
            "updated_rows": updated_rows,
            "errors": errors,
            "total_rows": len(structure["rows"]),
            "results": results
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
                "status": "error",
                "message": f"Structure '{structure_id}' does not exist."
            }
        
        results = []
        success_count = 0
        error_count = 0
        
        for op in operations:
            action = op.get("action")
            data = op.get("data", {})
            
            if action == "add":
                if not isinstance(data, dict):
                    results.append({"status": "error", "action": "add", "message": "Invalid data for add operation"})
                    error_count += 1
                    continue
                structure["rows"].append(data)
                results.append({"status": "success", "action": "add", "message": f"Row added to '{structure_id}'.", "row_data": data})
                success_count += 1
                
            elif action == "update":
                row_index = data.get("index")
                row_data = data.get("row_data", {})
                
                if row_index is None:
                    results.append({"status": "error", "action": "update", "message": "Missing 'index' for update operation"})
                    error_count += 1
                    continue
                    
                if not isinstance(row_data, dict):
                    results.append({"status": "error", "action": "update", "message": "Invalid 'row_data' for update operation"})
                    error_count += 1
                    continue
                    
                if row_index < 0 or row_index >= len(structure["rows"]):
                    results.append({"status": "error", "action": "update", "message": f"Row index {row_index} out of range."})
                    error_count += 1
                    continue
                    
                structure["rows"][row_index].update(row_data)
                results.append({"status": "success", "action": "update", "message": f"Row {row_index} updated in '{structure_id}'.", "row_index": row_index, "updated_data": row_data})
                success_count += 1
                
            else:
                results.append({"status": "error", "action": action, "message": f"Unknown action '{action}' in batch operations"})
                error_count += 1
        
        return {
            "status": "success",
            "message": f"Batch operations completed. {success_count} successful, {error_count} errors.",
            "structure_id": structure_id,
            "total_operations": len(operations),
            "successful_operations": success_count,
            "failed_operations": error_count,
            "total_rows": len(structure["rows"]),
            "results": results
        }

    def get_metrics(self, conversation_id: str, structure_id: str):
        """
        Automatically calculate indicators based on template type, such as completion rate, tick ratio, voting statistics, etc.
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return {
                "status": "error",
                "message": f"Structure '{structure_id}' does not exist."
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

        return metrics

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
        metrics = self.get_metrics(conversation_id, structure_id)
        summary = f"Structure '{structure_id}' ({template_type}) with {len(rows)} items.\nMetrics: {metrics}"

        return f"{summary}\n\n## Markdown\n{markdown}"
