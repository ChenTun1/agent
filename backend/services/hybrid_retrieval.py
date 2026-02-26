"""
混合检索器

Dense (向量) + Sparse (BM25) 双路召回 + RRF 融合
"""
from typing import List, Dict, Optional
from backend.services.sparse_retrieval import get_sparse_retriever


class HybridRetriever:
    """混合检索器 - 企业级 RAG 核心"""

    def __init__(self):
        """初始化混合检索器"""
        self.sparse_retriever = get_sparse_retriever()
        self._mock_dense_retrieval = False  # 测试模式

    def index_documents(self, pdf_id: str, chunks: List[Dict]):
        """
        索引文档

        Args:
            pdf_id: PDF ID
            chunks: 文档块列表
        """
        # 索引到 BM25
        self.sparse_retriever.index_document(pdf_id, chunks)

        # TODO: 索引到 Qdrant (向量数据库)
        # 当前阶段暂不实现,等 Phase 3 集成
        print(f"[Hybrid] Indexed {len(chunks)} chunks for {pdf_id}")

    def retrieve(
        self,
        query: str,
        pdf_id: str,
        top_k: int = 5,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5
    ) -> List[Dict]:
        """
        混合检索

        Args:
            query: 查询文本
            pdf_id: PDF ID
            top_k: 返回 Top-K
            dense_weight: 向量检索权重 (暂未使用)
            sparse_weight: BM25 权重 (暂未使用)

        Returns:
            融合后的检索结果
        """
        # 1. BM25 稀疏检索
        sparse_results = self.sparse_retriever.retrieve(
            query,
            pdf_id,
            top_k=20
        )

        # 2. 向量密集检索
        if self._mock_dense_retrieval:
            # 测试模式: 使用 sparse 结果模拟
            dense_results = sparse_results.copy()
        else:
            # TODO: 调用 Qdrant 检索 (Phase 3 实现)
            dense_results = []

        # 3. RRF 融合
        if dense_results:
            merged = self.rrf_fusion(dense_results, sparse_results)
        else:
            # 如果没有向量结果,只用 BM25
            merged = sparse_results

        # 4. 取 Top-K
        return merged[:top_k]

    def rrf_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        """
        RRF (Reciprocal Rank Fusion) 融合算法

        Score = sum(1 / (k + rank))

        Args:
            dense_results: 向量检索结果
            sparse_results: BM25 检索结果
            k: 常数 (通常 60)

        Returns:
            融合后的结果列表
        """
        scores = {}
        doc_map = {}

        # 处理 dense 结果
        for rank, doc in enumerate(dense_results, start=1):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        # 处理 sparse 结果
        for rank, doc in enumerate(sparse_results, start=1):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        # 排序
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 构建结果
        results = []
        for doc_id, score in ranked:
            doc = doc_map[doc_id].copy()
            doc['rrf_score'] = score
            doc['retrieval_method'] = 'hybrid'
            results.append(doc)

        print(f"[Hybrid] RRF fusion: {len(results)} unique documents")

        return results


# 全局单例
_hybrid_retriever = None


def get_hybrid_retriever() -> HybridRetriever:
    """获取全局混合检索器实例"""
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever
