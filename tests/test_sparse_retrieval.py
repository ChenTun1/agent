"""BM25 稀疏检索器测试"""
import pytest
from backend.services.sparse_retrieval import SparseRetriever


class TestSparseRetriever:
    """测试 BM25 检索器"""

    @pytest.fixture
    def retriever(self):
        """创建检索器实例"""
        return SparseRetriever()

    @pytest.fixture
    def sample_docs(self):
        """示例文档"""
        return [
            {
                'id': 'doc1',
                'text': '深度学习是机器学习的一个分支,使用多层神经网络。',
                'page': 1
            },
            {
                'id': 'doc2',
                'text': '机器学习包括监督学习、无监督学习和强化学习。',
                'page': 1
            },
            {
                'id': 'doc3',
                'text': '神经网络由输入层、隐藏层和输出层组成。',
                'page': 2
            }
        ]

    def test_index_documents(self, retriever, sample_docs):
        """测试文档索引"""
        pdf_id = 'test_pdf'

        # 索引文档
        retriever.index_document(pdf_id, sample_docs)

        # 验证索引已创建
        assert pdf_id in retriever.bm25_index
        assert pdf_id in retriever.documents
        assert len(retriever.documents[pdf_id]) == 3

    def test_retrieve_relevant_docs(self, retriever, sample_docs):
        """测试检索相关文档"""
        pdf_id = 'test_pdf'
        retriever.index_document(pdf_id, sample_docs)

        # 查询: "什么是深度学习"
        results = retriever.retrieve('什么是深度学习', pdf_id, top_k=2)

        # 验证
        assert len(results) == 2
        # 第一个结果应该是 doc1 (包含"深度学习")
        assert results[0]['id'] == 'doc1'
        # 分数应该 > 0
        assert results[0]['score'] > 0

    def test_retrieve_nonexistent_pdf(self, retriever):
        """测试查询不存在的 PDF"""
        results = retriever.retrieve('测试', 'nonexistent', top_k=5)

        # 应返回空列表
        assert results == []

    def test_chinese_tokenization(self, retriever):
        """测试中文分词"""
        tokens = retriever.tokenize('深度学习是机器学习的分支')

        # 验证分词结果
        assert '深度' in tokens or '深度学习' in tokens
        assert '机器' in tokens or '机器学习' in tokens
        assert len(tokens) > 0
