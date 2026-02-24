from typing import List


class QuestionSuggester:
    """智能问题推荐器，根据文档类型生成推荐问题"""

    def suggest(self, text: str, doc_type: str = 'general') -> List[str]:
        """根据文档类型推荐问题"""

        doc_type = self._detect_type(text) if doc_type == 'general' else doc_type

        templates = {
            'academic_paper': [
                "这篇论文的主要贡献是什么?",
                "使用了什么研究方法?",
                "实验结果如何?",
                "有哪些局限性?"
            ],
            'contract': [
                "合同的主要条款是什么?",
                "违约责任如何规定?",
                "支付条件是什么?",
                "合同期限多久?"
            ],
            'technical_doc': [
                "这个工具如何使用?",
                "有哪些主要功能?",
                "如何安装配置?",
                "常见问题有哪些?"
            ],
            'general': [
                "这份文档的主要内容是什么?",
                "有哪些关键信息?",
                "总结全文要点"
            ]
        }

        return templates.get(doc_type, templates['general'])

    def _detect_type(self, text: str) -> str:
        """简单的文档类型检测"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['abstract', 'introduction', 'method', 'result']):
            return 'academic_paper'
        elif any(word in text_lower for word in ['甲方', '乙方', '违约', '合同']):
            return 'contract'
        elif any(word in text_lower for word in ['api', 'install', 'usage', 'configuration']):
            return 'technical_doc'
        else:
            return 'general'
