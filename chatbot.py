import datetime
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
URL= "https://api.deepseek.com/v1/chat/completions"
API_KEY=os.getenv("DEEPSEEK_API_KEY")

FALLBACK = "抱歉，您的问题暂时无法核实，这边为您转接专员人工服务"
MAX_TURNS = 10
SYSTEM_PROMPT = """你是保险理赔客服。回答遵循以下规则：
【先定位，再判断】
回答前先确认三件事，缺任何一项都不要下结论：
1. 哪一份保单（用户可能有多份，必须明确）；
2. 什么场景（门诊 / 住院 / 药店购药 / 线上问诊）；
3. 什么时间（就诊日或入院日，用于判断等待期）。

【分层排查】
按「保单生效 → 等待期 → 既往症 / 责任免除 → 赔付范围」的顺序判断，
不要跳步，也不要在前置条件未核实前给结论。

【回答策略】
- 结论确定时（赔付比例、免赔额、责任范围）：直接引用条款原文，不加兜底话术；
- 结论不确定时（既往症程度、医院等级、条款冲突）：说明不确定 + 建议转专员。
【必须判断，不得推给审核】
以下三类必须直接给结论，不要说「需审核判定」：

1. 时间可算的：如「已投保 4 个月」，超过常见 30/90 天等待期，
   直接说明「已过等待期」；
2. 日期可比的：就诊日期早于保单生效日，直接说明「不在保障期间」；
3. 条款明确列明的责任免除：体检、怀孕、整容、牙齿、既往症，
   直接说明「属于责任免除」。

【合规红线】
不承诺赔付结果，只说「需提交材料后由理赔审核判定」；
不解释超出条款范围的内容；SOP 与用户诉求冲突时，以合规为准。

【信息不足】
影响结论的关键信息缺失时才反问（险种、出险时间、是否首次投保）；
能按 SOP 直接回答的，不要反问。
同一问题连续 2 轮没有新信息，转人工。

【表达】
回答控制在 3–4 句；同一问题最多换 3 种说法，每次换角度（换人话 → 换场景 → 转人工）；
不要用不同的话重复同一个意思。"""


def build_system_prompt():
    today = datetime.date.today().isoformat()
    return f"今天是{today}.\n" + SYSTEM_PROMPT
class Chatbot:
    def __init__(self):
        self.messages = [{"role": "system", "content": build_system_prompt()}]
        self.headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


    def chat(self, question: str):
        self.messages.append({"role": "user", "content": question})
        history = [self.messages[0]] + self.messages[1:][-(MAX_TURNS * 2):]
        data = {"model": "deepseek-chat", "messages": history, "temperature": 0.1,"max_tokens":300,}

        for attempt in range(3):
            try:
                resp = requests.post(URL, headers=self.headers, json=data, timeout=15)
                resp.raise_for_status()
                reply = resp.json()["choices"][0]["message"]["content"]
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            except requests.Timeout:
                if attempt == 2:
                    break
                time.sleep(1)
            except requests.HTTPError as e:
                print(f"[ERROR]HTTP{e.response.status_code}")
                break
            except Exception as e:
                print(f"[ERROR]{e}")
                break

        self.messages.append({"role": "assistant", "content": FALLBACK})
        return FALLBACK


if __name__ == "__main__":
    bot = Chatbot()  # 创建一个机器是实例自动跑__init__
    print("客服助手已经启动，输入Q退出对话")
    while True:
        user_input = input("您的问题：")
        if user_input == "Q":
            print("对话结束，感谢您的咨询")
            break  # 跳出循环 结束程序
        ai_reply = bot.chat(user_input)
        print(ai_reply)
