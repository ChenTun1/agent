"""混合检索测试"""
import pytest
from backend.services.hybrid_retrieval import HybridRetriever
from tests.fixtures.test_data import get_test_documents, get_test_queries


class TestHybridRetrieval:
    """测试混合检索"""

    @pytest.fixture
    def retriever(self):
        """创建混合检索器"""
        return HybridRetriever()

    @pytest.fixture
    def indexed_retriever(self, retriever):
        """创建已索引的检索器"""
        pdf_id = 'test_pdf'
        docs = get_test_documents()

        # 索引文档 (BM25)
        retriever.index_documents(pdf_id, docs)

        # 模拟向量检索 (简化版,返回相同文档)
        # 实际环境中会调用 Qdrant
        retriever._mock_dense_retrieval = True

        return retriever

    def test_rrf_fusion(self, retriever):
        """测试 RRF 融合算法"""
        # 模拟两路召回结果
        dense_results = [
            {'id': 'doc1', 'score': 0.9},
            {'id': 'doc2', 'score': 0.8},
            {'id': 'doc3', 'score': 0.7}
        ]

        sparse_results = [
            {'id': 'doc2', 'score': 5.0},  # BM25 分数范围不同
            {'id': 'doc1', 'score': 4.0},
            {'id': 'doc4', 'score': 3.0}
        ]

        # RRF 融合
        merged = retriever.rrf_fusion(dense_results, sparse_results, k=60)

        # 验证
        assert len(merged) > 0
        # doc1 和 doc2 在两路都出现,分数应该更高
        top_ids = [item['id'] for item in merged[:2]]
        assert 'doc1' in top_ids
        assert 'doc2' in top_ids

    def test_hybrid_retrieval_accuracy(self, indexed_retriever):
        """测试混合检索准确率"""
        pdf_id = 'test_pdf'
        queries = get_test_queries()

        correct = 0
        total = len(queries)

        for query_item in queries:
            query = query_item['query']
            expected_id = query_item['expected_chunk_id']

            # 检索
            results = indexed_retriever.retrieve(
                query,
                pdf_id,
                top_k=3
            )

            # 验证第一个结果
            if results and results[0]['id'] == expected_id:
                correct += 1
                print(f"✓ {query_item['description']}: {query}")
            else:
                print(f"✗ {query_item['description']}: {query}")
                if results:
                    print(f"  Got: {results[0]['id']}, Expected: {expected_id}")

        # 计算准确率
        accuracy = correct / total
        print(f"\nAccuracy: {accuracy:.1%} ({correct}/{total})")

        # 准确率应该 >= 60% (混合检索的基准)
        assert accuracy >= 0.6

    def test_retrieval_score_threshold(self, indexed_retriever):
        """测试检索分数阈值"""
        pdf_id = 'test_pdf'

        results = indexed_retriever.retrieve(
            '深度学习',
            pdf_id,
            top_k=5
        )

        # 第一个结果分数应该 > 0
        assert len(results) > 0
        assert results[0]['rrf_score'] > 0

        # 结果应该按分数降序排列
        scores = [r['rrf_score'] for r in results]
        assert scores == sorted(scores, reverse=True)
