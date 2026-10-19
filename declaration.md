# 声明

日期：2026-10-19　时区：UTC+8　姓名：zhao yinghao　报名编号：<编号>

## 五项必填

**真实 API 模型名称**
- 基础部分：`deepseek-flash`（经 `https://api.deepseek.com/chat/completions` 真实调用）。
- 进阶 B：**未使用**（全流程离线重放，`run_kind=offline_replay`，没有发出任何网络请求）。

**Token 消耗量级**
10 万以下。基础部分共 55 次成功调用，`max_tokens=256`，思考模式关闭；逐次 usage 见 `基础/results/results.csv` 的 `prompt_tokens`/`completion_tokens`/`usage_source` 列。

**AI 工具与主要用途**
- Claude（对话）：拆解题目要求、设计记录与判分的字段格式、解释报错、审查报告逻辑与措辞、起草报告骨架、逐条校对原文引用。
- DeepSeek API：作为**基础实验的被测对象**，不是辅助工具。

**本人核验并承担的关键判断及核验方法**
1. 基础 5 个条件的正确题数：用 `py 基础/results/scoring/summarize.py` 重算，与 `results.csv` 逐行核对后写入报告。
2. 68 条运行记录中 13 条未成功（dry_run 9 / 401 3 / 格式不符 1）：逐条查 `api_status` 与 `reason` 列确认，全部保留未删。
3. T01/T07/T08 全错、K 组仅 2/8：逐题看模型原始回答与引用编号，不是只看分数。
4. P1/P2 五条规则的原文：在 PDF 正文中逐字核对，未使用全文检索生成的文本（该文本存在分栏交错问题）。
5. B 的故障定位：亲自跑 `run_cases.py`、看 `challenge.py` 与 `server.py`、起服务取一次 R04，并把自己写的预测保存进 `diag.md` 后才动手改代码。
6. 修复只改两行：用 `git diff` 确认差异仅两行，且用回归对比确认答案/引用/证据/定位四项未变。

**未实现、未运行或未验证的内容**
- B 的 R02（缓存跨快照复用）、R03（选段名额被范围外段落占用）、R07 与 B1（范围不存在时未区分 `invalid_scope`）：**只登记，未修复、未做区分性干预**。
- 语义支持判定**未实现**：修复后 `support_status` 恒为 `not_checked`，系统不具备判断"支持/矛盾"的能力。
- 基础改进版（`improved`）**只在 evaluation 段被真实评测过 8 次**；dev 段 8 次是 dry_run，从未真实调用。
- 思考模式（`config.think.json`）会忽略 `temperature`，因此**不能声称"固定温度"**。
- B 全部为虚构数据与固定响应重放，**没有任何真实模型质量结论**。

## 其余字段

**开源/骨架/他人贡献及对应文件**
- `进阶/challenge_b/` 下的 `spec.md`、`data.json`、`server.py`、`run_cases.py`、`index.html` 初版：考核方提供的样机骨架。
- 本人改动：`challenge.py` 两行（见 `fix.diff`）、`index.html` 整份重写、新增 `variants.py`、新增 `diag.md`、生成 `runs/` 下三份结果文件。
- 参考文献 P1、P2 为他人论文，仅作为要求来源引用，未修改。

**本人能解释的模块，尚未理解的模块**
- 能解释：`challenge.Engine.evaluate` 全文（打分、排序、截断、范围过滤、引用子集判定、缓存读写）、`server.py` 的 `do_POST` 与 `do_GET`、页面 `draw()` 的字段渲染。
- 尚未完全理解：`run_cases.py` 通过 `--engine` 字符串动态加载引擎的机制细节；`HTTPServer` 单线程逐请求处理，多标签页同时点击时的行为未验证。

**重放/模拟清单**
- B 的 7 个案例与 3 个变体全部为固定响应重放，`run_kind=offline_replay`，无真实模型参与。
- 基础 9 条 `dry_run` 记录不是实测结果，已在报告 §5 单独标注。

**开发/评测接触及冻结后的改动**
- 基础 dev 段用于调试提示词与格式；evaluation 段在提示词与参数冻结后运行。
- 冻结后对已产生记录只做读取，未修改任何历史 `runs/` 文件；B 的修复另存 `runs/fixed.json`，基线 `runs/baseline.json` 从未覆盖。
- B 无官方评测集，不存在接触评测问题。

**数据/素材/代码使用来源与许可**
- P1：Sandve 等，2013，PLOS Comput Biol，DOI `10.1371/journal.pcbi.1003285`，CC-BY。
- P2：Rule 等，2019，PLOS Comput Biol，DOI `10.1371/journal.pcbi.1007007`，CC-BY。
- 两篇的 PDF/XML 原件未修改，SHA256 见 `materials/sources.json`。
- `challenge_b` 的虚构数据与样机代码为考核方提供。

本人确认以上按实际情况填写；不将模拟结果或他人贡献冒称本人实测。不要求承诺完全不用 AI。