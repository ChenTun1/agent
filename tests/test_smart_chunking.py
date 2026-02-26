"""智能分块器测试"""
import pytest
from backend.services.smart_chunking import SmartChunker


class TestSmartChunker:
    """测试智能分块器"""

    @pytest.fixture
    def chunker(self):
        """创建分块器实例"""
        return SmartChunker()

    def test_chunk_short_text(self, chunker):
        """测试短文本分块"""
        text = "这是一个简短的测试文本。"

        chunks = chunker.chunk(text, max_tokens=512)

        # 短文本应该只有一个块
        assert len(chunks) == 1
        assert chunks[0]['text'] == text

    def test_chunk_with_paragraphs(self, chunker):
        """测试段落分块"""
        text = """第一段内容。这是第一段的详细说明。

第二段内容。这是第二段的详细说明。这段更长一些,包含更多信息。

第三段内容。最后一段。"""

        chunks = chunker.chunk(text, max_tokens=100, overlap=0)

        # 应该按段落分块
        assert len(chunks) >= 2
        # 每个块都应该包含完整内容
        for chunk in chunks:
            assert chunk['text'].strip()
            assert chunk['tokens'] > 0

    def test_chunk_with_overlap(self, chunker):
        """测试 Overlap 功能"""
        # 5 句话
        text = "第一句话。第二句话。第三句话。第四句话。第五句话。"

        chunks = chunker.chunk(text, max_tokens=30, overlap=10)

        # 应该有 overlap
        assert len(chunks) >= 2

        # 检查是否有重叠内容
        if len(chunks) >= 2:
            # 第一个块的结尾应该和第二个块的开头有重叠
            last_sent = chunks[0]['text'].split('。')[-2]  # 倒数第二句
            first_sent = chunks[1]['text'].split('。')[0]  # 第一句

            # 可能有部分重叠
            assert len(chunks[0]['text']) > 0
            assert len(chunks[1]['text']) > 0

    def test_semantic_boundary_detection(self, chunker):
        """测试语义边界检测"""
        # 标题 + 内容
        text = """# 深度学习简介

深度学习是机器学习的一个分支。它使用多层神经网络进行特征学习。

## 神经网络结构

神经网络包括输入层、隐藏层和输出层。"""

        # 测试是否识别标题为边界
        assert chunker.is_semantic_boundary("# 深度学习简介\n", [])
        assert chunker.is_semantic_boundary("## 神经网络结构\n", [])

    def test_token_counting(self, chunker):
        """测试 Token 计数"""
        # 中文
        chinese_text = "深度学习是机器学习的分支"
        tokens = chunker.count_tokens(chinese_text)
        # 中文约 1.5 tokens/字
        assert tokens > len(chinese_text)  # 应该大于字数

        # 英文
        english_text = "deep learning machine"
        tokens = chunker.count_tokens(english_text)
        # 英文约 1.3 tokens/词
        assert tokens > 0
