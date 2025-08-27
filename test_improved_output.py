#!/usr/bin/env python3
"""
演示改进后的Statistical Evidence Tool输出
展示纯数字化、无结论性判断的统计分析结果
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.statistical_evidence import StatisticalEvidenceTool

def demo_improved_output():
    tool = StatisticalEvidenceTool()
    conv_id = "demo_improved"
    
    print("🔬 Statistical Evidence Tool - 改进后的输出演示")
    print("=" * 60)
    print("特点：")
    print("✅ 纯数字展示，无主观结论")
    print("✅ 详细注释解释统计指标含义")
    print("✅ 让AI自己判断统计显著性")
    print("=" * 60)
    
    # 演示1: 配对t检验
    print("\n📊 演示1: 配对t检验 (训练前后对比)")
    print("-" * 40)
    
    before_after_data = {
        "before": [70, 72, 68, 75, 73, 69, 71, 74],
        "after": [78, 80, 76, 83, 81, 77, 79, 82]
    }
    
    result1 = tool.analyze(conv_id, data=before_after_data, analysis_type="paired_comparison")
    print(result1)
    
    # 演示2: 多组比较 (ANOVA)
    print("\n\n📊 演示2: 多组比较 (不同教学方法效果)")
    print("-" * 40)
    
    teaching_groups = {
        "traditional": [72, 74, 70, 73, 71, 75],
        "interactive": [78, 82, 76, 80, 79, 81], 
        "ai_assisted": [88, 91, 86, 89, 87, 90]
    }
    
    result2 = tool.analyze(conv_id, groups=teaching_groups, analysis_type="anova_analysis")
    print(result2)
    
    # 演示3: 相关性分析
    print("\n\n📊 演示3: 相关性分析 (经验vs绩效)")
    print("-" * 40)
    
    correlation_data = {
        "experience_years": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "performance_score": [65, 68, 72, 75, 78, 82, 85, 88, 91, 95]
    }
    
    result3 = tool.analyze(conv_id, data=correlation_data, analysis_type="correlation_analysis")
    print(result3)
    
    # 演示4: 批量分析
    print("\n\n📊 演示4: 批量分析")
    print("-" * 40)
    
    batch_data = {
        "satisfaction": [7.2, 8.1, 6.8, 7.9, 8.3, 7.5, 8.0, 7.7],
        "productivity": [85, 92, 78, 89, 94, 82, 90, 87],
        "engagement": [6.5, 7.8, 6.2, 7.4, 8.1, 6.9, 7.6, 7.3]
    }
    
    batch_analyses = [
        {"type": "descriptive", "variables": ["satisfaction", "productivity"]},
        {"type": "correlation", "var1": "satisfaction", "var2": "productivity"},
        {"type": "correlation", "var1": "engagement", "var2": "productivity"}
    ]
    
    result4 = tool.batch_analyze(conv_id, batch_data, batch_analyses)
    print(result4)
    
    print("\n\n🎯 总结")
    print("=" * 60)
    print("改进后的输出特点：")
    print("• 所有p值都有详细解释其含义")
    print("• 效应量提供类别和解释标准")
    print("• 统计量包含计算说明")
    print("• 没有'显著'或'不显著'的主观判断")
    print("• AI可以基于数值自己做出合理判断")

if __name__ == "__main__":
    demo_improved_output()
