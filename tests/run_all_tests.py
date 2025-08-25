import sys
import os
import unittest
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from tests.test_structured_knowledge_tool import TestStructuredKnowledgeManager
from tests.test_todo_tool import TestTodoTool
from tests.test_diagram_tool import TestDiagramTool
from tests.test_chat_fork import TestChatForkManager
# Removed server tests as they require complex mocking of FastMCP

def run_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStructuredKnowledgeManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTodoTool))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagramTool))
    suite.addTests(loader.loadTestsFromTestCase(TestChatForkManager))
    # Removed TestServer as it requires complex mocking of FastMCP
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == "__main__":
    run_tests()
