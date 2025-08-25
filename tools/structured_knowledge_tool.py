from typing import Dict, List, Optional
import json

class StructuredKnowledgeManager:
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
        return f"Structure '{structure_id}' created with template '{template_type}'."

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
            return f"Structure '{structure_id}' does not exist."
        structure["rows"].append(row_data)
        return f"Row added to '{structure_id}'."

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
            return f"Structure '{structure_id}' does not exist."
        if row_index < 0 or row_index >= len(structure["rows"]):
            return f"Row index {row_index} out of range."
        structure["rows"][row_index].update(row_data)
        return f"Row {row_index} updated in '{structure_id}'."

    def get_metrics(self, conversation_id: str, structure_id: str):
        """
        Automatically calculate indicators based on template type, such as completion rate, tick ratio, voting statistics, etc.
        """
        self._ensure_conv(conversation_id)
        structure = self.conversations[conversation_id].get(structure_id)
        if not structure:
            return f"Structure '{structure_id}' does not exist."

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

        return f"{summary}\n\n## Markdown\n{markdown}\n\n## JSON\n{json_output}"
