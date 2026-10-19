# ANTLab Agent Tasks · 选拔任务提交

报名编号：【编号】　姓名：zhao yinghao　进阶选择：**B（系统失效诊断）**

本仓库包含两部分：**基础**（自编文档查证 Agent 的实现、40 次主结果与逐题核对）与**进阶 B**（对一个故意有缺陷的离线样机做故障诊断、区分性检查与最小修复）。

## 目录

| 路径 | 内容 |
|---|---|
| `基础/` | 基础任务：`starter/`（提示词与改进逻辑）、`runs/`（原始响应）、`results/results.csv`（68 条记录）、`results/scoring/`（答案键、判分与汇总脚本）、`decisions.md`、`remap_check.py` |
| `进阶/challenge_b/` | 进阶 B：题目自带样机（`spec.md`、`data.json`、`server.py`、`run_cases.py`、`index.html`）+ 本人的 `variants.py`、`diag.md`、`fix.diff` |
| `runs/` | 进阶 B 的结果：`baseline.json`（修复前）、`fixed.json`（修复后）、`variants.json`（变体与自造边界） |
| `report.md` | 整合报告（六节 + E1–E7 索引） |
| `decisions.md` | 决策记录表 |
| `declaration.md` | 声明（五项必填 + 其余字段） |

`基础/` **保持原位未移动**：它的脚本与历史记录使用相对路径，移动会破坏已冻结记录的复现链路。整合报告中的路径均按此结构书写。

## 怎么跑

不需要密钥（免费）的部分：

- 基础复算报告 §5 两张表：`py 基础/results/scoring/summarize.py`
- 进阶B 修复前基线（会覆盖现有文件，核对前请勿执行）：`py 进阶/challenge_b/run_cases.py --output runs/baseline.json`
- 进阶B 修复后：`py 进阶/challenge_b/run_cases.py --output runs/fixed.json`
- 进阶B 变体与自造边界：`py 进阶/challenge_b/variants.py`
- 进阶B 页面：`py 进阶/challenge_b/server.py`，然后用浏览器打开 `http://127.0.0.1:8766`

需要自备密钥（非必需）的部分：基础主实验入口为 `基础/starter/runner.py`，需要环境变量 `ASSESSMENT_API_KEY` 与 `基础/config.local.json`（该配置被 git 忽略，字段抄录在 `decisions.md` 与报告 §4）。评审不需要重跑这一步：`基础/runs/` 已保存每次的实际输入、原始响应与当时配置。

## 上游与本人修改

- 上游仓库：`https://github.com/Shiina413/ANTLab-Agent-Tasks`
- 本仓库：`https://github.com/cxkjtm325/ANTLab-Agent-Tasks`
- 修改前源码基点 commit：`a587aa3`
- - 最终 commit：`2e6c0b6`（代码与数据）；其后一次仅补填本行的登记提交，未改动任何代码或结果文件
- 查看本人全部改动：`git diff a587aa3 -- 进阶/challenge_b/` 与 `git log --oneline a587aa3..HEAD`

改动清单：`进阶/challenge_b/challenge.py` 两行（见 `fix.diff`）；`进阶/challenge_b/index.html` 整份重写；新增 `进阶/challenge_b/variants.py`、`diag.md`、`fix.diff`、`runs/` 下三份结果文件；仓库根目录新增 `report.md`、`decisions.md`、`declaration.md`、本 `README.md`。

## 接口字段对照

题目共同规则要求的字段与本仓库记录的对应关系如下。基础部分的若干字段**如实记为 null**，原因是当时的任务形态没有这些概念，不是漏记。

| 要求字段 | 基础 | 进阶B |
|---|---|---|
| `request_id` | `run_id` | `request_id` |
| `locator_status` | **null** —— 基础只检查引用是否来自输入资料（`citations_from_input`），没有位置校验 | `locator_status`（`valid`/`invalid`） |
| `support_status` | **null** —— 基础用 `judgment` 判答案对错，不判内容是否支持 | `support_status`（修复后恒为 `not_checked`） |
| `judgment_source` | 人工 + 答案键（`基础/results/scoring/`） | `locator_only`（系统自述，无法外部核验） |
| `run_kind` | `live_api`（真实调用）或 `dry_run`（未真调） | `offline_replay` |
| `elapsed_ms` | `elapsed_seconds × 1000` | `elapsed_ms` |
| `doc_id` / `snapshot` | 单一版本，无多快照 | `evidence[].doc_id` 与 `.snapshot` |
| 稳定块 ID / 页码 | **null** —— 资料未提供坐标 | `evidence[].id` 与 `.page` |

## 环境

- Windows，Python 3.14.7，命令一律用 `py`（`python` 在本机被 Microsoft Store 别名劫持，不可用）
- 进阶B 只用标准库（`http.server`、`json`、`hashlib`），无第三方依赖
- 基础部分的依赖见 `基础/starter/provider.py`