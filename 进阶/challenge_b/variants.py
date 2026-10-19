"""语义等价变体与自造边界：不改 data.json，每个案例用独立 Engine（缓存清零）。"""
import copy, json
from pathlib import Path
from challenge import Engine

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
CASES = {c['id']: c for c in DATA['cases']}
CORPUS = DATA['corpus']


def run(label, request, draft):
    out = Engine().evaluate(copy.deepcopy(request), CORPUS, copy.deepcopy(draft))
    return {'label': label, 'request': request,
            'evidence': [b['id'] for b in out['evidence']],
            'citations': out['citations'],
            'locator_status': out['locator_status'],
            'support_status': out['support_status'],
            'judgment_source': out['judgment_source'],
            'cache_hit': out['cache_hit'], 'status': out['status'],
            'answer': out['answer']}


V = []

# V1 语义等价：R04 的 query 换词序，词集合不变
r1 = copy.deepcopy(CASES['R04']['request']); r1['query'] = 'gpu resource cancel'
V.append(run('V1_R04_query_reordered', r1, CASES['R04']['draft']))

# V2 语义等价：R05 的 query 换词序，词集合不变
r2 = copy.deepcopy(CASES['R05']['request']); r2['query'] = 'beta metadata'
V.append(run('V2_R05_query_reordered', r2, CASES['R05']['draft']))

# B1 自造边界：文档存在但快照不存在（data.json 里没有这个案例）
r3 = copy.deepcopy(CASES['R01']['request']); r3['snapshot'] = 'v9'
V.append(run('B1_snapshot_not_exist', r3, CASES['R01']['draft']))

out = ROOT.parents[1] / 'runs' / 'variants.json'
out.write_text(json.dumps(V, ensure_ascii=False, indent=2), encoding='utf-8')
print(out)
for v in V:
    print(v['label'], '|ev:', v['evidence'], '|cit:', v['citations'],
          '|loc:', v['locator_status'], '|sup:', v['support_status'],
          '|status:', v['status'], '|hit:', v['cache_hit'])