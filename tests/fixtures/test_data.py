"""测试数据集"""


def get_test_documents():
    """获取测试文档集"""
    return [
        {
            'id': 'chunk_1',
            'text': '深度学习(Deep Learning)是机器学习的一个分支,它使用多层神经网络来学习数据的表示。深度学习在图像识别、语音识别等领域取得了突破性进展。',
            'page': 1
        },
        {
            'id': 'chunk_2',
            'text': '卷积神经网络(CNN)是一种专门用于处理图像数据的深度学习模型。CNN通过卷积层、池化层和全连接层的组合来提取图像特征。',
            'page': 1
        },
        {
            'id': 'chunk_3',
            'text': '循环神经网络(RNN)适合处理序列数据,如文本和时间序列。长短期记忆网络(LSTM)是RNN的一种改进,能够更好地捕捉长期依赖关系。',
            'page': 2
        },
        {
            'id': 'chunk_4',
            'text': '自然语言处理(NLP)使用深度学习技术来理解和生成人类语言。Transformer模型revolutionized了NLP领域,BERT和GPT是其代表性应用。',
            'page': 2
        },
        {
            'id': 'chunk_5',
            'text': '强化学习是机器学习的另一个重要分支,通过试错来学习最优策略。AlphaGo使用深度强化学习击败了人类围棋冠军。',
            'page': 3
        }
    ]


def get_test_queries():
    """获取测试查询集

    Returns:
        列表,每个元素包含 query 和 expected_chunk_id
    """
    return [
        {
            'query': '什么是深度学习?',
            'expected_chunk_id': 'chunk_1',  # 应该召回 chunk_1
            'description': '基础概念查询'
        },
        {
            'query': 'CNN 用于什么?',
            'expected_chunk_id': 'chunk_2',  # 应该召回 chunk_2
            'description': '专业术语查询'
        },
        {
            'query': '如何处理序列数据?',
            'expected_chunk_id': 'chunk_3',  # 应该召回 chunk_3
            'description': '功能性查询'
        },
        {
            'query': 'BERT 和 GPT 是什么?',
            'expected_chunk_id': 'chunk_4',  # 应该召回 chunk_4
            'description': '多实体查询'
        },
        {
            'query': 'AlphaGo 如何工作?',
            'expected_chunk_id': 'chunk_5',  # 应该召回 chunk_5
            'description': '实体+功能查询'
        }
    ]
