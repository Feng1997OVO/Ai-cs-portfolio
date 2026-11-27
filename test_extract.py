import json
from collections import defaultdict

from extract import extract

with open("cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

stat = defaultdict(lambda: [0, 0])      # 类目 -> [正确数, 总数]
right = 0

for c in cases:
    try:
        r = extract(c["question"])
        actual = r["intent"]
    except Exception as e:
        print(f'❌ #{c["id"]} 出错：{e}')
        continue

    expected = c["expect_intent"]
    ok = actual == expected
    right += ok

    stat[expected][1] += 1
    if ok:
        stat[expected][0] += 1

    flag = "✅" if ok else "❌"
    print(f'{flag} #{c["id"]:>2} 期望:{expected:<6} 实际:{actual:<6} | {c["question"][:24]}')

# —— 总体 ——
print(f"\n意图准确率：{right}/{len(cases)} = {right / len(cases) * 100:.0f}%")

# —— 分类 ——
print("\n各类准确率（按样本数排序）：")
for k, (r, t) in sorted(stat.items(), key=lambda x: -x[1][1]):
    pct = r / t * 100
    note = "   ← 样本不足，百分比不可信" if t < 3 else ""
    print(f"  {k:<8} {r}/{t}  {pct:>3.0f}%{note}")