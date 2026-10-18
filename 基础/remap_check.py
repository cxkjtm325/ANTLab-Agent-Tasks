"""不调用模型的检查：ID 重映射 / 输入顺序打乱后，改进方法是否仍按内容工作。"""
import json, random, copy
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'starter'))
import student

cases = json.loads((BASE / 'data/cases.json').read_text(encoding='utf-8'))
rng = random.Random(20261016)

for c in cases:
    if c['split'] != 'dev':
        continue
    by_id = {p['id']: p for p in c['passages']}
    original = [copy.deepcopy(by_id[i]) for i in c['conditions']['R0']]
    baseline = [p['text'] for p in student.improve(c['question'], copy.deepcopy(original))]

    mp = {p['id']: "P9" + str(9000 + i) for i, p in enumerate(original)}
    renamed = [{**copy.deepcopy(p), 'id': mp[p['id']]} for p in original]
    out_a = [p['text'] for p in student.improve(c['question'], copy.deepcopy(renamed))]

    shuffled = copy.deepcopy(original)
    rng.shuffle(shuffled)
    out_b = [p['text'] for p in student.improve(c['question'], copy.deepcopy(shuffled))]

    print(c['id'],
          '| A_ID重映射:', '一致' if out_a == baseline else '不一致',
          '| B_输入打乱:', '前两位一致' if out_b[:2] == baseline[:2] else '前两位变了')