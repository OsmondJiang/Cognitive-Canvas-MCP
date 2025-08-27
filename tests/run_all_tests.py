import sys
import os
import unittest
import importlib.util
from unittest.mock import patch

# Add the parent directory to Python path to import tools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def discover_and_run_tests():
    """Automatically discover and run all test files in the tests folder"""
    
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Get all test files in the tests directory
    test_files = []
    for file in os.listdir(tests_dir):
        if file.startswith('test_') and file.endswith('.py') and file != 'test_server.py':
            # Skip test_server.py as it requires complex FastMCP mocking
            test_files.append(file)
    
    print(f"Discovered test files: {test_files}")
    
    # Import and add each test module
    for test_file in test_files:
        try:
            # Get the full path to the test file
            test_file_path = os.path.join(tests_dir, test_file)
            module_name = test_file[:-3]  # Remove .py extension
            
            # Load the module using importlib.util
            spec = importlib.util.spec_from_file_location(module_name, test_file_path)
            test_module = importlib.util.module_from_spec(spec)
            
            # Execute the module
            spec.loader.exec_module(test_module)
            
            # Find all test classes in the module
            for name in dir(test_module):
                obj = getattr(test_module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, unittest.TestCase) and 
                    obj != unittest.TestCase):
                    print(f"Adding test class: {name} from {module_name}")
                    suite.addTests(loader.loadTestsFromTestCase(obj))
                    
        except Exception as e:
            print(f"Error loading test module {test_file}: {e}")
            continue
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip() if 'Error:' in traceback else 'See details above'}")
    
    return result

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("RUNNING ALL TESTS (Auto-Discovery)")
    print("=" * 60)
    print("Use --manual flag to run with manual imports if auto-discovery fails")
    print("=" * 60)
    discover_and_run_tests()
        
