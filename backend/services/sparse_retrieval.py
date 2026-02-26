"""
BM25 稀疏检索器

使用 BM25 算法进行关键词检索,适合精确匹配场景
"""
from rank_bm25 import BM25Okapi
import jieba
import numpy as np
from typing import List, Dict, Optional


class SparseRetriever:
    """BM25 稀疏检索器"""

    def __init__(self):
        """初始化检索器"""
        # {pdf_id: BM25Okapi 实例}
        self.bm25_index: Dict[str, BM25Okapi] = {}

        # {pdf_id: [文档列表]}
        self.documents: Dict[str, List[Dict]] = {}

    def tokenize(self, text: str) -> List[str]:
        """
        中文分词

        Args:
            text: 输入文本

        Returns:
            分词后的 token 列表
        """
        # 使用 jieba 分词
        tokens = list(jieba.cut(text))

        # 过滤空白符
        tokens = [t.strip() for t in tokens if t.strip()]

        return tokens

    def index_document(self, pdf_id: str, chunks: List[Dict]):
        """
        为文档建立 BM25 索引

        Args:
            pdf_id: PDF 唯一 ID
            chunks: 文档块列表,每个块包含 id, text, page
        """
        # 分词所有文档
        tokenized_docs = []
        for chunk in chunks:
            tokens = self.tokenize(chunk['text'])
            tokenized_docs.append(tokens)

        # 建立 BM25 索引
        self.bm25_index[pdf_id] = BM25Okapi(tokenized_docs)

        # 存储原始文档
        self.documents[pdf_id] = chunks

        print(f"[BM25] Indexed {len(chunks)} chunks for PDF {pdf_id}")

    def retrieve(
        self,
        query: str,
        pdf_id: str,
        top_k: int = 20
    ) -> List[Dict]:
        """
        BM25 检索

        Args:
            query: 查询文本
            pdf_id: PDF ID
            top_k: 返回 Top-K 结果

        Returns:
            检索结果列表,每个结果包含原始文档 + score
        """
        # 检查索引是否存在
        if pdf_id not in self.bm25_index:
            print(f"[BM25] No index found for PDF {pdf_id}")
            return []

        # 查询分词
        tokenized_query = self.tokenize(query)

        # BM25 打分
        scores = self.bm25_index[pdf_id].get_scores(tokenized_query)

        # 排序并取 Top-K
        top_indices = np.argsort(scores)[::-1][:top_k]

        # 构建结果
        results = []
        for idx in top_indices:
            # 跳过分数为 0 的结果
            if scores[idx] == 0:
                continue

            chunk = self.documents[pdf_id][idx].copy()
            chunk['score'] = float(scores[idx])
            chunk['retrieval_method'] = 'bm25'
            results.append(chunk)

        print(f"[BM25] Retrieved {len(results)} results for query: {query[:30]}...")

        return results

    def clear_index(self, pdf_id: str):
        """清除指定 PDF 的索引"""
        if pdf_id in self.bm25_index:
            del self.bm25_index[pdf_id]
            del self.documents[pdf_id]
            print(f"[BM25] Cleared index for PDF {pdf_id}")


# 全局单例
_sparse_retriever = None


def get_sparse_retriever() -> SparseRetriever:
    """获取全局 BM25 检索器实例"""
    global _sparse_retriever
    if _sparse_retriever is None:
        _sparse_retriever = SparseRetriever()
    return _sparse_retriever
