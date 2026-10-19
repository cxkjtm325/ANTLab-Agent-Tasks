记录时间：____（本地时间）

## 观察（只是事实）
1. R04 的 request 是 alpha / v2，k=2。返回 evidence=['b04']，locator_status='valid'，support_status='supported'。
2. b04 原文："客户端取消仅停止本地结果展示；本文没有测量服务端是否释放GPU计算资源。"
3. R04 的 draft.answer："点击取消就保证GPU立即停止计算并释放资源。"
4. 原文与这句话的关系：原文恰恰说明"没有测量"，因此不支持；方向相反。
5. challenge.py 里一行：'support_status': 'supported' if valid else 'not_checked'，其中 valid 只检查 citations 是否为 evidence 的子集。

## 主症状
R04：引用可定位，但页面宣称的"已验证"与原文内容相反。

## 解释 A（判定层出错）
support_status 在引擎里就是用 locator 的布尔值直接写出来的，系统没有独立的语义判定。
- 预测 A1：直接调 Engine.evaluate 得到 support_status='supported'。
- 预测 A2：通过 server 的 HTTP 接口取同一次 R04，support_status 仍是 'supported'，且接口里没有另一个与它矛盾的"已验证"字段。

## 解释 B（展示层出错）
引擎给出的值本身没错或无关紧要，错在接口/页面把 locator 当成了"已验证"来渲染。
- 预测 B1：Engine 层是 'supported'，但 server 返回体里存在另一个字段（如 verified / claim / support）与它不一致。
- 预测 B2：页面显示的"已验证"来自那个字段，而不是 support_status。

## 区分方法
起服务、取一次 R04，把 Engine 层与接口层的 support_status 并列比对，并列出接口返回的全部键。A 与 B 在这两处会给出不同结果。



## 区分结果（时间：10.18.23：29）
取 R04 一次，接口返回体全部键 = answer, citations, evidence, locator_status, support_status,
judgment_source, status, request_id, request, cache_hit, elapsed_ms, run_kind。
无 verified/claim/support 等额外字段。
server.py 的 do_POST 直接 reply(ENGINE.evaluate(...))，未做二次加工。
结论：预测 B1、B2 均未观察到 → 解释 B 被排除；解释 A 成立。


## 变体与边界（时间：10.18.23：45）
V1 R04 query 改词序 'gpu resource cancel' → ev ['b04']、loc valid，与 R04 一致；sup 仍 not_checked。
V2 R05 query 改词序 'beta metadata' → ev ['b05']、loc valid，与 R05 一致。
结论：语义等价改写不改变证据与定位结论。
B1 自造边界 snapshot='v9'（不存在）→ ev []、loc invalid、status ok。
结论：未区分"资料无此快照"与"引用无效"，spec 第 1 条要求的 invalid_scope 类状态缺失。
处置：不修，登记为未解边界。

## 已知行为变更（不是回归）
修复后 R01/R05/R06 的 support_status 由 supported 降为 not_checked，judgment_source 由 rule 改为 locator_only。
原因：原实现对这三条只是"碰巧"给出 supported，并没有做过内容核对；降级后不再冒充已验证。

## 登记但未修的症状
R02：request snapshot=v2，cache_hit=True，ev 仍是 v1 的 b01，答案仍是 30 秒。
R03：doc_ids=['beta']、k=1，ev 为空；b01/b02 占用了 k 的选段名额后才做范围过滤。
R07 / B1：范围不存在时不返回 invalid_scope，只有笼统的 invalid。