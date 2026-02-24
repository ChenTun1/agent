"""
答案验证模块
验证答案质量,检查引用准确性和内容一致性
"""

import re
from typing import Dict, List, Tuple, Optional


class AnswerValidator:
    """答案质量验证器"""

    def __init__(self):
        # 幻觉指示词
        self.hallucination_indicators = [
            '我认为', '我猜测', '我觉得', '可能是', '也许',
            '据我所知', '根据我的理解', '一般来说', '通常',
            '我推测', '我想', '大概', '估计'
        ]

        # 不确定性指示词(适度使用是可以的)
        self.uncertainty_indicators = [
            '可能', '也许', '似乎', '看起来', '大约'
        ]

        # 来源引用模式
        self.citation_patterns = [
            r'来源[：:]\s*第\s*\d+\s*页',
            r'\[来源[：:]\s*第\s*\d+\s*页\]',
            r'第\s*\d+\s*页',
            r'根据第\s*\d+\s*页',
            r'在第\s*\d+\s*页'
        ]

    def validate(self, answer: str, chunks: List[Dict]) -> Dict:
        """
        全面验证答案质量

        Args:
            answer: 生成的答案文本
            chunks: 用于生成答案的文档块

        Returns:
            验证结果字典,包含各项检查结果和置信度分数
        """
        result = {
            'has_citation': False,
            'citation_format_valid': False,
            'valid_pages': False,
            'page_coverage': 0.0,
            'consistent': False,
            'consistency_score': 0.0,
            'no_hallucination': True,
            'hallucination_indicators': [],
            'confidence': 0.0,
            'warnings': [],
            'details': {}
        }

        # 1. 检查引用标注
        citation_check = self._check_citation(answer, chunks)
        result.update(citation_check)

        # 2. 检查内容一致性
        consistency_check = self._check_consistency(answer, chunks)
        result.update(consistency_check)

        # 3. 检查幻觉
        hallucination_check = self._check_hallucination(answer, chunks)
        result.update(hallucination_check)

        # 4. 计算置信度
        result['confidence'] = self._calculate_confidence(result)

        # 5. 生成警告
        result['warnings'] = self._generate_warnings(result)

        return result

    def _check_citation(self, answer: str, chunks: List[Dict]) -> Dict:
        """检查引用标注"""
        result = {
            'has_citation': False,
            'citation_format_valid': False,
            'valid_pages': False,
            'cited_pages': [],
            'available_pages': [],
            'page_coverage': 0.0
        }

        # 提取可用页码
        available_pages = set(chunk.get('page', chunk.get('page_num', 0)) for chunk in chunks)
        result['available_pages'] = sorted(list(available_pages))

        # 检查是否有引用
        has_citation_marker = any(
            re.search(pattern, answer) for pattern in self.citation_patterns
        )

        if has_citation_marker:
            result['has_citation'] = True
            result['citation_format_valid'] = True

        # 提取引用的页码
        cited_pages = self._extract_cited_pages(answer)
        result['cited_pages'] = cited_pages

        # 验证页码有效性
        if cited_pages and available_pages:
            valid_pages = [p for p in cited_pages if p in available_pages]
            result['valid_pages'] = len(valid_pages) > 0
            result['page_coverage'] = len(valid_pages) / len(available_pages)

        return result

    def _check_consistency(self, answer: str, chunks: List[Dict]) -> Dict:
        """检查内容一致性"""
        result = {
            'consistent': False,
            'consistency_score': 0.0,
            'matched_phrases': [],
            'details': {}
        }

        if not chunks:
            return result

        # 提取答案中的关键短语
        answer_phrases = self._extract_key_phrases(answer)

        # 合并所有chunk文本
        chunk_text = ' '.join(
            chunk.get('text', '') for chunk in chunks
        ).lower()

        # 检查每个短语是否在chunk中
        matched = []
        for phrase in answer_phrases:
            if phrase.lower() in chunk_text:
                matched.append(phrase)

        result['matched_phrases'] = matched

        if answer_phrases:
            consistency_score = len(matched) / len(answer_phrases)
            result['consistency_score'] = consistency_score
            result['consistent'] = consistency_score >= 0.5

        result['details'] = {
            'total_phrases': len(answer_phrases),
            'matched_phrases': len(matched),
            'match_ratio': result['consistency_score']
        }

        return result

    def _check_hallucination(self, answer: str, chunks: List[Dict]) -> Dict:
        """检查幻觉内容"""
        result = {
            'no_hallucination': True,
            'hallucination_indicators': [],
            'hallucination_score': 0.0
        }

        # 检查幻觉指示词
        found_indicators = []
        for indicator in self.hallucination_indicators:
            if indicator in answer:
                found_indicators.append(indicator)

        if found_indicators:
            result['no_hallucination'] = False
            result['hallucination_indicators'] = found_indicators
            result['hallucination_score'] = len(found_indicators) / len(self.hallucination_indicators)

        # 检查是否有明确的"未找到"声明但仍给出答案
        not_found_indicators = ['未找到', '没有相关', '无相关', '文档中不包含']
        has_not_found = any(indicator in answer for indicator in not_found_indicators)

        if has_not_found and len(answer) > 100:
            # 说未找到但给了很长的答案,可能有问题
            result['hallucination_indicators'].append('声明未找到但提供了详细答案')

        return result

    def _calculate_confidence(self, validation_result: Dict) -> float:
        """
        计算置信度分数

        基于多个因素的加权组合:
        - 引用标注: 30%
        - 页码有效性: 40%
        - 内容一致性: 30%
        """
        score = 0.0

        # 引用标注 (30%)
        if validation_result.get('has_citation', False):
            score += 0.15
        if validation_result.get('citation_format_valid', False):
            score += 0.15

        # 页码有效性 (40%)
        if validation_result.get('valid_pages', False):
            score += 0.4

        # 内容一致性 (30%)
        consistency_score = validation_result.get('consistency_score', 0.0)
        score += consistency_score * 0.3

        # 幻觉惩罚
        if not validation_result.get('no_hallucination', True):
            hallucination_score = validation_result.get('hallucination_score', 0.0)
            score -= hallucination_score * 0.2

        return max(0.0, min(1.0, score))

    def _generate_warnings(self, validation_result: Dict) -> List[str]:
        """生成警告信息"""
        warnings = []

        if not validation_result.get('has_citation', False):
            warnings.append('答案缺少来源引用')

        if not validation_result.get('valid_pages', False) and validation_result.get('cited_pages'):
            warnings.append('引用的页码不在检索到的文档块中')

        if validation_result.get('consistency_score', 0.0) < 0.3:
            warnings.append('答案与检索内容一致性较低,可能存在幻觉')

        if not validation_result.get('no_hallucination', True):
            indicators = validation_result.get('hallucination_indicators', [])
            warnings.append(f'检测到可能的幻觉指示词: {", ".join(indicators[:3])}')

        if validation_result.get('confidence', 0.0) < 0.5:
            warnings.append('答案置信度较低,建议人工审核')

        return warnings

    def _extract_cited_pages(self, text: str) -> List[int]:
        """从文本中提取引用的页码"""
        pages = []
        # 匹配各种页码格式
        patterns = [
            r'第\s*(\d+)\s*页',
            r'page\s*(\d+)',
            r'p\.\s*(\d+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    pages.append(int(match))
                except ValueError:
                    pass

        return sorted(list(set(pages)))

    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取文本中的关键短语"""
        # 移除引用标注
        clean_text = text
        for pattern in self.citation_patterns:
            clean_text = re.sub(pattern, '', clean_text)

        # 按标点分割
        phrases = re.split(r'[,。.!?;:，。!?;:、\n]+', clean_text)

        # 过滤和清理
        key_phrases = []
        for phrase in phrases:
            phrase = phrase.strip()
            # 至少4个字符,不全是数字
            if len(phrase) >= 4 and not phrase.isdigit():
                # 移除常见停用词开头
                stop_words = ['但是', '然而', '因此', '所以', '根据', '在']
                for sw in stop_words:
                    if phrase.startswith(sw):
                        phrase = phrase[len(sw):].strip()

                if len(phrase) >= 4:
                    key_phrases.append(phrase)

        return key_phrases[:10]  # 最多取10个短语

    def validate_batch(self, qa_pairs: List[Tuple[str, List[Dict]]]) -> List[Dict]:
        """
        批量验证多个问答对

        Args:
            qa_pairs: [(answer, chunks), ...] 的列表

        Returns:
            验证结果列表
        """
        results = []
        for answer, chunks in qa_pairs:
            result = self.validate(answer, chunks)
            results.append(result)

        return results

    def get_summary_stats(self, validation_results: List[Dict]) -> Dict:
        """
        获取验证结果的汇总统计

        Args:
            validation_results: 验证结果列表

        Returns:
            汇总统计信息
        """
        if not validation_results:
            return {}

        total = len(validation_results)

        stats = {
            'total': total,
            'has_citation_count': sum(1 for r in validation_results if r.get('has_citation', False)),
            'valid_pages_count': sum(1 for r in validation_results if r.get('valid_pages', False)),
            'consistent_count': sum(1 for r in validation_results if r.get('consistent', False)),
            'no_hallucination_count': sum(1 for r in validation_results if r.get('no_hallucination', True)),
            'average_confidence': sum(r.get('confidence', 0.0) for r in validation_results) / total,
            'average_consistency': sum(r.get('consistency_score', 0.0) for r in validation_results) / total,
        }

        # 计算百分比
        stats['citation_rate'] = stats['has_citation_count'] / total
        stats['valid_pages_rate'] = stats['valid_pages_count'] / total
        stats['consistency_rate'] = stats['consistent_count'] / total
        stats['no_hallucination_rate'] = stats['no_hallucination_count'] / total

        return stats


def validate_answer(answer: str, chunks: List[Dict]) -> Dict:
    """
    便捷函数:验证单个答案

    Args:
        answer: 答案文本
        chunks: 文档块列表

    Returns:
        验证结果
    """
    validator = AnswerValidator()
    return validator.validate(answer, chunks)


if __name__ == "__main__":
    # 示例用法
    print("答案验证模块")
    print("="*60)

    # 示例1: 良好的答案
    good_answer = "根据第5页的内容,系统的准确率达到95.3%。[来源: 第5页]"
    good_chunks = [
        {'page': 5, 'text': '实验结果显示,系统的准确率达到95.3%,超过了基线方法。'}
    ]

    validator = AnswerValidator()
    result = validator.validate(good_answer, good_chunks)

    print("\n示例1 - 良好答案:")
    print(f"答案: {good_answer}")
    print(f"引用: {result['has_citation']}")
    print(f"页码有效: {result['valid_pages']}")
    print(f"一致性: {result['consistent']}")
    print(f"无幻觉: {result['no_hallucination']}")
    print(f"置信度: {result['confidence']:.2f}")
    print(f"警告: {result['warnings']}")

    # 示例2: 有问题的答案
    bad_answer = "我认为准确率应该是95%左右吧,虽然文档里没明确说明。"
    bad_chunks = [
        {'page': 3, 'text': '这是一些不相关的内容。'}
    ]

    result2 = validator.validate(bad_answer, bad_chunks)

    print("\n示例2 - 有问题的答案:")
    print(f"答案: {bad_answer}")
    print(f"引用: {result2['has_citation']}")
    print(f"页码有效: {result2['valid_pages']}")
    print(f"一致性: {result2['consistent']}")
    print(f"无幻觉: {result2['no_hallucination']}")
    print(f"置信度: {result2['confidence']:.2f}")
    print(f"警告: {result2['warnings']}")
