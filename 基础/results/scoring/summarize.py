"""按 (split, 条件, 变体) 汇总 results.csv，输出 markdown 表。"""
import csv, statistics, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE.parent / "results.csv", encoding="utf-8-sig")))

g = collections.defaultdict(list)
for r in rows:
    g[(r["split"], r["condition"], r["variant"])].append(r)

print("| split | 条件 | 变体 | n | 正确 | 技术失败 | 格式错误 | 正确率 | 耗时中位(s) | 引用合规 | 覆盖必需证据 |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for k in sorted(g):
    v = g[k]
    n = len(v)
    ok = sum(r["judgment"] == "正确" for r in v)
    fail = sum(r["judgment"] == "技术失败" for r in v)
    bad = sum(r["judgment"] == "格式错误" for r in v)
    el = [float(r["elapsed_seconds"]) for r in v if r["elapsed_seconds"]]
    med = "%.2f" % statistics.median(el) if el else "-"
    cit = sum(r["citations_from_input"] == "是" for r in v)
    cov = sum(r["citations_cover_key_ids"] == "是" for r in v)
    print("| %s | %s | %s | %d | %d | %d | %d | %.0f%% | %s | %d | %d |"
          % (k[0], k[1], k[2], n, ok, fail, bad, 100.0 * ok / n, med, cit, cov))