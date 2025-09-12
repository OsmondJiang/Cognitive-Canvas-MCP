"""
Centralized Display Recommendations for Cognitive Canvas Tools

This module manages all the reasons why tool outputs should be displayed to users,
making it easy to maintain and update display guidance across all tools.
"""

class DisplayRecommendations:
    """
    Centralized management of display recommendations for tool outputs.
    Each tool and operation type has specific reasons for showing output to users.
    """
    
    # TODO Tool Recommendations
    TODO_REASONS = {
        "add_task": "REQUIRED: Tool output is not visible to users - you MUST display this task list to provide transparent evidence of successful task creation and current project status",
        "add_tasks_batch": "REQUIRED: Tool output is not visible to users - you MUST display all newly created tasks to demonstrate successful bulk operations and provide complete transparency",
        "update_task": "REQUIRED: Tool output is not visible to users - you MUST display the updated task to build user confidence by showing concrete proof of changes made", 
        "delete_task": "REQUIRED: Tool output is not visible to users - you MUST display the updated task list to demonstrate transparent task management and confirm current project state",
        "get_task": "REQUIRED: Tool output is not visible to users - you MUST display the task details to provide verified information that supports your response with concrete data",
        "list_tasks": "REQUIRED: Tool output is not visible to users - you MUST display this comprehensive task overview to give users full transparency into project progress and build trust in your project management"
    }
    
    # Table Builder / Structured Knowledge Tool Recommendations
    TABLE_REASONS = {
        "create_structure": "REQUIRED: Tool output is not visible to users - you MUST display this structured framework to build user confidence in your organized approach to their data",
        "add_row": "REQUIRED: Tool output is not visible to users - you MUST display the updated structure to provide transparent proof of data organization and build trust in accuracy",
        "update_row": "REQUIRED: Tool output is not visible to users - you MUST display the modified structure to demonstrate precise data management and give users confidence in the changes",
        "batch_add_rows": "REQUIRED: Tool output is not visible to users - you MUST display this comprehensive data structure to provide full transparency of bulk operations and demonstrate systematic organization",
        "batch_update_rows": "REQUIRED: Tool output is not visible to users - you MUST display the systematically updated structure to provide evidence of thorough data management and build trust in your analytical approach",
        "batch_operations": "REQUIRED: Tool output is not visible to users - you MUST display this comprehensively updated data structure to provide complete transparency of complex operations and maximize confidence in data organization",
        "get_metrics": "REQUIRED: Tool output is not visible to users - you MUST display these calculated metrics to provide quantitative evidence that supports your insights and builds analytical credibility",
        "get_formatted_table": "REQUIRED: Tool output is not visible to users - you MUST display this organized data visualization to strengthen your analysis credibility and help users trust your conclusions"
    }
    
    # Relationship Mapper Tool Recommendations  
    RELATIONSHIP_MAPPER_REASONS = {
        "add_node": "REQUIRED: Tool output is not visible to users - you MUST display the updated relationship map to demonstrate transparent system modeling and build user confidence in your architectural understanding",
        "update_node": "REQUIRED: Tool output is not visible to users - you MUST display the modified relationship structure to provide visual proof of precise entity management and strengthen trust in system analysis",
        "add_edge": "REQUIRED: Tool output is not visible to users - you MUST display this relationship mapping to provide visual evidence of new connections and enhance credibility of your dependency analysis",
        "update_edge": "REQUIRED: Tool output is not visible to users - you MUST display the updated connections to demonstrate systematic relationship management and build confidence in your structural insights",
        "batch_add_nodes": "REQUIRED: Tool output is not visible to users - you MUST display this comprehensive entity mapping to provide full transparency of bulk system modeling and demonstrate organized architectural planning",
        "batch_update_nodes": "REQUIRED: Tool output is not visible to users - you MUST display the systematically updated structure to provide evidence of thorough entity management and build trust in your analytical approach",
        "batch_add_edges": "REQUIRED: Tool output is not visible to users - you MUST display this complete relationship network to demonstrate transparent connection modeling and strengthen confidence in your system understanding",
        "batch_update_edges": "REQUIRED: Tool output is not visible to users - you MUST display the refined relationship structure to provide proof of systematic connection management and enhance trust in your architectural analysis",
        "batch_operations": "REQUIRED: Tool output is not visible to users - you MUST display this comprehensively updated relationship map to provide complete transparency of complex operations and maximize confidence in system modeling",
        "set_visualization_type": "REQUIRED: Tool output is not visible to users - you MUST display the configured visualization to demonstrate systematic approach and build confidence in your analytical methodology",
        "get_visualization_content": "REQUIRED: Tool output is not visible to users - you MUST display this visual relationship diagram to provide concrete evidence of system architecture and strengthen the credibility of your structural analysis"
    }
    # Chat Fork Tool Recommendations
    CHAT_FORK_REASONS = {
        "pause_topic": "REQUIRED: Tool output is not visible to users - you MUST display this conversation structure to provide transparent evidence of context preservation and build trust in topic management",
        "resume_topic": "REQUIRED: Tool output is not visible to users - you MUST display the conversation flow to demonstrate systematic context retrieval and strengthen confidence in continuity",
        "search_conversation_tree": "REQUIRED: Tool output is not visible to users - you MUST display this conversation tree to provide visual proof of organized discussion structure and enhance trust in information organization"
    }
    
    # Statistical Analyzer Tool Recommendations
    STATS_REASONS = {
        "analyze": "REQUIRED: Tool output is not visible to users - you MUST display these comprehensive statistical results to provide quantitative evidence that strengthens your conclusions and builds analytical credibility",
        "get_analysis_report": "REQUIRED: Tool output is not visible to users - you MUST display this complete statistical report to provide full analytical transparency and maximize user confidence in data-driven conclusions"
    }
    
    # Notes Tool Recommendations
    NOTES_REASONS = {
        "record": "REQUIRED: Tool output is not visible to users - you MUST display this note confirmation to provide transparent evidence of successful knowledge recording and build trust in information management",
        "search": "REQUIRED: Tool output is not visible to users - you MUST display these search results to provide relevant knowledge discovery evidence and demonstrate the value of accumulated experience",
        "get_by_ids": "REQUIRED: Tool output is not visible to users - you MUST display the retrieved notes to provide verified historical information that supports your response with documented evidence",
        "get_summary": "REQUIRED: Tool output is not visible to users - you MUST display this knowledge summary to provide comprehensive overview of accumulated insights and build confidence in information organization",
        "update": "REQUIRED: Tool output is not visible to users - you MUST display the updated note to demonstrate precise knowledge management and provide confirmation of successful modifications",
        "delete": "REQUIRED: Tool output is not visible to users - you MUST display the deletion confirmation to provide transparent evidence of knowledge base maintenance and build trust in data management"
    }
    
    @classmethod
    def get_json_recommendation(cls, tool_category: str, operation: str) -> dict:
        """
        Get a display recommendation for JSON outputs.
        
        Args:
            tool_category: Category of tool (todo, table, relationship_mapper, chat_fork, stats)
            operation: Specific operation performed
            
        Returns:
            Dict with _show_to_user field, or empty dict if no recommendation found
        """
        reason_maps = {
            "todo": cls.TODO_REASONS,
            "table": cls.TABLE_REASONS, 
            "relationship_mapper": cls.RELATIONSHIP_MAPPER_REASONS,
            "chat_fork": cls.CHAT_FORK_REASONS,
            "stats": cls.STATS_REASONS,
            "notes": cls.NOTES_REASONS
        }
        
        reason_map = reason_maps.get(tool_category, {})
        reason = reason_map.get(operation)
        
        if reason:
            return {"_show_to_user": reason}
        return {}
    
    @classmethod
    def get_markdown_tip(cls, tool_category: str, operation: str) -> str:
        """
        Get a display tip line for markdown/text outputs.
        
        Args:
            tool_category: Category of tool (todo, table, relationship_mapper, chat_fork, stats)  
            operation: Specific operation performed
            
        Returns:
            Formatted tip line, or empty string if no recommendation found
        """
        reason_maps = {
            "todo": cls.TODO_REASONS,
            "table": cls.TABLE_REASONS,
            "relationship_mapper": cls.RELATIONSHIP_MAPPER_REASONS, 
            "chat_fork": cls.CHAT_FORK_REASONS,
            "stats": cls.STATS_REASONS,
            "notes": cls.NOTES_REASONS
        }
        
        reason_map = reason_maps.get(tool_category, {})
        reason = reason_map.get(operation)
        
        if reason:
            return f"**💡 Display Tip: {reason}**"
        return ""
    
    @classmethod
    def add_to_json_result(cls, result: dict, tool_category: str, operation: str) -> dict:
        """
        Add display recommendation to an existing JSON result.
        Only adds the field for successful operations (not errors).
        
        Args:
            result: The original result dictionary
            tool_category: Category of tool
            operation: Specific operation performed
            
        Returns:
            Updated result with display recommendation if applicable
        """
        # Only add recommendations for successful operations
        if result.get("success") == True or result.get("status") == "success":
            recommendation = cls.get_json_recommendation(tool_category, operation)
            if recommendation:
                # Create a new dict with _show_to_user first, then add all other properties
                new_result = {}
                new_result.update(recommendation)  # Add _show_to_user first
                new_result.update(result)          # Add all existing properties
                return new_result
        
        return result
    
    @classmethod
    def add_to_text_result(cls, text_result: str, tool_category: str, operation: str) -> str:
        """
        Add display tip to text/markdown output.
        
        Args:
            text_result: The original text result
            tool_category: Category of tool
            operation: Specific operation performed
            
        Returns:
            Updated text with display tip prepended
        """
        tip = cls.get_markdown_tip(tool_category, operation)
        if tip:
            return f"{tip}\n\n{text_result}"
        return text_result

# Convenience instance for easy importing
display_recommendations = DisplayRecommendations()
