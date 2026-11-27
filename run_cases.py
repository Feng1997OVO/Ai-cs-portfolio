import json
import subprocess
import time
from collections import defaultdict
from datetime import datetime

from chatbot import Chatbot

CASES_FILE = "cases.json"


def git_hash():
    """当前 commit，用来对上「哪版 prompt 出的结果」"""
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        return out.decode().strip()
    except Exception:
        return "unknown"


def load_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_session(items):
    bot = Chatbot()
    rows = []
    for case in items:
        q = case["question"]
        if case.get("policy"):
            q = f"【已选保单：{case['policy']}】{q}"
        start = time.time()
        try:
            ans = bot.chat(q)
            status = "OK"
        except Exception as e:
            ans = f"[异常] {e}"
            status = "ERROR"
        cost = time.time() - start
        rows.append((case["id"], case.get("session", "-"), q, ans, status, cost))
        print(f"  #{case['id']} {status} {cost:.1f}s")
        time.sleep(1)
    return rows


def save(rows):
    now = datetime.now()
    path = f"results_{now:%m%d_%H%M}.md"       # 自动命名，永不覆盖
    lines = [
        f"# 测试结果　{now:%Y-%m-%d %H:%M:%S}",
        f"prompt commit：{git_hash()}",
        f"共 {len(rows)} 条",
        "",
    ]
    for cid, sid, q, ans, status, cost in rows:
        lines += [f"## #{cid}　[{sid}]　{status}　{cost:.1f}s", "",
                  f"**问**：{q}", "", f"**答**：{ans}", "", "---", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n已保存：{path}")


if __name__ == "__main__":
    groups = defaultdict(list)
    for c in load_cases():
        groups[c.get("session", f"single-{c['id']}")].append(c)

    rows = []
    for sid, items in groups.items():
        print(f"=== 会话 {sid}（{len(items)} 条）===")
        rows.extend(run_session(items))
    save(rows)