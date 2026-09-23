# paired-eval

[English](README.md) · [方法与限制](docs/METHODS.md)

用于两个系统的一次预先指定比较：严格对齐样本或种子 ID，计算配对均值差、百分位 bootstrap 区间和双侧符号翻转检验。拒绝重复或缺失的配对，不会自动删掉失败实验。

运行：`paired-eval examples/runs.csv --baseline baseline --candidate candidate --seed 7 --format markdown`。损失指标加 `--direction lower`。

同一主体/训练种子有多行相关结果时可提供 cluster 列并加 `--cluster`。此时先按 cluster 求均值，再等权比较各 cluster；统计对象随之改变，不是给相关行假装增加独立样本数。小样本区间可能不稳定，本工具不处理多重比较、层次交叉抽样或可选停止。

## 安装与测试

需要 Python 3.10+，无第三方运行依赖。目前未发布到 PyPI，请从源码安装：

```bash
git clone https://github.com/FertayLageeze/paired-eval.git
cd paired-eval
python -m pip install .
python -m unittest discover -s tests -v
```

本项目是 0.1.0 版开源研究工具，不是已发表论文。引用请使用 [CITATION.cff](CITATION.cff) 并记录实际使用的提交哈希；尚无 DOI。示例是功能验证，不代表真实任务性能基准。
