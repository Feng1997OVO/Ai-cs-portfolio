import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
URL= "https://api.deepseek.com/v1/chat/completions"
API_KEY=os.getenv("DEEPSEEK_API_KEY")

FALLBACK = "抱歉，您的问题暂时无法核实，这边为您转接专员人工服务"
MAX_TURNS = 10


class Chatbot:
    def __init__(self):
        SYSTEM_PROMPT = """你是保险理赔客服助手。回答要求：
1. 信息不全时先反问补充（险种、住院时间、是否首次投保），不要急着给结论；
2. 只依据已知信息回答；不确定时说「这个我需要为您转接专员核实」，不得猜测；
3. 不得承诺赔付结果，只能说「需提交材料后由理赔审核判定」；
4. 涉及金额、比例、时效，必须说明「以条款为准」；
5. 回答控制在 3 句话以内，不要用不同的话重复同一个意思。
6.合规声明只在给出结论时出现一次，收集信息阶段不要重复。
7.给出结论时按「判断 → 依据 → 下一步」三段说，下一步必须给具体动作（提交材料 / 转人工 / 复核）。
8.涉及时间的，先算出间隔天数再判断。
9.信息足够时要给带前提的判断（若A则X，若B则Y），不要把判断全部推给审核；只有信息不足或超出权限时才转人工。"""

        self.messages = [{"role": "system", "content":SYSTEM_PROMPT}]
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
