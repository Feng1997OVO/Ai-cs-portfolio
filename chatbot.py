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
        self.messages = [{"role": "system", "content": "你是客服助手，回答简洁友好"}]

        self.headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


    def chat(self, question: str):
        self.messages.append({"role": "user", "content": question})
        history = [self.messages[0]] + self.messages[1:][-(MAX_TURNS * 2):]
        data = {"model": "deepseek-chat", "messages": history, "temperature": 0.1}

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
