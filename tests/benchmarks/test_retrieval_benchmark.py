"""检索性能基准测试"""
import pytest
import time
from backend.services.hybrid_retrieval import get_hybrid_retriever
from backend.services.sparse_retrieval import get_sparse_retriever
from tests.fixtures.test_data import get_test_documents, get_test_queries


class TestRetrievalBenchmark:
    """检索性能基准"""

    @pytest.fixture
    def setup_retrievers(self):
        """设置检索器"""
        pdf_id = 'benchmark_pdf'
        docs = get_test_documents()

        # BM25
        sparse = get_sparse_retriever()
        sparse.index_document(pdf_id, docs)

        # Hybrid
        hybrid = get_hybrid_retriever()
        hybrid._mock_dense_retrieval = True
        hybrid.index_documents(pdf_id, docs)

        return {
            'pdf_id': pdf_id,
            'sparse': sparse,
            'hybrid': hybrid,
            'queries': get_test_queries()
        }

    def test_sparse_retrieval_accuracy(self, setup_retrievers):
        """BM25 检索准确率基准"""
        data = setup_retrievers
        correct = 0

        for query_item in data['queries']:
            results = data['sparse'].retrieve(
                query_item['query'],
                data['pdf_id'],
                top_k=5
            )

            if results and results[0]['id'] == query_item['expected_chunk_id']:
                correct += 1

        accuracy = correct / len(data['queries'])
        print(f"\n[BM25] Accuracy: {accuracy:.1%}")

        # BM25 基准: >= 40%
        assert accuracy >= 0.4

    def test_hybrid_retrieval_accuracy(self, setup_retrievers):
        """混合检索准确率基准"""
        data = setup_retrievers
        correct = 0

        for query_item in data['queries']:
            results = data['hybrid'].retrieve(
                query_item['query'],
                data['pdf_id'],
                top_k=5
            )

            if results and results[0]['id'] == query_item['expected_chunk_id']:
                correct += 1

        accuracy = correct / len(data['queries'])
        print(f"\n[Hybrid] Accuracy: {accuracy:.1%}")

        # 混合检索基准: >= 60%
        assert accuracy >= 0.6

    def test_retrieval_latency(self, setup_retrievers):
        """检索延迟基准"""
        data = setup_retrievers
        query = "深度学习是什么?"

        # 测试 10 次取平均
        latencies = []
        for _ in range(10):
            start = time.time()
            data['hybrid'].retrieve(query, data['pdf_id'], top_k=5)
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        print(f"\n[Hybrid] Avg Latency: {avg_latency:.1f}ms")

        # 延迟基准: <= 250ms
        assert avg_latency <= 250

    def test_accuracy_improvement(self, setup_retrievers):
        """验证混合检索相比 BM25 的提升"""
        data = setup_retrievers

        # BM25 准确率
        bm25_correct = 0
        for query_item in data['queries']:
            results = data['sparse'].retrieve(
                query_item['query'],
                data['pdf_id'],
                top_k=5
            )
            if results and results[0]['id'] == query_item['expected_chunk_id']:
                bm25_correct += 1

        bm25_accuracy = bm25_correct / len(data['queries'])

        # 混合检索准确率
        hybrid_correct = 0
        for query_item in data['queries']:
            results = data['hybrid'].retrieve(
                query_item['query'],
                data['pdf_id'],
                top_k=5
            )
            if results and results[0]['id'] == query_item['expected_chunk_id']:
                hybrid_correct += 1

        hybrid_accuracy = hybrid_correct / len(data['queries'])

        improvement = (hybrid_accuracy - bm25_accuracy) / bm25_accuracy * 100 if bm25_accuracy > 0 else 0

        print(f"\n[Comparison]")
        print(f"  BM25: {bm25_accuracy:.1%}")
        print(f"  Hybrid: {hybrid_accuracy:.1%}")
        print(f"  Improvement: +{improvement:.1f}%")

        # 混合检索应该优于或等于 BM25
        assert hybrid_accuracy >= bm25_accuracy
