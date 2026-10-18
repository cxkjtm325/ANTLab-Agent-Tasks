"""逐例判分：机械部分自动判，答案对错读人工答案表 answer_key.json。
用法（在 基础 目录下）：py results/scoring/score.py
"""
import csv, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
RUNS = BASE / "runs"
OUT = BASE / "results" / "results.csv"

KEY = json.loads((HERE / "answer_key.json").read_text(encoding="utf-8"))
DEV = {d["id"]: d for d in json.loads((BASE / "data" / "dev_answers.json").read_text(encoding="utf-8"))}


def content_of(d):
    r = d.get("response")
    if not isinstance(r, dict):
        return None
    try:
        return r["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None


def parse_answer(text):
    if not isinstance(text, str):
        return None
    t = re.sub(r"^```(?:json)?\s*", "", text.strip())
    t = re.sub(r"\s*```$", "", t)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or "answer" not in obj or "citations" not in obj:
        return None
    return obj


def norm(s):
    return str(s).strip().replace(" ", "").replace("％", "%")


def same_answer(got, key):
    g = norm(got)
    cand = {norm(key["answer"])} | {norm(a) for a in key.get("aliases", [])}
    if g in cand:
        return True
    if g.endswith("%"):
        try:
            gv = float(g[:-1])
        except ValueError:
            return False
        for c in cand:
            if c.endswith("%"):
                try:
                    if abs(gv - float(c[:-1])) < 1e-9:
                        return True
                except ValueError:
                    pass
    return False


def main():
    runs = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(RUNS.glob("*.json"))]
    runs.sort(key=lambda d: d.get("utc", ""))

    seen = {}
    rows = []
    for d in runs:
        k = (d["case_id"], d["condition"], d["variant"])
        seen[k] = seen.get(k, 0) + 1
        attempt = "首次" if seen[k] == 1 else "重试%d" % (seen[k] - 1)

        text = content_of(d)
        obj = parse_answer(text) if d.get("status") == "ok" else None
        usage = d.get("usage") or {}
        sel = d.get("selected_passage_ids") or []
        judge, reason = "未判", ""

        if d.get("status") != "ok":
            judge, reason = "技术失败", "API状态=" + str(d.get("status")) + " HTTP=" + str(d.get("http_status"))
        elif obj is None:
            judge, reason = "格式错误", "内容不是含 answer/citations 的合法JSON对象"
        else:
            key = KEY.get(d["case_id"]) or None
            if key is None and d["case_id"] in DEV:
                key = {"answer": DEV[d["case_id"]]["answer"], "aliases": DEV[d["case_id"]].get("aliases", []),
                       "supporting_ids": DEV[d["case_id"]].get("evidence_ids", []), "my_reason": DEV[d["case_id"]]["reason"]}
            if key is None:
                judge, reason = "未判", "没有答案表"
            elif same_answer(obj.get("answer"), key):
                judge, reason = "正确", ""
            else:
                judge, reason = "错误", "应为 " + key["answer"] + "；" + key.get("my_reason", "")

        cits = obj.get("citations") if obj else None
        rows.append({
            "run_id": d.get("run_id"),
            "split": d.get("split"),
            "case_id": d["case_id"],
            "condition": d["condition"],
            "variant": d["variant"],
            "attempt": attempt,
            "mode": d.get("mode"),
            "api_status": d.get("status"),
            "http_status": d.get("http_status"),
            "elapsed_seconds": round(d["elapsed_seconds"], 3) if d.get("elapsed_seconds") is not None else "",
            "usage_source": "API usage字段" if d.get("usage") else "",
            "prompt_tokens": usage.get("prompt_tokens", ""),
            "completion_tokens": usage.get("completion_tokens", ""),
            "format_ok": "是" if obj else "否",
            "answer_raw": (obj or {}).get("answer", ""),
            "citations": json.dumps(cits, ensure_ascii=False) if cits is not None else "",
            "citations_from_input": "是" if cits is not None and all(c in sel for c in cits) else "否",
            "citations_cover_key_ids": "",
            "judgment": judge,
            "reason": reason,
        })

    # 引用是否覆盖必需证据（机械判定，不等于语义支持）
    for r in rows:
        key = KEY.get(r["case_id"])
        if not key or not r["citations"]:
            continue
        cits = json.loads(r["citations"])
        r["citations_cover_key_ids"] = "是" if set(key["supporting_ids"]) <= set(cits) else "否"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("已写出", OUT, "共", len(rows), "行")
    agg = {}
    for r in rows:
        key = (r["split"], r["condition"], r["variant"])
        a = agg.setdefault(key, [0, 0])
        a[1] += 1
        if r["judgment"] == "正确":
            a[0] += 1
    for k in sorted(agg):
        print(k, "%d/%d" % (agg[k][0], agg[k][1]))


if __name__ == "__main__":
    main()