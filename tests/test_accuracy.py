"""
准确率测试模块
测试系统对Golden Q&A测试集的准确率
目标: >80% 准确率
"""

import pytest
import json
import os
from typing import Dict, List, Tuple
from pathlib import Path


class AccuracyTester:
    """准确率测试器"""

    def __init__(self, golden_set_path: str = "tests/golden_qa_set.json"):
        with open(golden_set_path, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)

        self.target_accuracy = self.test_data.get('target_accuracy', 0.80)
        self.results = []

    def evaluate_answer(
        self,
        answer: Dict,
        expected_pages: List[int],
        expected_keywords: List[str],
        category: str
    ) -> Dict:
        """
        评估单个答案的质量

        Args:
            answer: 系统返回的答案,包含answer和cited_pages
            expected_pages: 期望的页码
            expected_keywords: 期望的关键词
            category: 问题类别

        Returns:
            评估结果字典
        """
        result = {
            'page_match': False,
            'keyword_match': False,
            'has_citation': False,
            'no_hallucination': True,
            'score': 0.0
        }

        answer_text = answer.get('answer', '')
        cited_pages = answer.get('cited_pages', [])

        # 1. 检查是否有引用标注
        if '来源' in answer_text and '页' in answer_text:
            result['has_citation'] = True

        # 2. 检查页码准确性
        if expected_pages:
            # 至少有一个页码匹配
            if any(page in cited_pages for page in expected_pages):
                result['page_match'] = True
        else:
            # 对于not_found类别,不应该有页码
            if category == 'not_found':
                result['page_match'] = len(cited_pages) == 0

        # 3. 检查关键词
        if expected_keywords:
            matched_keywords = sum(
                1 for kw in expected_keywords
                if kw.lower() in answer_text.lower()
            )
            # 至少匹配50%的关键词
            keyword_ratio = matched_keywords / len(expected_keywords)
            result['keyword_match'] = keyword_ratio >= 0.5
        else:
            # 对于not_found类别,检查是否说明未找到
            if category == 'not_found':
                not_found_indicators = ['未找到', '没有', '不存在', '无相关']
                result['keyword_match'] = any(
                    indicator in answer_text
                    for indicator in not_found_indicators
                )
            else:
                result['keyword_match'] = True

        # 4. 幻觉检测(简化版)
        # 检查是否包含明显的幻觉标志
        hallucination_indicators = [
            '我认为', '我猜测', '可能是', '据我所知',
            '根据我的理解', '一般来说'
        ]
        if any(indicator in answer_text for indicator in hallucination_indicators):
            result['no_hallucination'] = False

        # 5. 计算总分
        weights = self.test_data['evaluation_criteria']
        score = 0.0

        if result['has_citation']:
            score += 0.2  # 基础分

        if result['page_match']:
            score += weights['page_citation_accuracy']['weight']

        if result['keyword_match']:
            score += weights['keyword_presence']['weight']

        if result['no_hallucination']:
            score += weights['no_hallucination']['weight']

        result['score'] = min(score, 1.0)

        return result

    def run_test_suite(self, qa_system) -> Dict:
        """
        运行完整的测试套件

        Args:
            qa_system: 问答系统实例,需要有process_pdf和answer_question方法

        Returns:
            测试结果统计
        """
        total_questions = 0
        total_score = 0.0
        passed = 0

        for test_case in self.test_data['test_cases']:
            test_id = test_case['test_id']
            pdf_path = test_case['pdf']

            # 检查PDF文件是否存在
            if not os.path.exists(pdf_path):
                print(f"警告: PDF文件不存在 - {pdf_path}")
                continue

            # 处理PDF
            try:
                pdf_id = f"test-{test_id}"
                qa_system.process_pdf(pdf_path, pdf_id)
            except Exception as e:
                print(f"处理PDF失败 {pdf_path}: {e}")
                continue

            # 测试每个问题
            for question_data in test_case['questions']:
                total_questions += 1

                question = question_data['question']
                expected_pages = question_data['expected_pages']
                expected_keywords = question_data['expected_keywords']
                category = question_data['category']

                try:
                    # 获取答案
                    answer = qa_system.answer_question(pdf_id, question)

                    # 评估答案
                    eval_result = self.evaluate_answer(
                        answer,
                        expected_pages,
                        expected_keywords,
                        category
                    )

                    # 记录结果
                    question_result = {
                        'test_id': test_id,
                        'question_id': question_data['id'],
                        'question': question,
                        'answer': answer.get('answer', ''),
                        'cited_pages': answer.get('cited_pages', []),
                        'expected_pages': expected_pages,
                        'category': category,
                        'evaluation': eval_result,
                        'passed': eval_result['score'] >= 0.7
                    }

                    self.results.append(question_result)
                    total_score += eval_result['score']

                    if question_result['passed']:
                        passed += 1

                    # 打印详细结果
                    status = "✓" if question_result['passed'] else "✗"
                    print(f"{status} [{test_id}] {question}")
                    print(f"  分数: {eval_result['score']:.2f}")
                    print(f"  引用页码: {answer.get('cited_pages', [])}")
                    print(f"  期望页码: {expected_pages}")
                    print()

                except Exception as e:
                    print(f"问题测试失败 {question}: {e}")
                    self.results.append({
                        'test_id': test_id,
                        'question_id': question_data['id'],
                        'question': question,
                        'error': str(e),
                        'passed': False
                    })

        # 计算统计
        accuracy = passed / total_questions if total_questions > 0 else 0
        avg_score = total_score / total_questions if total_questions > 0 else 0

        stats = {
            'total_questions': total_questions,
            'passed': passed,
            'failed': total_questions - passed,
            'accuracy': accuracy,
            'average_score': avg_score,
            'target_accuracy': self.target_accuracy,
            'meets_target': accuracy >= self.target_accuracy
        }

        return stats

    def generate_report(self, stats: Dict, output_path: str = "tests/accuracy_report.md"):
        """生成测试报告"""
        report = f"""# 准确率测试报告

## 测试摘要

- **总问题数**: {stats['total_questions']}
- **通过数量**: {stats['passed']}
- **失败数量**: {stats['failed']}
- **准确率**: {stats['accuracy']:.1%}
- **平均分数**: {stats['average_score']:.2f}/1.0
- **目标准确率**: {stats['target_accuracy']:.1%}
- **达标状态**: {'✓ 达标' if stats['meets_target'] else '✗ 未达标'}

## 分类统计

"""
        # 按类别统计
        categories = {}
        for result in self.results:
            if 'category' in result:
                cat = result['category']
                if cat not in categories:
                    categories[cat] = {'total': 0, 'passed': 0}
                categories[cat]['total'] += 1
                if result.get('passed', False):
                    categories[cat]['passed'] += 1

        report += "| 类别 | 通过/总数 | 准确率 |\n"
        report += "|------|----------|--------|\n"

        for cat, data in categories.items():
            acc = data['passed'] / data['total'] if data['total'] > 0 else 0
            report += f"| {cat} | {data['passed']}/{data['total']} | {acc:.1%} |\n"

        report += "\n## 失败案例详情\n\n"

        for result in self.results:
            if not result.get('passed', False) and 'error' not in result:
                report += f"### {result['question_id']}: {result['question']}\n\n"
                report += f"- **类别**: {result['category']}\n"
                report += f"- **答案**: {result.get('answer', 'N/A')[:200]}...\n"
                report += f"- **引用页码**: {result.get('cited_pages', [])}\n"
                report += f"- **期望页码**: {result['expected_pages']}\n"

                eval_result = result.get('evaluation', {})
                report += f"- **评估**:\n"
                report += f"  - 有引用: {'✓' if eval_result.get('has_citation') else '✗'}\n"
                report += f"  - 页码匹配: {'✓' if eval_result.get('page_match') else '✗'}\n"
                report += f"  - 关键词匹配: {'✓' if eval_result.get('keyword_match') else '✗'}\n"
                report += f"  - 无幻觉: {'✓' if eval_result.get('no_hallucination') else '✗'}\n"
                report += f"  - 分数: {eval_result.get('score', 0):.2f}\n\n"

        # 写入报告
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"测试报告已生成: {output_path}")


# Pytest集成
@pytest.fixture
def qa_system():
    """
    创建QA系统实例
    需要在实际测试时导入真实的系统
    """
    try:
        from backend.pipeline import PDFPipeline
        from backend.retrieval import RetrievalService
        from backend.qa_service import QAService

        class QASystemWrapper:
            def __init__(self):
                self.pipeline = PDFPipeline()
                self.retrieval = RetrievalService()
                self.qa = QAService()

            def process_pdf(self, pdf_path: str, pdf_id: str):
                result = self.pipeline.process_pdf(pdf_path, pdf_id)
                if not result.get('success'):
                    raise Exception(f"PDF处理失败: {result.get('error')}")

            def answer_question(self, pdf_id: str, question: str) -> Dict:
                chunks = self.retrieval.retrieve(question, pdf_id, k=5)
                answer = self.qa.answer(question, chunks)
                return answer

        return QASystemWrapper()
    except ImportError as e:
        pytest.skip(f"QA系统模块未实现: {e}")


def test_golden_qa_accuracy(qa_system):
    """测试Golden Q&A准确率"""
    tester = AccuracyTester()
    stats = tester.run_test_suite(qa_system)

    # 生成报告
    tester.generate_report(stats)

    # 打印结果
    print("\n" + "="*60)
    print("准确率测试结果")
    print("="*60)
    print(f"总问题数: {stats['total_questions']}")
    print(f"通过数量: {stats['passed']}")
    print(f"失败数量: {stats['failed']}")
    print(f"准确率: {stats['accuracy']:.1%}")
    print(f"平均分数: {stats['average_score']:.2f}/1.0")
    print(f"目标准确率: {stats['target_accuracy']:.1%}")
    print(f"达标状态: {'✓ 达标' if stats['meets_target'] else '✗ 未达标'}")
    print("="*60)

    # 断言准确率达标
    assert stats['accuracy'] >= stats['target_accuracy'], \
        f"准确率 {stats['accuracy']:.1%} 未达到目标 {stats['target_accuracy']:.1%}"


def test_citation_accuracy(qa_system):
    """测试引用准确率"""
    tester = AccuracyTester()
    tester.run_test_suite(qa_system)

    # 统计引用准确率
    total = len(tester.results)
    with_citation = sum(
        1 for r in tester.results
        if r.get('evaluation', {}).get('has_citation', False)
    )

    citation_accuracy = with_citation / total if total > 0 else 0

    print(f"\n引用准确率: {citation_accuracy:.1%} ({with_citation}/{total})")

    # 引用准确率应该 >90%
    assert citation_accuracy >= 0.90, \
        f"引用准确率 {citation_accuracy:.1%} 未达到90%"


def test_no_hallucination(qa_system):
    """测试零幻觉"""
    tester = AccuracyTester()
    tester.run_test_suite(qa_system)

    # 统计幻觉情况
    total = len(tester.results)
    no_hallucination = sum(
        1 for r in tester.results
        if r.get('evaluation', {}).get('no_hallucination', True)
    )

    hallucination_rate = (total - no_hallucination) / total if total > 0 else 0

    print(f"\n幻觉率: {hallucination_rate:.1%} ({total - no_hallucination}/{total})")

    # 幻觉率应该 <10%
    assert hallucination_rate < 0.10, \
        f"幻觉率 {hallucination_rate:.1%} 超过10%"


if __name__ == "__main__":
    """直接运行测试"""
    print("准备运行准确率测试...")
    print("注意: 需要先实现backend模块(pipeline, retrieval, qa_service)")
    print("\n运行方式:")
    print("  pytest tests/test_accuracy.py -v")
    print("  或")
    print("  python tests/test_accuracy.py")
