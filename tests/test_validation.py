"""
答案验证模块的单元测试
"""

import pytest
from backend.validation import AnswerValidator, validate_answer


class TestAnswerValidator:
    """AnswerValidator类的测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.validator = AnswerValidator()

    def test_validate_answer_with_citation(self):
        """测试带有正确引用的答案"""
        answer = "根据第5页的内容,准确率是95%。[来源: 第5页]"
        chunks = [{'page': 5, 'text': '准确率是95%'}]

        result = self.validator.validate(answer, chunks)

        assert result['has_citation'] is True
        assert result['citation_format_valid'] is True
        assert result['valid_pages'] is True
        assert result['confidence'] > 0.8
        assert len(result['warnings']) == 0

    def test_validate_answer_without_citation(self):
        """测试缺少引用的答案"""
        answer = "准确率是95%"
        chunks = [{'page': 5, 'text': '准确率是95%'}]

        result = self.validator.validate(answer, chunks)

        assert result['has_citation'] is False
        assert '答案缺少来源引用' in result['warnings']
        assert result['confidence'] < 0.8

    def test_validate_answer_with_invalid_pages(self):
        """测试引用了不存在页码的答案"""
        answer = "根据第10页,准确率是95%。[来源: 第10页]"
        chunks = [{'page': 5, 'text': '准确率是95%'}]

        result = self.validator.validate(answer, chunks)

        assert result['has_citation'] is True
        assert result['valid_pages'] is False
        assert '引用的页码不在检索到的文档块中' in result['warnings']

    def test_validate_answer_with_hallucination(self):
        """测试包含幻觉的答案"""
        answer = "我认为准确率应该是95%左右吧。[来源: 第5页]"
        chunks = [{'page': 5, 'text': '这是一些不相关的内容'}]

        result = self.validator.validate(answer, chunks)

        assert result['no_hallucination'] is False
        assert len(result['hallucination_indicators']) > 0
        assert '我认为' in result['hallucination_indicators']

    def test_validate_answer_consistency(self):
        """测试答案一致性检查"""
        # 高一致性
        answer = "系统使用了深度学习方法,在ImageNet数据集上进行训练。"
        chunks = [
            {'page': 3, 'text': '我们使用深度学习方法'},
            {'page': 5, 'text': '在ImageNet数据集上进行了训练'}
        ]

        result = self.validator.validate(answer, chunks)

        assert result['consistent'] is True
        assert result['consistency_score'] >= 0.5

    def test_validate_answer_low_consistency(self):
        """测试低一致性答案"""
        answer = "系统使用了量子计算和区块链技术"
        chunks = [
            {'page': 3, 'text': '我们使用传统的机器学习方法'},
        ]

        result = self.validator.validate(answer, chunks)

        assert result['consistent'] is False
        assert '一致性较低' in ' '.join(result['warnings'])

    def test_extract_cited_pages(self):
        """测试页码提取"""
        text = "根据第5页和第10页的内容,以及第23页的结论。[来源: 第5页, 第10页]"
        pages = self.validator._extract_cited_pages(text)

        assert 5 in pages
        assert 10 in pages
        assert 23 in pages

    def test_extract_key_phrases(self):
        """测试关键短语提取"""
        text = "系统使用了深度学习方法,在ImageNet数据集上训练,准确率达到95%。"
        phrases = self.validator._extract_key_phrases(text)

        assert len(phrases) > 0
        assert any('深度学习' in p for p in phrases)

    def test_validate_batch(self):
        """测试批量验证"""
        qa_pairs = [
            ("第5页说准确率是95%。[来源: 第5页]", [{'page': 5, 'text': '准确率是95%'}]),
            ("方法在第3页描述。", [{'page': 3, 'text': '方法描述'}])
        ]

        results = self.validator.validate_batch(qa_pairs)

        assert len(results) == 2
        assert results[0]['has_citation'] is True
        assert results[1]['has_citation'] is False

    def test_get_summary_stats(self):
        """测试汇总统计"""
        results = [
            {'has_citation': True, 'valid_pages': True, 'consistent': True,
             'no_hallucination': True, 'confidence': 0.9, 'consistency_score': 0.8},
            {'has_citation': False, 'valid_pages': False, 'consistent': False,
             'no_hallucination': True, 'confidence': 0.3, 'consistency_score': 0.2},
        ]

        stats = self.validator.get_summary_stats(results)

        assert stats['total'] == 2
        assert stats['citation_rate'] == 0.5
        assert stats['average_confidence'] == 0.6

    def test_confidence_calculation(self):
        """测试置信度计算"""
        # 完美答案
        perfect_result = {
            'has_citation': True,
            'citation_format_valid': True,
            'valid_pages': True,
            'consistency_score': 1.0,
            'no_hallucination': True,
            'hallucination_score': 0.0
        }

        confidence = self.validator._calculate_confidence(perfect_result)
        assert confidence >= 0.9

        # 差答案
        poor_result = {
            'has_citation': False,
            'citation_format_valid': False,
            'valid_pages': False,
            'consistency_score': 0.0,
            'no_hallucination': False,
            'hallucination_score': 0.5
        }

        confidence = self.validator._calculate_confidence(poor_result)
        assert confidence < 0.3

    def test_not_found_answer(self):
        """测试'未找到'类型的答案"""
        answer = "文档中未找到相关内容。"
        chunks = []

        result = self.validator.validate(answer, chunks)

        # 这种答案是有效的,不应该有太多警告
        assert result is not None

    def test_multiple_pages_citation(self):
        """测试引用多个页码"""
        answer = "根据第5页和第10页的内容,准确率在95%-98%之间。[来源: 第5页, 第10页]"
        chunks = [
            {'page': 5, 'text': '准确率至少95%'},
            {'page': 10, 'text': '最高达到98%'}
        ]

        result = self.validator.validate(answer, chunks)

        assert result['has_citation'] is True
        assert result['valid_pages'] is True
        assert 5 in result['cited_pages']
        assert 10 in result['cited_pages']

    def test_page_coverage(self):
        """测试页面覆盖率"""
        answer = "根据第5页。[来源: 第5页]"
        chunks = [
            {'page': 5, 'text': 'content 5'},
            {'page': 6, 'text': 'content 6'},
            {'page': 7, 'text': 'content 7'}
        ]

        result = self.validator.validate(answer, chunks)

        # 引用了1/3的可用页面
        assert result['page_coverage'] > 0.3
        assert result['page_coverage'] < 0.4


class TestValidateAnswerFunction:
    """测试便捷函数"""

    def test_validate_answer_function(self):
        """测试validate_answer便捷函数"""
        answer = "根据第5页,准确率是95%。[来源: 第5页]"
        chunks = [{'page': 5, 'text': '准确率是95%'}]

        result = validate_answer(answer, chunks)

        assert result is not None
        assert 'confidence' in result
        assert 'has_citation' in result


class TestEdgeCases:
    """边界情况测试"""

    def setup_method(self):
        self.validator = AnswerValidator()

    def test_empty_answer(self):
        """测试空答案"""
        result = self.validator.validate("", [])
        assert result['confidence'] < 0.5

    def test_empty_chunks(self):
        """测试空chunks"""
        answer = "这是一个答案"
        result = self.validator.validate(answer, [])
        assert result is not None

    def test_very_long_answer(self):
        """测试很长的答案"""
        answer = "根据文档内容," + "这是内容。" * 100 + "[来源: 第5页]"
        chunks = [{'page': 5, 'text': '这是内容'}]

        result = self.validator.validate(answer, chunks)
        assert result is not None

    def test_special_characters(self):
        """测试特殊字符"""
        answer = "根据第5页,准确率是95%!@#$%^&*()。[来源: 第5页]"
        chunks = [{'page': 5, 'text': '准确率是95%'}]

        result = self.validator.validate(answer, chunks)
        assert result['has_citation'] is True

    def test_mixed_language(self):
        """测试中英文混合"""
        answer = "根据第5页,accuracy is 95%。[来源: 第5页]"
        chunks = [{'page': 5, 'text': 'The accuracy is 95%'}]

        result = self.validator.validate(answer, chunks)
        assert result['has_citation'] is True


# 集成测试
class TestIntegration:
    """集成测试"""

    def test_full_validation_workflow(self):
        """测试完整验证流程"""
        validator = AnswerValidator()

        # 准备测试数据
        test_cases = [
            {
                'answer': "根据第5页,准确率是95%。[来源: 第5页]",
                'chunks': [{'page': 5, 'text': '实验准确率达到95%'}],
                'expected_confidence': 0.8
            },
            {
                'answer': "我觉得可能是95%吧",
                'chunks': [{'page': 5, 'text': '实验准确率达到95%'}],
                'expected_confidence': 0.3
            }
        ]

        for case in test_cases:
            result = validator.validate(case['answer'], case['chunks'])

            # 基本检查
            assert 'confidence' in result
            assert 'warnings' in result

            # 置信度检查
            if case['expected_confidence'] >= 0.8:
                assert result['confidence'] >= 0.7
            else:
                assert result['confidence'] < 0.5

    def test_batch_processing(self):
        """测试批量处理"""
        validator = AnswerValidator()

        qa_pairs = [
            ("答案1 [来源: 第1页]", [{'page': 1, 'text': 'content'}]),
            ("答案2 [来源: 第2页]", [{'page': 2, 'text': 'content'}]),
            ("答案3", [{'page': 3, 'text': 'content'}])
        ]

        results = validator.validate_batch(qa_pairs)
        stats = validator.get_summary_stats(results)

        assert stats['total'] == 3
        assert stats['citation_rate'] > 0.5


if __name__ == "__main__":
    """运行测试"""
    pytest.main([__file__, '-v', '--tb=short'])
