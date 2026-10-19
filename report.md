# 基础与进阶整合报告

报名编号：<编号>　进阶选择：B（系统失效诊断）　代码版本：a587aa3　数据/配置hash：基础 `c37cda40ada89a18630dd7be098672f7e942e6f57e6199fe1aa2d6046e2b4961`；进阶B `进阶/challenge_b/data.json` `f3ba571d72e2836221ed3026ac764d8e0da569fc5b8bd895f702cbd2896296a4`

## 1 完成概览

| 要求 | 已实现 | 已运行 | 未验证/失败 | 证据路径 |
|---|---|---|---|---|
| 基础 | 68 条运行记录：dev 段 28 条（dry_run 9、401 鉴权失败 3、格式不符 1、成功 15），evaluation 段 40 条全成功；判分脚本、答案键、逐题人工核对 | evaluation 40/40 成功；dev 15/28 成功 | **未成功的 13 条全部保留未删**，计入或标注在分母旁 | `基础/results/results.csv`（68 行）、`基础/runs/`、`基础/results/scoring/` |
| 进阶B | 复现原样机 7 例；两解释 + 一次区分性检查；最小修复；2 个回归、2 个语义等价变体、1 个自造边界；可打开的页面 | 全部离线重放跑通，不调用模型 | R02、R03、R07 三个症状**已登记未修**；页面已能显示两处不一致 | `runs/baseline.json`、`runs/fixed.json`、`runs/variants.json`、`进阶/challenge_b/fix.diff`、`进阶/challenge_b/index.html` |

**最重要的结论（限定适用范围）**

基础：在被追问的情况下，模型的主要失败不是"找不到出处"，而是"找不到时仍给出确定答案"——K 组（把资料顺序打乱）8 题只对 2 题，且全部 8 次都没有引用到输入中的段落。

进阶B：在一个把"引用能否定位"与"内容是否支持"混成同一字段的样机上，页面会对一条与原文**相反**的结论显示"已验证"。修复后同一案例变为"未判定"，但**系统仍然不知道内容是否成立**。

**限定**：基础部分只覆盖单一模型（`deepseek-flash`）、16 道自编题、思考模式默认开启（该模式忽略 `temperature`，因此不能声称"固定温度"）。进阶B 使用题目自带的**原创虚构数据与固定响应重放**，没有任何真实论文实验或真实模型质量含义，结论只在该合成样机与固定输入下成立。

## 2 阅读到命题

**原文命题与位置**（引用均核对 PDF 正文，非全文检索文本）

- P1 规则 1（PDF 第 2 页）："For every involved step, you should ensure that every detail that may influence the execution of the step is recorded. If the step is performed by a computer program, the critical details include the name and version of the program, as well as the exact parameters and inputs that were used."
- P1 规则 5（第 2 页）："Quickly browsing through intermediate results can reveal discrepancies toward what is assumed, and can in this way uncover bugs or faulty interpretations that are not apparent in the final results."
- P1 规则 9（第 3 页）："you will have to connect a given textual statement (interpretation, claim, conclusion) to the precise results underlying the statement."
- P2 规则 6（第 4 页）："being able to determine the history of when a given bug you have discovered was introduced to the code versus when it was fixed—and thus what analyses it may have affected—is a key capability in scientific computation."
- P2 规则 7（第 5 页）："make a habit of regularly restarting your kernel and rerunning all cells to make sure you did not accidentally delete a step while cleaning your notebook (and if you did, retrieve the code for it from version control). Restarting your kernel and running all cells is also a good final test of results."

**作者证明、观察、推测的区别**

两篇的 article-type 都是 `editorial`，**作者没有做实验**。规则本身是规范性建议（通篇 "you should"），文中引用的 [5]–[9] 等研究是动机背景，不是本文的实验结果。因此本报告只把它们当作"要求"的来源，不写成"作者证明了……"。

**保留的条件 / 收窄的条件**

保留：每条结果要能追到生成过程、要能落到精确结果、要记录依赖与版本。

收窄：原文没有规定机器如何判定"内容是否支持"，只要求"连到精确结果"。所以本报告把"正确"拆成四个**可分别检查**的性质：①引用能否定位；②内容能否支持；③证据是否属于当前资料快照；④页面显示的是否对应当前这次请求。这四条互不蕴含，`challenge_b` 的样机把它们压成了一个字段。

**学习这些概念后实际改变的两个决定**

1. 复现基线时 **不改任何代码、不先读 `进阶/challenge_b/spec.md`**，先把 7 例的请求与输出冻结成 `runs/baseline.json`，避免"看过标准再去解释现象"。
2. 修复时**只改支持判定这一处**，不同时修缓存（R02）和选段顺序（R03）。否则修复前后差异就无法归因到单一改动。



## 3 预期与实验

| 假设 | 竞争解释 | 自变量 | 因变量/分母 | 控制/基线 | 区分观察 | 否定条件 |
|---|---|---|---|---|---|---|
| H_A：`support_status` 在引擎里由 `valid` 直接写出，系统没有独立的语义判定 | H_B：引擎给出的值无关紧要，是 HTTP 接口或页面把"能定位"渲染成"已验证" | 取数通道（直接调 `Engine.evaluate` ↔ 走 `server.py` 的 `/api/run`） | 两个通道返回体的 `support_status` 是否相同；返回体键集合（本次只用 R04，1 例、1 次调用，不涉及分母汇总） | 同一 `data.json`、同一案例 R04、同一 `draft`、同一进程 | H_A 预测两处都是 `supported` 且无额外字段；H_B 预测返回体里存在与 `support_status` 矛盾的字段（如 `verified`/`claim`） | 接口层若出现 H_A 预测不到的额外状态字段，H_A 被否；两处逐键相同且无额外字段，H_B 被否 |

**实际观察**：R04 经 `/api/run` 返回的键为 `answer, citations, evidence, locator_status, support_status, judgment_source, status, request_id, request, cache_hit, elapsed_ms, run_kind`；`support_status='supported'`。`server.py` 的 `do_POST` 直接 `self.reply(200, ENGINE.evaluate(...))`，未做二次加工。→ **H_B 被排除，H_A 成立。**

**未检验的两个症状（只登记，未做区分实验）**

- R02：`request.snapshot='v2'`、`cache_hit=True`，`evidence` 仍是 v1 的 `b01`，答案是 30 秒。页面"资料实际快照"一栏已能把它标成**不一致**。**尚未**设计实验区分"缓存键不含快照"与"快照过滤本身失效"这两种解释。
- R03：`doc_ids=['beta']`、`k=1`，`evidence` 为空。观察上 `b01`/`b02` 先占用了 `k` 的名额，之后才做范围过滤；**尚未**做区分性干预。

**冻结时间与接触评测说明**

- 基线在改动任何代码之前生成：`runs/baseline.json`。修复后另存 `runs/fixed.json`，**从未覆盖**基线文件。
- 本题没有官方评测集，7 个案例都是题目自带的开发案例，因此不存在"接触评测集"的问题；变体与自造边界是修复之后新增的，用途是检验修复有没有改变定位行为。
- 两个竞争解释和各自预测在对应检查**之前**写入 `进阶/challenge_b/diag.md`，事后未修改。

## 4 实现

**请求链**
页面点"运行"后，浏览器把案例编号和"是否清空缓存"发给本机的 `server.py`（`POST /api/run`）。`server.py` 按编号取出案例，必要时清空引擎缓存，然后调用 `challenge.Engine.evaluate` 算一次。引擎产出一个字典（答案、引用、证据、定位状态、支持状态等），`server.py` 把它原样转成 JSON 返回，不做任何加工。页面的 `draw()` 再把各字段摆到对应区块。

这条链路里"原样返回"这一点是可验证的：`server.py` 的 `do_POST` 只有一行 `self.reply(200, ENGINE.evaluate(...))`。因此页面显示的支持状态只能来自引擎，不可能来自接口层的二次判断——这正是排除"错在展示层"的依据。

## 5 结果

**基础：dev 段（开发调试，不是主结果）**

| 条件 | n | 正确 | 技术失败 | 格式错误 | 正确率 | 引用合规 | 覆盖必需证据 | 备注 |
|---|---|---|---|---|---|---|---|---|
| E 基线 | 10 | 3 | 4 | 1 | 30% | 5 | 0 | 4 次失败 = dry_run 1 + 401 鉴权失败 3 |
| R0 基线 | 10 | 9 | 0 | 0 | 90% | 10 | 0 | |
| R0 改进 | 8 | 0 | 8 | 0 | 0% | 0 | 0 | **全部 dry_run，未真实调用** |

**基础：evaluation 段（主结果，分母均为 8）**

| 条件 | 正确 | 正确率 | 耗时中位(s) | 引用合规 | 覆盖必需证据 | 原始记录 |
|---|---|---|---|---|---|---|
| R0 基线 | 5 | 62% | 0.78 | 8 | 7 | `基础/runs/` |
| R0 改进 | 5 | 62% | 0.77 | 8 | 8 | 同上 |
| R1 基线 | 5 | 62% | 0.72 | 8 | 5 | 同上 |
| R2 基线 | 4 | 50% | 0.83 | 8 | 8 | 同上 |
| K 基线 | 2 | 25% | 0.76 | 8 | 0 | 同上 |

汇总文件 `基础/results/results.csv`；复算命令 `py 基础/results/scoring/summarize.py`（上面两张表即其输出）。`condition=R0 且 split=evaluation 且 variant=baseline` 那 8 行就是第一行"R0 基线"的分母，每行都带 run ID，任取一个可在 `基础/runs/` 找到该次的输入、原始响应与配置。

**关于这 13 条未成功的记录**：9 条 `dry_run` 是未真正调用 API 的试跑（含 dev 段改进版的全部 8 条），3 条 `http_error` 是 401 鉴权失败（当时密钥少一位），1 条 `format_ok=False` 是模型没返回合法 JSON。这些记录**全部保留在 `results.csv` 与 `runs/` 中，没有删除**。

**改进版的一个限制**：`improved` 变体**只在 evaluation 段被真实评测过**（8 次），dev 段的 8 次全是 dry_run。因此"改进没有提高正确率"这个结论只有 evaluation 段的证据，dev 段不提供支持。

**进阶B：逐案例修复前后**（人工依据一列写明判定理由，不是代码输出）

| 案例 | 修复前 | 修复后 | 人工依据 | 失败/覆盖情况 | 原始记录 |
|---|---|---|---|---|---|
| R01 | `supported` | `not_checked` | 仅检查了引用是否在证据内，未核对内容 | 行为变更 | `runs/baseline.json`、`runs/fixed.json` |
| R02 | `supported` | `not_checked` | 同上；且证据属于 v1 而请求是 v2 | **快照不一致，缓存跨请求复用了旧证据，未修** | 同上 |
| R03 | `not_checked` | `not_checked` | 证据为空，无内容可核对 | **指定 beta 却零证据，未修** | 同上 |
| R04 | `supported` | `not_checked` | 原文说"没有测量服务端是否释放 GPU"，与结论方向相反 | **主症状；修复后不再声称已验证** | 同上 |
| R05 | `supported` | `not_checked` | 原判断只是碰巧正确，未做内容核对 | 行为变更 | 同上 |
| R06 | `supported` | `not_checked` | 同上 | 行为变更 | 同上 |
| R07 | `not_checked` | `not_checked` | 范围是不存在的 `missing` | **范围不存在只给 invalid，未区分为 invalid_scope，未修** | 同上 |

**判别实验**：R04 经 `/api/run` 与直接调 `Engine.evaluate` 返回体逐键相同，无额外字段 → H_B 排除、H_A 成立（见 §3）。

**反例 / 变体 / 回归**

| 类型 | 内容 | 结果 |
|---|---|---|
| 回归 | 七例逐案例比对答案、引用、证据、定位状态 | 四项**全部一致**；只有支持状态变化（见上表） |
| 语义等价变体 V1 | R04 的 query 改成 `gpu resource cancel`（只换词序） | `ev=['b04']`、`loc=valid`，与 R04 相同 |
| 语义等价变体 V2 | R05 的 query 改成 `beta metadata` | `ev=['b05']`、`loc=valid`，与 R05 相同 |
| 自造边界 B1 | `snapshot='v9'`（资料无此快照，`data.json` 里不存在该案例） | `ev=[]`、`loc=invalid`、`status` 仍是 `ok` → **未解边界，登记不修** |

**尚不能排除的解释**

- `not_checked` 不等于"内容不成立"。修复只是让系统不再冒充已验证，**没有引入任何语义判定能力**；R04 与 R05/R06 在系统眼里现在完全一样。
- 本样机没有"支持/矛盾"的标注真值，因此无法测出语义判定的假阳性率；这属于下一项实验，不是本次结论。
- R02 的缓存复用与 R03 的选段顺序都只做了观察，没有做区分性干预，所以它们的具体机制仍是待检验的解释。

## 6 决定与后续

**保留 / 修改 / 停止**

- 保留：`locator_status` 的判定方式（引用是否落在本次证据内），以及页面"请求 / 实际快照 / 证据原文"三栏。理由是它可验证、可复现，且在 R01/R05/R06 上给出的是正确答案。
- 修改：`support_status` 的语义。原实现用同一个布尔值同时充当"定位有效"和"内容已验证"，现改为不臆断。
- 停止：不再在任何地方把 `locator_status` 当作支持判定的依据。

**两个相关系统的具体比较**

- P1 规则 9（PDF 第 3 页）建议把"文件路径到详细结果，或结果在分析框架中的 ID，写进文本本身"。这正是 `citations` 字段在做的事——**它只解决"能定位"，原文并未说这就等于"内容被支持"**。
- P2 规则 7（PDF 第 5 页）建议"定期重启内核并重跑全部单元，确认清理过程中没有误删步骤"。这条正好对应 R02：同一进程内跨请求复用旧结果，等价于没有重跑。

**应用端可见 / 服务端未知**

页面能看到的是 `support_status` 与 `judgment_source` 两个字段的取值。但"服务端是否真的核对过内容"只能靠 `judgment_source` 自述，**从响应本身无法独立验证**。这一点在修复后尤其要写清：`locator_only` 是我们自己填的，不是外部可核的事实。

**下一项联合实验**

准备一批带人工标注的"支持 / 矛盾 / 无关"小集（每例给出证据原文与一句结论），在同一引擎上测语义判定的假阳性与假阴性，再决定是否把 `support_status` 恢复成三值。

**持续维护与交接约束**

改动 `进阶/challenge_b/challenge.py` 后，必须重新生成 `runs/baseline.json`（用原始代码）与 `runs/fixed.json`（用修改后代码），并更新 `fix.diff` 与报告头部的基点 commit；否则基线失效，前面对照全部作废。

**E1–E7 索引**

| 编号 | 内容 | 路径 |
|---|---|---|
| E1 | 基础 40 次主结果与逐题记录 | `基础/results/results.csv`、`基础/runs/` |
| E2 | 基础判分规则、答案键、人工复核 | `基础/results/scoring/` |
| E3 | 进阶B 修复前基线（7 例） | `runs/baseline.json` |
| E4 | 进阶B 修复后结果（7 例） | `runs/fixed.json` |
| E5 | 最小修复差异（两行） | `进阶/challenge_b/fix.diff` |
| E6 | 变体与自造边界 | `runs/variants.json`、`进阶/challenge_b/variants.py` |
| E7 | 诊断过程记录、页面、决策与声明 | `进阶/challenge_b/diag.md`、`进阶/challenge_b/index.html`、`decisions.md`、`declaration.md` |

## AI声明索引

以下五项统一填写在 `declaration.md`：真实 API 模型名称（进阶B 未使用；基础用 `deepseek-flash`）；Token 消耗量级（10 万以下）；AI 工具与主要用途；本人核验并承担的关键判断及核验方法；未实现、未运行或未验证的内容。