import json
import time
from collections import defaultdict

from extract import extract

with open("cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

stat = defaultdict(lambda: [0, 0])
right = wrong = error = 0

for c in cases:
    actual = None
    last_err = None

    for attempt in range(3):                    # 最多试 3 次
        try:
            actual = extract(c["question"])["intent"]
            break
        except Exception as e:
            last_err = e
            if attempt < 2:
                time.sleep(2)                   # 网络抖动，等两秒再来

    if actual is None:
        error += 1
        print(f'⚠️  #{c["id"]:>2} 调用失败，不计入准确率：{last_err}')
        continue

    expected = c["expect_intent"]
    ok = actual == expected
    if ok:
        right += 1
    else:
        wrong += 1

    stat[expected][1] += 1
    if ok:
        stat[expected][0] += 1

    flag = "✅" if ok else "❌"
    print(f'{flag} #{c["id"]:>2} 期望:{expected:<6} 实际:{actual:<6} | {c["question"][:24]}')

valid = right + wrong
print(f"\n有效测试：{valid} 条（跳过 {error} 条）")
print(f"意图准确率：{right}/{valid} = {right / valid * 100:.0f}%" if valid else "无可测数据")

print("\n各类准确率（按样本数排序）：")
for k, (r, t) in sorted(stat.items(), key=lambda x: -x[1][1]):
    pct = r / t * 100
    note = "   ← 样本不足，百分比不可信" if t < 3 else ""
    print(f"  {k:<8} {r}/{t}  {pct:>3.0f}%{note}")