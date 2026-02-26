"""
智能分块器

基于语义边界的动态分块,保持语义完整性
"""
import re
from typing import List, Dict


class SmartChunker:
    """智能分块器 - 基于语义边界"""

    def chunk(
        self,
        text: str,
        max_tokens: int = 512,
        overlap: int = 50
    ) -> List[Dict]:
        """
        智能分块

        Args:
            text: 输入文本
            max_tokens: 最大 token 数
            overlap: 重叠 token 数

        Returns:
            分块列表,每个块包含 text 和 tokens
        """
        # 1. 句子分割
        sentences = self.split_sentences(text)

        if not sentences:
            return []

        chunks = []
        current_chunk = []
        current_tokens = 0

        for i, sent in enumerate(sentences):
            sent_tokens = self.count_tokens(sent)

            # 2. 检查语义边界
            next_sents = sentences[i+1:i+3] if i+1 < len(sentences) else []
            is_boundary = self.is_semantic_boundary(sent, next_sents)

            # 如果是边界且当前块已有内容,切分
            # 段落边界(\n\n)优先级更高,不需要 token 限制
            is_paragraph_boundary = '\n\n' in sent
            if is_boundary and current_chunk and (is_paragraph_boundary or current_tokens > 200):
                chunk_text = ''.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'tokens': current_tokens
                })

                # 3. Overlap 处理
                if overlap > 0 and len(current_chunk) >= 2:
                    overlap_sents = current_chunk[-2:]
                    current_chunk = overlap_sents
                    current_tokens = sum(
                        self.count_tokens(s) for s in overlap_sents
                    )
                else:
                    current_chunk = []
                    current_tokens = 0

            # 添加当前句子
            current_chunk.append(sent)
            current_tokens += sent_tokens

            # 4. 超长强制切分
            if current_tokens >= max_tokens:
                chunk_text = ''.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'tokens': current_tokens
                })

                # Overlap
                if overlap > 0 and len(current_chunk) >= 2:
                    overlap_sents = current_chunk[-2:]
                    current_chunk = overlap_sents
                    current_tokens = sum(
                        self.count_tokens(s) for s in overlap_sents
                    )
                else:
                    current_chunk = []
                    current_tokens = 0

        # 最后一个块
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'tokens': current_tokens
            })

        return chunks

    def is_semantic_boundary(self, current: str, next_sents: List[str]) -> bool:
        """
        判断是否语义边界

        Args:
            current: 当前句子
            next_sents: 后续句子

        Returns:
            是否为边界
        """
        # 规则检测
        boundary_patterns = [
            r'\n\n',           # 段落结束
            r'^#+\s',          # Markdown 标题
            r'^\d+\.\s',       # 数字列表
            r'^[-*]\s',        # 无序列表
            r'。\s*$',         # 句号结尾
            r'[。!?]\s*$',     # 标点结尾
        ]

        for pattern in boundary_patterns:
            if re.search(pattern, current):
                return True

        return False

    def split_sentences(self, text: str) -> List[str]:
        """
        句子分割

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        # 使用标点符号分割
        sentences = re.split(r'([。!?;;\n]+)', text)

        # 合并标点到句子
        result = []
        for i in range(0, len(sentences)-1, 2):
            sent = sentences[i]
            if i+1 < len(sentences):
                sent += sentences[i+1]

            if sent.strip():
                result.append(sent)

        # 处理最后一个句子(如果没有标点)
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1])

        return result

    def count_tokens(self, text: str) -> int:
        """
        Token 计数 (近似)

        规则:
        - 中文: 1字 ≈ 1.5 tokens
        - 英文: 1词 ≈ 1.3 tokens

        Args:
            text: 输入文本

        Returns:
            Token 数量
        """
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', text))

        # 估算 tokens
        tokens = int(chinese_chars * 1.5 + english_words * 1.3)

        return max(tokens, 1)  # 至少 1 个 token


# 全局单例
_smart_chunker = None


def get_smart_chunker() -> SmartChunker:
    """获取全局智能分块器实例"""
    global _smart_chunker
    if _smart_chunker is None:
        _smart_chunker = SmartChunker()
    return _smart_chunker
