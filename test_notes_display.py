#!/usr/bin/env python3
"""
测试Notes工具的Display Recommendations
=====================================

验证notes工具的display recommendations是否正确工作
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.notes import NotesManager
from tools.display_recommendations import DisplayRecommendations


def test_notes_display_recommendations():
    """测试notes工具的display recommendations"""
    print("🧪 Testing Notes Display Recommendations")
    print("=" * 45)
    
    manager = NotesManager()
    conversation_id = "display_test"
    
    # 测试记录note
    print("\n1. 测试记录note")
    result = manager.record_note(
        conversation_id=conversation_id,
        content="This is a test note for display recommendations",
        title="Test Note",
        note_type="general",
        tags=["test", "display"]
    )
    
    print(f"Record result has _show_to_user: {'_show_to_user' in result}")
    if '_show_to_user' in result:
        print(f"Display message length: {len(result['_show_to_user'])}")
    
    # 测试搜索notes
    print("\n2. 测试搜索notes")
    search_result = manager.search_notes(
        conversation_id=conversation_id,
        query="test note",
        search_type="semantic"
    )
    
    print(f"Search result has _show_to_user: {'_show_to_user' in search_result}")
    if '_show_to_user' in search_result:
        print(f"Display message length: {len(search_result['_show_to_user'])}")
    
    # 测试获取summary
    print("\n3. 测试获取summary")
    summary_result = manager.get_conversation_summary(conversation_id)
    
    print(f"Summary result has _show_to_user: {'_show_to_user' in summary_result}")
    if '_show_to_user' in summary_result:
        print(f"Display message length: {len(summary_result['_show_to_user'])}")
    
    # 测试DisplayRecommendations类的方法
    print("\n4. 测试DisplayRecommendations类")
    
    # 测试获取notes recommendations
    record_rec = DisplayRecommendations.get_json_recommendation("notes", "record")
    search_rec = DisplayRecommendations.get_json_recommendation("notes", "search")
    
    print(f"Record recommendation available: {'_show_to_user' in record_rec}")
    print(f"Search recommendation available: {'_show_to_user' in search_rec}")
    
    # 测试添加到结果
    test_result = {"success": True, "data": "test"}
    updated_result = DisplayRecommendations.add_to_json_result(test_result, "notes", "record")
    
    print(f"Updated result has _show_to_user: {'_show_to_user' in updated_result}")
    
    print("\n✅ Notes Display Recommendations测试完成")


if __name__ == "__main__":
    test_notes_display_recommendations()
