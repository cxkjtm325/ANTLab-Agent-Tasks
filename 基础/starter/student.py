"""文档核对题：组装消息，并提供一种基于内容的段落组织方法。"""

import re

SYSTEM = (
    "你是一名严谨的文档核对员。你只能使用用户提供的资料回答，不得使用资料以外的知识。"
    "资料中可能出现同名的项目、版本、月份、批次或指标，回答前先核对这几项是否完全一致。"
    "题目里的指标名称可能与资料中的措辞不完全相同。遇到比例类指标（率、百分比）时，"
    "只要资料给出了可用的计数，就必须按资料写明的口径相除并输出百分数，"
    "不得因为资料里没有出现该指标的名字而回答「证据不足」。"
    "如果需要把两段资料里的数字相除、相减或比较才能得到答案，就计算后输出结果。"
    "只有当题目所问的具体对象（型号、编号、名称、字段）在资料中完全没有出现，"
    "或所需的分母无法确定时，才把 answer 写成「证据不足」；"
    "此时 citations 列出你检查过的、最相关的段落ID。"
    "answer 只写答案本身，严格按题目要求的形式。"
    "citations 必须是上面【可用资料】中实际出现过的段落ID。"
    "只输出一个 JSON 对象，不要输出任何解释文字，不要使用 Markdown 代码块。"
)


def prepare_messages(question, passages):
    """返回 [{"role": "system", ...}, {"role": "user", ...}]。"""
    blocks = []
    for p in passages:
        blocks.append(f"[{p['id']}] 来源：{p['source']}\n{p['text']}")
    materials = "\n\n".join(blocks)
    user = (
        f"【题目】\n{question}\n\n"
        f"【可用资料】\n{materials}\n\n"
        "【输出要求】\n只输出一个 JSON 对象，格式如下：\n"
        '{"answer": "简短答案", "citations": ["段落ID"]}\n'
        "citations 里的段落ID 必须来自上面【可用资料】中实际出现过的ID。"
    )
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]


PROJ = re.compile(r'[\u4e00-\u9fff]{2}项目')
VER = re.compile(r'R\d+')
MON = re.compile(r'\d{4}-\d{2}')
BATCH = re.compile(r'[A-Z]{2}\d{2}')
KEYWORDS = ('正式', '压力组', '探索组', '迁移批次', '复核补页', '单并发', '同机', '夜间组', '校内组')


def _score(p, proj, ver, mon, kws):
    t = p['text']
    s = 0
    for x in proj:
        if x in t:
            s += 3
    for x in ver:
        if x in t:
            s += 2
    for x in mon:
        if x in t:
            s += 2
    for k in kws:
        if k in t:
            s += 2
    return s


def improve(question, passages):
    """只重排、不删减：七段全保留，仅把最相关的提到前面。"""
    proj = set(PROJ.findall(question))
    ver = set(VER.findall(question))
    mon = set(MON.findall(question))
    kws = [k for k in KEYWORDS if k in question]

    scored = [(_score(p, proj, ver, mon, kws), p) for p in passages]
    scored.sort(key=lambda x: x[0], reverse=True)

    code = None
    for _, p in scored:
        m = BATCH.search(p['text'])
        if m:
            code = m.group(0)
            break

    if code:
        scored.sort(key=lambda x: (code in x[1]['text'], x[0]), reverse=True)

    return [p for _, p in scored]