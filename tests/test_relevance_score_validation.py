#!/usr/bin/env python3
"""
Semantic Search Relevance Score Validation Tests
===============================================

专门测试语义搜索相关度分数的计算准确性和合理性
"""
import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.notes import NotesManager


class TestRelevanceScoreValidation(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment and precise relevance test data"""
        self.manager = NotesManager()
        self.conversation_id = "relevance_test_conversation"
        
        # Create test documents with different relevance levels
        self.test_documents = [
            # High relevance document - direct match
            {
                "title": "Deep Learning with Neural Networks",
                "content": "Deep learning neural networks use backpropagation for training. "
                          "Convolutional neural networks process images effectively. "
                          "Recurrent neural networks handle sequential data patterns.",
                "tags": ["deep-learning", "neural-networks", "backpropagation"],
                "note_type": "general",
                "expected_score_range": (0.4, 1.0)  # Expected high score
            },
            
            # Medium relevance document - partial match
            {
                "title": "Machine Learning Fundamentals", 
                "content": "Machine learning algorithms learn patterns from data. "
                          "Supervised learning requires labeled training examples. "
                          "Feature engineering improves model performance significantly.",
                "tags": ["machine-learning", "algorithms", "supervised"],
                "note_type": "general", 
                "expected_score_range": (0.1, 0.25)  # Expected medium score (adjusted)
            },
            
            # Low relevance document - conceptually related but not direct
            {
                "title": "Artificial Intelligence Ethics",
                "content": "AI systems must consider fairness and transparency issues. "
                          "Algorithmic bias affects decision making processes. "
                          "Responsible AI development requires ethical guidelines.",
                "tags": ["ai", "ethics", "fairness"],
                "note_type": "problem",
                "expected_score_range": (0.05, 0.2)  # Expected lower score
            },
            
            # Very low relevance document - technical but different domain
            {
                "title": "Web Development Best Practices",
                "content": "Frontend frameworks like React improve user interfaces. "
                          "Backend APIs handle data processing and storage. "
                          "DevOps practices ensure reliable application deployment.",
                "tags": ["web-development", "frontend", "backend"],
                "note_type": "solution",
                "expected_score_range": (0.0, 0.1)  # Expected very low score
            },
            
            # No relevance document - completely different domain
            {
                "title": "Cooking Recipe Management",
                "content": "Recipe storage requires organized ingredient lists. "
                          "Cooking time calculations depend on portion sizes. "
                          "Kitchen equipment affects preparation methods significantly.",
                "tags": ["cooking", "recipes", "ingredients"],
                "note_type": "general",
                "expected_score_range": (0.0, 0.05)  # Expected minimal score
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
    
    def test_score_ranges_for_neural_network_query(self):
        """Test relevance score ranges for neural network query"""
        query = "deep learning neural networks"
        
        result = self.manager.search_notes(
            conversation_id=self.conversation_id,
            query=query,
            search_type="semantic",
            limit=10
        )
        
        self.assertTrue(result["success"])
        results = result.get("results", [])
        self.assertGreater(len(results), 0, "Should return results for neural network query")
        
        # Verify each document's score is within expected range
        for note in results:
            title = note.get("title", "")
            score = note.get("relevance_score", 0)
            
            # Find corresponding expected score range
            expected_range = None
            for doc in self.test_documents:
                if doc["title"] == title:
                    expected_range = doc["expected_score_range"]
                    break
            
            if expected_range:
                min_score, max_score = expected_range
                self.assertGreaterEqual(score, min_score,
                                      f"Score {score:.3f} for '{title}' should be >= {min_score}")
                self.assertLessEqual(score, max_score,
                                   f"Score {score:.3f} for '{title}' should be <= {max_score}")
                
                print(f"✓ '{title}': {score:.3f} (expected: {min_score}-{max_score})")
    
    def test_score_distribution_patterns(self):
        """Test score distribution patterns for different queries"""
        test_queries = [
            {
                "query": "deep learning neural networks training",
                "expected_top_score_min": 0.35,
                "expected_score_spread": 0.2,  # 最高分和最低分应有合理差距
                "description": "具体技术术语应产生明确的分数层次"
            },
            {
                "query": "machine learning algorithms",
                "expected_top_score_min": 0.25,
                "expected_score_spread": 0.15,
                "description": "通用概念应产生中等分数分布"
            },
            {
                "query": "artificial intelligence",
                "expected_top_score_min": 0.15,
                "expected_score_spread": 0.1,
                "description": "宽泛概念应产生较低但分布的分数"
            }
        ]
        
        for case in test_queries:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=5
                )
                
                self.assertTrue(result["success"])
                results = result.get("results", [])
                
                if results:
                    scores = [note.get("relevance_score", 0) for note in results]
                    top_score = max(scores)
                    min_score = min(scores)
                    score_spread = top_score - min_score
                    
                    # 验证最高分合理性
                    self.assertGreaterEqual(top_score, case["expected_top_score_min"],
                                          f"Top score {top_score:.3f} should be >= {case['expected_top_score_min']} "
                                          f"for query '{case['query']}'")
                    
                    # 验证分数分布合理性
                    if len(scores) > 2:  # 只在有足够结果时检查分布
                        self.assertGreaterEqual(score_spread, case["expected_score_spread"],
                                              f"Score spread {score_spread:.3f} should be >= {case['expected_score_spread']} "
                                              f"for query '{case['query']}' to show discrimination")
                    
                    print(f"📊 Query: '{case['query']}'")
                    print(f"   Top score: {top_score:.3f}, Spread: {score_spread:.3f}")
    
    def test_semantic_similarity_accuracy(self):
        """Test accuracy of semantic similarity calculations"""
        similarity_cases = [
            {
                "query": "neural network deep learning",
                "similar_terms": ["neural networks", "deep learning", "backpropagation"],
                "dissimilar_terms": ["cooking", "recipe", "ingredients"],
                "description": "神经网络相关词汇应比烹饪词汇更相似"
            },
            {
                "query": "machine learning algorithms", 
                "similar_terms": ["supervised learning", "algorithms", "training"],
                "dissimilar_terms": ["frontend", "backend", "deployment"],
                "description": "机器学习词汇应比Web开发词汇更相似"
            }
        ]
        
        for case in similarity_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic",
                    limit=10
                )
                
                self.assertTrue(result["success"])
                results = result.get("results", [])
                
                # 计算包含相似词汇和不相似词汇的文档的平均分数
                similar_scores = []
                dissimilar_scores = []
                
                for note in results:
                    content = (note.get("title", "") + " " + note.get("content", "")).lower()
                    score = note.get("relevance_score", 0)
                    
                    has_similar = any(term.lower() in content for term in case["similar_terms"])
                    has_dissimilar = any(term.lower() in content for term in case["dissimilar_terms"])
                    
                    if has_similar and not has_dissimilar:
                        similar_scores.append(score)
                    elif has_dissimilar and not has_similar:
                        dissimilar_scores.append(score)
                
                # 验证相似词汇文档的平均分数高于不相似词汇文档
                if similar_scores and dissimilar_scores:
                    avg_similar = sum(similar_scores) / len(similar_scores)
                    avg_dissimilar = sum(dissimilar_scores) / len(dissimilar_scores)
                    
                    self.assertGreater(avg_similar, avg_dissimilar,
                                     f"Documents with similar terms should score higher on average. "
                                     f"Similar avg: {avg_similar:.3f}, Dissimilar avg: {avg_dissimilar:.3f}")
                    
                    print(f"🎯 Similarity test for '{case['query']}':")
                    print(f"   Similar terms avg score: {avg_similar:.3f}")
                    print(f"   Dissimilar terms avg score: {avg_dissimilar:.3f}")
    
    def test_score_normalization(self):
        """Test correctness of score normalization"""
        queries = [
            "deep learning neural networks",
            "machine learning algorithms", 
            "artificial intelligence ethics",
            "web development practices"
        ]
        
        all_scores = []
        
        for query in queries:
            result = self.manager.search_notes(
                conversation_id=self.conversation_id,
                query=query,
                search_type="semantic",
                limit=5
            )
            
            if result["success"]:
                scores = [note.get("relevance_score", 0) for note in result.get("results", [])]
                all_scores.extend(scores)
        
        if all_scores:
            min_score = min(all_scores)
            max_score = max(all_scores)
            
            # 验证分数在合理范围内（0-1之间）
            self.assertGreaterEqual(min_score, 0.0,
                                  f"All scores should be >= 0, found minimum: {min_score}")
            self.assertLessEqual(max_score, 1.0,
                                f"All scores should be <= 1, found maximum: {max_score}")
            
            # 验证分数分布合理（不是所有分数都一样）
            unique_scores = len(set(round(score, 3) for score in all_scores))
            self.assertGreater(unique_scores, 1,
                             "Should have variety in scores, not all the same")
            
            print(f"📏 Score normalization check:")
            print(f"   Range: {min_score:.3f} - {max_score:.3f}")
            print(f"   Unique scores: {unique_scores}/{len(all_scores)}")
    
    def test_query_term_matching_accuracy(self):
        """Test accuracy of query term matching"""
        term_matching_cases = [
            {
                "query": "deep learning",
                "must_contain_terms": ["deep learning"],
                "should_boost_terms": ["neural", "networks", "training"],
                "expected_min_score": 0.3,
                "description": "包含确切查询词汇的文档应获得高分"
            },
            {
                "query": "neural networks",
                "must_contain_terms": ["neural networks"],
                "should_boost_terms": ["deep", "learning", "backpropagation"],
                "expected_min_score": 0.3,
                "description": "神经网络文档应被神经网络查询高分匹配"
            },
            {
                "query": "machine learning algorithms",
                "must_contain_terms": ["machine learning", "algorithms"],
                "should_boost_terms": ["supervised", "training", "patterns"],
                "expected_min_score": 0.25,
                "description": "机器学习算法文档应被相关查询匹配"
            }
        ]
        
        for case in term_matching_cases:
            with self.subTest(query=case["query"]):
                result = self.manager.search_notes(
                    conversation_id=self.conversation_id,
                    query=case["query"],
                    search_type="semantic", 
                    limit=5
                )
                
                self.assertTrue(result["success"])
                results = result.get("results", [])
                
                # 找到包含必需词汇的文档
                exact_match_found = False
                exact_match_score = 0
                
                for note in results:
                    content = (note.get("title", "") + " " + note.get("content", "")).lower()
                    score = note.get("relevance_score", 0)
                    
                    # 检查是否包含必需词汇
                    contains_required = all(
                        term.lower() in content 
                        for term in case["must_contain_terms"]
                    )
                    
                    if contains_required:
                        exact_match_found = True
                        exact_match_score = max(exact_match_score, score)
                
                # 验证找到了包含必需词汇的文档
                self.assertTrue(exact_match_found,
                              f"Should find document containing {case['must_contain_terms']} "
                              f"for query '{case['query']}'")
                
                # 验证精确匹配获得了合理分数
                self.assertGreaterEqual(exact_match_score, case["expected_min_score"],
                                      f"Document with exact term matches should score >= {case['expected_min_score']}, "
                                      f"got {exact_match_score:.3f} for query '{case['query']}'")
                
                print(f"🔍 Term matching for '{case['query']}': {exact_match_score:.3f}")


def run_relevance_score_validation():
    """Run relevance score validation tests"""
    print("🎯 Running Relevance Score Validation Tests")
    print("=" * 55)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRelevanceScoreValidation)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*55}")
    print("📊 Relevance Score Validation Results")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failed Validation Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            
    if result.errors:
        print(f"\n💥 Validation Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print(f"\n✅ All relevance score validations passed!")
        print("🎉 Semantic search scoring is accurate and reliable!")
    else:
        print(f"\n⚠️ Some validations failed - review scoring algorithm")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_relevance_score_validation()
    sys.exit(0 if success else 1)
