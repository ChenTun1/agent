# 测试数据集说明

## 概述

此目录包含用于测试的PDF样本文件。

## 所需文件

为了运行完整的准确率测试套件,需要以下PDF文件:

1. **academic_paper.pdf** - 学术论文示例
   - 用于测试学术文献的问答能力
   - 应包含:摘要、引言、方法、实验结果、相关工作、结论等章节
   - 至少47页

2. **technical_manual.pdf** - 技术文档示例
   - 用于测试技术文档的问答能力
   - 应包含:安装说明、系统要求、功能介绍等
   - 至少10页

3. **sample_contract.pdf** - 合同文档示例
   - 用于测试合同文档的问答能力
   - 应包含:合同条款、有效期、违约责任等
   - 至少10页

4. **sample.pdf** - 通用测试文档
   - 用于边界情况和基础功能测试
   - 至少10页

## 准备测试数据

### 选项1: 使用真实PDF

将符合要求的PDF文件放入此目录,并按照上述名称命名。

### 选项2: 生成测试PDF

运行生成脚本创建测试PDF:

```bash
python tests/generate_test_pdfs.py
```

### 选项3: 使用示例数据

从示例数据仓库下载:

```bash
# 示例命令(需要根据实际情况调整)
wget https://example.com/test-data/academic_paper.pdf -O tests/fixtures/academic_paper.pdf
```

## 文件清单

创建测试数据后,此目录应包含:

```
tests/fixtures/
├── README.md                 # 本文件
├── academic_paper.pdf        # 学术论文样本
├── technical_manual.pdf      # 技术文档样本
├── sample_contract.pdf       # 合同文档样本
└── sample.pdf               # 通用测试文档
```

## 注意事项

- 所有PDF文件应该是文本型PDF,而非扫描件
- 确保PDF可以正常提取文本
- 文件大小建议在10MB以内
- 不要上传包含敏感信息的真实文档

## 版权声明

测试PDF文件应使用公开可用的文档或自行创建的示例文档,避免版权问题。
