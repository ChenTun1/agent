from anthropic import Anthropic
from typing import List, Dict
from backend.config import get_settings
import re

settings = get_settings()


class QAService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    def answer(self, question: str, chunks: List[Dict]) -> Dict:
        """Generate answer with forced citations"""
        # Build context from chunks
        context = self._build_context(chunks)

        # Build prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(question, context)

        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        answer_text = response.content[0].text

        # Extract cited pages
        cited_pages = self._extract_cited_pages(answer_text)

        return {
            'answer': answer_text,
            'cited_pages': cited_pages,
            'model': self.model
        }

    def _get_system_prompt(self) -> str:
        return """你是一个专业的PDF文档助手。

严格规则(必须遵守):
1. 只回答PDF文档中明确提到的内容
2. 每个回答必须标注来源页码,格式:[来源: 第X页]
3. 如果文档中没有相关信息,明确说"文档中未找到相关内容"
4. 绝对不要编造、推测或使用文档外的知识
5. 如果多个页面都提到相关内容,列出所有页码

回答格式示例:
根据第23页的内容,实验的准确率达到95.3%。[来源: 第23页]

记住:准确性 > 完整性。宁可说"未找到",也不要猜测!"""

    def _build_context(self, chunks: List[Dict]) -> str:
        context = ""
        for idx, chunk in enumerate(chunks, 1):
            context += f"\n[段落{idx} - 第{chunk['page']}页]\n"
            context += chunk['text']
            context += "\n---\n"
        return context

    def _build_user_prompt(self, question: str, context: str) -> str:
        return f"""基于以下PDF文档内容回答问题:

{context}

用户问题: {question}

请严格按照系统规则回答,必须标注来源页码!"""

    def _extract_cited_pages(self, answer: str) -> List[int]:
        """Extract page numbers from answer"""
        pages = []
        # Match patterns like "第5页", "第12页"
        matches = re.findall(r'第\s*(\d+)\s*页', answer)
        for match in matches:
            pages.append(int(match))
        return sorted(list(set(pages)))
