#!/usr/bin/env python3
"""
Semantic Search Accuracy Test Cases
==================================

Test semantic search accuracy and relevance to ensure search results meet expectations
"""
import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.notes import NotesManager


class TestNotesSemanticAccuracy(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with standardized test data"""
        self.manager = NotesManager()
        self.conversation_id = "accuracy_test_conversation"
        
        # Create standardized test documents with varying relevance levels
        self.test_documents = [
            # High relevance group - AI/ML content
            {
                "title": "Deep Learning Neural Networks",
                "content": "Neural networks are the foundation of deep learning. Backpropagation algorithm trains multi-layer perceptrons. Convolutional neural networks excel at image recognition tasks.",
                "tags": ["deep-learning", "neural-networks", "ai", "machine-learning"],
                "note_type": "general"
            },
            {
                "title": "Machine Learning Algorithms Overview",
                "content": "Supervised learning uses labeled data for training models. Unsupervised learning finds patterns in unlabeled data. Reinforcement learning agents learn through interaction.",
                "tags": ["machine-learning", "algorithms", "supervised", "unsupervised"],
                "note_type": "general"
            },
            {
                "title": "Artificial Intelligence Ethics",
                "content": "AI systems must address fairness and transparency. Algorithmic bias can lead to discrimination. Responsible AI development requires ethical guidelines.",
                "tags": ["ai", "ethics", "bias", "fairness"],
                "note_type": "problem"
            },
            
            # Medium relevance group - Database content
            {
                "title": "Database Query Optimization",
                "content": "SQL query performance optimization through proper indexing. Connection pooling reduces database overhead. Query execution plan analysis identifies bottlenecks.",
                "tags": ["database", "sql", "optimization", "performance"],
                "note_type": "solution"
            },
            {
                "title": "NoSQL Database Design",
                "content": "Document databases store JSON-like structures. Key-value stores provide fast retrieval. Graph databases model relationships between entities effectively.",
                "tags": ["nosql", "database", "document", "graph"],
                "note_type": "general"
            },
            
            # Low relevance group - Web development
            {
                "title": "Frontend Framework Comparison",
                "content": "React uses virtual DOM for efficient rendering. Vue.js provides reactive data binding. Angular offers comprehensive development framework with TypeScript.",
                "tags": ["frontend", "react", "vue", "angular"],
                "note_type": "experience"
            },
            {
                "title": "CSS Grid Layout Techniques",
                "content": "Grid layout provides two-dimensional design control. Flexbox handles one-dimensional arrangements. Responsive design ensures cross-device compatibility.",
                "tags": ["css", "grid", "layout", "responsive"],
                "note_type": "general"
            },
            
            # Zero relevance group - Completely unrelated
            {
                "title": "Cooking Recipe Collection",
                "content": "Pasta cooking requires salted boiling water. Timing is crucial for perfect texture. Fresh herbs enhance flavor profiles significantly.",
                "tags": ["cooking", "recipe", "pasta", "herbs"],
                "note_type": "general"
            }
        ]
        
        # Add all test documents
        for doc in self.test_documents:
            self.manager.record_note(
                conversation_id=self.conversation_id,
                content=doc["content"],
                title=doc["title"],
                note_type=doc["note_type"],
                tags=doc["tags"]
            )
    
    def test_high_relevance_semantic_queries(self):
        """Test that high-relevance queries return correct top results with good scores"""
        test_cases = [
            {
                "query": "deep learning neural networks",
                "expected_top_title": "Deep Learning Neural Networks",
                "min_score": 0.65,  # Raised from 0.3 - expects strong semantic match
                "description": "Direct match of technical terms should score highly"
            },
            {
                "query": "machine learning algorithms supervised",
                "expected_top_title": "Machine Learning Algorithms Overview",
                "min_score": 0.45,  # Raised from 0.25 - expects good conceptual match
                "description": "Algorithm overview document should match ML query"
            },
            {
                "query": "artificial intelligence ethics bias",
                "expected_top_title": "Artificial Intelligence Ethics",
                "min_score": 0.35,  # Raised from 0.25 - expects solid thematic match
                "description": "Ethics document should match AI ethics query"
            },
            {
                "query": "database SQL optimization performance",
                "expected_top_title": "Database Query Optimization",
                "min_score": 0.45,  # Raised from 0.25 - expects strong technical match
                "description": "Database optimization should match performance query"
            }
        ]
        
        for case in test_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                # Verify search succeeded
                self.assertTrue(result["success"], 
                              f"Search should succeed for query: {case['query']}")
                
                # Verify results returned
                self.assertGreater(len(result["results"]), 0,
                                 f"Should return results for query: {case['query']}")
                
                # Verify correct document is ranked first
                top_result = result["results"][0]
                self.assertEqual(top_result["title"], case["expected_top_title"],
                               f"Expected '{case['expected_top_title']}' as top result for '{case['query']}', "
                               f"got '{top_result['title']}'")
                
                # Verify score meets minimum threshold
                top_score = top_result.get("relevance_score", 0)
                self.assertGreaterEqual(top_score, case["min_score"],
                                      f"Score {top_score:.3f} should be >= {case['min_score']} for '{case['query']}'")
    
    def test_relevance_ranking_correctness(self):
        """Test that results are ranked in correct order by relevance"""
        ranking_cases = [
            {
                "query": "neural network deep learning",
                "expected_top_documents": [
                    "Deep Learning Neural Networks",
                    "Machine Learning Algorithms Overview"
                ],
                "description": "Neural network query should rank DL doc first, ML doc second"
            },
            {
                "query": "database design optimization",
                "expected_top_documents": [
                    "Database Query Optimization",
                    "NoSQL Database Design"
                ],
                "description": "Database query should rank optimization first, design second"
            }
        ]
        
        for case in ranking_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                self.assertTrue(result["success"])
                self.assertGreaterEqual(len(result["results"]), 2)
                
                # Check top documents appear in expected order
                actual_titles = [doc["title"] for doc in result["results"][:2]]
                expected_titles = case["expected_top_documents"]
                
                for i, expected_title in enumerate(expected_titles):
                    if i < len(actual_titles):
                        self.assertIn(expected_title, actual_titles,
                                    f"Expected '{expected_title}' in top 2 results for '{case['query']}'")
                
                # Verify scores are in descending order
                scores = [doc.get("relevance_score", 0) for doc in result["results"]]
                self.assertEqual(scores, sorted(scores, reverse=True),
                               f"Scores should be in descending order for '{case['query']}'")
    
    def test_irrelevant_query_filtering(self):
        """Test that irrelevant queries don't highly match unrelated content"""
        irrelevant_cases = [
            {
                "query": "cooking pasta recipe herbs",
                "max_tech_score": 0.15,
                "description": "Cooking query should not highly match technical documents"
            },
            {
                "query": "boiling water salt timing",
                "max_ai_score": 0.15,
                "description": "Cooking terms should not highly match AI/ML content"
            },
            {
                "query": "nonexistent gibberish random words",
                "max_score": 0.1,
                "max_results": 3,
                "description": "Nonsensical queries should return low scores and few results"
            }
        ]
        
        for case in irrelevant_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                self.assertTrue(result["success"])
                results = result.get("results", [])
                
                # Check maximum results constraint
                if "max_results" in case:
                    self.assertLessEqual(len(results), case["max_results"],
                                       f"Should return <= {case['max_results']} results for irrelevant query")
                
                # Check maximum score constraint
                if results and "max_score" in case:
                    top_score = results[0].get("relevance_score", 0)
                    self.assertLessEqual(top_score, case["max_score"],
                                       f"Top score {top_score:.3f} should be <= {case['max_score']}")
                
                # Check technical documents don't score highly for cooking queries
                if "max_tech_score" in case or "max_ai_score" in case:
                    tech_keywords = ["neural", "machine", "learning", "database", "algorithm"]
                    max_allowed = case.get("max_tech_score", case.get("max_ai_score", 0.15))
                    
                    for doc in results:
                        content_text = (doc.get("title", "") + " " + doc.get("content", "")).lower()
                        if any(keyword in content_text for keyword in tech_keywords):
                            score = doc.get("relevance_score", 0)
                            self.assertLessEqual(score, max_allowed,
                                               f"Technical doc '{doc['title']}' scored {score:.3f}, "
                                               f"should be <= {max_allowed} for cooking query")
    
    def test_semantic_understanding_vs_keyword_matching(self):
        """Test semantic understanding performs better than simple keyword matching"""
        semantic_cases = [
            {
                "query": "neural networks artificial intelligence",
                "should_find_highly": "Deep Learning Neural Networks",
                "should_not_find_highly": "CSS Grid Layout Techniques",
                "min_relevant_score": 0.4  # Raised expectation for strong match
            },
            {
                "query": "database performance tuning optimization",
                "should_find_highly": "Database Query Optimization",
                "should_not_find_highly": "Cooking Recipe Collection", 
                "min_relevant_score": 0.35  # Raised expectation for technical match
            },
            {
                "query": "supervised machine learning training",
                "should_find_highly": "Machine Learning Algorithms Overview",
                "should_not_find_highly": "Frontend Framework Comparison",
                "min_relevant_score": 0.3   # Raised expectation for conceptual match
            }
        ]
        
        for case in semantic_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                self.assertTrue(result["success"])
                results = result.get("results", [])
                self.assertGreater(len(results), 0)
                
                # Find scores for relevant and irrelevant documents
                relevant_score = 0
                irrelevant_score = 0
                relevant_found = False
                
                for doc in results:
                    title = doc.get("title", "")
                    score = doc.get("relevance_score", 0)
                    
                    if title == case["should_find_highly"]:
                        relevant_score = score
                        relevant_found = True
                    elif title == case["should_not_find_highly"]:
                        irrelevant_score = score
                
                # Verify relevant document was found
                self.assertTrue(relevant_found,
                              f"Should find '{case['should_find_highly']}' for query '{case['query']}'")
                
                # Verify relevant document meets minimum score
                self.assertGreaterEqual(relevant_score, case["min_relevant_score"],
                                      f"Relevant document should score >= {case['min_relevant_score']}, "
                                      f"got {relevant_score:.3f}")
                
                # Verify relevant document scores higher than irrelevant (if found)
                if irrelevant_score > 0:
                    self.assertGreater(relevant_score, irrelevant_score,
                                     f"Relevant doc ({relevant_score:.3f}) should outscore "
                                     f"irrelevant doc ({irrelevant_score:.3f})")
    
    def test_combined_search_tag_boosting(self):
        """Test that combined search properly boosts documents with matching tags"""
        boost_cases = [
            {
                "query": "machine learning",
                "boost_tags": ["deep-learning", "neural-networks"],
                "target_document": "Deep Learning Neural Networks",
                "min_boost": 0.7  # Raised from 0.15 - expects strong tag boost (70% of actual ~1.04)
            },
            {
                "query": "database optimization",
                "boost_tags": ["sql", "performance"], 
                "target_document": "Database Query Optimization",
                "min_boost": 0.5  # Raised from 0.1 - expects strong tag boost (60% of actual ~0.83)
            }
        ]
        
        for case in boost_cases:
            with self.subTest(query=case["query"], tags=case["boost_tags"]):
                # Get baseline semantic search score
                semantic_result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                # Get combined search score with tag boost
                combined_result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_tags=case["boost_tags"],
                    search_type="combined",
                    limit=5
                )
                
                self.assertTrue(semantic_result["success"])
                self.assertTrue(combined_result["success"])
                
                # Find target document scores in both results
                semantic_score = 0
                combined_score = 0
                
                for doc in semantic_result.get("results", []):
                    if doc.get("title") == case["target_document"]:
                        semantic_score = doc.get("relevance_score", 0)
                        break
                
                for doc in combined_result.get("results", []):
                    if doc.get("title") == case["target_document"]:
                        combined_score = doc.get("relevance_score", 0)
                        break
                
                # Verify tag boost occurred
                if semantic_score > 0:
                    self.assertGreater(combined_score, semantic_score,
                                     f"Combined search should boost score. "
                                     f"Semantic: {semantic_score:.3f}, Combined: {combined_score:.3f}")
                    
                    boost_amount = combined_score - semantic_score
                    self.assertGreaterEqual(boost_amount, case["min_boost"],
                                          f"Boost amount {boost_amount:.3f} should be >= {case['min_boost']}")
    
    def test_search_result_consistency(self):
        """Test that repeated searches return consistent results"""
        consistency_queries = [
            "deep learning neural networks",
            "database query optimization",
            "machine learning algorithms"
        ]
        
        for query in consistency_queries:
            with self.subTest(query=query):
                # Run same query multiple times
                search_results = []
                for _ in range(3):
                    result = self.manager.search_notes(
                        conversation_id=self.conversation_id,
                        query=query,
                        search_type="semantic",
                        limit=3
                    )
                    self.assertTrue(result["success"])
                    search_results.append(result)
                
                # Check consistency across runs
                if len(search_results) > 1:
                    first_titles = [doc["title"] for doc in search_results[0]["results"]]
                    
                    for i, current_result in enumerate(search_results[1:], 1):
                        current_titles = [doc["title"] for doc in current_result["results"]]
                        
                        # Top result should be consistent
                        if first_titles and current_titles:
                            self.assertEqual(first_titles[0], current_titles[0],
                                           f"Top result should be consistent for '{query}'")
                        
                        # At least 50% overlap in top results
                        if len(first_titles) >= 2 and len(current_titles) >= 2:
                            overlap = len(set(first_titles[:2]).intersection(set(current_titles[:2])))
                            self.assertGreaterEqual(overlap, 1,
                                                  f"Should have overlap in top results for '{query}'")


def run_semantic_accuracy_tests():
    """Run semantic search accuracy test suite"""
    print("🎯 Running Semantic Search Accuracy Tests")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNotesSemanticAccuracy)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*50}")
    print("📊 Test Results Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n✅ All accuracy tests passed!")
        print("🎉 Semantic search accuracy validated!")
    else:
        print("\n⚠️ Some tests failed - review implementation")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_semantic_accuracy_tests()
    sys.exit(0 if success else 1)
